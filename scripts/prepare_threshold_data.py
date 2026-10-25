"""Build a separate, audited threshold-evidence overlay; never mutate frozen inputs."""
import argparse
import base64
import copy
import csv
from datetime import date, timedelta
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import baseline

ROOT=baseline.ROOT
FOLDER=ROOT/'data/snapshots/threshold-data-2026-10-25'


def canonical_url(url):
    parts=urlsplit(url)
    if parts.scheme not in ('http','https') or not parts.netloc:
        raise ValueError('Expected attributed public source URL')
    return parts.netloc.lower()+unquote(parts.path).rstrip('/')


def temporal_features(poll,election_date):
    day=date.fromisoformat(election_date);publication=date.fromisoformat(poll['published_on'])
    updated=poll.get('source_updated_on')
    available=max(publication,date.fromisoformat(updated)) if updated else publication
    start,end=poll.get('fieldwork_start'),poll.get('fieldwork_end')
    if publication>=day or available>=day:
        raise ValueError('Post-election publication/revision cannot enter historical overlay')
    if start and end and start>end:raise ValueError('Reversed fieldwork dates')
    if end and end>poll['published_on']:raise ValueError('Fieldwork after publication requires explicit conflict handling')
    lead=(day-publication).days
    cutoff=day-timedelta(days=1)
    effective=date.fromisoformat(end) if end else publication
    return {'publication_lead_days':lead,'availability_lead_days':(day-available).days,
        'fieldwork_lead_days':(day-date.fromisoformat(end)).days if end else None,
        'publication_horizon_band':'1_7' if lead<=7 else '8_14' if lead<=14 else '15_28',
        'date_eligible_at_t1_under_original_age_gate':available<=cutoff and effective>=cutoff-timedelta(days=14),
        'availability_basis':'known_source_update' if updated else 'publication_proxy_revision_unknown'}


def pre_election_features(row):
    """Explicit whitelist: final outcomes never become predictor fields."""
    return {k:row[k] for k in ('poll_id','election_id','party_id','pollster_group','publisher',
        'reported_vote_pct','percentage_status','projected_seats','seat_value_basis',
        'publication_lead_days','availability_lead_days','fieldwork_lead_days','publication_horizon_band',
        'date_eligible_at_t1_under_original_age_gate','sample_size','mode','undecided_pct',
        'undecided_approximate','denominator_status','undecided_allocation','wave_linkage_uncertain',
        'strict_valid_vote_denominator_verified','archival_vintage_verified')}


def observations(polls,registries,truth):
    rows=[];unmapped=[]
    for poll in polls:
        election=poll['election_id'];registry=registries[election]
        timing=temporal_features(poll,registry['date'])
        shares=poll.get('reported_below_threshold_pct',{})
        labels=poll.get('percentage_raw_labels',{})
        if set(shares)-set(registry['lists']):raise ValueError('Unreviewed percentage identity')
        for key,item in registry['lists'].items():
            value=shares.get(key)
            if value is not None and (isinstance(value,bool) or not 0<=value<=100):raise ValueError('Invalid percent')
            row={'poll_id':poll['id'],'election_id':election,'party_id':key,'party_label_he':item.get('label_he'),
                'party_label_en':item['label_en'],'pollster_group':poll['pollster_group'],'publisher':poll['publisher'],
                'source_url':poll['source_url'],'published_on':poll['published_on'],
                'source_updated_on':poll.get('source_updated_on'),'overlay_built_on':'2026-10-25',
                'source_audited_on':poll.get('percentage_rechecked_on',poll.get('retrieved_on')),
                'original_audit_retrieved_on':poll.get('retrieved_on'),
                'source_origin':poll['extension_origin'],'reported_vote_pct':value,
                'percentage_raw_label_he':labels.get(key),
                'percentage_status':'exact_as_published' if value is not None else 'not_reported_or_not_retrieved',
                'projected_seats':poll['reported_seats'].get(key,0),
                'seat_value_basis':'explicit_seat_entry' if key in poll['reported_seats'] else 'zero_allocation_from_complete_table',
                'denominator_status':poll.get('denominator_status','unspecified_publisher_vote_intention_basis'),
                'undecided_allocation':poll.get('undecided_allocation'),
                'undecided_pct':poll.get('undecided_pct'),'undecided_approximate':poll.get('undecided_approximate',False),
                'sample_size':poll.get('sample_size'),'mode':poll.get('mode'),
                'wave_linkage_uncertain':bool(poll.get('possible_reused_fieldwork_metadata_with')),
                'strict_valid_vote_denominator_verified':False,'archival_vintage_verified':False,
                **timing,'actual_seats':truth[election]['seat_results'][key],
                'actually_represented':truth[election]['seat_results'][key]>0}
            rows.append(row)
        for item in poll.get('unmapped_percentages',[]):
            unmapped.append({'poll_id':poll['id'],'election_id':election,'source_url':poll['source_url'],**item})
    return rows,unmapped


