"""Matched chronological turnout ablations with explicit source-vintage gates."""
import argparse
import base64
import csv
from datetime import date, timedelta
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import statistics
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import baseline, turnout_history, turnout_models as tm

ROOT = baseline.ROOT
CONFIG = ROOT / 'config/turnout-context.json'


def load_inputs(config):
    folder = ROOT / config['context_path']
    audit = baseline.load_json(folder / 'audit.json')
    manifest = baseline.load_json(folder / 'worldbank/manifest.json')
    series = {}
    for source in manifest['sources']:
        path = folder / 'worldbank' / source['file']
        if hashlib.sha256(path.read_bytes()).hexdigest() != source['sha256']:
            raise ValueError(f'Source hash mismatch: {path}')
        raw = baseline.load_json(path)
        if source['kind'] == 'observations':
            if raw[0]['pages'] != 1:
                raise ValueError('Uncollected source pages')
            if any(r['countryiso3code'] != 'ISR' or r['indicator']['id'] != source['indicator'] for r in raw[1]):
                raise ValueError('Unexpected country/indicator')
            series[source['indicator']] = {int(r['date']): r['value'] for r in raw[1]}
    history = baseline.load_json(ROOT / config['history_path'])
    events = sorted(history['conflict_events'] + audit['conflicts']['additional_events'], key=lambda e: e['onset'])
    if len({e['id'] for e in events}) != len(events):
        raise ValueError('Duplicate conflict event IDs')
    return history['elections'], series, events, audit


def demographics(target_date, series, config, audit, strict=False):
    year = min(date.fromisoformat(target_date).year-config['demographic_lag_years'],
               config['demographic_max_reference_year'])
    if strict and not audit['demographics']['historical_availability_verified']:
        return None, {'reference_year': year, 'status': 'historical_release_unverified'}
    codes = ('SP.POP.65UP.TO.ZS', 'SP.POP.2024.FE.5Y', 'SP.POP.2529.FE.5Y')
    values = [series.get(code, {}).get(year) for code in codes]
    if any(v is None for v in values):
        return None, {'reference_year': year, 'status': 'missing_exact_reference_year'}
    if not all(0 <= v <= 100 for v in values) or values[1]+values[2] > 100:
        raise ValueError('Invalid demographic percentages')
    return {'resident_65plus_pct': values[0], 'female_resident_20_29_pct': values[1]+values[2]}, {
        'reference_year': year, 'status': 'retrospective_revised_vintage',
        'historical_availability_verified': False}


def conflict(cutoff, events, audit, strict=False):
    if strict and not audit['conflicts']['historical_availability_verified']:
        return None, {'status': 'historical_release_unverified'}
    if cutoff > audit['conflicts']['coverage_end']:
        return None, {'status': 'catalogue_coverage_incomplete'}
    day = date.fromisoformat(cutoff)
    past = [e for e in events if e['onset'] <= cutoff]
    if not past:
        return None, {'status': 'no_known_prior_onset'}
    lag = (day-date.fromisoformat(past[-1]['onset'])).days
    # This counts known catalogue entries, never encodes peace/active status.
    return {'catalogued_onsets_365d': float(sum(0 <= (day-date.fromisoformat(e['onset'])).days < 365 for e in past)),
            'catalogued_onset_gap_capped10y': min(10., lag/365.2425)}, {
        'status': 'retrospective_curated_onset_index', 'last_onset_id': past[-1]['id'],
        'active_status': None, 'end_date_used': None}


def feature_row(earlier, target_date, cutoff, series, events, config, audit):
    if not earlier or any(r['election_date'] > cutoff for r in earlier) or cutoff >= target_date:
        raise ValueError('Features require completed earlier elections and pre-election cutoff')
    prior = earlier[-1]
    history = {'lag1': prior['turnout_pct'],
               'gap_years': (date.fromisoformat(target_date)-date.fromisoformat(prior['election_date'])).days/365.2425}
    dem, dem_detail = demographics(target_date, series, config, audit)
    con, con_detail = conflict(cutoff, events, audit)
    return {'features': {'history': history,
            'demographics': {**history, **dem} if dem is not None else None,
            'conflict': {**history, **con} if con is not None else None,
            'both': {**history, **dem, **con} if dem is not None and con is not None else None},
            'cutoff': cutoff, 'demographics': dem_detail, 'conflict': con_detail}


