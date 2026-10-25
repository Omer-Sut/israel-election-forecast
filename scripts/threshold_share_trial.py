"""E020: matched past-only reported-share ablations, separate from frozen models."""
import argparse
import base64
import copy
from datetime import date, timedelta
import gzip
import hashlib
from html import escape
import json
import math
from pathlib import Path
import statistics
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import baseline, prepare_threshold_data as data, threshold_trial as tt

ROOT = baseline.ROOT
CONFIG = ROOT / 'config/threshold-share-trial.json'
FEATURES = {
    'seat': ['fraction_firms_projecting_seats', 'mean_positive_seats'],
    'missing': ['fraction_firms_projecting_seats', 'mean_positive_seats', 'reported_share_coverage'],
    'share': ['fraction_firms_projecting_seats', 'mean_positive_seats', 'reported_share_coverage', 'mean_reported_pct'],
}


def select_history(polls, cutoff, window):
    """Explicit empty coverage; reject future revisions and stale fieldwork first."""
    end = date.fromisoformat(cutoff); start = end - timedelta(days=window)
    eligible = []
    for raw in polls:
        p = copy.deepcopy(raw)
        if p.get('source_updated_on') is None:
            p.pop('source_updated_on', None)
        publication = date.fromisoformat(p['published_on'])
        available = date.fromisoformat(p.get('source_updated_on', p['published_on']))
        effective = date.fromisoformat(p.get('fieldwork_end') or p['published_on'])
        if effective > publication:
            raise ValueError('Fieldwork after publication')
        if publication <= end and available <= end and effective >= start:
            eligible.append(p)
    if not eligible:
        return [], []
    selected, _ = baseline.select_polls(eligible, cutoff, window)
    return selected, sorted(eligible, key=lambda p: (p['pollster_group'], p['published_on'], p['id']))


def cases_from_overlay(overlay, horizon, mode, config):
    old = tt.historical_cases(baseline.load_json(tt.CONFIG)); cases = []; coverage = []
    for original in old:
        cutoff = (date.fromisoformat(original['election_date']) - timedelta(days=horizon)).isoformat()
        polls = [p for p in overlay['releases'] if p['election_id'] == original['election_id']]
        selected, history = select_history(polls, cutoff, config['window_days'])
        coverage.append({'election': original['election_id'], 'cutoff': cutoff,
            'firms': len(selected), 'selected_ids': [p['id'] for p in selected],
            'history_ids': [p['id'] for p in history],
            'status': 'available' if selected else 'no_eligible_release'})
        # The T-1 primary preserves three-firm coverage; early sensitivity may have one.
        if not selected or (horizon == 1 and len(selected) < 3):
            continue
        vectors = [[p['reported_seats'].get(key, 0) for key in original['ids']] for p in selected]
        case = {k: copy.deepcopy(original[k]) for k in ('election_id', 'election_date', 'ids', 'actual', 'period')}
        case.update(cutoff=cutoff, vectors=vectors,
            anchor=[statistics.mean(c) for c in zip(*vectors)], selected_polls=selected,
            percentage_polls=selected if mode == 'latest' else history)
        cases.append(case)
    return cases, coverage


def rows(case, config):
    result = []
    for index, key in enumerate(case['ids']):
        seats = [v[index] for v in case['vectors']]; positive = [v for v in seats if v > 0]
        groups = {}
        for p in case['percentage_polls']:
            groups.setdefault(p['pollster_group'], []).append(p)
        values = []; coverage = []; evidence = []
        for group in sorted(groups):
            polls = groups[group]
            observed = [(p, p.get('reported_below_threshold_pct', {}).get(key)) for p in polls]
            known = [(p, v) for p, v in observed if v is not None]
            coverage.append(len(known) / len(polls))
            if known:
                values.append(statistics.mean(v for p, v in known))
                evidence.extend({'poll_id': p['id'], 'firm': group, 'published_on': p['published_on'],
                    'reported_pct': v} for p, v in known)
        candidate = bool(positive or values) and statistics.mean(seats) <= config['candidate_mean_max'] and max(seats) <= config['candidate_poll_max']
        result.append({'id': key, 'candidate': candidate, 'poll_seats': seats,
            'seat': [len(positive)/len(seats), statistics.mean(positive) if positive else 0.],
            'coverage': statistics.mean(coverage), 'share': statistics.mean(values) if values else None,
            'percentage_evidence': evidence, 'all_zero_with_percentage': not positive and bool(values),
            'positive_seats': [max(config['minimum_positive_seats'], v) for v in positive] or [config['all_zero_positive_branch_seats']]})
    return result


