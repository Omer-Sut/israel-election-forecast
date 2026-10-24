"""Freeze a review package without changing the selected E011 forecast."""
import argparse
import base64
import csv
import gzip
import hashlib
from html import escape
import json
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import baseline, electoral_review, forecast_review
from scripts.bader_ofer import validate_active_forecast

ROOT = baseline.ROOT


def build():
    reference = electoral_review.build()['active_draft']
    frozen_path = ROOT/'reports/electoral-review-2026-10-24/submission-draft.json'
    if reference != baseline.load_json(frozen_path):
        raise ValueError('Active forecast changed: review selection before freezing')
    review = forecast_review.build_review()
    contract = baseline.load_json(ROOT/'config/submission-fields.json')
    fields = review['fields']
    fixed = {fields.index(k): 0 for k in ('amcha_yisrael','blue_and_white','other_qualifying_lists')}
    scenarios = {}
    for count in (0,3,4):
        assumptions = {**fixed, fields.index('reservists_economic'): count}
        vector = forecast_review.constrained_decision(review['vectors'],minimum=3,fixed=assumptions)
        seats = dict(zip(fields,vector))
        validate_active_forecast(seats,float(reference['national_turnout_pct']),contract,other_lists={})
        scenarios[str(count)] = {'seats':seats,
            'delta_from_reference':{k:seats[k]-reference['seats'][k] for k in fields},
            'total':sum(vector),
            'sum_squared_distance_to_mean':sum((a-b)**2 for a,b in zip(vector,review['continuous_mean'])),
            'interpretation':'Conditional seat-space decision. No probability assigned; not a vote-to-seat simulation.'}
    if scenarios['3']['seats'] != reference['seats']:
        raise AssertionError('Three-seat scenario must reproduce the reference')
    return {'status':'frozen_review_package_not_submitted',
            'forecast_cutoff':'2026-10-24', 'reference':reference,
            'reference_source':str(frozen_path.relative_to(ROOT)).replace('\\','/'),
            'reference_sha256':hashlib.sha256(frozen_path.read_bytes()).hexdigest(),
            'fields':fields,'selected_poll_ids':[p['id'] for p in review['selected_polls']],
            'reservists_scenarios':scenarios,
            'scenario_controls':{'minimum_individual_seats':3,'amcha_yisrael':0,
                'blue_and_white':0,'other_qualifying_lists':0,
                'objective':'Squared distance to the same seven-group mean; ties by absolute poll disagreement, then field order'},
            'source_freeze_complete':False, 'exact_current_bader_ofer':False,
            'limitations':['Complete current vote shares and their denominator are missing.',
                'Current surplus agreements are news-reported, not verified official filings.',
                'Kan23 Democrats8/9 conflict and Channel16 original-source gap remain excluded.',
                'Current Joint List and Religious Zionism form mappings remain explicit assumptions.',
                'Reservists3 is a constrained compromise; selected polls report0or4, not3.',
                'Historical outcomes have been inspected; no untouched validation or calibrated probabilities.',
                'Form decimal increments, personal details, track/team and presentation agreement are not completed here.']}


