"""E005: poll errors, chronological tuning, dynamic features and geographic readiness.

No current forecast changes. Broad index statistics remain a lower evidence tier.
"""
from __future__ import annotations
import copy
import base64
import csv
from datetime import date, timedelta
import gzip
import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import statistics as st
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.baseline import ROOT, load_json
from scripts.backtest import historical_vector, score_seats
from scripts.campaign_history import prepare_variants, write_json
from scripts.experiments import build_case, dynamic_prediction, evaluate_cases, reconcile
from scripts.robustness import evaluate_fraction
from scripts.build_database import build, records

FRACTIONS = (0, .025, .05, .10, .25, .5, 1)
OUT = ROOT / "output/research-trial"


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
            w.writeheader()
            w.writerows(rows)


def norm(label):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\[[^]]*\]', '', label).lower().replace('&', 'and'))


def aliases(snapshot, k):
    result = {norm(r['label_en']): r['id'] for r in snapshot['lists']}
    def add(stem, *names):
        matches = [r['id'] for r in snapshot['lists'] if r['id'].startswith(stem+'_')]
        if len(matches) != 1:
            raise ValueError(f'Ambiguous alias {k} {stem}')
        for n in names:
            result[norm(n)] = matches[0]
    add('united_torah_judaism', 'UTJ')
    if k == 20:
        add('zionist_union', 'Labor + Hatnuah')
        add('joint_list', "Hadash + UAL-Ta'al + Balad")
        add('yachad', 'Otzma + Yachad')
    if k == 21:
        add('union_right_wing_parties', 'URWP')
    if k == 22:
        add('democratic_union', 'Dem. Union')
        add('likud', 'Likud-Kulanu')
    if k == 23:
        add('labor_gesher_meretz', 'Emet')
        add('otzma_yehudit', 'Otzma')
    if k == 24:
        add('joint_list', 'Joint List')
        add('religious_zionism_otzma', 'Religious Zionist', 'RZ + OtzmaYehudit-Noam')
        add('new_economic', 'NewEconomic', 'NEP')
        add('blue_and_white', 'B&W')
        add('yisrael_beiteinu', 'YB')
    if k == 25:
        add('religious_zionism_otzma', 'RZP-OY', 'ReligiousZionist + OtzmaYehudit')
        add('national_unity', 'NUP/B&W-NH')
    return result


def index_vector(values, mapping, ids):
    """Lower-tier complete-seat transcription, NOT original-release certification.

    Infer unallocated residual zeros only after all positive seat cells map and sum120.
    Never convert percent support into seats or combine hypothetical component lists.
    """
    found, zeros = {}, []
    for cell in values:
        label = norm(cell['list_label'])
        if cell['column_role'] == 'aggregate_or_comparison' or label in ('gov', 'opp', 'opposition', 'government'):
            continue
        value = cell['value'] if cell['unit'] == 'seats' else None
        if value is None:
            zeros.append(cell['list_label'])
            continue
        if value < 0 or int(value) != value:
            raise ValueError('invalid_seat_value')
        if not value:
            continue
        key = mapping.get(label)
        if key is None:
            raise ValueError('unknown_positive_list:'+cell['list_label'])
        if key in found:
            raise ValueError('duplicate_positive_list')
        found[key] = int(value)
    if sum(found.values()) != 120:
        raise ValueError('mapped_numeric_seats_not_120')
    return [found.get(key, 0) for key in ids], zeros


def describe(values):
    return dict(n=len(values), mean=st.mean(values), variance=st.variance(values) if len(values)>1 else None,
                sd=st.stdev(values) if len(values)>1 else None, median=st.median(values), minimum=min(values), maximum=max(values))


def bucket(days):
    return '01-07' if days <= 7 else '08-14' if days <=14 else '15-30' if days<=30 else '31-90' if days<=90 else '91+'