def features(row, arm):
    return row['seat'] + ([row['coverage']] if arm in ('missing', 'share') else []) + ([row['share']] if arm == 'share' else [])


def fit(train, targets, arm, alpha):
    """Train-only weighted imputation/scaling and unpenalized-intercept ridge logit."""
    import numpy as np
    from scipy.special import expit
    from scipy.optimize import minimize
    weights = np.array([r['weight'] for r in train], dtype=float); weights /= weights.sum()
    raw = np.array([features(r, arm) for r in train], dtype=float)
    impute = []
    for j in range(raw.shape[1]):
        observed = np.isfinite(raw[:, j])
        impute.append(float(weights[observed] @ raw[observed, j] / weights[observed].sum()) if observed.any() else 0.)
        raw[~observed, j] = impute[-1]
    center = weights @ raw; scale = np.sqrt(weights @ ((raw-center)**2)); scale[scale < 1e-12] = 1.
    z = np.column_stack([np.ones(len(raw)), (raw-center)/scale])
    y = np.array([r['represented'] for r in train]); mass = float(weights @ y)
    penalty = np.diag([0.] + [alpha]*raw.shape[1])
    if len(set(y.tolist())) == 1:
        campaigns = len({r['election'] for r in train}); p = (mass*campaigns+.5)/(campaigns+1)
        beta = np.array([math.log(p/(1-p))]+[0.]*raw.shape[1]); status = 'single_class_fallback'; gradient = None
    else:
        def objective(b):
            eta = z @ b
            return float(weights @ (np.logaddexp(0, eta)-y*eta)+.5*b@penalty@b), z.T @ (weights*(expit(eta)-y))+penalty@b
        def hessian(b):
            p = expit(z@b)
            return z.T @ ((weights*p*(1-p))[:, None]*z)+penalty
        initial = np.array([math.log(mass/(1-mass))]+[0.]*raw.shape[1])
        solved = minimize(objective, initial, jac=True, hess=hessian, method='trust-exact', options={'gtol': 1e-11, 'maxiter': 100})
        beta = solved.x; gradient = float(np.max(np.abs(objective(beta)[1])))
        if gradient > 1e-8:
            raise ValueError('Share-model fit did not converge')
        status = 'converged'
    probabilities = {}
    for row in targets:
        if row['candidate']:
            x = np.array(features(row, arm), dtype=float); x[~np.isfinite(x)] = np.array(impute)[~np.isfinite(x)]
            probabilities[row['id']] = float(expit(np.r_[1., (x-center)/scale]@beta))
    return probabilities, {'arm': arm, 'alpha': alpha, 'feature_names': FEATURES[arm], 'status': status,
        'impute': impute, 'centers': center.tolist(), 'scales': scale.tolist(), 'coefficients': beta.tolist(),
        'gradient_max': gradient, 'training_rows': [{k: r[k] for k in ('election', 'id', 'represented', 'weight')} for r in train],
        'training_campaigns': sorted({r['election'] for r in train})}


def predict(case, past, config, arm, alpha):
    train = []
    for old in past:
        if old['election_date'] >= case['election_date']:
            raise ValueError('Target/future campaign in training')
        eligible = [r for r in rows(old, config) if r['candidate']]
        for row in eligible:
            train.append({**row, 'election': old['election_id'], 'represented': int(old['actual'][row['id']]>0), 'weight': 1/len(eligible)})
    if len({r['election'] for r in train}) < config['minimum_training_campaigns']:
        return None
    target = rows(case, config); probabilities, fitted = fit(train, target, arm, alpha)
    distributions = []
    for row in target:
        if row['candidate']:
            p = probabilities[row['id']]; positive = row['positive_seats']
            dist = [(0., 1-p)]+[(v, p/len(positive)) for v in positive]
        else:
            dist = [(v, 1/len(row['poll_seats'])) for v in row['poll_seats']]
        distributions.append(dist)
    fixed = {case['ids'].index('other_qualifying_lists'): 0} if 'other_qualifying_lists' in case['ids'] else {}
    seats = tt.expected_loss_decision(distributions, case['anchor'], minimum=3, fixed=fixed)
    return {'seats': seats, 'probabilities': probabilities, 'fit': fitted}


def current_case():
    case = tt.current_case(); audit = baseline.load_json(ROOT/'data/snapshots/vote-input-audit-2026-10-24/audit.json')
    shares = {p['poll_id']: p['reported_vote_percentages'] for p in audit['polls']}
    if set(shares) != {p['id'] for p in case['selected_polls']}:
        raise ValueError('Current percentage and seat releases differ')
    case['percentage_polls'] = [{**p, 'reported_below_threshold_pct': shares[p['id']]} for p in case['selected_polls']]
    return case


