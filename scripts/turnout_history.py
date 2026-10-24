"""Past-election turnout diagnostics; leaves the working forecast unchanged."""
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

if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts import baseline

ROOT=baseline.ROOT
INPUT=ROOT/'data/snapshots/turnout-history-2026-10-24/inputs.json'
METHODS=('previous_election','last_three_mean','last_three_median')


def forecasts(earlier):
    """Fixed references only: caller must pass strictly earlier outcomes."""
    if len(earlier)<3: raise ValueError('Three earlier elections required')
    values=[r['turnout_pct'] for r in earlier]
    return dict(zip(METHODS,(values[-1],statistics.mean(values[-3:]),statistics.median(values[-3:]))))


def rolling_checks(rows):
    result=[]
    for i in range(3,len(rows)):
        row=rows[i];pred=forecasts(rows[:i])
        result.append({'knesset':row['knesset'],'election_date':row['election_date'],
            'actual':row['turnout_pct'],'training_knessets':[r['knesset'] for r in rows[:i]],
            'predictions':pred,'absolute_errors':{k:abs(v-row['turnout_pct']) for k,v in pred.items()}})
    return result


def first_election_context(rows,events,kinds):
    """First election after each selected onset; never double-count an election."""
    mapped={}
    for event in events:
        if event['kind'] not in kinds:continue
        # One-day-before-election information boundary, even for context coding.
        eligible=[r for r in rows if date.fromisoformat(event['onset']) <= date.fromisoformat(r['election_date'])-timedelta(days=1)]
        if not eligible:continue
        target=eligible[0]
        mapped.setdefault(target['knesset'],[]).append(event['id'])
    result=[]
    for i,row in enumerate(rows):
        if row['knesset'] in mapped:
            result.append({'knesset':row['knesset'],'election_date':row['election_date'],
                'events':mapped[row['knesset']],
                'turnout_change_pp':None if i==0 else row['turnout_pct']-rows[i-1]['turnout_pct']})
    return result


def summary(values):
    return {'n':len(values),'mean':statistics.mean(values) if values else None,
            'median':statistics.median(values) if values else None,
            'sample_sd':statistics.stdev(values) if len(values)>1 else None}


def form_candidate(value,contract):
    field=contract['turnout_field']
    return {'unconstrained_pct':value,'formatted':f'{value:.2f}',
            'within_form_bounds':field['minimum']<=value<=field['maximum']}