def poll_diagnostics(config_path):
    config = load_json(config_path)
    history = load_json(ROOT/config['historical_config'])
    targets = load_json(ROOT/history['outcomes_path'])['elections']
    snapshots = {int(s['id'].split('_')[1]): load_json(ROOT/s['polls_path']) for s in history['elections']}
    rows, excluded = [], []
    index_polls = list(records(ROOT/'data/database/polls.jsonl.gz'))
    index_values, index_rows = {}, {r['row_id']: r for r in records(ROOT/'data/database/poll_rows.jsonl.gz')}
    for v in records(ROOT/'data/database/poll_values.jsonl.gz'):
        index_values.setdefault(v['poll_id'], []).append(v)
    seen = set()
    for k, snapshot in snapshots.items():
        ids = [r['id'] for r in snapshot['lists']]
        actual = [targets[snapshot['election_id']]['seat_results'][key] for key in ids]
        for p in snapshot['polls']:
            days = (date.fromisoformat(snapshot['election_date'])-date.fromisoformat(p['published_on'])).days
            if days <= 0 or p.get('kind') != 'pre_election_poll':
                continue
            vector = historical_vector(p, ids)
            rows.append(dict(tier='audited_release', election=snapshot['election_id'], knesset=k, poll_id=p['id'],
                creator=p['pollster_group'], publisher=p.get('publisher',''), days=days, horizon_bin=bucket(days),
                date_basis='audited_publication', sample_size=p.get('sample_size'),
                error=sum(abs(x-y) for x,y in zip(vector,actual)), references=p['source_url'],
                residual_zero_assumption='audited_complete_allocation', allocations=json.dumps(dict(zip(ids,vector)),ensure_ascii=False)))
        mapping = aliases(snapshot, k)
        for p in index_polls:
            if p['knesset'] != k or not p['campaign_main'] or p['record_kind'] != 'poll_index_row' or p['date_proxy'] >= snapshot['election_date']:
                continue
            try:
                vector, zeros = index_vector(index_values.get(p['poll_id'],[]), mapping, ids)
            except ValueError as exc:
                excluded.append(dict(poll_id=p['poll_id'], election=snapshot['election_id'], reason=str(exc)))
                continue
            creator = re.sub(r'\[[^]]*\]', '', ' / '.join(p['metadata'])).strip()
            signature = (k,p['date_proxy'],creator,tuple(vector))
            if signature in seen:
                excluded.append(dict(poll_id=p['poll_id'], election=snapshot['election_id'], reason='exact_same_day_label_vector_duplicate'))
                continue
            seen.add(signature)
            days = (date.fromisoformat(snapshot['election_date'])-date.fromisoformat(p['date_proxy'])).days
            raw = index_rows[p['row_id']]
            rows.append(dict(tier='index_exploratory_not_certified',election=snapshot['election_id'],knesset=k,poll_id=p['poll_id'],
                creator=creator,publisher='',days=days,horizon_bin=bucket(days),date_basis='index_date_proxy_not_publication',sample_size=None,
                error=sum(abs(x-y) for x,y in zip(vector,actual)), references=' | '.join(raw['references']),
                residual_zero_assumption='numeric_mapped_seats_sum120_other_cells_not_vote_zeros:'+ '|'.join(zeros),
                allocations=json.dumps(dict(zip(ids,vector)),ensure_ascii=False)))
    write_csv(OUT/'poll-errors.csv', rows)
    write_json(OUT/'index-exclusions.json', excluded)
    summaries=[]
    for tier in sorted({r['tier'] for r in rows}):
        for election in sorted({r['election'] for r in rows}):
            subset=[r for r in rows if r['tier']==tier and r['election']==election]
            for window in ('all_retained_pre_election','last_90_days','last_14_days'):
                selected=[r for r in subset if window=='all_retained_pre_election' or r['days'] <= (90 if window=='last_90_days' else 14)]
                if selected:
                    summaries.append(dict(tier=tier,election=election,window=window,**describe([r['error'] for r in selected])))
    write_csv(OUT/'campaign-summary.csv',summaries)
    groups={}
    for r in rows:
        for dimension, value in (('creator',r['creator']),('horizon_bin',r['horizon_bin'])):
            groups.setdefault((r['tier'],r['election'],dimension,value),[]).append(r['error'])
    write_csv(OUT/'poll-patterns.csv',[dict(tier=t,election=e,dimension=d,value=v,**describe(x)) for (t,e,d,v),x in groups.items()])
    return rows,summaries,snapshots,targets


