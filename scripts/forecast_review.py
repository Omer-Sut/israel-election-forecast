"""Prepare reviewable forecast decisions and bounded threshold sensitivities."""
from __future__ import annotations
import argparse
import base64
import csv
from datetime import date, timedelta
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import baseline

ROOT = baseline.ROOT
CONFIG = ROOT/'config/forecast-review.json'


def constrained_decision(vectors, total=120, minimum=3, objective='square', fixed=None, exempt=()):
    """Seat-space sensitivity only; minimum is an assumption, not an allocator."""
    baseline.validate_vectors(vectors, total)
    if minimum not in (3, 4) or objective not in ('square', 'absolute'):
        raise ValueError('Unknown sensitivity')
    fixed = fixed or {}
    width, count = len(vectors[0]), len(vectors)
    if any(type(i) is not int or not 0 <= i < width or not baseline.seat_integer(v) or v > total for i,v in fixed.items()):
        raise ValueError('Invalid fixed seat assumption')
    states = {0: (0, 0, ())}
    for i, column in enumerate(zip(*vectors)):
        choices = [fixed[i]] if i in fixed else ([0]+list(range(minimum,total+1)) if i not in exempt else range(total+1))
        costs = {}
        for value in choices:
            absolute = sum(abs(value-v) for v in column)
            square = (count*value-sum(column))**2
            costs[value] = (square, absolute) if objective == 'square' else (absolute, square)
        next_states = {}
        for allocated, previous in states.items():
            for value, cost in costs.items():
                if allocated+value > total:
                    continue
                candidate = (previous[0]+cost[0],previous[1]+cost[1],previous[2]+(value,))
                new_total = allocated+value
                if new_total not in next_states or candidate < next_states[new_total]:
                    next_states[new_total] = candidate
        states = next_states
    if total not in states:
        raise ValueError('Infeasible seat assumptions')
    return list(states[total][2])


def choices(vectors, exempt=()):
    result = {'rounded_mean':baseline.rounded_mean(vectors,120),
              'empirical_l1':baseline.l1_consensus(vectors,120)}
    for objective in ('square','absolute'):
        for minimum in (3,4):
            result[f'{objective}_zero_or_{minimum}plus'] = constrained_decision(vectors, minimum=minimum,objective=objective,exempt=exempt)
    return result


def historical_check():
    config_path = ROOT/'data/snapshots/screening-six-elections-2026-10-21/prepared/historical.json'
    config = baseline.load_json(config_path)
    outcomes = baseline.load_json(ROOT/config['outcomes_path'])['elections']
    results = []
    for item in config['elections']:
        snapshot = baseline.load_json(ROOT/item['polls_path'])
        cutoff = (date.fromisoformat(snapshot['election_date'])-timedelta(days=1)).isoformat()
        polls,_ = baseline.select_polls(snapshot['polls'],cutoff,config['poll_window_days'])
        ids = sorted(p['id'] for p in snapshot['lists'])
        vectors = [[p['reported_seats'].get(i,0) for i in ids] for p in polls]
        truth = [outcomes[item['id']]['seat_results'][i] for i in ids]
        result = choices(vectors)
        results.append({'election':item['id'],'cutoff':cutoff,'poll_ids':[p['id'] for p in polls],
                        'errors':{k:sum(abs(a-b) for a,b in zip(v,truth)) for k,v in result.items()},
                        'predictions':dict(zip(result,result.values())),'party_ids':ids})
    return results