def configurations(config):
    return [{'id': f'{family}__{block}__w{window or "all"}__a{alpha:g}',
             'family': family, 'block': block, 'window': window, 'alpha': alpha}
            for block in config['blocks'] for family in config['families']
            for window in config['training_windows'] for alpha in config['alphas']]


def metrics(records):
    if not records:
        return None
    recent = [r for r in records if r['knesset'] >= 20]
    blocks = [[r for r in recent if r['knesset'] == 20],
              [r for r in recent if 21 <= r['knesset'] <= 24],
              [r for r in recent if r['knesset'] == 25]]
    nonempty = [b for b in blocks if b]
    return {'folds': len(records), 'all_mae_pp': statistics.mean(r['absolute_error_pp'] for r in records),
            'recent_mae_pp': statistics.mean(r['absolute_error_pp'] for r in recent) if recent else None,
            'recent_block_mae_pp': statistics.mean(statistics.mean(r['absolute_error_pp'] for r in b) for b in nonempty) if nonempty else None,
            'recent_worst_pp': max(r['absolute_error_pp'] for r in recent) if recent else None,
            'invalid_folds': sum(not r.get('eligible', True) for r in records)}


def build(config=None, rows=None, inputs=None):
    import numpy as np
    import scipy
    config = config or baseline.load_json(CONFIG)
    loaded, series, events, audit = inputs or load_inputs(config)
    rows = loaded if rows is None else rows
    contract = baseline.load_json(ROOT / 'config/submission-fields.json')
    candidates = configurations(config)
    panel = {}
    for i in range(3, len(rows)):
        cutoff = (date.fromisoformat(rows[i]['election_date'])-timedelta(days=1)).isoformat()
        panel[i] = feature_row(rows[:i], rows[i]['election_date'], cutoff, series, events, config, audit)
    common = [i for i, row in panel.items() if all(row['features'][b] is not None for b in config['blocks'])]
    folds = [i for i in common if sum(j < i for j in common) >= config['minimum_training_elections']]
    if len(folds) < 6 or not all(any(rows[i]['knesset'] == k for i in folds) for k in range(20, 26)):
        raise ValueError('Insufficient matched coverage: require six recent election targets')
    predictions = []; nested = []; current = {}; selections = {}
    for i in folds+[len(rows)]:
        future = i == len(rows)
        target_date = config['forecast_election_date'] if future else rows[i]['election_date']
        target = feature_row(rows[:i], target_date, config['forecast_cutoff'], series, events, config, audit) if future else panel[i]
        now = {name: {'prediction_pct': value, 'family': 'reference', 'eligible': tm.allowed(value, contract),
                     'fit': {'status': 'reference'}} for name, value in turnout_history.forecasts(rows[:i]).items()}
        for c in candidates:
            indices = [j for j in common if j < i]
            if c['window']:
                indices = indices[-c['window']:]
            feat = target['features'][c['block']]
            if feat is None:
                now[c['id']] = {'prediction_pct': None, 'family': c['family'], 'eligible': False,
                    'fit': {'status': 'missing_current_context', 'training_knessets': [rows[j]['knesset'] for j in indices]}}
                continue
            examples = [{'knesset': rows[j]['knesset'], 'turnout_pct': rows[j]['turnout_pct'],
                         'previous_turnout': rows[j-1]['turnout_pct'], 'features': panel[j]['features'][c['block']]} for j in indices]
            value, detail = tm.fit_predict(examples, feat, rows[i-1]['turnout_pct'], c)
            now[c['id']] = {'prediction_pct': value, 'family': c['family'],
                           'eligible': detail['status'] == 'converged' and tm.allowed(value, contract), 'fit': detail}
        # Four separate selectors share folds and identical budgets; no target outcome enters selection.
        choices = {}
        for block in config['blocks']:
            ids = {c['id'] for c in candidates if c['block'] == block} | set(tm.REFERENCES)
            choices[block] = tm.choose([r for r in predictions if r['id'] in ids],
                {k: v for k, v in now.items() if k in ids}, config['minimum_selection_folds'], config['selection_lookback'])
        if future:
            current = now; selections = choices; current_features = target
            break
        truth = rows[i]['turnout_pct']
        for block, choice in choices.items():
            value = now[choice['selected']]['prediction_pct']
            nested.append({'block': block, 'knesset': rows[i]['knesset'], 'election_date': target_date,
                           **choice, 'prediction_pct': value, 'actual_pct': truth, 'absolute_error_pp': abs(value-truth)})
        for ident, item in now.items():
            value = item['prediction_pct']
            predictions.append({'id': ident, 'knesset': rows[i]['knesset'], 'election_date': target_date,
                'family': item['family'], 'prediction_pct': value, 'actual_pct': truth,
                'absolute_error_pp': abs(value-truth), 'eligible': item['eligible'],
                'fit_status': item['fit']['status'], 'training_knessets': item['fit'].get('training_knessets', [])})
    scores = {ident: metrics([r for r in predictions if r['id'] == ident]) for ident in current}
    policy_scores = {b: metrics([r for r in nested if r['block'] == b]) for b in config['blocks']}
    # Paired fixed-hyperparameter contrasts isolate added context without best-of-grid cherry-picking.
    paired = []
    for c in candidates:
        if c['block'] == 'history':
            continue
        control = c['id'].replace('__'+c['block']+'__', '__history__')
        paired.append({'id': c['id'], 'control_id': control,
            'recent_mae_delta_pp': scores[c['id']]['recent_mae_pp']-scores[control]['recent_mae_pp'],
            'all_mae_delta_pp': scores[c['id']]['all_mae_pp']-scores[control]['all_mae_pp'],
            'block_mae_delta_pp': scores[c['id']]['recent_block_mae_pp']-scores[control]['recent_block_mae_pp']})
    return {'config': config, 'tier': 'retrospective_revised_vintage_sensitivity',
        'strict_context_eligible': False, 'configuration_count': len(candidates), 'configurations': candidates,
        'matched_training_knessets': [rows[j]['knesset'] for j in common],
        'matched_outer_knessets': [rows[j]['knesset'] for j in folds],
        'feature_panel': [{'knesset': rows[i]['knesset'], **row} for i, row in panel.items()],
        'historical_predictions': predictions, 'nested_selections': nested, 'scores': scores,
        'policy_scores': policy_scores, 'paired_fixed_hyperparameter_deltas': paired,
        'current_fits': current, 'current_selections': selections, 'current_features': current_features,
        'environment': {'numpy': np.__version__, 'scipy': scipy.__version__, 'seed': 'not_applicable_deterministic'},
        'decision': 'No model adoption. Existing turnout and seat forecast unchanged.', 'source_audit': audit}


