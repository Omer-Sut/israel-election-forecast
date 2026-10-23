"""E006: explicit prior-list geographic-context ablation; no forecast replacement."""
from __future__ import annotations
import base64
import argparse
import copy
from datetime import date, timedelta
import gzip
import hashlib
import html
import json
import os
from pathlib import Path
import statistics as st
import sys
import time

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.baseline import ROOT, load_json
from scripts.build_database import records
from scripts.campaign_history import prepare_variants, write_json
from scripts.experiments import build_case, evaluate_cases, project
from scripts.research_trial import write_csv
from scripts.robustness import evaluate_fraction

OUT = ROOT / 'output/party-area-trial'
LINEAGE = ROOT / 'config/party-area-lineage.json'
EDITION = ROOT / 'data/snapshots/party-area-edition-audit-2026-10-23.json'
CITY = ROOT / 'data/snapshots/party-area-vintage-2018-2026-10-22.json'
ABLATIONS = ('original', 'cities_continuity', 'cities_pooled',
             'edition2015_continuity', 'edition2015_pooled')
METHODS = ('ridge_10', 'forest_3_5', 'xgb_2_50')
FRACTIONS = (0, .025, .05, .1, .25, .5, 1)
AREA_FEATURES = ('prior_area_index', 'matched_prior_vote_fraction',
                 'area_missing', 'pooled_lineage_proxy')


def validate_lineage(lineage, official):
    for k, spec in lineage['elections'].items():
        if spec['source_knesset'] != int(k)-1:
            raise ValueError('Only immediately previous elections may supply votes')
        targets, used = set(), set()
        for row in spec['mappings']:
            if row['target_id'] in targets:
                raise ValueError('Duplicate target identity')
            targets.add(row['target_id'])
            codes = row['source_ballot_codes']
            if not codes or len(codes) != len(set(codes)):
                raise ValueError('Empty or duplicated predecessor')
            if row['status'] not in ('continuity', 'pooled_proxy'):
                raise ValueError('Unknown lineage status')
            if row['status'] == 'continuity' and len(codes) != 1:
                raise ValueError('Continuity requires one predecessor')
            for code in codes:
                if (spec['source_knesset'], code) not in official:
                    raise ValueError('Predecessor absent from official inventory')
                if code in used:
                    raise ValueError('Predecessor reused across targets: possible hidden split')
                used.add(code)


def collect_area_totals():
    """Aggregate locality votes ONCE; no ballots, national duplication or imputation."""
    cities = load_json(CITY)
    audit = load_json(EDITION)
    measures = {'cities': {r['code']: r['index'] for r in cities['cities']}}
    ses = [r for r in records(ROOT/'data/cbs-2026-10-21/cbs_socioeconomic.jsonl.gz')
           if r['reference_year'] == audit['reference_year'] and r['source_id'] == audit['source_id']]
    measures['edition2015'] = {r['locality_code']: round(r['index_value'], 3)
                               for r in ses if r['index_value'] is not None}
    if len(measures['edition2015']) != 1183:
        raise ValueError('Unexpected frozen socioeconomic coverage')
    for check in audit['spot_checks']:
        if measures['edition2015'][check['locality_code']] != check['index']:
            raise ValueError('Dated edition spot check differs from frozen workbook')
    sources = {r['source_id']: r for r in records(ROOT/'data/cbs-2026-10-21/cbs_sources.jsonl.gz')}
    if sources[audit['source_id']]['sha256'] != audit['workbook_sha256']:
        raise ValueError('Workbook edition hash changed')
    official = {(r['knesset'], r['ballot_code']): r
                for r in records(ROOT/'data/database/official_lists.jsonl.gz')}
    geo = {r['geo_id']: r for r in records(ROOT/'data/database/geographies.jsonl.gz')
           if r['granularity'] == 'locality'}
    totals = {}
    for row in records(ROOT/'data/database/geographic_votes.jsonl.gz'):
        g = geo.get(row['geo_id'])
        if not g:
            continue
        code = str(int(g['attributes']['סמל ישוב']))
        if code in ('0', '9999', '99999'):
            continue
        for scope, values in measures.items():
            if code not in values:
                continue
            key = (scope, g['knesset'], row['ballot_code'])
            num, den = totals.get(key, (0, 0))
            totals[key] = (num + row['votes']*values[code], den + row['votes'])
    return totals, official, {'cities': cities['publication_date'],
                            'edition2015': audit['conservative_available_after']}