def quality_trial(rows):
    """Only audited releases can train this trial; campaign-blocked historical predictions."""
    import numpy as np
    from sklearn.linear_model import Ridge
    from sklearn.preprocessing import StandardScaler
    audited=[r for r in rows if r['tier']=='audited_release']
    predictions=[]
    for election in sorted({r['election'] for r in audited}):
        test=[r for r in audited if r['election']==election]
        training=[r for r in audited if r['knesset']<test[0]['knesset']]
        if len({r['election'] for r in training})<2:
            continue
        creators=sorted({r['creator'] for r in training})
        def x(r):
            n=r['sample_size']
            return [math.log1p(r['days']),math.log(n) if n else 0,int(not n)]+[int(r['creator']==c) for c in creators]
        weights=[1/sum(t['election']==r['election'] for t in training) for r in training]
        weights=np.asarray(weights)*len(weights)/sum(weights)
        scaler=StandardScaler().fit([x(r) for r in training],sample_weight=weights)
        learner=Ridge(alpha=10,solver='svd').fit(scaler.transform([x(r) for r in training]),[r['error'] for r in training],sample_weight=weights)
        estimates=learner.predict(scaler.transform([x(r) for r in test]))
        election_means=[st.mean([r['error'] for r in training if r['election']==e]) for e in sorted({r['election'] for r in training})]
        baseline=st.mean(election_means)
        scale=max(1,st.stdev([r['error'] for r in training]))
        for r,estimate in zip(test,estimates):
            expected=max(1,float(estimate))
            predictions.append(dict(election=election,poll_id=r['poll_id'],actual_error=r['error'],expected_error=expected,
                prior_campaign_mean_baseline=baseline,severity_ratio=r['error']/expected,
                severity_standardized=(r['error']-expected)/scale,
                unnormalized_inverse_expected_error_weight=1/expected,
                training_elections='|'.join(sorted({t['election'] for t in training})),
                sample_size_known=bool(r['sample_size']),status='exploratory_no_probability_calibration_no_weights_adopted'))
    write_csv(OUT/'quality-oof.csv',predictions)
    return predictions


def select_past(options, cutoff, minimum=2):
    """No present/future case can influence correction/parameter selection."""
    groups={}
    for r in options:
        if r['election_date'] < cutoff:
            groups.setdefault((r['method'],r['fraction']),[]).append(r)
    eligible=[]
    for (method,fraction),rows in groups.items():
        if len({r['election'] for r in rows})>=minimum:
            eligible.append((st.mean(r['integer_error'] for r in rows),fraction,method,rows))
    if not eligible:
        return None
    # Prefer smaller correction on a loss tie, then stable model ID.
    _,fraction,method,rows=min(eligible,key=lambda r:r[:3])
    return method,fraction,sorted({r['election'] for r in rows})


def prior_area_profiles():
    """Dated city subset; prior-election votes only, explicit stable-core scope."""
    source=load_json(ROOT/'data/snapshots/party-area-vintage-2018-2026-10-22.json')
    cities={r['code']:r for r in source['cities']}
    # No inference from reused party ballot codes or changed alliance names.
    core_codes={'shas':'שס','united_torah_judaism':'ג','yisrael_beiteinu':'ל'}
    official={(r['knesset'],r['ballot_code']):r for r in records(ROOT/'data/database/official_lists.jsonl.gz')}
    geo={r['geo_id']:r for r in records(ROOT/'data/database/geographies.jsonl.gz') if r['granularity']=='locality'}
    sums={}; verified_cities=set()
    for row in records(ROOT/'data/database/geographic_votes.jsonl.gz'):
        g=geo.get(row['geo_id'])
        if not g or row['ballot_code'] not in core_codes.values():
            continue
        attr=g['attributes']; code=str(int(attr['סמל ישוב']))
        if code not in cities:
            continue
        name=attr.get('שם ישוב','')
        clean=lambda s:re.sub(r'[^א-ת]','',s)
        if clean(name)!=clean(cities[code]['name_he']):
            raise ValueError(f'City code/name mismatch: {code}, {name}')
        verified_cities.add(code)
        key=(g['knesset'],row['ballot_code'])
        numerator,denominator=sums.get(key,(0,0))
        sums[key]=(numerator+row['votes']*cities[code]['index'],denominator+row['votes'])
    if verified_cities != set(cities):
        raise ValueError('A transcribed CBS city code is not matched to official votes')
    result=[]
    for (k,code),(num,den) in sums.items():
        party=next(name for name,c in core_codes.items() if c==code)
        result.append(dict(source_knesset=k,party_core=party,mean_city_index=num/den,matched_party_votes=den,
            national_party_votes=official[k,code]['votes'],vote_coverage=den/official[k,code]['votes'],
            cbs_publication_date=source['publication_date'],geography_scope='15 large cities only',
            eligibility='Can enter only later elections after CBS publication; core names explicitly scoped, no merger redistribution'))
    write_csv(OUT/'prior-city-profiles.csv',result)
    return result,source['publication_date']


