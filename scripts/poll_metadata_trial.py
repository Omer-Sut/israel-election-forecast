"""E008: poll metadata as learner inputs and past-only training reliability weights."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import date, timedelta
import hashlib
import html
import json
import math
import os
from pathlib import Path
import sys
import time

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.baseline import ROOT, load_json, rounded_mean
from scripts.campaign_history import AUDIT, prepare_variants, write_json
from scripts.experiments import build_case, supervised_prediction
from scripts.research_trial import creator_key
from scripts.robustness import evaluate_fraction, project

ABLATIONS = ('aggregate', 'poll_basic', 'poll_metadata', 'poll_metadata_weighted')
METHODS = ('ridge_10', 'forest_3_5', 'xgb_2_50')
FRACTIONS = (0, .05, .25, 1)
SEED = 20261021


def poll_metadata(poll, election_date):
    """Only stored source facts; no inferred firm/method or outcome information."""
    end, start = poll.get('fieldwork_end'), poll.get('fieldwork_start')
    n = poll.get('sample_size')
    mode_raw = poll.get('mode') or ''
    text = mode_raw.lower()
    mode = ('mixed_internet_telephone' if 'internet' in text and 'telephone' in text
            else 'unclassified_reported' if text else 'unknown')
    lead = (date.fromisoformat(election_date)-date.fromisoformat(poll['published_on'])).days
    if lead <= 0 or (n is not None and (type(n) is not int or n <= 0)):
        raise ValueError('Invalid pre-election metadata')
    duration = (date.fromisoformat(end)-date.fromisoformat(start)).days+1 if end and start else None
    if duration is not None and duration <= 0:
        raise ValueError('Invalid fieldwork interval')
    return dict(poll_id=poll['id'], creator=creator_key(poll['pollster_group']),
                creator_raw=poll['pollster_group'], publisher=poll.get('publisher') or 'unknown',
                mode=mode, mode_raw=mode_raw or None, sample_size=n,
                publication_lead_days=lead, fieldwork_duration_days=duration,
                publication_lag_days=(date.fromisoformat(poll['published_on'])-date.fromisoformat(end)).days if end else None,
                source_url=poll['source_url'])


def vocabulary(rows):
    return {key: sorted({r[key] for r in rows}) for key in ('creator', 'publisher', 'mode')}


def encode_metadata(row, vocab):
    n, duration, lag = row['sample_size'], row['fieldwork_duration_days'], row['publication_lag_days']
    values = [math.log(n) if n else 0, int(n is None), duration or 0,
              int(duration is None), lag or 0, int(lag is None)]
    for key, categories in vocab.items():
        values.extend(int(row[key] == category) for category in categories)
        values.append(int(row[key] not in categories))
    return values


def base_weights(rows):
    """Each campaign sums to one; each firm has equal mass regardless of release count."""
    firms = {}
    for row in rows:
        firms.setdefault(row['election'], set()).add(row['creator'])
    counts = Counter((r['election'], r['creator']) for r in rows)
    return [1 / (len(firms[r['election']]) * counts[r['election'], r['creator']]) for r in rows]


def normalize_campaign_weights(rows, multipliers):
    weights = [a*b for a,b in zip(base_weights(rows), multipliers)]
    totals = Counter()
    for row, w in zip(rows, weights):
        totals[row['election']] += w
    return [w/totals[row['election']] for row,w in zip(rows,weights)]


def fit_predict(spec, x, y, weights, test):
    import numpy as np
    weights = np.asarray(weights) * len(weights) / sum(weights)
    x, test = np.asarray(x), np.asarray(test)
    if spec['family'] == 'ridge':
        from sklearn.preprocessing import StandardScaler
        from sklearn.linear_model import Ridge
        scaler = StandardScaler().fit(x, sample_weight=weights)
        model = Ridge(alpha=spec['alpha'], solver='svd')
        x, test = scaler.transform(x), scaler.transform(test)
    elif spec['family'] == 'forest':
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=spec['n_estimators'], max_depth=spec['max_depth'],
                    min_samples_leaf=spec['min_samples_leaf'], random_state=SEED, n_jobs=1)
    else:
        from xgboost import XGBRegressor
        model = XGBRegressor(objective='reg:squarederror', tree_method='hist', device='cpu',
                    n_estimators=spec['n_estimators'], max_depth=spec['max_depth'], learning_rate=spec['learning_rate'],
                    reg_lambda=1, subsample=1, colsample_bytree=1, random_state=SEED, n_jobs=1)
    model.fit(x, y, sample_weight=weights)
    return [float(v) for v in model.predict(test)]


def reliability(past_rows, current_rows):
    """Predict total poll error using earlier campaigns only; current outcomes never read."""
    if any(p['election_date'] >= c['election_date'] for p in past_rows for c in current_rows):
        raise ValueError('Reliability history must precede the scored campaign')
    training_ids = sorted({r['election'] for r in past_rows})
    if len(training_ids) < 2:
        return [dict(expected_error=None, multiplier=1.0, training_elections=training_ids,
                     status='warmup_uniform') for _ in current_rows]
    vocab = vocabulary(past_rows)
    feature = lambda r: [math.log1p(r['publication_lead_days'])] + encode_metadata(r, vocab)
    weights = base_weights(past_rows)
    prior = sum(w*r['error'] for w,r in zip(weights,past_rows))/sum(weights)
    predicted = fit_predict({'family':'ridge','alpha':10}, [feature(r) for r in past_rows],
                            [r['error'] for r in past_rows], weights, [feature(r) for r in current_rows])
    return [dict(expected_error=max(1,p), multiplier=.5+.5*min(2,max(.5,prior/max(1,p))),
                 training_elections=training_ids, status='earlier_campaign_prediction') for p in predicted]


def poll_prediction(spec, training_rows, target_rows, metadata, weighted):
    """Targets are source-only rows. Target election outcomes are neither required nor read."""
    if any(p['election_date'] >= t['election_date'] for p in training_rows for t in target_rows):
        raise ValueError('Forecast training must precede target election')
    vocab = vocabulary(training_rows)
    def feature(row, seats):
        basic = [seats, int(seats == 0), math.log1p(row['publication_lead_days'])]
        if not metadata:
            return basic
        # Firm-by-size interaction allows size-dependent directional correction without
        # equating historical party identities or importing current alliance aliases.
        return basic + encode_metadata(row,vocab) + [seats*int(row['creator']==c) for c in vocab['creator']]
    weights = normalize_campaign_weights(training_rows, [r['reliability']['multiplier'] if weighted else 1 for r in training_rows])
    x, y, w = [], [], []
    for row, weight in zip(training_rows,weights):
        for seats, actual in zip(row['vector'],row['actual']):
            x.append(feature(row,seats)); y.append(actual-seats); w.append(weight/len(row['vector']))
    test = [feature(row,s) for row in target_rows for s in row['vector']]
    correction = fit_predict(spec,x,y,w,test)
    width = len(target_rows[0]['vector'])
    corrected = [[s+correction[j*width+i] for i,s in enumerate(row['vector'])] for j,row in enumerate(target_rows)]
    return [sum(col)/len(corrected) for col in zip(*corrected)], vocab


def choose_fraction(scores, election_date, ablation, method):
    past = [r for r in scores if r['election_date'] < election_date and r['ablation']==ablation and r['method']==method]
    elections = sorted({r['election'] for r in past})
    if len(elections) < 2:
        return 0, elections
    losses = {f:sum(r['integer_error'] for r in past if r['fraction']==f)/len(elections) for f in FRACTIONS}
    return min(FRACTIONS,key=lambda f:(losses[f],f)), elections


def run(out):
    start=time.perf_counter()
    configs=prepare_variants(out/'inputs')
    config=load_json(configs['expanded_history']); history=load_json(ROOT/config['historical_config'])
    targets=load_json(ROOT/history['outcomes_path'])['elections']
    specs=[m for m in config['models'] if m['id'] in METHODS]
    cases=[]; all_rows=[]; scores=[]; selection=[]; coverage=[]; vocabularies=[]
    for item in history['elections']:
        snapshot=load_json(ROOT/item['polls_path'])
        cutoff=(date.fromisoformat(snapshot['election_date'])-timedelta(days=1)).isoformat()
        case=build_case(snapshot,cutoff,history['poll_window_days'],history['minimum_groups'])
        case['election_date']=snapshot['election_date']
        case['horizon_days']=1
        actual=targets[case['election_id']]['seat_results']
        rows=[]
        for poll,vector in zip(case['history'],case['history_vectors']):
            rows.append(dict(**poll_metadata(poll,case['election_date']), election=case['election_id'],
                             election_date=case['election_date'], vector=vector, ids=case['ids']))
        quality=reliability(all_rows,rows)
        for row,q in zip(rows,quality): row['reliability']=q
        selected_ids={p['id'] for p in case['selected_polls']}
        target_rows=[r for r in rows if r['poll_id'] in selected_ids]
        ref_integer=rounded_mean(case['vectors'],120)
        truth=[actual[k] for k in case['ids']]
        ref_error=sum(abs(a-b) for a,b in zip(ref_integer,truth))
        coverage.append(dict(election=case['election_id'],eligible_releases=len(rows),selected_releases=len(target_rows),
            sample_known=sum(r['sample_size'] is not None for r in rows),mode_known=sum(r['mode']!='unknown' for r in rows),
            duration_known=sum(r['fieldwork_duration_days'] is not None for r in rows),
            creators=sorted({r['creator'] for r in rows}),reference_integer_error=ref_error,
            reference_continuous_error=sum(abs(a-b) for a,b in zip(project(case['anchor']),truth))))
        if len(cases)>=2:
            for ablation in ABLATIONS:
                for spec in specs:
                    if ablation=='aggregate':
                        raw=supervised_prediction(spec,cases,case,SEED)
                    else:
                        raw,vocab=poll_prediction(spec,all_rows,target_rows,ablation!='poll_basic',ablation=='poll_metadata_weighted')
                        vocabularies.append(dict(election=case['election_id'],ablation=ablation,method=spec['id'],
                            training_vocabulary=vocab,unseen_target_creators=sorted({r['creator'] for r in target_rows}-set(vocab['creator']))))
                    for fraction in FRACTIONS:
                        continuous,integer,ce,ie=evaluate_fraction(case['anchor'],raw,truth,fraction)
                        if fraction==0:
                            integer=ref_integer; ie=ref_error  # preserve exact rational tie order
                        scores.append(dict(election=case['election_id'],election_date=case['election_date'],
                            ablation=ablation,method=spec['id'],fraction=fraction,continuous_error=ce,integer_error=ie,
                            reference_integer_error=ref_error,continuous_prediction=continuous,integer_prediction=integer,
                            party_ids=case['ids'],training_elections=[c['election_id'] for c in cases]))
                    fraction,earlier=choose_fraction(scores,case['election_date'],ablation,spec['id'])
                    row=next(r for r in scores if r['election']==case['election_id'] and r['ablation']==ablation and r['method']==spec['id'] and r['fraction']==fraction)
                    selection.append(dict(election=case['election_id'],ablation=ablation,method=spec['id'],fraction=fraction,
                        selection_elections=earlier,integer_error=row['integer_error'],continuous_error=row['continuous_error'],
                        reference_integer_error=ref_error,status='earlier_OOF_selected' if len(earlier)>=2 else 'warmup_exact_reference'))
        # Attach labels only after predictions and past-only reliability have been constructed.
        for row in rows:
            row['actual']=truth; row['error']=sum(abs(a-b) for a,b in zip(row['vector'],truth))
        case['actual']=actual; cases.append(case); all_rows.extend(rows)
    report=dict(protocol='E008 training metadata trial; retrospective inspected outcomes, no forecast adoption',
                seed=SEED,ablations=ABLATIONS,methods=METHODS,fractions=FRACTIONS,scores=scores,selection=selection,
                coverage=coverage,poll_rows=all_rows,vocabularies=vocabularies)
    write_json(out/'results.json',report)
    summary=['# E008: poll metadata in training','',
        'All fits use earlier elections only. Four eligible OOF elections; 2021/2022 are previously inspected comparisons.',
        'Aggregate control; individual polls with seats/zero/lead time; added source metadata; added past-only training weights.',
        'Reliability alters training weights only. Target latest-group predictions are averaged equally. Missing metadata stays explicit.',
        'No party-identity continuity is inferred. Creator-by-seat-size interactions are not a party-specific house-effect model.',
        '', '| Inputs | Learner | 2021 fixed25% / selected | 2022 fixed25% / selected |','|---|---|---:|---:|']
    for a in ABLATIONS:
        for method in METHODS:
            cells=[]
            for election in ('knesset_24_2021','knesset_25_2022'):
                fixed=next(r for r in scores if r['election']==election and r['ablation']==a and r['method']==method and r['fraction']==.25)
                chosen=next(r for r in selection if r['election']==election and r['ablation']==a and r['method']==method)
                cells.append(f"{fixed['integer_error']} / {chosen['integer_error']} (fraction {chosen['fraction']})")
            summary.append(f'| {a} | {method} | {cells[0]} | {cells[1]} |')
    summary += ['', 'Reference errors: 2021=20, 2022=12. Lower is better. Full continuous errors and vectors are in results.json.',
        'Correction fractions {0,5,25,100}% chosen on at least two strictly earlier OOF campaigns; ties prefer zero/smaller corrections. Families/ablations are not automatically selected.',
        'No claim of independent poll/party samples, calibrated reliability or superiority from a hindsight best cell. Training balances campaigns and firms before bounded reliability adjustment.',
        'Sampling design, effective sample size, panel provider, likely-voter and undecided rules require additional audited metadata; they are not invented from publisher names.', '']
    (out/'summary.md').write_text('\n'.join(summary),encoding='utf-8',newline='\n')
    chart(report,out/'performance.svg')
    paths=[Path(__file__), ROOT/'scripts/experiments.py',ROOT/'scripts/research_trial.py',ROOT/'scripts/robustness.py',ROOT/'scripts/campaign_history.py',ROOT/'scripts/backtest.py',ROOT/'scripts/baseline.py',ROOT/'config/experiments.json',ROOT/history['outcomes_path']]
    # Hash actual consumed expanded source snapshots; exclude output-path-dependent configs.
    paths += [ROOT/i['polls_path'] for i in history['elections']]
    paths += [AUDIT, ROOT/load_json(ROOT/'config/experiments.json')['historical_config']]
    manifest=dict(commit=os.environ.get('GITHUB_SHA','local'),runtime_seconds=round(time.perf_counter()-start,3),
                  hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    write_json(out/'manifest.json',manifest)
    # Compact public text recovery; no credentials or copyrighted source prose.
    import base64,gzip
    bundle={p.name:p.read_text(encoding='utf-8') for p in (out/'results.json',out/'summary.md',out/'performance.svg',out/'manifest.json')}
    encoded=base64.b64encode(gzip.compress(json.dumps(bundle,ensure_ascii=False).encode())).decode()
    print('E008_FILES_BASE64_BEGIN')
    for i in range(0,len(encoded),8000): print(encoded[i:i+8000])
    print('E008_FILES_BASE64_END')
    print('\n'.join(summary))


def chart(report,path):
    colors=['#777','#ab6400','#176caa','#00806b']
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="510" viewBox="0 0 1120 510">',
           '<rect width="1120" height="510" fill="white"/><g font-family="Arial,sans-serif" fill="#18314a">',
           '<text x="25" y="28" font-size="21">Poll metadata: fixed 25% correction, total absolute seat error</text>']
    elections=[c['election'] for c in report['coverage']][2:]
    labels=['Sep2019','2020','2021','2022']
    for j,method in enumerate(METHODS):
        left=55+365*j
        parts.append(f'<text x="{left}" y="65" font-size="17">{method}</text>')
        maxerr=max(40,max(r['integer_error'] for r in report['scores'] if r['method']==method and r['fraction']==.25))
        y=lambda v:365-270*v/maxerr
        for tick in range(0,int(maxerr)+1,10):
            parts.append(f'<path d="M{left},{y(tick)}h280" stroke="#ddd"/><text x="{left-28}" y="{y(tick)+4}" font-size="12">{tick}</text>')
        for a,color in zip(ABLATIONS,colors):
            pts=[]
            for i,e in enumerate(elections):
                r=next(r for r in report['scores'] if r['method']==method and r['ablation']==a and r['fraction']==.25 and r['election']==e)
                xx=left+20+i*80; yy=y(r['integer_error']); pts.append(f'{xx},{yy}')
                parts.append(f'<circle cx="{xx}" cy="{yy}" r="4" fill="{color}"/>')
            parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2"/>')
        for i,label in enumerate(labels): parts.append(f'<text x="{left+i*80}" y="390" font-size="12">{label}</text>')
    for i,(a,color) in enumerate(zip(ABLATIONS,colors)):
        xx=25+i*275
        parts.append(f'<path d="M{xx},430h20" stroke="{color}" stroke-width="3"/><text x="{xx+25}" y="435" font-size="13">{html.escape(a)}</text>')
    parts+=['<text x="25" y="475" font-size="13">Lower is better. Full continuous and earlier-OOF-selected results are saved alongside this plot.</text>','</g></svg>']
    path.write_text('\n'.join(parts)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=ROOT/'output/poll-metadata-trial')
    run(parser.parse_args().out_dir.resolve())