def validate_release(poll,registry,window):
    raw=poll['reported_seats']
    if not poll.get('seat_projection_complete') or set(raw)-set(registry['lists']) or sum(raw.values())!=120 or any(not baseline.seat_integer(v) for v in raw.values()):
        raise ValueError('Require a complete historical120-seat table with reviewed identities')
    timing=temporal_features(poll,registry['date'])
    if not 1<=timing['publication_lead_days']<=window:raise ValueError('Outside frozen discovery window')
    if not poll.get('source_url'):raise ValueError('Missing original source')
    canonical_url(poll['source_url'])


def build():
    protocol=baseline.load_json(FOLDER/'protocol.json')
    additions=baseline.load_json(FOLDER/'additions.json')
    config=baseline.load_json(ROOT/protocol['historical_config'])
    truth=baseline.load_json(ROOT/config['outcomes_path'])['elections']
    registries={};original=[];input_paths=[]
    for spec in config['elections']:
        snap=baseline.load_json(ROOT/spec['polls_path']);input_paths.append(spec['polls_path'])
        registries[spec['id']]={'date':snap['election_date'],'lists':{p['id']:p for p in snap['lists']}}
        for raw in snap['polls']:
            poll=copy.deepcopy(raw);poll['extension_origin']='inherited_frozen_audit'
            original.append(poll)
    original_rows,_=observations(original,registries,truth)
    augmented=copy.deepcopy(original);by_id={p['id']:p for p in augmented}
    for extra in additions['enrich_existing']:
        if extra['poll_id'] not in by_id:raise ValueError('Unknown inherited release')
        poll=by_id[extra['poll_id']]
        if canonical_url(poll['source_url'])!=canonical_url(extra['source_url']) or poll['election_id']!=extra['election_id']:
            raise ValueError('Enrichment crossed release identity')
        for key,value in extra.items():
            if key not in ('poll_id','election_id','source_url','percentages'):
                poll[key]=copy.deepcopy(value)
        poll['percentage_raw_labels']={}
        for item in extra['percentages']:
            key,value=item['party_id'],item['value']
            old=poll.setdefault('reported_below_threshold_pct',{}).get(key)
            if old is not None and old!=value:raise ValueError('Conflicting inherited percentage')
            poll['reported_below_threshold_pct'][key]=value
            poll['percentage_raw_labels'][key]=item['raw_label_he']
        poll['extension_origin']='existing_release_percentage_enrichment'
        poll['percentage_rechecked_on']=additions['reviewed_on']
    for raw in additions['new_releases']:
        if raw['id'] in by_id:raise ValueError('Duplicate poll ID')
        poll=copy.deepcopy(raw);poll.update(kind='pre_election_poll',seat_projection_complete=True,
            retrieved_on=additions['reviewed_on'],extension_origin='new_original_publisher_release',
            reported_below_threshold_pct={r['party_id']:r['value'] for r in raw['percentages']},
            percentage_raw_labels={r['party_id']:r['raw_label_he'] for r in raw['percentages']})
        augmented.append(poll);by_id[poll['id']]=poll
    if len(by_id)!=len(augmented):raise ValueError('Duplicate inherited ID')
    urls=[canonical_url(p['source_url']) for p in augmented]
    if len(set(urls))!=len(urls):raise ValueError('Syndicated/alternate URL duplicate; reconcile before admission')
    for poll in augmented:validate_release(poll,registries[poll['election_id']],protocol['discovery_window_days'])
    rows,unmapped=observations(augmented,registries,truth)
    coverage=[]
    for election,registry in registries.items():
        before=[r for r in original_rows if r['election_id']==election and r['reported_vote_pct'] is not None]
        after=[r for r in rows if r['election_id']==election and r['reported_vote_pct'] is not None]
        coverage.append({'election_id':election,'original_releases':sum(p['election_id']==election for p in original),
            'extended_releases':sum(p['election_id']==election for p in augmented),
            'original_exact_percentage_observations':len(before),'extended_exact_percentage_observations':len(after),
            'eventual_pass_observations':sum(r['actually_represented'] for r in after),
            'eventual_fail_observations':sum(not r['actually_represented'] for r in after),
            'unique_percentage_list_outcomes':len({r['party_id'] for r in after}),
            'horizon_counts':{band:sum(r['publication_horizon_band']==band for r in after) for band in ('1_7','8_14','15_28')}})
    exact=[r for r in rows if r['reported_vote_pct'] is not None]
    summary={'original_releases':len(original),'extended_releases':len(augmented),
        'new_releases':len(additions['new_releases']),'enriched_existing_releases':len(additions['enrich_existing']),
        'original_exact_percentages':sum(r['reported_vote_pct'] is not None for r in original_rows),
        'extended_exact_percentages':len(exact),'percentage_campaigns':sum(c['extended_exact_percentage_observations']>0 for c in coverage),
        'eventual_pass_observations':sum(r['actually_represented'] for r in exact),
        'eventual_fail_observations':sum(not r['actually_represented'] for r in exact),
        'unique_percentage_list_outcomes':len({(r['election_id'],r['party_id']) for r in exact}),
        'unique_eventual_pass_list_outcomes':len({(r['election_id'],r['party_id']) for r in exact if r['actually_represented']}),
        'unmapped_percentage_observations':len(unmapped),'strict_valid_vote_comparable_observations':0,
        'model_fitted':False,'forecast_changed':False}
    return {'protocol':protocol,'summary':summary,'coverage':coverage,'observations':rows,
        'unmapped_observations':unmapped,'releases':augmented,'input_paths':input_paths+[config['outcomes_path']],
        'decision':'Keep audited overlay; no automatic training promotion, model fit or forecast change.'}