def build(config=None):
    config = config or baseline.load_json(CONFIG); overlay = data.build(); panels = {}
    methods = [('seat_a0.1', 'seat', .1), ('missing_a0.1', 'missing', .1), ('share_a0.1', 'share', .1), ('share_a0.01', 'share', .01), ('share_a1', 'share', 1.)]
    for horizon in config['horizons_days']:
        for mode in config['percentage_modes']:
            cases, coverage = cases_from_overlay(overlay, horizon, mode, config); records = []; past = []; selections = []
            for case in cases:
                target = rows(case, config); now = tt.controls(case)
                for ident, arm, alpha in methods:
                    item = predict(case, past, config, arm, alpha)
                    if item is not None:
                        now[ident] = item
                learned = 'seat_a0.1' in now; choice = tt.select(records, now)
                for ident, item in now.items():
                    records.append({'election': case['election_id'], 'election_date': case['election_date'], 'period': case['period'],
                        'cutoff': case['cutoff'], 'method': ident, 'learned_available': learned,
                        'candidate_ids': [r['id'] for r in target if r['candidate']], 'target_rows': [r for r in target if r['candidate']],
                        'party_ids': case['ids'], **item, **tt.score(case, item, target)})
                selected = next(r for r in records if r['election']==case['election_id'] and r['method']==choice['id'])
                selections.append({'election': case['election_id'], **choice, 'seat_l1': selected['seat_l1']})
                past.append(case)
            summaries = {}
            for ident in list(tt.CONTROLS)+[m[0] for m in methods]:
                scored = [r for r in records if r['method']==ident and r['learned_available']]
                ps = [r['candidate_brier'] for r in scored if r['candidate_brier'] is not None]
                periods = sorted({r['period'] for r in scored})
                summaries[ident] = {'folds': len(scored), 'mean_seat_l1': statistics.mean(r['seat_l1'] for r in scored) if scored else None,
                    'equal_period_seat_l1': statistics.mean(statistics.mean(r['seat_l1'] for r in scored if r['period']==p) for p in periods) if periods else None,
                    'brier': statistics.mean(ps) if ps else None,
                    'false_positive': sum(len(r['false_positive']) for r in scored), 'false_negative': sum(len(r['false_negative']) for r in scored)}
            current = {}
            # Current only has audited latest-release percentages. Do not invent older coverage.
            if horizon == 1 and mode == 'latest':
                case = current_case()
                for ident, arm, alpha in methods:
                    current[ident] = predict(case, past, config, arm, alpha)
            panels[f't{horizon}_{mode}'] = {'coverage': coverage, 'records': records, 'summaries': summaries,
                'selections': selections, 'current': current}
    return {'config': config, 'panels': panels, 'decision': config['decision'],
        'limits': ['Repeated campaigns/firm/list outcomes are dependent; no untouched holdout or calibrated crossing probabilities.',
            'Reported percentages have unknown denominator/undecided treatment, not valid-vote shares.',
            'Percentage reporting is selective. Candidate roster includes all-zero lists with any observed share in the chosen mode, identically in all arms.',
            'For all-zero candidates, conditional representation is assigned four seats as an explicit assumption, not inferred votes.',
            'Latest-firm seat projections are identical across arms; eligible-history shares are a separately labelled source-age sensitivity, never backfilled latest values.',
            'History averages within firm then across observed firms; coverage averages within every eligible firm. No independent-sample weight for repeated releases.',
            'T-8 may have one firm and different campaign coverage; compare arms only within a panel, not panel averages as model gains.',
            'Current percentages are only the audited seven latest releases; its October24 cutoff is T-3, not historical T-1.',
            'Current/history firm count and reporting patterns differ. Combined other is fixed at zero; no new unmapped list is predicted.',
            'Sum120 and zero-or-at-least3 are seat-space decision assumptions, not a complete Bader–Ofer simulation.']}