def temporal_trial(config_paths):
    scores, selections=[] ,[]
    profiles,published=prior_area_profiles()
    for variant in ('reference','expanded_history'):
        config=load_json(config_paths[variant]); history=load_json(ROOT/config['historical_config'])
        outcomes={k:v['seat_results'] for k,v in load_json(ROOT/history['outcomes_path'])['elections'].items()}
        config['models']=[m for m in config['models'] if m['family']!='ensemble']
        config['ensemble_members']=[m['id'] for m in config['models'][:1]]
        families={m['id']:m['family'] for m in config['models']}
        cases=[]
        for spec in history['elections']:
            snapshot=load_json(ROOT/spec['polls_path'])
            cutoff=(date.fromisoformat(snapshot['election_date'])-timedelta(days=1)).isoformat()
            case=build_case(snapshot,cutoff,history['poll_window_days'],history['minimum_groups'])
            case['horizon_days']=1
            cases.append(case)
        for features in ('original','dynamic_gap','prior_city_core','dynamic_plus_prior_city_core'):
            trial=copy.deepcopy(cases)
            if features in ('dynamic_gap','dynamic_plus_prior_city_core'):
                for c in trial:
                    filtered=dynamic_prediction(c,1,4)
                    c['features']=[x+[v-a] for x,v,a in zip(c['features'],filtered,c['anchor'])]
            if features in ('prior_city_core','dynamic_plus_prior_city_core'):
                for c in trial:
                    k=int(c['election_id'].split('_')[1])
                    for i,key in enumerate(c['ids']):
                        core=next((p for p in ('shas','united_torah_judaism','yisrael_beiteinu') if key.startswith(p+'_')),None)
                        profile=next((p for p in profiles if p['source_knesset']==k-1 and p['party_core']==core),None)
                        if profile and published<c['cutoff']:
                            c['features'][i]+=[profile['mean_city_index'],profile['vote_coverage'],0]
                        else:
                            c['features'][i]+=[0,0,1]
            results=evaluate_cases(trial,outcomes,config)
            block=[]
            for c in results:
                actual=[outcomes[c['election_id']][key] for key in c['ids']]
                for method,entry in c['methods'].items():
                    if 'continuous_unshrunk' not in entry:
                        continue
                    for fraction in FRACTIONS:
                        cp,ip,ce,ie=evaluate_fraction(c['anchor'],entry['continuous_unshrunk'],actual,fraction)
                        r=dict(variant=variant,features=features,election=c['election_id'],election_date=c['election_date'],cutoff=c['cutoff'],
                            method=method,family=families[method],fraction=fraction,integer_error=ie,continuous_error=ce,
                            reference_error=c['methods']['rounded_mean_reference']['score']['total_absolute_seat_error'],
                            prediction=json.dumps(dict(zip(c['ids'],ip))),training_elections='|'.join(c['training_elections']))
                        block.append(r)
            for c in results:
                for family in sorted(set(families.values())):
                    pool=[r for r in block if r['family']==family]
                    choice=select_past(pool,c['cutoff'])
                    if not choice:
                        selections.append(dict(variant=variant,features=features,election=c['election_id'],family=family,
                            selected_method='rounded_mean_reference',fraction=0,selection_elections='',
                            integer_error=c['methods']['rounded_mean_reference']['score']['total_absolute_seat_error'],
                            reference_error=c['methods']['rounded_mean_reference']['score']['total_absolute_seat_error'],status='insufficient_earlier_oof_use_reference'))
                    else:
                        method,fraction,earlier=choice
                        target=next(r for r in pool if r['election']==c['election_id'] and r['method']==method and r['fraction']==fraction)
                        selections.append(dict(variant=variant,features=features,election=c['election_id'],family=family,
                            selected_method=method,fraction=fraction,selection_elections='|'.join(earlier),
                            integer_error=target['integer_error'],reference_error=target['reference_error'],status='chronological_inner_oof_selection'))
            scores.extend(block)
    write_csv(OUT/'parameter-sensitivity.csv',scores)
    write_csv(OUT/'chronological-selection.csv',selections)
    return selections