def build_review():
    config = baseline.load_json(CONFIG)
    snapshot = baseline.load_json(ROOT/config['poll_snapshot'])
    contract = baseline.load_json(ROOT/'config/submission-fields.json')
    mapping = baseline.load_json(ROOT/'config/poll-mappings.json')
    fields = [f['id'] for f in contract['seat_fields']]
    selected,rejected = baseline.select_polls(snapshot['polls'],config['as_of_date'],config['poll_window_days'])
    vectors = [baseline.poll_vector(p,contract,mapping) for p in selected]
    exemption = [fields.index('other_qualifying_lists')]
    methods = choices(vectors,exemption)
    scenarios = {}
    for amcha in (0,4):
        for reservists in (0,4):
            fixed = {fields.index('amcha_yisrael'):amcha,fields.index('reservists_economic'):reservists}
            scenarios[f'amcha_{amcha}_reservists_{reservists}'] = constrained_decision(vectors,minimum=4,fixed=fixed,exempt=exemption)
    turnout = baseline.load_json(ROOT/config['turnout_reference'])['turnout_pct']
    for allocation in list(methods.values())+list(scenarios.values()):
        baseline.validate_forecast(dict(zip(fields,allocation)),turnout,contract)
    source_sensitivities = {}
    for gap in snapshot['not_ingested']:
        alternate = list(zip(selected,vectors))
        if gap['id'].startswith('kan'):
            alternate = [(p,v) for p,v in alternate if p['pollster_group'] != 'kantar']
        alternative_vectors = [v for p,v in alternate]+[gap['secondary_seats']+[0]]
        baseline.validate_vectors(alternative_vectors,120)
        source_sensitivities[gap['id']] = {'status':gap['status'],'used_in_recommendation':False,
            'action':'replace_kantar' if gap['id'].startswith('kan') else 'add_new_firm',
            'rounded_mean':baseline.rounded_mean(alternative_vectors,120)}
    return dict(status='review_package_not_submitted',as_of_date=config['as_of_date'],
        selected_polls=selected,excluded_or_archived=rejected,fields=fields,vectors=vectors,
        continuous_mean=[sum(c)/len(vectors) for c in zip(*vectors)],
        methods=methods,threshold_scenarios=scenarios,
        threshold_assumption='Zero-or-minimum-seat sensitivities and fixed0/4 scenarios operate on published seat space. They are not vote-share thresholding, Bader-Ofer allocation, probabilities or verified legal feasibility.',
        source_sensitivities=source_sensitivities,
        leave_one_group_out=[{'omitted':p['pollster_group'],'rounded_mean':baseline.rounded_mean(vectors[:i]+vectors[i+1:],120)} for i,p in enumerate(selected)],
        current_source_audit=snapshot['rule_and_eligibility_audit'],not_ingested=snapshot['not_ingested'],
        historical_check=historical_check(),
        turnout={'value':turnout,'formatted':f'{turnout:.2f}','method':config['turnout_method'],
                 'bounds':[contract['turnout_field']['minimum'],contract['turnout_field']['maximum']]},
        recommendation={'method':'rounded_mean','status':'provisional_due_to_source_gaps',
            'reason':'Retain the established reference: no learned correction earned adoption; no new threshold policy selected from already-inspected outcomes. All alternatives remain reviewable.',
            'seats':dict(zip(fields,methods['rounded_mean'])),'national_turnout_pct':f'{turnout:.2f}',
            'arithmetic_and_turnout_validated':True,'official_inventory_and_allocator_verified':False,
            'source_freeze_complete':False})


