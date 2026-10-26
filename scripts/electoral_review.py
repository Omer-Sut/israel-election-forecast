"""Active E011 decision and vote-allocation verification; archives E010 unchanged."""
import argparse
import base64
import gzip
import hashlib
import json
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import baseline, forecast_review
from scripts.bader_ofer import allocate, validate_active_forecast

ROOT = baseline.ROOT
AGREEMENTS_2022 = [('מחל','ט'), ('פה','כן'), ('שס','ג'), ('אמת','מרצ')]


def official_2022():
    rows = [json.loads(line) for line in gzip.decompress(
        (ROOT/'data/database/official_lists.jsonl.gz').read_bytes()).decode().splitlines()]
    rows = [r for r in rows if r['knesset'] == 25]
    return {r['ballot_code']: r['votes'] for r in rows}, {r['ballot_code']: r['seats'] for r in rows}


def build():
    old = forecast_review.build_review()
    fields = old['fields']
    # No exemptions: even the sum of individually qualifying other lists cannot
    # be one or two. This is NOT a threshold applied to their pooled votes.
    vector = forecast_review.constrained_decision(old['vectors'], minimum=3)
    seats = dict(zip(fields, vector))
    if seats['other_qualifying_lists']:
        raise ValueError('Disaggregate other lists before preparing an active export')
    contract = baseline.load_json(ROOT/'config/submission-fields.json')
    validate_active_forecast(seats, old['turnout']['value'], contract, other_lists={})
    draft = {'method':'nearest_mean_zero_or_3plus', 'seats':seats,
             'national_turnout_pct':old['turnout']['formatted'],
             'status':'provisional_constrained_seat_space_decision_not_submitted',
             'no_one_or_two_seats':True, 'sum_seats':sum(vector),
             'exact_current_bader_ofer':False, 'source_freeze_complete':False,
             'other_individual_list_allocations':{},
             'limitation':'Complete current vote shares and officially verified agreements are missing; do not infer votes from seats.'}
    votes, truth = official_2022()
    verification = allocate(votes, total_valid_votes=4764742, agreements=AGREEMENTS_2022)
    if verification['seats'] != truth:
        raise AssertionError('2022 allocation does not match the official complete result')
    config = baseline.load_json(ROOT/'data/snapshots/screening-six-elections-2026-10-21/prepared/historical.json')
    outcomes = baseline.load_json(ROOT/config['outcomes_path'])['elections']
    comparisons = []
    for row, item in zip(old['historical_check'], config['elections']):
        snap = baseline.load_json(ROOT/item['polls_path'])
        selected, _ = baseline.select_polls(snap['polls'], row['cutoff'], config['poll_window_days'])
        vectors = [[p['reported_seats'].get(k,0) for k in row['party_ids']] for p in selected]
        truth_vector = [outcomes[row['election']]['seat_results'][k] for k in row['party_ids']]
        mean = [sum(c)/len(vectors) for c in zip(*vectors)]
        comparisons.append({'election':row['election'],
            'continuous_l1_error':sum(abs(a-b) for a,b in zip(mean,truth_vector)),
            'largest_remainder_l1_error':row['errors']['rounded_mean'],
            'constrained_l1_error':row['errors']['square_zero_or_3plus']})
    return {'active_draft':draft, 'previous_draft_status':'superseded: contains prohibited 1/2-seat entries',
            'changed_fields':{k:{'before':old['recommendation']['seats'][k], 'after':seats[k]}
                              for k in fields if old['recommendation']['seats'][k] != seats[k]},
            'selected_poll_ids':[p['id'] for p in old['selected_polls']],
            'official_2022_verification':{'all_40_lists_match':True, 'allocation':verification,
                'purpose':'Post-election allocator verification, not forecast accuracy or backtest input',
                'agreement_provenance':'2022 original publisher reports; CEC notice indexed but full notice not retrieved'},
            'historical_rounding_comparison':comparisons}