def build():
    inputs=baseline.load_json(INPUT);rows=inputs['elections'];events=inputs['conflict_events']
    if len(rows)!=25 or [r['knesset'] for r in rows]!=list(range(1,26)):
        raise ValueError('Require all25 distinct Knesset elections; no2001 PM-only row')
    for r in rows:
        if not 0<=r['valid']<=r['ballots']<=r['electorate']:
            raise ValueError('Count denominator mismatch')
        if abs(100*r['ballots']/r['electorate']-r['turnout_pct'])>0.051:
            raise ValueError('Published turnout/count discrepancy exceeds rounding precision')
    folds=rolling_checks(rows);recent=[r for r in folds if r['knesset']>=20]
    #2019–2021 is one evaluation block as a sensitivity, not four independent replications.
    blocks=[[r for r in recent if r['knesset']==20],
            [r for r in recent if 21<=r['knesset']<=24],
            [r for r in recent if r['knesset']==25]]
    metrics={}
    for name in METHODS:
        metrics[name]={'all_common_folds_mae':statistics.mean(r['absolute_errors'][name] for r in folds),
            'recent_six_mae':statistics.mean(r['absolute_errors'][name] for r in recent),
            'recent_three_block_mae':statistics.mean(statistics.mean(r['absolute_errors'][name] for r in b) for b in blocks)}
    history=[]
    for i,r in enumerate(rows):
        history.append({**r,'change_pp':None if i==0 else r['turnout_pct']-rows[i-1]['turnout_pct'],
            'days_since_previous':None if i==0 else (date.fromisoformat(r['election_date'])-date.fromisoformat(rows[i-1]['election_date'])).days})
    context={}
    for label,kinds in [('six_named_wars',{'war'}),('wars_plus_four_operations',{'war','operation'})]:
        matches=first_election_context(rows,events,kinds);selected={r['knesset'] for r in matches}
        context[label]={'first_elections':matches,
            'following_onset_change':summary([r['turnout_change_pp'] for r in matches if r['turnout_change_pp'] is not None]),
            'other_changes':summary([r['change_pp'] for r in history if r['knesset'] not in selected and r['change_pp'] is not None]),
            'onset_windows':{}}
        for window in inputs['conflict_protocol']['windows_days']:
            chosen=[r for r in history if r['change_pp'] is not None and any(
                e['kind'] in kinds and 1<=(date.fromisoformat(r['election_date'])-date.fromisoformat(e['onset'])).days<=window for e in events)]
            context[label]['onset_windows'][str(window)]={**summary([r['change_pp'] for r in chosen]),'knessets':[r['knesset'] for r in chosen]}
    config_path=ROOT/'data/snapshots/screening-six-elections-2026-10-21/prepared/historical.json'
    config=baseline.load_json(config_path);polls=[];panel_count=0
    for e in config['elections']:
        snap=baseline.load_json(ROOT/e['polls_path']);panel_count+=len(snap['polls'])
        for p in snap['polls']:
            if 'turnout_intention_pct' not in p:continue
            actual=next(r['turnout_pct'] for r in rows if r['election_date']==snap['election_date'])
            polls.append({'id':p['id'],'election_date':snap['election_date'],'published_on':p['published_on'],
                'source_updated_on':p.get('source_updated_on'),'source_url':p['source_url'],
                'reported_intention_pct':p['turnout_intention_pct'],'actual_turnout_pct':actual,
                'intention_minus_actual_pp':p['turnout_intention_pct']-actual,
                'usage':'Descriptive only; one independent election, no calibration fitted.'})
    contract=baseline.load_json(ROOT/'config/submission-fields.json')
    draft_path=ROOT/'reports/review-package-2026-10-24/forecast.json'
    draft=baseline.load_json(draft_path)
    return {'scope':inputs['coverage'],'history':history,'folds':folds,'recent_folds':recent,
        'metrics':metrics,'period_summaries':{
            '1949_1999':summary([r['turnout_pct'] for r in rows if r['knesset']<=15]),
            '2003_2022':summary([r['turnout_pct'] for r in rows if r['knesset']>=16]),
            '2015_2022':summary([r['turnout_pct'] for r in rows if r['knesset']>=20])},
        'conflict_context':context,'poll_intentions':polls,
        'poll_coverage':{'release_rows':panel_count,'known_numeric_rows':len(polls),
            'independent_elections':len({p['election_date'] for p in polls})},
        'candidate_values_for_next_election':{k:form_candidate(v,contract) for k,v in forecasts(rows).items()},
        'current_forecast':{'unchanged':True,'turnout_pct':draft['national_turnout_pct'],
            'path':str(draft_path.relative_to(ROOT)).replace('\\','/'),
            'sha256':hashlib.sha256(draft_path.read_bytes()).hexdigest()},
        'decision':'Historical analysis only. No turnout or seat forecast change; no war adjustment or poll calibration adopted.',
        'limits':{'historical_vintage':inputs['historical_availability_limit'],
            'conflict':inputs['conflict_protocol']['limitations'],
            'selection':'References fixed for this analysis; already-inspected outcomes, small correlated recent sample, no untouched holdout.'}}