def write_review(report,out):
    out.mkdir(parents=True,exist_ok=True)
    (out/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    contract = baseline.load_json(ROOT/'config/submission-fields.json')
    columns = {'continuous_mean':report['continuous_mean'],**report['methods'],**report['threshold_scenarios']}
    with (out/'seat-options.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(['field_id','label_en',*columns])
        for i,field in enumerate(contract['seat_fields']):
            writer.writerow([field['id'],field['label_en'],*[values[i] for values in columns.values()]])
    lines=['# Forecast review — October 24','',
        'Seven reviewed polling groups. Recommended reference is provisional: source freeze and official inventory verification remain incomplete. No competition entry submitted.','',
        '| Form field | Mean before rounding | Rounded mean | Empirical L1 | Zero-or-4 square sensitivity |',
        '| --- | ---: | ---: | ---: | ---: |']
    for i,field in enumerate(contract['seat_fields']):
        lines.append(f"| {field['label_en']} | {report['continuous_mean'][i]:.3f} | {report['methods']['rounded_mean'][i]} | {report['methods']['empirical_l1'][i]} | {report['methods']['square_zero_or_4plus'][i]} |")
    lines+=['',f"Turnout persistence: **{report['turnout']['formatted']}%**. Every exported option sums120 and satisfies configured fields/turnout bounds.",'',
        '![Decision sensitivity](decision-sensitivity.svg)','',
        '## Retrospective threshold check','',
        'Already-inspected elections; these comparisons cannot provide a fresh model ranking. Minimum3/4 sensitivities are explicit assumptions, not verified electoral allocation.','',
        '| Election | Rounded mean | L1 | Square 0/3+ | Square 0/4+ | L1 0/3+ | L1 0/4+ |','| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in report['historical_check']:
        lines.append('| '+row['election']+' | '+' | '.join(str(row['errors'][name]) for name in report['methods'])+' |')
    lines+=['','## Sources','']
    lines += [f"- {p['published_on']} [{p['publisher']}]({p['source_url']}); {p['pollster_group']}" for p in report['selected_polls']]
    lines+=['','## Remaining limitations','',
        '- Kan final Democrats8/9 source conflict; original final page unavailable. Channel16 original graphic unverified. Sensitivities are saved separately and not adopted.',
        '- Israel Hayom and Kan share Kantar: a later verified Kan release would replace the Kantar anchor, not add a polling firm.',
        '- Next Data/Filber and Direct Polls/Sharon are separate current reporting groups with common lineage; independence is not assumed. Omission sensitivities show both.',
        '- Blue and White full withdrawal is reported by news quoting CEC. Official notice remains inaccessible; all selected complete polls already allocate zero. Keep its form field.',
        '- Existing accepted Joint List and Religious Zionism alliance mappings are retained assumptions. Full official inventory, agreements, operative blackout text and allocator remain unverified.',
        '- Partial vote percentages cannot reconstruct full vote shares. No probabilities assigned to the four threshold scenarios. Other-list thresholds must never be applied to pooled votes.',
        '- Turnout intentions vary by question and denominator; they are not directly substituted for national turnout.',
        '- Small positive seats in the reference summarize poll disagreement; they are not a simulated feasible election. No unvalidated threshold correction selected.','']
    (out/'summary.md').write_text('\n'.join(lines),encoding='utf-8',newline='\n')
    parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1150" height="650" viewBox="0 0 1150 650">',
        '<rect width="1150" height="650" fill="white"/><g font-family="Arial,sans-serif" fill="#18324a">',
        '<text x="25" y="35" font-size="23">Forecast decisions: how threshold assumptions change seats</text>',
        '<text x="25" y="62" font-size="14">Provisional reviewed inputs. Scenario markers are assumptions, not probabilities or a verified vote allocator.</text>']
    for i,field in enumerate(contract['seat_fields']):
        y=100+31*i
        label = 'Other qualifying lists (combined)' if field['id']=='other_qualifying_lists' else field['label_en']
        parts.append(f'<text x="25" y="{y+5}" font-size="13">{escape(label)}</text>')
        vals=[v[i] for v in report['threshold_scenarios'].values()]
        parts.append(f'<path d="M{400+min(vals)*25},{y}H{400+max(vals)*25}" stroke="#d18b2c" stroke-width="5"/>')
        for key,color,dy in [('rounded_mean','#216aa4',-3),('empirical_l1','#298269',3)]:
            v=report['methods'][key][i]
            parts.append(f'<circle cx="{400+v*25}" cy="{y+dy}" r="4" fill="{color}"/>')
    parts+=['<text x="25" y="590" font-size="14" fill="#216aa4">Blue: rounded mean</text><text x="240" y="590" font-size="14" fill="#298269">Green: empirical L1</text><text x="470" y="590" font-size="14" fill="#a36916">Orange: four fixed0/4 scenarios</text>',
        '<text x="25" y="625" font-size="13">All options sum120. Saved JSON/CSV includes all vectors, omitted-source sensitivities and historical checks.</text></g></svg>']
    (out/'decision-sensitivity.svg').write_text('\n'.join(parts)+'\n',encoding='utf-8',newline='\n')
    method='''The forecast uses the latest reviewed eligible release from each polling group within a 14-day window, with equal group weights. Published complete seat allocations are mapped explicitly to the competition fields. Their mean is rounded by the largest-remainder method so that all 15 seat fields sum to120. Current alliance mappings retain their source labels; historical elections retain their own identities. Zero seats inferred from a complete table do not imply zero voter support.

Ridge, random forests, XGBoost, ensembles, trend/geographic features and past-only poll reliability weights were evaluated chronologically using earlier elections. None established a dependable improvement over the reference, so their corrections are not included. Historical outcomes have already been inspected and do not constitute an untouched holdout.

Alternative absolute-loss and threshold-sensitive allocations are documented for review. Partial vote percentages do not support a complete vote-to-seat simulation or calibrated threshold probabilities. The arithmetic reference can assign small positive seat estimates to borderline lists; it represents a point estimate rather than a simulated election outcome.

Turnout uses the previous official election's70.63% as a persistence reference, validated against the form's inclusive40–100% bounds and displayed to two decimals. Self-reported voting intentions are diagnostic only.

Source versions, dates, exclusions, code and results are versioned in GitHub. The package remains provisional because final-source conflicts and direct official-list/rule verification are unresolved. No competition entry has been submitted.
'''
    assert len(method.split())<=500
    (out/'method-draft.txt').write_text(method,encoding='utf-8',newline='\n')
    paths=[CONFIG,ROOT/baseline.load_json(CONFIG)['poll_snapshot'],ROOT/'config/submission-fields.json',ROOT/'config/poll-mappings.json',ROOT/'scripts/forecast_review.py',ROOT/'scripts/baseline.py',
           ROOT/'data/snapshots/screening-six-elections-2026-10-21/prepared/historical.json']
    hc=baseline.load_json(paths[-1]);paths += [ROOT/hc['outcomes_path'],ROOT/baseline.load_json(CONFIG)['turnout_reference']]+[ROOT/e['polls_path'] for e in hc['elections']]
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (out/'inputs-manifest.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8',newline='\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=ROOT/'output/forecast-review')
    args=parser.parse_args();report=build_review();write_review(report,args.out_dir)
    files={p.name:p.read_text(encoding='utf-8') for p in sorted(args.out_dir.iterdir()) if p.is_file()}
    encoded=base64.b64encode(gzip.compress(json.dumps(files,ensure_ascii=False).encode())).decode()
    print('E010_FILES_BASE64_BEGIN')
    for i in range(0,len(encoded),8000):print(encoded[i:i+8000])
    print('E010_FILES_BASE64_END')
    print((args.out_dir/'summary.md').read_text(encoding='utf-8'))
