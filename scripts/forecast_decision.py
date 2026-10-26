"""Apply the user-approved turnout decision while preserving reviewed seat inputs."""
import argparse
import base64
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import baseline, review_package, turnout_history
from scripts.bader_ofer import validate_active_forecast

ROOT = baseline.ROOT
CONFIG = ROOT/'config/forecast-decision.json'


def build():
    config = baseline.load_json(CONFIG)
    previous = baseline.load_json(ROOT/'reports/review-package-2026-10-24/package.json')
    if review_package.build() != previous:
        raise ValueError('Inherited seat review changed; reconcile before exporting a decision')
    source = baseline.load_json(ROOT/config['seat_reference'])
    if source != previous['reference']:
        raise ValueError('Seat reference mismatch')
    history = baseline.load_json(ROOT/config['turnout_history'])['elections']
    if any(r['election_date'] >= config['decision_date'] for r in history):
        raise ValueError('Turnout history includes uncompleted election')
    if config['turnout_method'] != 'last_three_mean':
        raise ValueError('Only the user-approved turnout method is enabled')
    value = turnout_history.forecasts(history)['last_three_mean']
    contract = baseline.load_json(ROOT/'config/submission-fields.json')
    formatted = f"{value:.{contract['turnout_field']['output_decimal_places']}f}"
    if formatted != config['turnout_display']:
        raise ValueError('Turnout inputs changed: review the adopted point value')
    forecast = copy.deepcopy(source)
    forecast.update(national_turnout_pct=formatted, turnout_method=config['turnout_method'],
                    decision_date=config['decision_date'],
                    status='user_approved_turnout_with_provisional_seats_not_submitted')
    validate_active_forecast(forecast['seats'], value, contract,
                            other_lists=forecast['other_individual_list_allocations'])
    validate_active_forecast(forecast['seats'], float(formatted), contract,
                            other_lists=forecast['other_individual_list_allocations'])
    for scenario in previous['reservists_scenarios'].values():
        validate_active_forecast(scenario['seats'], float(formatted), contract, other_lists={})
    return {'config': config, 'forecast': forecast,
        'previous_forecast': source, 'turnout': {'method': 'last_three_mean',
            'input_elections': [{k:r[k] for k in ('knesset','election_date','turnout_pct')} for r in history[-3:]],
            'unrounded_pct': value, 'formatted_pct': formatted,
            'change_from_previous_pp': float(formatted)-float(source['national_turnout_pct']),
            'authority': config['turnout_authority'], 'war_or_demographic_adjustment': False},
        'reservists_scenarios': previous['reservists_scenarios'],
        'source_audit': baseline.load_json(ROOT/config['source_audit']),
        'seat_forecast_changed': False, 'source_freeze_complete': False,
        'exact_current_bader_ofer': False, 'submitted': False}