def write(report, out):
    out.mkdir(parents=True, exist_ok=True)
    def save(name, text):
        (out/name).write_text(text, encoding='utf-8', newline='\n')
    save('review.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    save('submission-draft.json',json.dumps(report['active_draft'],ensure_ascii=False,indent=2)+'\n')
    lines = ['# Electoral allocation and rounding — October 24, 2026','',
        'E011 supersedes the E010 submission draft. No competition entry submitted.', '',
        'The active draft minimizes squared distance to the seven-group mean over integer vectors summing to120, with each list either zero or at least3 seats. The secondary tie-break is absolute poll disagreement, then configured field order. This is an interim seat-space decision, not an exact current Bader–Ofer allocation. It enforces the user’s requested rule without inventing vote shares.', '',
        '**Changes:** Amcha1→0; Reservists2→3. Other entries and turnout70.63% remain unchanged. Three seats are permitted by the statutory initial quota; four is common but is not a universal legal minimum. No new model was fitted.', '',
        '**Vote allocator:** inclusive3.25% of all valid votes, integer initial quota, separate qualification before surplus pooling, highest quotients for remaining seats, pair-internal redistribution and the section81(d)(4) half-seat safeguard. Equal highest quotients raise an unresolved-lottery error. Complete 2022 votes reproduce all40 official list allocations exactly using the four historically reported agreements. This validates calculation on observed votes; it does not measure forecast accuracy.', '',
        '**Current limitation:** the reviewed current releases have complete seat tables but partial vote percentages. An exact current vote-to-seat result cannot be identified. Zero published seats do not mean zero support. Complete shares for every individual list and verified current agreements remain necessary. The code refuses incomplete vote totals; other qualifying lists must be allocated individually before aggregation.', '',
        '## Why rounding changes error','',
        'Old rounding was largest remainder: floor every mean, then award the unallocated seats to the largest fractional parts (ties by field order). This guarantees120 but ignores thresholds and agreements. It is not Bader–Ofer.', '',
        'The competition loss is L1 = sum |prediction−truth|. Rounding minimizes neither future L1 error nor an unknown outcome. Fractional predictions lie in a larger decision space and small changes can cross integer boundaries. Rounding can help or hurt. With truth(61,59), forecast(60.6,59.4) has error0.8 and rounds to error0; forecast(60.4,59.6) has error1.2 and rounds to error2. Integer vectors both totaling120 have even total absolute error.', '',
        'These retrospective comparisons use already-inspected elections, not a new holdout. Continuous scores remain useful diagnostics; only constrained integer outputs are active drafts.', '',
        '![Before and after rounding](rounding-error.svg)','',
        '| Election | Continuous L1 | Largest remainder | Active 0/3+ constraint |',
        '| --- | ---: | ---: | ---: |']
    for r in report['historical_rounding_comparison']:
        lines.append(f"| {r['election']} | {r['continuous_l1_error']:.3f} | {r['largest_remainder_l1_error']} | {r['constrained_l1_error']} |")
    lines += ['', '## Sources and limits','',
        '- [Knesset allocation explanation](https://main.knesset.gov.il/EN/About/Lexicon/pages/seats.aspx), retrieved indexed text October24,2026: threshold, quota and surplus method.',
        '- [CEC 2021 law book](https://www.gov.il/BlobFolder/generalpage/elections-law24/he/candidates-list_disqualification_full-law-book.pdf), sections81–82: integer quota, lottery, half-seat safeguard and paired redistribution. Indexed primary text; full operative2026 consolidation remains unverified.',
        '- [2022 agreement report](https://www.mako.co.il/news-israel-elections/election_2022/Article-aef85a44fc8f381026.htm): Likud/RZ, YeshAtid/NationalUnity, Shas/UTJ, Labor/Meretz. Meretz fails independently. Agreement fixture is news-reported, not a retrieved official agreement notice.',
        '- Official2022 votes and final seats: versioned complete CEC national rows in data/database/official_lists.jsonl.gz; retained original source provenance. No historical forecasts consume these votes.',
        '- Kan23/Channel16 source gaps and current official inventory/rules/agreements verification remain open. This package is provisional.','']
    save('analysis.md','\n'.join(lines))
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="430" viewBox="0 0 1000 430"><rect width="1000" height="430" fill="white"/><g font-family="Arial" fill="#18324a"><text x="25" y="30" font-size="21">Absolute seat error before and after rounding</text><text x="25" y="55" font-size="13">Six already-inspected campaigns; allocator verification is a separate check. Lower is better.</text>']
    colors=['#216aa4','#b87922','#298269']
    keys=['continuous_l1_error','largest_remainder_l1_error','constrained_l1_error']
    for tick in range(0,51,10):
        y=345-tick*5
        svg.append(f'<path d="M60,{y}H970" stroke="#e0e5ea"/><text x="30" y="{y+4}">{tick}</text>')
    for i,r in enumerate(report['historical_rounding_comparison']):
        for j,key in enumerate(keys):
            v=r[key]; x=85+145*i+28*j
            svg.append(f'<rect x="{x}" y="{345-v*5}" width="23" height="{v*5}" fill="{colors[j]}"/><text x="{x}" y="{338-v*5}" font-size="10">{v:.1f}</text>')
        svg.append(f'<text x="{80+145*i}" y="370" font-size="12">{r["election"]}</text>')
    for i,label in enumerate(['Continuous mean','Largest remainder','Constrained 0/3+']):
        svg.append(f'<text x="{35+310*i}" y="410" fill="{colors[i]}" font-size="15">{label}</text>')
    save('rounding-error.svg','\n'.join(svg)+ '</g></svg>\n')
    method = '''The forecast uses the latest reviewed release per polling group within14days, giving each of seven groups equal weight. Published complete seat tables are mapped explicitly to the form. We choose the integer vector closest to the mean in squared distance, subject to total120 and each electoral list having either zero or at least3seats. Ties minimize absolute poll disagreement, then use fixed field order. This enforces the requested exclusion of1/2-seat predictions; it is a constrained seat-space estimate, not an exact current Bader–Ofer allocation.

The separate vote allocator implements the inclusive3.25% valid-vote threshold, statutory integer quota, surplus agreements and highest-quotient remainders, with exact rational comparisons. It reproduces all40 official2022 list allocations using historically reported agreements. This is calculation verification, not predictive performance. Current polls provide only partial vote percentages, so no complete current vote reconstruction or vote-based allocation is claimed.

Chronological historical model trials did not establish dependable improvements warranting learned corrections. Already-inspected historical results are diagnostics, not untouched validation. Current alliance mappings remain explicit assumptions, separate from historical identities. Other lists must be thresholded and allocated individually before aggregation.

Turnout remains the last official election’s70.63%, within configured40–100% bounds. Source conflicts and current official inventory/agreement verification remain unresolved; the package is provisional. No competition entry has been submitted.
'''
    assert len(method.split()) <= 500
    save('method-draft.txt', method)
    paths=['scripts/bader_ofer.py','scripts/electoral_review.py','scripts/forecast_review.py',
           'config/forecast-review.json','config/submission-fields.json','config/poll-mappings.json',
           'data/snapshots/polls-2026-10-24.json','data/database/official_lists.jsonl.gz',
           'data/snapshots/screening-six-elections-2026-10-21/prepared/historical.json']
    hc=baseline.load_json(ROOT/paths[-1])
    paths += [hc['outcomes_path'],'data/snapshots/results-2022.json','scripts/baseline.py']+[e['polls_path'] for e in hc['elections']]
    save('inputs-manifest.json',json.dumps({p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},indent=2)+'\n')


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir',type=Path,default=ROOT/'output/electoral-review')
    args=parser.parse_args()
    write(build(),args.out_dir)
    files={p.name:p.read_text(encoding='utf-8') for p in sorted(args.out_dir.iterdir()) if p.is_file()}
    encoded=base64.b64encode(gzip.compress(json.dumps(files,ensure_ascii=False).encode())).decode()
    print('E011_FILES_BASE64_BEGIN')
    for i in range(0,len(encoded),8000): print(encoded[i:i+8000])
    print('E011_FILES_BASE64_END')
    print(files['analysis.md'])