def write(report, out):
    out.mkdir(parents=True, exist_ok=True)
    def save(name, text):
        (out/name).write_text(text, encoding='utf-8', newline='\n')
    compact = {k: v for k, v in report.items() if k != 'historical_predictions'}
    compact['historical_predictions_file'] = 'predictions.csv'
    save('results.json', json.dumps(compact, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    with (out/'predictions.csv').open('w', encoding='utf-8', newline='') as f:
        fields = list(report['historical_predictions'][0])
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); writer.writeheader()
        for r in report['historical_predictions']:
            writer.writerow({**r, 'training_knessets': json.dumps(r['training_knessets'])})
    lines = ['# E016: turnout context ablations', '',
        'Retrospective revised-vintage sensitivity. No strict real-time demographic/conflict backtest is certified.', '',
        f"{report['configuration_count']} configurations; common outer Knessets: {report['matched_outer_knessets']}. Two history, two demographic, two conflict features at most; identical training/evaluation rows across blocks.", '',
        '| Past-only selected block | Recent six MAE pp | Equal-three-block MAE pp | All-fold MAE pp |',
        '|---|---:|---:|---:|']
    for block, score in report['policy_scores'].items():
        lines.append(f"| {block} | {score['recent_mae_pp']:.3f} | {score['recent_block_mae_pp']:.3f} | {score['all_mae_pp']:.3f} |")
    score = report['scores']['last_three_mean']
    lines += [f"| last-three mean reference | {score['recent_mae_pp']:.3f} | {score['recent_block_mae_pp']:.3f} | {score['all_mae_pp']:.3f} |", '',
        'Positive paired error deltas mean context made predictions worse. Fixed-grid rankings are hindsight diagnostics, not model selections.', '',
        'Demographics: exact year minus2, capped at2022.65+ denominator is total resident population;20-29 denominator is female resident population. Neither is the electorate. Current reference year2022 is deliberately stale; no projection used. Historical publication/revision vintages unverified.', '',
        'Conflict: count of curated onsets365days and time since latest onset capped10years. Zero means no entry in this catalogue, not peace. End/active status/severity unknown and unused. Catalogue incomplete after2022: current conflict/both model estimates are unavailable rather than set to zero.', '',
        'Three past OOF folds required for selection; last6 past errors only, references included and form bounds enforced before selection. First three outer folds use persistence. Scalers fit on training rows only. One election has one weight; no ballot-count GLM weighting.', '',
        'Four2019-2021 elections remain dependent; equal2015/2019-21/2022 block scores reported. Outcomes were previously inspected; no untouched holdout or causal interpretation. No forecast changed.', '',
        'See results.json for feature coverage, all paired contrasts, selections, coefficients/scalers and current missing-context diagnostics. Historical rows stored once in predictions.csv.']
    save('analysis.md', '\n'.join(lines)+'\n')
    paths = ['scripts/turnout_context.py', 'scripts/turnout_models.py', 'config/turnout-context.json',
             report['config']['history_path']]
    folder = ROOT/report['config']['context_path']
    paths += [p.relative_to(ROOT).as_posix() for p in sorted(folder.rglob('*')) if p.is_file()]
    save('inputs-manifest.json', json.dumps({p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}, indent=2)+'\n')
    plot(report, out)


def plot(report, out):
    # Standalone SVG: equal-election spacing deliberately labels every election date.
    palette = ['#2468a0', '#269073', '#c27717', '#9558a5', '#46525d']
    series = {b: [r for r in report['nested_selections'] if r['block'] == b and r['knesset'] >= 20] for b in report['config']['blocks']}
    series['last-three mean'] = [r for r in report['historical_predictions'] if r['id'] == 'last_three_mean' and r['knesset'] >= 20]
    maximum = max(8., max(r['absolute_error_pp'] for rows in series.values() for r in rows))*1.1
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="610" viewBox="0 0 1120 610"><rect width="1120" height="610" fill="white"/><g font-family="Arial,sans-serif" fill="#19334a">',
         '<text x="25" y="30" font-size="23">Turnout context: chronological selected-model errors</text>',
         '<text x="25" y="55" font-size="14">Retrospective revised-vintage sensitivity. Lower is better; no forecast adoption.</text>']
    for j in range(5):
        value = maximum*j/4; y = 440-340*j/4
        p.append(f'<path d="M85,{y}H1060" stroke="#e1e6ea"/><text x="25" y="{y+4}" font-size="12">{value:.1f}pp</text>')
    for j, (name, rows) in enumerate(series.items()):
        pts = [(110+185*i, 440-r['absolute_error_pp']/maximum*340) for i, r in enumerate(rows)]
        p.append('<polyline points="'+' '.join(f'{x},{y:.2f}' for x,y in pts)+f'" fill="none" stroke="{palette[j]}" stroke-width="2"/>')
        for (x,y),r in zip(pts,rows):
            p.append(f'<circle cx="{x}" cy="{y:.2f}" r="4" fill="{palette[j]}"><title>{escape(name)}: {r["absolute_error_pp"]:.3f}pp</title></circle>')
        p.append(f'<text x="{25+(j%3)*365}" y="{510+27*(j//3)}" fill="{palette[j]}" font-size="15">{escape(name)}</text>')
    for i, r in enumerate(series['history']):
        p.append(f'<text x="{75+185*i}" y="466" font-size="12">{r["election_date"]}</text>')
    p.append('<text x="25" y="580" font-size="13">2019-2021 outcomes are correlated. Each block selects only from earlier OOF errors and simple references.</text></g></svg>')
    (out/'chronological-errors.svg').write_text('\n'.join(p)+'\n', encoding='utf-8', newline='\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, default=ROOT/'output/turnout-context')
    args = parser.parse_args(); write(build(), args.out_dir)
    files = {p.name: p.read_text(encoding='utf-8') for p in sorted(args.out_dir.iterdir()) if p.is_file()}
    encoded = base64.b64encode(gzip.compress(json.dumps(files, ensure_ascii=False).encode())).decode()
    print('E016_FILES_BASE64_BEGIN')
    for i in range(0, len(encoded), 8000):
        print(encoded[i:i+8000])
    print('E016_FILES_BASE64_END'); print(files['analysis.md'])