def write(report,out):
    out.mkdir(parents=True,exist_ok=True)
    def save(name,text):(out/name).write_text(text,encoding='utf-8',newline='\n')
    save('results.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    with (out/'history.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['knesset','date','turnout_pct','change_pp','days_since_previous','eligible','ballots','valid_votes','count_ratio_pct','source'])
        for r in report['history']:w.writerow([r['knesset'],r['election_date'],r['turnout_pct'],r['change_pp'],r['days_since_previous'],r['electorate'],r['ballots'],r['valid'],r['derived_ratio_pct'],r['source_url']])
    with (out/'backtest.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(['knesset','date','actual','method','prediction','absolute_error_pp'])
        for r in report['folds']:
            for m in METHODS:w.writerow([r['knesset'],r['election_date'],r['actual'],m,r['predictions'][m],r['absolute_errors'][m]])
    lines=['# Turnout: past-election analysis','',
        '**25 Knesset elections,1949–2022. The working forecast stays70.63%.** This is the first systematic turnout check; earlier work only carried2022 forward.2001 elected only a prime minister and is excluded.', '',
        'Turnout means ballots cast divided by eligible registered voters, including invalid ballots in the numerator. Party percentages use valid votes, a different denominator. Preserve published precision: CBS older rows have one decimal; recent CEC percentages have two. Count-derived ratios are separate diagnostics.', '',
        'Source check: retrieved CBS text gives79.8% for1984, while its own counts imply78.7837%. The archived CEC row and IDI both give78.8%, which is used explicitly in analysis; the original retrieved value is preserved. Whether the discrepancy is in rendering or source text remains unresolved. Other archived CEC inconsistencies for1961/2003 are not imported: count-consistent CBS values are retained. See input source_conflicts.', '',
        '![National turnout history](turnout-history.svg)','', '## What changed historically?','']
    for label,s in report['period_summaries'].items():
        lines.append(f"- {label.replace('_','–')}: {s['n']} elections, mean{s['mean']:.2f}%, sample SD{s['sample_sd']:.2f} percentage points.")
    lines += ['', 'The low2003–2006 period followed a large break from the pre-2000 period. Repeated elections did not produce a monotone decline: turnout rose in September2019 and March2020, then fell in2021 and rose in2022. Election fatigue alone is not an established forecast rule. Pandemic, participation composition, competition and election spacing are possible explanations; none is isolated causally here.', '',
        '## Does the previous election predict the next one?','',
        'For each election t, use only elections before t: previous=T(t−1); mean3=(T(t−1)+T(t−2)+T(t−3))/3; median3=median of those three. Loss is absolute error in percentage points. No fitted coefficients, parameter search or future outcomes enter these predictors. The common comparison begins at K4 after three warm-up elections. Retrospective source versions are used; original historical releases were not reconstructed.', '',
        '| Election | Actual | Previous prediction / error | Mean3 prediction / error | Median3 prediction / error |',
        '| --- | ---: | ---: | ---: | ---: |']
    for r in report['recent_folds']:
        lines.append('| '+r['election_date']+f" | {r['actual']:.2f}% | "+' | '.join(f"{r['predictions'][m]:.2f}% / {r['absolute_errors'][m]:.2f}" for m in METHODS)+' |')
    lines += ['', '| Method | Recent six MAE | Three-block sensitivity MAE | All22 common folds MAE |', '| --- | ---: | ---: | ---: |']
    for m,s in report['metrics'].items():lines.append(f"| {m} | {s['recent_six_mae']:.3f} | {s['recent_three_block_mae']:.3f} | {s['all_common_folds_mae']:.3f} |")
    lines += ['', 'The block sensitivity gives equal weight to2015, the2019–2021 cluster and2022; it does not manufacture independent observations. The smoothing methods may improve an aggregate score while badly missing2015. These are already-inspected elections and a small recent sample, so the table is evidence to discuss, not an automatic model-selection certificate.', '',
        '![Recent forecast errors](turnout-errors.svg)','', '## Conflict context: does war imply higher turnout?','',
        'A curated core uses six named wars and assigns the first election following each onset (which may occur while fighting continues). A sensitivity adds four specified Gaza operations. Multiple events pointing to one election are counted once.1949 has no previous election and cannot contribute a change. Event dates/provenance and all window rules are in the input JSON. This is exploratory, not a preregistered or exhaustive conflict dataset. Onset is not an end date; neither ongoing conflict nor time since war end is measured.', '',
        '| Definition | Elections with a change | Mean change after onset | Mean other change |', '| --- | ---: | ---: | ---: |']
    for label,c in report['conflict_context'].items():
        s=c['following_onset_change'];lines.append(f"| {label} | {s['n']} | {s['mean']:+.3f}pp | {c['other_changes']['mean']:+.3f}pp |")
    lines += ['', 'Definition sensitivity is itself a limitation: wars, operations, era and turnout trends are mixed. No significance test or causal coefficient is reported, and no war bonus/penalty is added to2026.', '',
        '| First election | Included events | Turnout change |', '| --- | --- | ---: |']
    for r in report['conflict_context']['wars_plus_four_operations']['first_elections']:
        d='No earlier election' if r['turnout_change_pp'] is None else f"{r['turnout_change_pp']:+.2f}pp"
        lines.append(f"| {r['election_date']} | {', '.join(r['events'])} | {d} |")
    lines += ['', '365/730/1095-day onset windows are saved separately in results.json, with election IDs and sample sizes. The collection omits the intifadas, War of Attrition and other operations: none of its comparisons establishes how an ongoing2026 conflict would affect turnout. The WHO pandemic characterization on March11,2020 followed the March2 election;2021 followed that declaration. This does not mean COVID was absent before March11 or that the2021 decline was caused by COVID.', '',
        '## What do turnout polls tell us?','',
        f"The existing six-election panel contains{report['poll_coverage']['release_rows']} release rows but only{report['poll_coverage']['known_numeric_rows']} numeric turnout-intention observations, both from one election. Missing observations stay missing. Two releases are not two independent election targets. Original2021 final N12/C13 articles were checked, without recovering a comparable national numeric measure.", '',
        '| Release | Reported voting intention | Actual national turnout | Intention minus actual |', '| --- | ---: | ---: | ---: |']
    for p in report['poll_intentions']:
        lines.append(f"| [{p['published_on']}]({p['source_url']}) | {p['reported_intention_pct']:.2f}% | {p['actual_turnout_pct']:.2f}% | {p['intention_minus_actual_pp']:+.2f}pp |")
    lines += ['', 'The2022 intentions undershot actual turnout. Do not assume a universal upward self-report bias or subtract one fixed number from current surveys. TheOctober24 wording reports intention to vote; October28 asks whether the respondent would come if the election were today. Current definitely-vote questions and different populations/denominators need their own audit. No poll-to-turnout calibration is fitted from this one election.', '',
        '## Implication for the current forecast','']
    for m,v in report['candidate_values_for_next_election'].items():lines.append(f"- {m}: {v['formatted']}%; within configured form bounds: {v['within_form_bounds']}.")
    lines += ['', 'Keep70.63% as the working placeholder for now. A recent mean is a concrete lightweight alternative to discuss, with the observed2015 failure and small-sample caveats. This analysis does not overwrite the frozen review package, seats, turnout or method text. No current war, economic or demographic adjustment has been adopted. The next useful turnout work is comparable historical intention-question coverage and carefully defined participation groups, rather than a broad model search.', '',
        '## Sources and reproducibility','',
        '- [CBS table27.2](https://www.cbs.gov.il/he/publications/DocLib/2022/ShnatonElectionsTheKnessetandGovernment.27/st27_02.pdf), published August2,2022: heading1949–2022, rows actually stop at March2021.2022 is appended separately from [CEC final results](https://votes25.bechirot.gov.il/nationalresults).',
        '- Existing versioned CEC national totals supply recent exact percentages; [Knesset official reference](https://main.knesset.gov.il/EN/activity/mmm/me03504.pdf) corroborates2013 turnout67.77%. Raw count ratios and published values are both retained.',
        '- Primary IDF/Ministry of Defense event URLs are stored individually in the input. Only onset facts are used, not their political interpretations. [WHO dated report](https://www.who.int/docs/default-source/coronaviruse/situation-REPORTS/20200311-SITREP-51-COVID-19.PDF) supplies the pandemic characterization date.',
        '- Run `python scripts/turnout_history.py`. Input data: data/snapshots/turnout-history-2026-10-24/inputs.json. Historical-vintage limits and omitted events are explicit. No raw PDF/page checksum is invented; the manifest hashes versioned inputs and code.','']
    # Put spaces around embedded numerals in prose; IDs/links remain untouched in JSON/CSV.
    import re
    prose='\n'.join(lines)
    pieces=re.split(r'(\]\([^)]*\)|`[^`]*`)',prose)
    prose=''.join(re.sub(r'(?<=[A-Za-z])(?=[0-9])|(?<=[0-9])(?=[A-Za-z])',' ',p)
                  if i%2==0 else p for i,p in enumerate(pieces))
    # Keep the method IDs in the summary table readable; this affects prose only.
    save('analysis.md',prose)
    draw_plots(report,out)
    config_path=ROOT/'data/snapshots/screening-six-elections-2026-10-21/prepared/historical.json'
    config=baseline.load_json(config_path)
    paths=[INPUT,Path(__file__),ROOT/'config/submission-fields.json',config_path,
           ROOT/'data/database/elections.jsonl.gz',ROOT/report['current_forecast']['path']]+[ROOT/e['polls_path'] for e in config['elections']]
    save('inputs-manifest.json',json.dumps({str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')


def draw_plots(report,out):
    def save(name,parts):
        (out/name).write_text('\n'.join(parts)+ '</g></svg>\n',encoding='utf-8',newline='\n')
    def start(title,sub):return ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="520" viewBox="0 0 1100 520"><rect width="1100" height="520" fill="white"/><g font-family="Arial,sans-serif" fill="#18324a">',f'<text x="25" y="30" font-size="22">{escape(title)}</text>',f'<text x="25" y="55" font-size="13">{escape(sub)}</text>']
    s=start('National turnout: 25 Knesset elections, 1949–2022','Ballots / registered eligible voters. 2001 PM-only election excluded. Older published values have one decimal.')
    for v in (60,65,70,75,80,85,90):
        y=420-(v-60)*10;s.append(f'<path d="M65,{y}H1060" stroke="#e1e6ea"/><text x="25" y="{y+4}">{v}%</text>')
    points=[]
    for r in report['history']:
        d=date.fromisoformat(r['election_date']);year=d.year+(d.timetuple().tm_yday-1)/366
        x=70+(year-1949)*13.2;y=420-(r['turnout_pct']-60)*10
        points.append((x,y,r))
    s.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y,r in points)+'" fill="none" stroke="#216aa4" stroke-width="2.5"/>')
    for x,y,r in points:
        s.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4" fill="#216aa4"><title>{r["election_date"]}: {r["turnout_pct"]}%</title></circle>')
        if r['knesset'] in (1,2,15,16,17,20):
            s.append(f'<text x="{x-15:.2f}" y="{y-12:.2f}" font-size="12">{r["turnout_pct"]:.1f}%</text>')
    for year in (1950,1960,1970,1980,1990,2000,2010,2020):
        x=70+(year-1949)*13.2;s.append(f'<text x="{x-16}" y="450" font-size="12">{year}</text>')
    s += ['<text x="25" y="485" font-size="14">1999 → 2003: large decline. Recent elections fluctuate around a lower level.</text>',
          '<text x="25" y="507" font-size="12">The long-run level is context, not a stationary average to substitute into the 2026 forecast.</text>']
    save('turnout-history.svg',s)
    s=start('Turnout prediction errors: six recent elections','Strictly earlier outcome inputs. Retrospective source versions; already-inspected elections. Lower error is better.')
    colors=['#216aa4','#298269','#b87922']
    for v in range(0,9,2):
        y=420-v*38;s.append(f'<path d="M65,{y}H1060" stroke="#e1e6ea"/><text x="25" y="{y+4}">{v}pp</text>')
    for i,r in enumerate(report['recent_folds']):
        for j,m in enumerate(METHODS):
            v=r['absolute_errors'][m];x=95+158*i+29*j;y=420-v*38
            s.append(f'<rect x="{x}" y="{y:.2f}" width="25" height="{v*38:.2f}" fill="{colors[j]}"/><text x="{x}" y="{y-7:.2f}" font-size="11">{v:.2f}</text>')
        s.append(f'<text x="{88+158*i}" y="445" font-size="12">{r["election_date"]}</text>')
    for j,m in enumerate(METHODS):s.append(f'<text x="{25+350*j}" y="485" fill="{colors[j]}" font-size="15">{escape(m)}</text>')
    s.append('<text x="25" y="510" font-size="12">Four outcomes in 2019–2021 are a correlated cluster. No current forecast changed.</text>')
    save('turnout-errors.svg',s)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=ROOT/'output/turnout-history')
    args=parser.parse_args();write(build(),args.out_dir)
    files={p.name:p.read_text(encoding='utf-8') for p in sorted(args.out_dir.iterdir()) if p.is_file()}
    encoded=base64.b64encode(gzip.compress(json.dumps(files,ensure_ascii=False).encode())).decode()
    print('E014_FILES_BASE64_BEGIN')
    for i in range(0,len(encoded),8000):print(encoded[i:i+8000])
    print('E014_FILES_BASE64_END')
    print(files['analysis.md'])