def write(report, out):
    out.mkdir(parents=True, exist_ok=True)
    def save(name, text): (out/name).write_text(text, encoding='utf-8', newline='\n')
    save('results.json', json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    summary = {'config': report['config'], 'decision': report['decision'], 'limits': report['limits'], 'panels': {}}
    for panel, item in report['panels'].items():
        summary['panels'][panel] = {'coverage': item['coverage'], 'summaries': item['summaries'], 'selections': item['selections'],
            'records': [{k: r[k] for k in ('election', 'method', 'learned_available', 'candidate_ids', 'seat_l1',
                'candidate_brier', 'candidate_log_loss', 'false_positive', 'false_negative')} for r in item['records']],
            'current': {m: None if r is None else {'seats': r['seats'], 'probabilities': r['probabilities']} for m, r in item['current'].items()}}
    save('summary.json', json.dumps(summary, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    lines = ['# E020: matched reported-percentage ablation', '', report['decision'], '',
        'Primary: T−1/latest, fixed alpha0.1. Missingness-only isolates selective coverage; other panels/penalties are sensitivity diagnostics, not a new grid-selected winner.', '']
    for panel, item in report['panels'].items():
        lines += ['## '+panel, '', '| Method | Matched folds | Mean seat L1 | Equal-period L1 | Brier | FP/FN |', '|---|---:|---:|---:|---:|---:|']
        for method, s in item['summaries'].items():
            fmt = lambda v: '—' if v is None else f'{v:.4f}'
            lines.append(f"|{method}|{s['folds']}|{fmt(s['mean_seat_l1'])}|{fmt(s['equal_period_seat_l1'])}|{fmt(s['brier'])}|{s['false_positive']}/{s['false_negative']}|")
        lines += ['', 'Earlier-OOF-only selector: '+str(item['selections']), '']
    lines += ['## Current diagnostic (T−3, latest sources only)', '', '| Method | Reservists seats / p | Amcha seats / p |', '|---|---:|---:|']
    ids = current_case()['ids']
    for method, r in report['panels']['t1_latest']['current'].items():
        if r is None: continue
        cells = [f"{r['seats'][ids.index(k)]} / {r['probabilities'].get(k, float('nan')):.4f}" for k in ('reservists_economic', 'amcha_yisrael')]
        lines.append('|'+method+'|'+'|'.join(cells)+'|')
    lines += ['', '![Matched campaign errors](matched-errors.svg)', '', '![Training support and extrapolation](support-diagnostics.svg)', '', '## Limits', '']+['- '+x for x in report['limits']]
    save('analysis.md', '\n'.join(lines)+'\n')
    historical = baseline.load_json(ROOT/'config/threshold-trial.json')['historical_config']
    hc = baseline.load_json(ROOT/historical)
    paths = ['scripts/threshold_share_trial.py', 'config/threshold-share-trial.json', 'scripts/prepare_threshold_data.py',
        'scripts/threshold_trial.py', 'scripts/baseline.py', 'scripts/forecast_review.py', 'scripts/experiments.py',
        'scripts/backtest.py', 'config/threshold-trial.json', 'config/forecast-review.json', 'config/poll-mappings.json',
        'config/submission-fields.json', 'data/snapshots/polls-2026-10-24.json', 'requirements-turnout.txt', historical, hc['outcomes_path'],
        'data/snapshots/vote-input-audit-2026-10-24/audit.json', 'reports/forecast-decision-2026-10-25/forecast.json']
    paths += ['data/snapshots/threshold-data-2026-10-25/'+x for x in ('protocol.json', 'additions.json', 'source-audit.json')]
    paths += [s['polls_path'] for s in hc['elections']]
    save('inputs-manifest.json', json.dumps({p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set(paths))}, indent=2)+'\n')
    plot(report, out)
    support_diagnostics(report, out)


def support_diagnostics(report, out):
    """Post-fit support warnings only; no modification of features or predictions."""
    primary = report['panels']['t1_latest']['records']; diagnostics = []
    for target in primary:
        if target['method'] != 'share_a0.1':
            continue
        campaigns = set(target['fit']['training_campaigns'])
        training = [row['share'] for r in primary if r['method']=='square_0or3' and r['election'] in campaigns
                    for row in r['target_rows'] if row['share'] is not None]
        lo = min(training) if training else None; hi = max(training) if training else None
        observed = [{'id': row['id'], 'reported_pct': row['share'],
                     'outside_training_range': lo is None or not lo <= row['share'] <= hi,
                     'p': target['probabilities'][row['id']]}
                    for row in target['target_rows'] if row['share'] is not None]
        diagnostics.append({'election': target['election'], 'training_observed_count': len(training),
            'training_observed_min': lo, 'training_observed_max': hi,
            'standardized_share_coefficient': target['fit']['coefficients'][-1],
            'observed_targets': observed})
    (out/'support-diagnostics.json').write_text(json.dumps(diagnostics, indent=2)+'\n', encoding='utf-8', newline='\n')
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="600" viewBox="0 0 1100 600"><rect width="1100" height="600" fill="white"/><g font-family="Arial,sans-serif" fill="#21384b">',
        '<text x="25" y="32" font-size="23">Why the percentage model is unstable</text>',
        '<text x="25" y="60" font-size="14">Primary T−1/latest. Range of measured training features versus measured target features.</text>']
    for i, d in enumerate(diagnostics):
        y = 125+i*95
        p.append(f'<text x="25" y="{y}" font-size="14">{escape(d["election"])}</text>')
        p.append(f'<path d="M300,{y}H1000" stroke="#dce2e6"/>')
        if d['training_observed_min'] is not None:
            x1 = 300+700*d['training_observed_min']/3.5; x2 = 300+700*d['training_observed_max']/3.5
            p.append(f'<path d="M{x1:.2f},{y}H{x2:.2f}" stroke="#4d839d" stroke-width="12"/>')
        for row in d['observed_targets']:
            x = 300+700*row['reported_pct']/3.5; color = '#bf513a' if row['outside_training_range'] else '#21384b'
            p.append(f'<circle cx="{x:.2f}" cy="{y}" r="5" fill="{color}"><title>{escape(row["id"])}: {row["reported_pct"]:.3f}%, p={row["p"]:.4f}</title></circle>')
        p.append(f'<text x="300" y="{y+27}" font-size="12">Observed training rows: {d["training_observed_count"]}; standardized share slope: {d["standardized_share_coefficient"]:.3f}</text>')
    for i in range(8):
        p.append(f'<text x="{292+i*100}" y="505" font-size="12">{i*.5:.1f}%</text>')
    p.append('<text x="25" y="550" font-size="14">Blue: training range. Dots: target shares; red means outside measured training range.</text><text x="25" y="580" font-size="13">Repeated party/campaign rows are dependent. No measured shares in September2019 target latest polls.</text></g></svg>')
    (out/'support-diagnostics.svg').write_text('\n'.join(p)+'\n', encoding='utf-8', newline='\n')


def plot(report, out):
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="930" viewBox="0 0 1160 930"><rect width="1160" height="930" fill="white"/><g font-family="Arial,sans-serif" fill="#21384b">',
        '<text x="25" y="30" font-size="22">Matched historical seat errors: percentages versus reporting coverage</text>',
        '<text x="25" y="55" font-size="13">Same sources, cutoff and candidate roster within each panel. Lower is better. Forecast unchanged.</text>']
    methods = ['square_0or3', 'seat_a0.1', 'missing_a0.1', 'share_a0.1']; colors = ['#777777', '#246e9b', '#b47822', '#8a4284']
    for index, (panel, item) in enumerate(report['panels'].items()):
        left = 60+(index%2)*570; top = 100+(index//2)*370
        records = [r for r in item['records'] if r['learned_available']]; dates = sorted({r['election_date'] for r in records})
        maximum = max([24]+[r['seat_l1'] for r in records])*1.1
        p.append(f'<text x="{left}" y="{top}" font-size="18">{escape(panel)}</text>')
        for k in range(5):
            y = top+260-k*55
            p.append(f'<path d="M{left},{y}h480" stroke="#dce2e6"/><text x="{left-30}" y="{y+4}" font-size="11">{maximum*k/4:.0f}</text>')
        for method, color in zip(methods, colors):
            pts = []
            for r in records:
                if r['method'] != method: continue
                x = left+35+410*dates.index(r['election_date'])/max(1,len(dates)-1); y = top+260-220*r['seat_l1']/maximum
                pts.append(f'{x:.2f},{y:.2f}')
                p.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="{color}"><title>{escape(method)} {r["election"]}: {r["seat_l1"]}</title></circle>')
            p.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2"/>')
        for j, day in enumerate(dates):
            x = left+410*j/max(1,len(dates)-1)
            p.append(f'<text x="{x}" y="{top+285}" font-size="11">{day}</text>')
    for j, (method, color) in enumerate(zip(methods, colors)):
        p.append(f'<text x="{25+j*285}" y="875" font-size="14" fill="{color}">{escape(method)}</text>')
    p.append('<text x="25" y="910" font-size="13">Sparse dependent campaigns; reporting denominators unknown. T−8 coverage differs; no cross-panel ranking.</text></g></svg>')
    (out/'matched-errors.svg').write_text('\n'.join(p)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, default=ROOT/'output/threshold-share-trial')
    args = parser.parse_args(); write(build(), args.out_dir)
    files = {p.name: p.read_text(encoding='utf-8') for p in sorted(args.out_dir.iterdir()) if p.is_file()}
    encoded = base64.b64encode(gzip.compress(json.dumps(files, ensure_ascii=False).encode())).decode()
    print('E020_FILES_BASE64_BEGIN')
    for i in range(0, len(encoded), 8000): print(encoded[i:i+8000])
    print('E020_FILES_BASE64_END'); print(files['analysis.md'])