def area_context(k, target_id, cutoff, ablation, lineage, totals, official, available):
    """Fail closed for splits/new lists. Full edition is an explicit sensitivity."""
    spec = lineage['elections'].get(str(k))
    missing = dict(feature_values=[0, 0, 1, 0], source_knesset=k-1,
                   source_ballot_codes='', source_labels_he='', scope='none',
                   source_available_after='', matched_prior_votes=0, prior_national_votes=0,
                   area_index=None, vote_coverage=0, lineage_status='unmapped',
                   vintage_status='no_eligible_measure',
                   reason=spec['unmapped_reason'] if spec else lineage['initial_election']['reason'])
    if not spec:
        return missing
    row = next((r for r in spec['mappings'] if r['target_id'] == target_id), None)
    if not row:
        return missing
    if row['status'] == 'pooled_proxy' and not ablation.endswith('_pooled'):
        return {**missing, 'lineage_status':'pooled_proxy_disabled', 'reason':row['rationale']}
    scope = 'edition2015' if ablation.startswith('edition2015') and available['edition2015'] < cutoff else 'cities'
    if available[scope] >= cutoff:
        return {**missing, 'reason':'CBS measure not available before forecast cutoff'}
    previous = spec['source_knesset']
    if previous >= k:
        raise ValueError('Same/future election votes forbidden')
    codes = row['source_ballot_codes']
    pairs = [totals.get((scope, previous, c), (0, 0)) for c in codes]
    numerator, denominator = sum(x[0] for x in pairs), sum(x[1] for x in pairs)
    national = sum(official[previous, c]['votes'] for c in codes)
    if not denominator or not national:
        return {**missing, 'lineage_status':row['status'], 'reason':'No matched prior votes'}
    if denominator > national:
        raise ValueError('Matched votes exceed national predecessor votes')
    value, coverage = numerator/denominator, denominator/national
    return dict(feature_values=[value, coverage, 0, int(row['status']=='pooled_proxy')],
                source_knesset=previous, source_ballot_codes='|'.join(codes),
                source_labels_he=' | '.join(official[previous,c].get('party_name_he') or
                                            official[previous,c].get('party_name_en','') for c in codes),
                scope=scope, source_available_after=available[scope], matched_prior_votes=denominator,
                prior_national_votes=national, area_index=value, vote_coverage=coverage,
                lineage_status=row['status'],
                vintage_status=('dated_press_release_transcription' if scope=='cities' else
                                'edition_linked_assumption_not_authenticated_archive'),
                reason=row['rationale'])


def choose_earlier(rows, cutoff, metric):
    grouped = {}
    for row in rows:
        if row['election_date'] < cutoff:
            grouped.setdefault(row['fraction'], []).append(row)
    eligible = [(st.mean(r[metric] for r in group), fraction, group)
                for fraction, group in grouped.items()
                if len({r['election'] for r in group}) >= 2]
    if not eligible:
        return None
    _, fraction, group = min(eligible, key=lambda x:x[:2])
    return fraction, '|'.join(sorted({r['election'] for r in group}))