def geographic_readiness():
    destination=OUT/'elections.sqlite'
    build(ROOT/'data/database',destination)
    db=sqlite3.connect(destination); db.row_factory=sqlite3.Row
    result=[]
    for k in range(20,26):
        for party in db.execute('SELECT * FROM official_lists WHERE knesset=?',(k,)).fetchall():
            row=dict(knesset=k,ballot_code=party['ballot_code'],party_name=party['party_name_en'] or party['party_name_he'],
                party_national_votes=party['votes'],demographic_year=2021,socioeconomic_year=2019,
                feature_interpretation='vote-weighted characteristics of areas, NOT individual party voters',
                historical_feature_eligible=False,eligibility_reason='historical_CBS_release_dates_unverified; use only prior-election votes with reviewed list lineage')
            for field in ('male_percent','age65_plus_percent','age0_19_percent'):
                q=db.execute(f'''SELECT SUM(v.votes*p.{field})/NULLIF(SUM(v.votes),0) AS measure,SUM(v.votes) AS matched
                    FROM cbs_locality_vote_shares v JOIN cbs_locality_profiles p USING(locality_code)
                    WHERE v.knesset=? AND v.ballot_code=? AND p.reference_year=2021 AND p.{field} IS NOT NULL
                    AND NOT ((v.knesset=20 AND v.locality_code='0') OR(v.knesset=21 AND v.locality_code='99999') OR(v.knesset>=22 AND v.locality_code='9999'))''',(k,party['ballot_code'])).fetchone()
                row[field]=q['measure']; row[field+'_vote_coverage']=q['matched']/party['votes'] if q['matched'] and party['votes'] else 0
            q=db.execute('''SELECT SUM(v.votes*s.index_value)/NULLIF(SUM(v.votes),0) AS measure,SUM(v.votes) AS matched
                FROM cbs_locality_vote_shares v JOIN cbs_socioeconomic s USING(locality_code)
                WHERE v.knesset=? AND v.ballot_code=? AND s.reference_year=2019 AND s.index_value IS NOT NULL
                AND NOT ((v.knesset=20 AND v.locality_code='0') OR(v.knesset=21 AND v.locality_code='99999') OR(v.knesset>=22 AND v.locality_code='9999'))''',(k,party['ballot_code'])).fetchone()
            row['area_socioeconomic_index']=q['measure']; row['socioeconomic_vote_coverage']=q['matched']/party['votes'] if q['matched'] and party['votes'] else 0
            result.append(row)
    write_csv(OUT/'party-area-footprints.csv',result)
    db.close()
    return result