def write(package, out):
    out.mkdir(parents=True, exist_ok=True)
    def save(name, value):
        (out/name).write_text(value, encoding='utf-8', newline='\n')
    def save_json(name, value):
        save(name, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
    save_json('forecast.json', package['forecast']); save_json('package.json', package)
    legacy = ROOT/'reports/review-package-2026-10-24'
    for name in ('scenario-comparison.csv', 'reservists-scenarios.svg'):
        save(name, (legacy/name).read_text(encoding='utf-8'))
    old_sentence = 'Turnout uses the last official election’s 70.63% as a persistence estimate, checked against the inclusive 40–100% form bounds and displayed to two decimals. Poll voting intentions are not substituted for turnout.'
    method = (legacy/'method-description.txt').read_text(encoding='utf-8')
    if method.count(old_sentence) != 1:
        raise ValueError('Inherited method text changed; update turnout explanation deliberately')
    method = method.replace(old_sentence,
        'National turnout is the arithmetic mean of the last three completed Knesset elections:71.52%,67.44% and70.63%, giving69.86% to two decimals. This simple rule was accepted after chronological turnout comparisons; fitted regressions and demographic/conflict sensitivities did not show dependable improvement. Both unrounded and displayed values satisfy the inclusive40–100% form bounds. No war adjustment or poll-intention substitution is applied.')
    if len(method.split()) > 500:
        raise ValueError('Method exceeds500words')
    save('method-description.txt', method)
    contract = baseline.load_json(ROOT/'config/submission-fields.json')
    lines = ['# Forecast decision — October25,2026', '',
        '**Adopted turnout:69.86%. Seat recommendation retained, total120. Not submitted.**', '',
        'The user accepted the simple three-election turnout average. Original frozen reports remain historical records; this dated package is the active decision. Seat-source review remains provisional.', '',
        '| Form field | Recommended seats |', '|---|---:|']
    for field in contract['seat_fields']:
        lines.append(f"| {field['label_en']} | {package['forecast']['seats'][field['id']]} |")
    lines += ['| **Total** | **120** |', '',
        '## Turnout decision', '',
        '(71.52 +67.44 +70.63)/3 =69.863333…%, displayed **69.86%**. These are2020,2021 and2022 Knesset turnout observations. The change from the previous70.63% reference is−0.77 percentage points after display rounding.', '',
        'Recent six-election absolute errors: previous-election persistence3.117pp; three-election mean2.059pp. Equal-three-block sensitivity3.488vs3.032pp. Over all22 older common folds, persistence2.385 beats mean2.530pp. This is a deliberate simple-rule decision for the current setting, not proof of universal superiority or calibrated uncertainty. Historical outcomes have been inspected.', '',
        'No fitted correction, demographic coefficient, war bonus or poll-intention calibration enters the adopted value.', '',
        '## Seat alternatives', '',
        'Keep Reservists3 and Amcha0 as the reviewed constrained compromise. Conditional Reservists0 adds one seat each to Likud,UTJ andRaam; Reservists4 removes one from ReligiousZionism. Each option totals120, excludes1/2-seat outputs and uses turnout69.86%. No probabilities assigned.', '',
        '![Conditional seat changes](reservists-scenarios.svg)', '',
        'The scenario chart/CSV are unchanged seat-only artifacts from the earlier review. The new forecast.json and method-description.txt supersede its old turnout value.', '',
        '## Source review and limits', '',
        'October25 bounded recheck did not recover the official candidate/agreements inventory or a matching complete vote-share vector. The CEC poll page remains a dynamic template; other official routes are inaccessible. Kan’s secondary121-seat table remains inconsistent; a legacy Zman corroboration URL now renders an unrelated feed. Channel16 remains secondary-only. Neither is promoted into the seven-group reference. BlueandWhite withdrawal is again news-reported, not authenticated from a direct official notice; selected polls already give zero. No redistribution invented.', '',
        'Thus source freeze remains incomplete and this is a constrained seat-space forecast, not an exact current vote-based Bader–Ofer allocation. The existing allocator reproduces official2022 results but lacks complete current inputs. JointList/form mapping assumptions remain explicit. See package.json source_audit for URLs and reader outcomes.', '',
        '## Ready for review', '',
        'forecast.json contains all required public prediction fields; method-description.txt is below500words. Arithmetic, configured fields, turnout bounds and individual other-list allocation checks are applied. Exact accepted form decimal increments and personal/team choices remain unverified. No entry submitted, personal responses recorded or branches merged.', '']
    save('review.md', '\n'.join(lines))
    paths = ['scripts/forecast_decision.py','config/forecast-decision.json',package['config']['seat_reference'],
             package['config']['turnout_history'], package['config']['source_audit'],
             'scripts/turnout_history.py','scripts/review_package.py','scripts/bader_ofer.py','scripts/baseline.py',
             'config/submission-fields.json','reports/review-package-2026-10-24/package.json',
             'reports/review-package-2026-10-24/inputs-manifest.json']
    inherited = baseline.load_json(legacy/'inputs-manifest.json')
    paths = sorted(set(paths+list(inherited)+['reports/review-package-2026-10-24/'+n for n in
        ('scenario-comparison.csv','reservists-scenarios.svg','method-description.txt')]))
    save_json('inputs-manifest.json', {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})
    save_json('validation.json', {'seat_vector_equal_to_previous': True,
        'total_seats': sum(package['forecast']['seats'].values()), 'turnout_pct': package['turnout']['formatted_pct'],
        'unrounded_and_displayed_turnout_within_configured_bounds': True,
        'all_scenarios_valid': True, 'method_word_count': len(method.split()),
        'forecast_sha256': hashlib.sha256((out/'forecast.json').read_bytes()).hexdigest(),
        'source_freeze_complete': False, 'submitted': False})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out-dir', type=Path, default=ROOT/'output/forecast-decision')
    args = parser.parse_args(); write(build(), args.out_dir)
    files = {p.name:p.read_text(encoding='utf-8') for p in sorted(args.out_dir.iterdir()) if p.is_file()}
    encoded = base64.b64encode(gzip.compress(json.dumps(files, ensure_ascii=False).encode())).decode()
    print('E017_FILES_BASE64_BEGIN')
    for i in range(0,len(encoded),8000):
        print(encoded[i:i+8000])
    print('E017_FILES_BASE64_END'); print(files['review.md'])