def chart(scores):
    colors = dict(zip(ABLATIONS, ('#333333','#0072b2','#009e73','#d55e00','#cc79a7')))
    elections = sorted({r['election'] for r in scores})
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="530" viewBox="0 0 1160 530">',
           '<rect width="1160" height="530" fill="white"/>',
           '<g font-family="Arial,sans-serif" fill="#222">',
           '<text x="30" y="28" font-size="19">E006: fixed 25% correction — total absolute seat error</text>',
           '<text x="30" y="50" font-size="13">Exploratory retrospective comparisons; edition-linked inputs retain revision uncertainty.</text>']
    maximum = max(32, max(r['integer_error'] for r in scores if r['fraction']==.25)+2)
    for panel, method in enumerate(METHODS):
        left, top, width, height = 55+panel*385, 100, 290, 280
        svg.append(f'<text x="{left}" y="85" font-size="16">{html.escape(method)}</text>')
        for tick in range(0, int(maximum)+1, 10):
            y = top+height-height*tick/maximum
            svg.append(f'<path d="M{left},{y}h{width}" stroke="#ddd"/><text x="{left-28}" y="{y+4}" font-size="12">{tick}</text>')
        for feature in (*ABLATIONS, 'mean_reference'):
            pts=[]
            for i, election in enumerate(elections):
                r=next(r for r in scores if r['method']==method and r['ablation']==('original' if feature=='mean_reference' else feature) and r['election']==election and r['fraction']==.25)
                value=r['reference_integer_error'] if feature=='mean_reference' else r['integer_error']
                x,y=left+i*width/(len(elections)-1),top+height-height*value/maximum
                pts.append(f'{x},{y}')
                if feature=='original':
                    svg.append(f'<text x="{x-21}" y="{top+height+22}" font-size="12">{election.split("_")[-1]}</text>')
            color=colors.get(feature,'#888888')
            dash=' stroke-dasharray="6 4"' if feature=='mean_reference' else ''
            svg.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2"{dash}/>')
    for i, feature in enumerate((*ABLATIONS,'mean_reference')):
        x,y=35+(i%3)*385,435+(i//3)*27
        svg.append(f'<path d="M{x},{y}h25" stroke="{colors.get(feature,"#888")}" stroke-width="3"/><text x="{x+32}" y="{y+4}" font-size="13">{feature}</text>')
    svg += ['<text x="30" y="515" font-size="12">Lower is better. Sep2019 and 2020 provide earlier OOF history; 2021/2022 were already inspected.</text>','</g></svg>']
    (OUT/'performance.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')


def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=OUT)
    OUT=parser.parse_args().out_dir.resolve()
    start=time.perf_counter(); OUT.mkdir(parents=True,exist_ok=True)
    configs=prepare_variants(OUT/'inputs')
    config=load_json(configs['expanded_history'])
    config['models']=[m for m in config['models'] if m['id'] in METHODS]
    config['ensemble_members']=[METHODS[0]]
    history=load_json(ROOT/config['historical_config'])
    outcomes={k:v['seat_results'] for k,v in load_json(ROOT/history['outcomes_path'])['elections'].items()}
    cases=[]
    for spec in history['elections']:
        snapshot=load_json(ROOT/spec['polls_path'])
        cutoff=(date.fromisoformat(snapshot['election_date'])-timedelta(days=1)).isoformat()
        c=build_case(snapshot,cutoff,history['poll_window_days'],history['minimum_groups'])
        c['horizon_days']=1; cases.append(c)
    totals,official,available=collect_area_totals()
    lineage=load_json(LINEAGE); validate_lineage(lineage,official)
    # Catch typos that would otherwise silently make a configured target missing.
    for c in cases:
        k=int(c['election_id'].split('_')[1])
        if not {r['target_id'] for r in lineage['elections'].get(str(k),{}).get('mappings',[])} <= set(c['ids']):
            raise ValueError('Configured lineage target absent from model panel')
    contexts,scores,selections,coverage=[],[],[],[]
    for ablation in ABLATIONS:
        trial=copy.deepcopy(cases)
        for c in trial:
            k=int(c['election_id'].split('_')[1]); available_rows=[]
            if ablation!='original':
                for i,target in enumerate(c['ids']):
                    ctx=area_context(k,target,c['cutoff'],ablation,lineage,totals,official,available)
                    c['features'][i]+=ctx['feature_values']
                    contexts.append(dict(ablation=ablation,election=c['election_id'],target_id=target,
                                         cutoff=c['cutoff'],**{k:v for k,v in ctx.items() if k!='feature_values'}))
                    available_rows.append(ctx)
                coverage.append(dict(ablation=ablation,election=c['election_id'],lists=len(c['ids']),
                                     lists_with_profile=sum(not r['feature_values'][2] for r in available_rows),
                                     mean_coverage_of_available=st.mean(r['vote_coverage'] for r in available_rows if not r['feature_values'][2]) if any(not r['feature_values'][2] for r in available_rows) else 0))
        results=evaluate_cases(trial,outcomes,config)
        block=[]
        for c in results:
            actual=[outcomes[c['election_id']][key] for key in c['ids']]
            ref_cont=sum(abs(a-b) for a,b in zip(project(c['anchor']),actual))
            for method in METHODS:
                entry=c['methods'][method]
                if 'continuous_unshrunk' not in entry:
                    continue
                for fraction in FRACTIONS:
                    cp,ip,ce,ie=evaluate_fraction(c['anchor'],entry['continuous_unshrunk'],actual,fraction)
                    block.append(dict(ablation=ablation,election=c['election_id'],election_date=c['election_date'],
                                      cutoff=c['cutoff'],method=method,fraction=fraction,continuous_error=ce,
                                      integer_error=ie,reference_continuous_error=ref_cont,
                                      reference_integer_error=c['methods']['rounded_mean_reference']['score']['total_absolute_seat_error'],
                                      continuous_prediction=json.dumps(dict(zip(c['ids'],cp))),
                                      integer_prediction=json.dumps(dict(zip(c['ids'],ip))),
                                      training_elections='|'.join(c['training_elections'])))
        scores.extend(block)
        for c in results:
            for method in METHODS:
                pool=[r for r in block if r['method']==method]
                for metric in ('continuous_error','integer_error'):
                    selected=choose_earlier(pool,c['cutoff'],metric)
                    target=next((r for r in pool if r['election']==c['election_id'] and selected and r['fraction']==selected[0]),None)
                    selections.append(dict(ablation=ablation,election=c['election_id'],method=method,selection_metric=metric,
                        fraction=selected[0] if selected else 0,selection_elections=selected[1] if selected else '',
                        continuous_error=target['continuous_error'] if target else sum(abs(a-outcomes[c['election_id']][key]) for a,key in zip(project(c['anchor']),c['ids'])),
                        integer_error=target['integer_error'] if target else c['methods']['rounded_mean_reference']['score']['total_absolute_seat_error'],
                        reference_error=c['methods']['rounded_mean_reference']['score']['total_absolute_seat_error'],
                        status='selected_on_at_least_two_earlier_oof' if selected else 'insufficient_oof_use_exact_reference'))
    write_csv(OUT/'contexts.csv',contexts); write_csv(OUT/'coverage.csv',coverage)
    write_csv(OUT/'scores.csv',scores); write_csv(OUT/'selection.csv',selections)
    chart(scores)
    lines=['# E006: expanded party-area context trial','',
           'No current forecast, turnout, poll weights, merge or submission changed.',
           'Only three fixed existing learners, one expanded audited history, T-1 and earlier-election training. No new model/hyperparameter grid.',
           '', '## Fixed 25% corrections: final comparison elections','',
           '| Features | Method | 2021 integer / continuous error | 2022 integer / continuous error |',
           '|---|---|---:|---:|']
    for ablation in ABLATIONS:
        for method in METHODS:
            late=[next(r for r in scores if r['ablation']==ablation and r['method']==method and r['election']==e and r['fraction']==.25) for e in ('knesset_24_2021','knesset_25_2022')]
            lines.append(f'| {ablation} | {method} | {late[0]["integer_error"]} / {late[0]["continuous_error"]:.3f} | {late[1]["integer_error"]} / {late[1]["continuous_error"]:.3f} |')
    lines+=['','Reference integer errors: 2021=20; 2022=12. Lower is better.',
            '', 'See selection.csv for correction fractions chosen using continuous OR integer loss on at least two earlier OOF elections. Feature sets and model IDs themselves are NOT selected by this inner rule.',
            '', 'City profiles use the dated 2018 release. Full 2015 edition (1183 localities) begins only after2019-08-31, falling back to the city subset before then. Its dated publication/table linkage and spot checks do NOT authenticate an archived workbook or prove absence of revisions; remains separately labeled retrospective sensitivity. No CBS historical_availability flag changed.',
            '', 'Continuity means an explicit retained-party/whole-alliance geographic proxy, not unchanged voters. Pooled mode adds five explicit predecessor pools. Splits/new lists remain missing. Previous votes are pooled BEFORE averaging characteristics; no seats or target-election votes enter geographic features. Coverage is matched predecessor votes / predecessor NATIONAL votes, not target votes.',
            '', 'All appended features are exported by target in contexts.csv with source election, codes, labels, date, vintage tier and missing reason. Four feature names: '+', '.join(AREA_FEATURES)+'.',
            '', 'Age/sex remain outside historical fitting pending date audit. 2017 SES release/revision was located but is not fitted here. No individual voter demographic inference; no ballot-neighborhood claim. Previously inspected national outcomes are exploratory, not blind validation.',
            '', f'Runtime seconds={time.perf_counter()-start:.3f}; code_commit={os.environ.get("GITHUB_SHA","local")}. Seed={config["seed"]}. User hands-on/cumulative effort unmeasured; no local setup required.']
    (OUT/'summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    files=[Path(__file__),LINEAGE,EDITION,CITY,ROOT/'scripts/experiments.py',ROOT/'scripts/robustness.py',ROOT/'scripts/campaign_history.py',ROOT/'config/experiments.json']+list((ROOT/'data/database').glob('*.jsonl.gz'))+list((ROOT/'data/cbs-2026-10-21').glob('*.jsonl.gz'))+list((ROOT/'data/snapshots').rglob('*.json'))+list((OUT/'inputs').rglob('*.json'))
    write_json(OUT/'manifest.json',dict(code_commit=os.environ.get('GITHUB_SHA','local'),seed=config['seed'],methods=METHODS,fractions=FRACTIONS,ablations=ABLATIONS,area_features=AREA_FEATURES,
        input_hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        policy='Explicit prior-election proxies only; full edition is retrospective assumption sensitivity; no final adoption.'))
    print('\n'.join(lines),flush=True)
    public={p.name:p.read_text(encoding='utf-8') for p in OUT.iterdir() if p.is_file() and p.suffix in ('.csv','.json','.svg','.md')}
    encoded=base64.b64encode(gzip.compress(json.dumps(public,ensure_ascii=False).encode('utf-8'),mtime=0)).decode('ascii')
    print('E006_REPORT_BASE64_BEGIN',flush=True)
    for i in range(0,len(encoded),8000):
        print(encoded[i:i+8000],flush=True)
    print('E006_REPORT_BASE64_END',flush=True)


if __name__=='__main__':
    main()
