"""Reproducible descriptive linkage examples, not forecasting features or voter profiles."""
import argparse
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def weighted_percent(rows, field):
    valid = [r for r in rows if r[field] is not None and r['population'] is not None and r['population'] > 0]
    denominator = sum(r['population'] for r in valid)
    return {'percent': round(sum(r[field] * r['population'] for r in valid) / denominator, 6) if denominator else None,
            'population_with_measure': denominator, 'localities_with_measure': len(valid)}


def report(db):
    original_factory = db.row_factory
    db.row_factory = sqlite3.Row
    try:
        return _report(db)
    finally:
        db.row_factory = original_factory


def _report(db):
    linkage = []
    for election in db.execute('SELECT knesset,valid FROM elections ORDER BY knesset'):
        k = election['knesset']
        row = dict(db.execute('''SELECT COUNT(*) AS locality_records,
            SUM(CASE WHEN p.locality_code IS NOT NULL THEN 1 ELSE 0 END) AS matched_localities,
            SUM(CASE WHEN p.locality_code IS NOT NULL THEN g.valid ELSE 0 END) AS matched_valid_votes
            FROM geography_totals g LEFT JOIN cbs_locality_profiles p
            ON p.reference_year=2022 AND p.locality_code=CAST(CAST(g.locality_code AS INTEGER) AS TEXT)
            WHERE g.knesset=? AND g.granularity='locality' ''', (k,)).fetchone())
        row.update(knesset=k, census_year=2022, comparison='retrospective code-link coverage, not pre-election feature eligibility',
                   national_valid_votes=election['valid'], matched_share_of_national_valid_percent=round(100 * row['matched_valid_votes'] / election['valid'], 6))
        special = db.execute('''SELECT COALESCE(SUM(valid),0) FROM geography_totals
            WHERE knesset=? AND granularity='locality' AND
            ((knesset=20 AND CAST(locality_code AS INTEGER)=0) OR
             (knesset=21 AND CAST(locality_code AS INTEGER)=99999) OR
             (knesset>=22 AND CAST(locality_code AS INTEGER)=9999))''', (k,)).fetchone()[0]
        row['special_unlocated_valid_votes'] = special
        row['matched_share_of_located_valid_percent'] = round(100 * row['matched_valid_votes'] / (election['valid'] - special), 6)
        linkage.append(row)
    # Common geographic cohort; one row per locality, avoiding repeated population per party/ballot.
    profiles = [dict(row) for row in db.execute('''SELECT p.* FROM cbs_locality_profiles p
        JOIN cbs_locality_geography c USING(reference_year,locality_code)
        JOIN geography_totals g ON CAST(CAST(g.locality_code AS INTEGER) AS TEXT)=p.locality_code
        WHERE p.reference_year=2018 AND c.district_code='4' AND g.knesset=21 AND g.granularity='locality' ''')]
    vote_totals = dict(db.execute('''SELECT COUNT(*) AS localities,SUM(votes) AS party_votes,
        SUM(valid) AS valid_votes,100.0*SUM(votes)/SUM(valid) AS party_vote_percent
        FROM cbs_locality_election_context WHERE knesset=21 AND demographic_year=2018
        AND district_code='4' AND ballot_code=?''', ('מחל',)).fetchone())
    vote_totals['party_vote_percent'] = round(vote_totals['party_vote_percent'], 6)
    census = json.loads(db.execute('''SELECT attributes FROM cbs_census_records
        WHERE source_id='census-broad.xlsx' AND sheet='District Sub-District Natural  '
        AND district_code='4' AND subdistrict_code IS NULL AND natural_area_code IS NULL''').fetchone()[0])
    return {
        'purpose': 'Descriptive geographic association only. It does not identify how men, women or age groups voted.',
        'linkage_coverage': linkage,
        'central_district_2018_april2019': {
            'demographic_year': 2018, 'election_date': '2019-04-09', 'district_code': '4',
            'population_in_matched_localities': sum(r['population'] for r in profiles),
            'male_share': weighted_percent(profiles, 'male_percent'),
            'age65_plus_share': weighted_percent(profiles, 'age65_plus_percent'),
            'likud': vote_totals,
            'availability': 'Release availability not certified; not a leakage-safe backtest feature set.',
            'missingness': 'Each demographic measure uses its own complete-measure population denominator. The vote share uses all matched localities including zero-party-vote records.'},
        'central_district_census2022': {
            'reference_date': '2022-04', 'source_id': 'census-broad.xlsx',
            'population': census['pop_approx'], 'median_age': census['age_median'],
            'median_male_age': census['m_age_median'], 'median_female_age': census['w_age_median'],
            'note': 'Published district medians, not averages of locality medians; source workbook under 2025 publication path.'}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, default=ROOT / 'output/elections.sqlite')
    parser.add_argument('--out', type=Path, default=ROOT / 'output/cbs-linkage.json')
    args = parser.parse_args()
    with sqlite3.connect(args.db) as connection:
        result = report(connection)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