def charts(rows,summaries):
    panels=[]
    for tier in sorted({r['tier'] for r in rows}):
        for election in sorted({r['election'] for r in rows}):
            subset=[r for r in rows if r['tier']==tier and r['election']==election and r['days']<=90]
            panels.append((tier,election,subset))
    width,height=1100,70+math.ceil(len(panels)/2)*260
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" font-size="12"><text x="20" y="25" font-size="20">Individual poll absolute seat error vs days before election</text><text x="20" y="48">Last90 days; shared scales; index dates are proxies. Blue=audited, orange=index-only. Lower is better.</text>']
    ymax=max(10,max(r['error'] for r in rows))
    for n,(tier,election,subset) in enumerate(panels):
        x,y=55+(n%2)*550,105+(n//2)*260
        svg.append(f'<text x="{x}" y="{y-12}">{html.escape(election)} / {"audited" if tier=="audited_release" else "index exploratory"} (n={len(subset)})</text>')
        for tick in range(0,101,20):
            py=y+160*(1-tick/ymax)
            if py>=y:
                svg.append(f'<path d="M{x} {py}h460" stroke="#ddd"/><text x="{x-25}" y="{py+4}">{tick}</text>')
        for tick in (0,7,30,60,90):
            svg.append(f'<text x="{x+tick/90*460}" y="{y+180}">{tick}</text>')
        for r in subset:
            color='#2266aa' if tier=='audited_release' else '#bf7400'
            svg.append(f'<circle cx="{x+r["days"]/90*460}" cy="{y+160*(1-r["error"]/ymax)}" r="3" opacity=".55" fill="{color}"><title>{html.escape(r["creator"])}: {r["error"]}</title></circle>')
        svg.append(f'<text x="{x+130}" y="{y+205}">Days before election (date basis differs by tier)</text>')
    svg.append('</g></svg>'); (OUT/'poll-error-trends.svg').write_text('\n'.join(svg),encoding='utf-8')
    page='''<!doctype html><meta charset="utf-8"><title>E005 research trial</title><style>body{font:16px sans-serif;max-width:1200px;margin:30px auto;padding:15px}img{width:100%}td,th{padding:7px;border-bottom:1px solid #ddd}table{border-collapse:collapse}</style><h1>Poll accuracy and bounded model trials</h1><p>Index statistics are exploratory retained-row summaries, NOT every independently verified poll. Source dates, lineups, missing metadata and syndicated duplicates limit inference. No poll weight or final model adopted. Variance is sample variance of poll total absolute seat errors, not predictive variance.</p><p><a href="summary.md">Summary</a> | <a href="poll-errors.csv">Individual polls</a> | <a href="campaign-summary.csv">All campaign summaries</a> | <a href="poll-patterns.csv">Creator/horizon patterns</a> | <a href="quality-oof.csv">Audited-only quality trial</a> | <a href="chronological-selection.csv">Chronological tuning</a> | <a href="party-area-footprints.csv">Geographic footprints, descriptive only</a></p><h2>Last90 days: means and sample variances</h2><table><tr><th>Tier</th><th>Election</th><th>N</th><th>Mean absolute seat error</th><th>Sample variance (seats squared)</th></tr>'''
    for s in summaries:
        if s['window']=='last_90_days':
            page+=f'<tr><td>{s["tier"]}</td><td>{s["election"]}</td><td>{s["n"]}</td><td>{s["mean"]:.2f}</td><td>{s["variance"]:.2f}</td></tr>' if s['variance'] is not None else ''
    page+='</table><img src="poll-error-trends.svg" alt="Individual poll errors by horizon and evidence tier">'
    (OUT/'index.html').write_text(page,encoding='utf-8')


def main():
    start=time.perf_counter(); OUT.mkdir(parents=True,exist_ok=True)
    configs=prepare_variants(OUT/'inputs')
    rows,summaries,_,_=poll_diagnostics(configs['expanded_history'])
    quality=quality_trial(rows)
    selections=temporal_trial(configs)
    geo=geographic_readiness()
    charts(rows,summaries)
    lines=['# E005 bounded research trial','', 'All results exploratory; no current forecast/turnout/model/poll-weight change.',
        '',f'Poll rows: audited={sum(r["tier"]=="audited_release" for r in rows)}, exploratory mapped index={sum(r["tier"]!="audited_release" for r in rows)}. See explicit exclusions; these are not certified independent releases.',
        '', '## Campaign errors, all retained pre-election rows', '', '| Tier | Election | N | Mean total absolute seat error | Sample variance |','|---|---|---:|---:|---:|']
    for s in summaries:
        if s['window']=='all_retained_pre_election':
            lines.append(f'| {s["tier"]} | {s["election"]} | {s["n"]} | {s["mean"]:.3f} | {s["variance"]} |')
    lines+=['','## Chronological parameter selection: 2021/2022','', '| History | Features | Election | Family | Selected | Fraction | Loss / mean loss |','|---|---|---|---|---|---:|---:|']
    for r in selections:
        if r['election'] in ('knesset_24_2021','knesset_25_2022'):
            lines.append(f'| {r["variant"]} | {r["features"]} | {r["election"]} | {r["family"]} | {r["selected_method"]} | {r["fraction"]} | {r["integer_error"]} / {r["reference_error"]} |')
    if quality:
        mae=st.mean(abs(r['actual_error']-r['expected_error']) for r in quality)
        base=st.mean(abs(r['actual_error']-r['prior_campaign_mean_baseline']) for r in quality)
        lines+=['',f'Audited-only error-prediction trial OOF MAE={mae:.3f}; prior campaign-mean baseline MAE={base:.3f}. These are poll-error prediction losses, not seat-forecast competition losses. No weighting adopted.']
    lines+=['',f'Audited sample-size coverage: {sum(bool(r["sample_size"]) for r in rows if r["tier"]=="audited_release")}/27. Index sample sizes are unknown, not imputed.',
        '',f'Geographic footprint rows={len(geo)}. All descriptive-only: CBS historical release dates unverified; current-election application additionally needs prior-election party/merger lineage. Profiles use2021 area demographics and2019 socioeconomic index. No individual demographic voting inference, no future-CBS historical model fitting.',
        '', 'In contrast to the broad descriptive profiles, the restricted prior-city-core ablation uses the dated November28,2018 CBS2015 press-release table, all15large cities, and only the PREVIOUS election votes for Shas/UTJ/Yisrael Beiteinu. Features: vote-weighted area index, matched-vote coverage, missing flag; no future/same-election outcomes, no new-alliance transfer assumptions. It is a partial geographic trial, not full age/sex/party-identity modeling.',
        '', 'Dynamic-gap ablation adds only a pre-cutoff filtered-level-minus-anchor feature, using fixed Q/R=1; no outcome enters feature extraction. Parameter/fraction selection uses at least two strictly earlier OOF elections; ties prefer smaller corrections. Earlier insufficient selections fall back to mean. Existing inspected outcomes are not new blind evidence.',
        '', 'Final integer allocations now have an explicit post-rounding sum120/nonnegative/integer assertion in addition to score validation. Largest-remainder allocation already preserves the total; independent nearest-integer rounding is not used.',
        '',f'Runtime seconds={time.perf_counter()-start:.3f}; commit={os.environ.get("GITHUB_SHA","local")}. Turnout/political-war-economic features deferred as requested.']
    (OUT/'summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    consumed=[Path(__file__),ROOT/'scripts/experiments.py',ROOT/'scripts/campaign_history.py',ROOT/'scripts/baseline.py',ROOT/'scripts/backtest.py',ROOT/'scripts/robustness.py',ROOT/'config/experiments.json']+list((ROOT/'data/database').glob('*.jsonl.gz'))+list((ROOT/'data/cbs-2026-10-21').glob('*.jsonl.gz'))+list((ROOT/'data/snapshots').rglob('*.json'))
    write_json(OUT/'manifest.json',dict(commit=os.environ.get('GITHUB_SHA','local'),fractions=FRACTIONS,feature_trial='original/dynamic_gap/prior_city_core/dynamic_plus_prior_city_core',
        input_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in consumed},
        policy='Index descriptive only; quality model audited only; no final selection; geographic historical eligibility gate remains closed'))
    print('\n'.join(lines),flush=True)
    # Public numerical results only: durable connector-readable fallback when binary
    # artifact downloads cannot be consumed by the current sandbox. No raw sources.
    compact={p.name:p.read_text(encoding='utf-8') for p in OUT.iterdir()
             if p.is_file() and p.suffix in ('.csv','.json','.svg','.html','.md')}
    encoded=base64.b64encode(gzip.compress(json.dumps(compact,ensure_ascii=False).encode('utf-8'),mtime=0)).decode('ascii')
    print('E005_REPORT_BASE64_BEGIN',flush=True)
    for n in range(0,len(encoded),8000):
        print(encoded[n:n+8000],flush=True)
    print('E005_REPORT_BASE64_END',flush=True)


if __name__=='__main__':
    main()