def write(report,out):
    out.mkdir(parents=True,exist_ok=True)
    def save(name,text):(out/name).write_text(text,encoding='utf-8',newline='\n')
    def jsave(name,value):save(name,json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    jsave('coverage.json',{k:report[k] for k in ('summary','coverage','decision')})
    jsave('releases.json',report['releases']);jsave('unmapped.json',report['unmapped_observations'])
    with (out/'observations.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(report['observations'][0]),lineterminator='\n')
        writer.writeheader();writer.writerows(report['observations'])
    jsave('predictor-records.json',[pre_election_features(r) for r in report['observations']])
    lines=['# E019: extended historical threshold evidence','',report['decision'],'',
        f"Audited releases: {report['summary']['original_releases']} → {report['summary']['extended_releases']}. Exact reported percentage observations: {report['summary']['original_exact_percentages']} → {report['summary']['extended_exact_percentages']}. These are repeated poll/list measurements, not independent election outcomes.",'',
        '| Campaign | Releases before/after | Exact percentages before/after | Eventual passes/fails* |',
        '|---|---:|---:|---:|']
    for c in report['coverage']:
        lines.append(f"| {c['election_id']} | {c['original_releases']}/{c['extended_releases']} | {c['original_exact_percentage_observations']}/{c['extended_exact_percentage_observations']} | {c['eventual_pass_observations']}/{c['eventual_fail_observations']} |")
    s=report['summary']
    lines+=['',f"*Among exact reported-share observations: {s['eventual_pass_observations']} later-pass records and {s['eventual_fail_observations']} later-fail records, covering {s['unique_percentage_list_outcomes']} unique election/list outcomes ({s['unique_eventual_pass_list_outcomes']} that passed). Repeated releases share the same result.",'',
        '![Percentage coverage extension](percentage-coverage.svg)','','## What improved','',
        'Eight complete original-publisher releases add trajectories and another firm in April2019; two existing releases gain explicit percentages. We now retain Raam–Balad2019Apr and Raam/Meretz2021 examples with below-threshold published support that later won seats. The original exact-percentage subset contained only eventual failures. This corrects a training-data coverage limitation, not a forecast error by itself.','',
        'Source publication, fieldwork and known revision dates are separate. Discovery includes final28publication days; horizon bands1–7,8–14,15–28 and the original T−1 effective-age gate are exported separately. Never pool these as matched final-week observations.','',
        '## Quality limits and gates','',
        'The reported percentage denominator and allocation of undecided voters remain unverified. None is certified directly comparable to valid-vote share. No shares are normalized, inferred from seats or assigned numerical lower bounds from positive seat projections. Missing values stay blank/null, never zero. Retrospective source versions are not authenticated historical archives.','',
        'The two Walla2020 releases print identicalFeb16–17fieldwork,N502/invited3486 despite different publication dates/results. A wave-linkage warning is retained; these cannot be counted as independent samples. N12 and Walla share Midgam, while MakoMorningApril2019 uses PanelsPolitics; commissioner and firm are separate fields.','',
        '2015 still lacks recovered numerical shares in the reviewed original articles. New2021percentage coverage is concentrated in one polling firm. One Maan2021percentage is retained in unmapped.json pending an official identity check and is excluded from outcome-linked counts. No full current vote vector or new current forecast is supplied.','',
        'A blocked official2022PDF is only a discovery lead in source-audit.json, not admitted data. Secondary contradictory tables and earlier-wave comparison figures are not silently copied.','',
        'observations.csv includes evaluation labels; predictor-records.json is an explicit pre-election whitelist and excludes outcomes. Any later learner must use earlier campaigns only and preserve campaign/firm/release dependence. The export is a separate overlay; all frozen model inputs and adopted69.86%turnout/seat forecast remain unchanged.','']
    save('analysis.md','\n'.join(lines)+'\n')
    paths=['scripts/prepare_threshold_data.py','data/snapshots/threshold-data-2026-10-25/protocol.json',
        'data/snapshots/threshold-data-2026-10-25/additions.json','data/snapshots/threshold-data-2026-10-25/source-audit.json',
        report['protocol']['historical_config'],'scripts/baseline.py']+report['input_paths']
    jsave('inputs-manifest.json',{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set(paths))})
    plot(report,out)


def plot(report,out):
    maximum=max(c['extended_exact_percentage_observations'] for c in report['coverage'])+2
    p=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="520" viewBox="0 0 1100 520"><rect width="1100" height="520" fill="white"/><g font-family="Arial,sans-serif" fill="#19364b">',
       '<text x="25" y="30" font-size="23">Historical threshold data: recovered reported percentages</text>',
       '<text x="25" y="57" font-size="14">Counts of poll/list measurements. Same-election records are dependent; no model fit.</text>']
    labels=['2015','2019 Apr','2019 Sep','2020','2021','2022']
    for i,c in enumerate(report['coverage']):
        x=100+i*165
        for offset,key,color in [(0,'original_exact_percentage_observations','#8594a0'),(43,'extended_exact_percentage_observations','#217eaa')]:
            value=c[key];height=value/maximum*290
            p.append(f'<rect x="{x+offset}" y="{380-height:.2f}" width="36" height="{height:.2f}" fill="{color}"/><text x="{x+offset+8}" y="{370-height:.2f}" font-size="13">{value}</text>')
        p.append(f'<text x="{x-4}" y="405" font-size="14">{labels[i]}</text>')
    p.append('<text x="25" y="445" fill="#8594a0" font-size="15">Gray: frozen audited snapshot</text><text x="430" y="445" fill="#217eaa" font-size="15">Blue: separate reviewed extension</text><text x="25" y="485" font-size="13">All percentage denominators remain unverified; counts measure data coverage, not predictive accuracy.</text></g></svg>')
    (out/'percentage-coverage.svg').write_text('\n'.join(p)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=ROOT/'output/threshold-data')
    args=parser.parse_args();write(build(),args.out_dir)
    files={p.name:p.read_text(encoding='utf-8') for p in sorted(args.out_dir.iterdir()) if p.is_file()}
    encoded=base64.b64encode(gzip.compress(json.dumps(files,ensure_ascii=False).encode())).decode()
    print('E019_FILES_BASE64_BEGIN')
    for i in range(0,len(encoded),8000):print(encoded[i:i+8000])
    print('E019_FILES_BASE64_END');print(files['analysis.md'])