def write(package,out):
    out.mkdir(parents=True,exist_ok=True)
    def save(name,text):
        (out/name).write_text(text,encoding='utf-8',newline='\n')
    def as_json(value): return json.dumps(value,ensure_ascii=False,indent=2)+'\n'
    save('package.json',as_json(package))
    # Preserve the selected draft byte-for-byte, including its provisional flags.
    save('forecast.json',(ROOT/package['reference_source']).read_text(encoding='utf-8'))
    contract = baseline.load_json(ROOT/'config/submission-fields.json')
    fields = package['fields']
    labels = {f['id']:f['label_en'] for f in contract['seat_fields']}
    scenarios = package['reservists_scenarios']
    with (out/'scenario-comparison.csv').open('w',encoding='utf-8',newline='') as f:
        writer = csv.writer(f,lineterminator='\n')
        writer.writerow(['field_id','label_en','reference','reservists_0','delta_0','reservists_3','delta_3','reservists_4','delta_4'])
        for k in fields:
            writer.writerow([k,labels[k],package['reference']['seats'][k],
                *[v for n in ('0','3','4') for v in (scenarios[n]['seats'][k],scenarios[n]['delta_from_reference'][k])]])
    lines = ['# Forecast review package — October 24, 2026','',
        '**Working reference retained: Reservists3, Amcha0; total120; turnout70.63%.**',
        'This freezes the review artifact, not a claim that source collection is complete. No competition entry submitted.', '',
        '## Full forecast and conditional alternatives','',
        'The middle column is the selected working reference. Alternatives hold Amcha, Blue and White and other qualifying lists at zero; every remaining list follows the same zero-or-at-least3 rule. Only the Reservists assumption changes. Each alternative minimizes squared distance to the same poll mean and reallocates seats to maintain120. These are seat-space comparisons, not Bader–Ofer simulations or assigned probabilities.', '',
        '| Form field | Reservists0 | Reference: Reservists3 | Reservists4 |',
        '| --- | ---: | ---: | ---: |']
    for k in fields:
        lines.append('| '+labels[k]+' | '+' | '.join(str(scenarios[n]['seats'][k]) for n in ('0','3','4'))+' |')
    lines += ['| **Total** | **120** | **120** | **120** |','',
        'National turnout in every option: **70.63%**. This is the last-official-election persistence estimate, not a conversion from poll voting intentions.', '',
        '![Seat changes under the Reservists assumptions](reservists-scenarios.svg)','',
        '## Which parties change?','']
    for n in ('0','4'):
        changes = ', '.join(f"{labels[k]} {d:+d}" for k,d in scenarios[n]['delta_from_reference'].items() if d)
        lines.append(f'- Reservists{n} versus reference: {changes}.')
    lines += ['', '## Decision and explanation','',
        'Retain the reference rule already adopted after the user excluded1/2-seat outputs. No new model was fitted and no scenario was selected using hindsight historical gains. Reservists3 is a constrained compromise between polls giving0or4. It is not a claim that3is the most likely outcome. A zero-or-4 rule would be an additional modeling restriction, not a verified universal legal requirement.', '',
        'The decision solves min sum_i (s_i−mean_i)^2 subject to sum_i s_i=120 and s_i in {0,3,4,...,120}. Absolute disagreement with the selected polls breaks objective ties, followed by configured field order. This is a transparent way to enforce the requested output rule; competition evaluation remains total absolute seat error against the eventual result.', '',
        'The old largest-remainder method floored the means and assigned remaining seats by fractional parts. It maintained120 but could produce1/2 seats. See the [before/after rounding analysis](../electoral-review-2026-10-24/analysis.md) and [plot](../electoral-review-2026-10-24/rounding-error.svg). Continuous scores are diagnostics; they do not certify a feasible final election.', '',
        '## Sources and remaining limits','',
        'The [seven-release review](../forecast-review-2026-10-24/summary.md) records publisher links and selection. The [vote-input audit](../vote-input-audit-2026-10-24/analysis.md) records the bounded attempt to recover complete shares. The [allocator verification](../electoral-review-2026-10-24/analysis.md) reproduces2022 seats from official votes; it does not validate a current forecast.', '']
    lines += ['- '+s for s in package['limitations']]
    lines += ['', '## Review artifacts','',
        '- forecast.json: exact copy of the retained draft, with provisional flags.',
        '- scenario-comparison.csv and package.json: complete vectors, signed changes, assumptions and input identities.',
        '- method-description.txt: actual implemented method, below500words.',
        '- validation.json and inputs-manifest.json: arithmetic/contract checks and hashes.',
        '- No personal information, presentation consent or competition submission is included.','']
    save('review.md','\n'.join(lines))
    method = '''We use the latest reviewed release from each polling group within a 14-day window, with equal weights across seven groups. Complete published seat tables are mapped explicitly to the competition fields. We select the integer vector minimizing squared distance to their mean, subject to a total of 120 and each electoral list receiving either zero or at least three seats. Ties minimize absolute poll disagreement, then follow fixed field order. This implements the requested exclusion of one- and two-seat predictions. The retained forecast gives Amcha zero and Reservists three seats; the latter is a constrained compromise, not a poll-reported outcome or estimated mode.

Conditional alternatives fix Reservists at zero or four while keeping Amcha, Blue and White and other qualifying lists at zero, then reallocate the remaining seats under the same objective and constraints. They have no assigned probabilities and are not vote-to-seat simulations.

A separate exact vote allocator implements Bader–Ofer thresholding, surplus agreements and remainder allocation, and reproduces all 40 official 2022 list results using historically reported agreements. Current polls provide only partial vote percentages, so we cannot identify a complete current vote-based allocation. We do not infer votes from published seats. Current alliance-to-form mappings remain explicit assumptions; historical identities remain separate. Other qualifying lists must be allocated individually before aggregation.

Chronological trials of alternative models and features did not establish dependable improvements warranting learned corrections. Historical outcomes have already been inspected and are not an untouched holdout. Continuous errors remain diagnostics; the competition loss is total absolute seat error.

Turnout uses the last official election’s 70.63% as a persistence estimate, checked against the inclusive 40–100% form bounds and displayed to two decimals. Poll voting intentions are not substituted for turnout.

Inputs, code and outputs are versioned in GitHub. Source conflicts and official inventory/agreement verification remain unresolved. The package is provisional and no competition entry has been submitted.
'''
    count = len(method.split())
    if count > 500: raise ValueError('Method description exceeds form word limit')
    save('method-description.txt',method)
    # A small static change plot; the full fifteen-field comparison stays above.
    changed = [k for k in fields if any(scenarios[n]['delta_from_reference'][k] for n in ('0','4'))]
    height = 140+58*len(changed)
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{height}" viewBox="0 0 1000 {height}">',
        f'<rect width="1000" height="{height}" fill="white"/><g font-family="Arial,sans-serif" fill="#18324a">',
        '<text x="25" y="30" font-size="21">Reservists scenarios: seat changes from the retained forecast</text>',
        '<text x="25" y="55" font-size="13">Amcha fixed at0. Same mean, minimum3 and total120 throughout. Scenarios have no assigned probabilities.</text>']
    for tick in range(-3,4):
        x=590+tick*65
        svg.append(f'<path d="M{x},75V{height-65}" stroke="#d8e0e5"/><text x="{x-5}" y="{height-45}" font-size="12">{tick:+d}</text>')
    for i,k in enumerate(changed):
        y=105+i*58
        svg.append(f'<text x="25" y="{y+4}" font-size="14">{escape(labels[k])}</text>')
        for n,color,dy in [('0','#216aa4',-7),('4','#b87922',7)]:
            d=scenarios[n]['delta_from_reference'][k]; x=590+d*65
            svg.append(f'<path d="M590,{y+dy}H{x}" stroke="{color}" stroke-width="3"/><circle cx="{x}" cy="{y+dy}" r="5" fill="{color}"/>')
    svg += [f'<text x="25" y="{height-15}" fill="#216aa4" font-size="14">Blue: Reservists0</text><text x="260" y="{height-15}" fill="#b87922" font-size="14">Orange: Reservists4</text><text x="550" y="{height-15}" font-size="13">Zero line: retained Reservists3 reference</text></g></svg>']
    save('reservists-scenarios.svg','\n'.join(svg)+'\n')
    paths = ['scripts/review_package.py','scripts/electoral_review.py','scripts/forecast_review.py',
        'scripts/bader_ofer.py','scripts/baseline.py','config/forecast-review.json','config/submission-fields.json',
        'config/poll-mappings.json','data/snapshots/polls-2026-10-24.json',package['reference_source'],
        'data/snapshots/vote-input-audit-2026-10-24/audit.json']
    inherited_manifest = 'reports/electoral-review-2026-10-24/inputs-manifest.json'
    paths = sorted(set(paths+[inherited_manifest]+list(baseline.load_json(ROOT/inherited_manifest))))
    save('inputs-manifest.json',as_json({p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}))
    save('validation.json',as_json({'reference_equal_to_fresh_E011':True,
        'forecast_copy_sha256':hashlib.sha256((out/'forecast.json').read_bytes()).hexdigest(),
        'reference_sha256':package['reference_sha256'],
        'scenarios_pass_contract_total_minimum_and_turnout':True,'scenario3_matches_reference':True,
        'method_word_count':count,'source_freeze_complete':False,'submitted':False}))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=ROOT/'output/review-package')
    args=parser.parse_args();write(build(),args.out_dir)
    files={p.name:p.read_text(encoding='utf-8') for p in sorted(args.out_dir.iterdir()) if p.is_file()}
    encoded=base64.b64encode(gzip.compress(json.dumps(files,ensure_ascii=False).encode())).decode()
    print('E013_FILES_BASE64_BEGIN')
    for i in range(0,len(encoded),8000):print(encoded[i:i+8000])
    print('E013_FILES_BASE64_END')
    print(files['review.md'])
