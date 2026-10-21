"""Build the portable research database offline, using only Python's standard library."""
import argparse
import gzip
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = ['sources', 'elections', 'official_lists', 'geographies', 'geographic_votes',
          'poll_tables', 'poll_rows', 'polls', 'poll_values', 'ines_studies',
          'ines_variables', 'ines_frequencies', 'ines_value_labels']
KEYS = {'sources': 'source_id', 'elections': 'knesset', 'official_lists': 'knesset,ballot_code',
        'geographies': 'geo_id', 'geographic_votes': 'geo_id,ballot_code',
        'poll_tables': 'table_id', 'poll_rows': 'row_id', 'polls': 'poll_id',
        'poll_values': 'poll_id,value_index', 'ines_studies': 'study_year',
        'ines_variables': 'study_year,variable'}
CBS_TABLES = ['cbs_sources', 'cbs_locality_geography', 'cbs_age_sex', 'cbs_population_2018',
              'cbs_socioeconomic', 'cbs_census_records', 'cbs_census_variables', 'cbs_raw_rows']
KEYS.update({'cbs_sources': 'source_id', 'cbs_locality_geography': 'reference_year,locality_code',
             'cbs_age_sex': 'reference_year,locality_code,sex', 'cbs_population_2018': 'reference_year,locality_code',
             'cbs_socioeconomic': 'reference_year,locality_code', 'cbs_census_records': 'record_id',
             'cbs_census_variables': 'source_id,sheet,variable', 'cbs_raw_rows': 'source_id,sheet,row_number'})


def records(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        for line in stream:
            yield json.loads(line)


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def build(inputs, destination, cbs_inputs=None):
    cbs_inputs = cbs_inputs or inputs.parent / 'cbs-2026-10-21'
    tables = TABLES + (CBS_TABLES if cbs_inputs.exists() else [])
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    connection = sqlite3.connect(destination)
    counts, hashes = {}, {}
    for table in tables:
        path = (cbs_inputs if table.startswith('cbs_') else inputs) / (table + '.jsonl.gz')
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        # Infer a union schema from the frozen input; dictionaries/arrays remain valid JSON.
        columns, types = [], {}
        for row in records(path):
            for key, value in row.items():
                if key not in columns:
                    columns.append(key)
                kind = 'TEXT' if isinstance(value, (str, dict, list)) else ('REAL' if isinstance(value, float) else 'INTEGER')
                if value is not None:
                    types[key] = 'TEXT' if types.get(key) == 'TEXT' or kind == 'TEXT' else ('REAL' if types.get(key) == 'REAL' or kind == 'REAL' else 'INTEGER')
        definitions = ','.join(quote(c) + ' ' + types.get(c, 'TEXT') for c in columns)
        primary = ', PRIMARY KEY (' + KEYS[table] + ')' if table in KEYS else ''
        connection.execute(f'CREATE TABLE {table} ({definitions}{primary})')
        def values():
            for row in records(path):
                yield [json.dumps(row.get(c), ensure_ascii=False) if isinstance(row.get(c), (dict, list)) else row.get(c) for c in columns]
        connection.executemany(f'INSERT INTO {table} ({",".join(map(quote, columns))}) VALUES ({",".join("?" for _ in columns)})', values())
        counts[table] = connection.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]
    connection.executescript('''
    CREATE INDEX geography_election ON geographies(knesset,granularity);
    CREATE INDEX polls_election_date ON polls(knesset,date_proxy);
    CREATE INDEX frequency_variable ON ines_frequencies(study_year,variable);
    CREATE VIEW campaign_poll_candidates AS
      SELECT p.* FROM polls p JOIN elections e USING(knesset)
      WHERE campaign_main=1 AND record_kind='poll_index_row' AND date_proxy < election_date;
    CREATE VIEW national_results AS SELECT l.*, e.election_date FROM official_lists l JOIN elections e USING(knesset);
    CREATE VIEW poll_seat_diagnostics AS SELECT p.poll_id,p.knesset,p.date_proxy,
      SUM(CASE WHEN v.unit='seats' AND v.column_role='list_or_unresolved' THEN v.value ELSE 0 END) AS reported_seat_sum,
      SUM(CASE WHEN v.unit='unparsed' THEN 1 ELSE 0 END) AS unparsed_cells
      FROM polls p JOIN poll_values v USING(poll_id) GROUP BY p.poll_id;
    CREATE VIEW geography_totals AS SELECT geo_id,knesset,granularity,source_id,
      json_extract(attributes,'$."שם ישוב"') AS locality_name_he,
      json_extract(attributes,'$."סמל ישוב"') AS locality_code,
      json_extract(attributes,'$."קלפי"') AS ballot_number,
      CAST(json_extract(attributes,'$."בזב"') AS INTEGER) AS electorate,
      CAST(json_extract(attributes,'$."מצביעים"') AS INTEGER) AS ballots,
      CAST(json_extract(attributes,'$."כשרים"') AS INTEGER) AS valid,
      CAST(json_extract(attributes,'$."פסולים"') AS INTEGER) AS invalid
      FROM geographies;
    ''')
    if 'cbs_sources' in tables:
        add_cbs_views(connection)
    validate(connection)
    connection.commit()
    coverage = connection.execute('''SELECT e.knesset,e.election_date,
        (SELECT COUNT(*) FROM official_lists l WHERE l.knesset=e.knesset),
        (SELECT COUNT(*) FROM campaign_poll_candidates p WHERE p.knesset=e.knesset),
        (SELECT COUNT(*) FROM geographies g WHERE g.knesset=e.knesset AND granularity='locality'),
        (SELECT COUNT(*) FROM geographies g WHERE g.knesset=e.knesset AND granularity='ballot')
        FROM elections e ORDER BY knesset''').fetchall()
    report = {'tables': counts, 'coverage_columns': ['knesset', 'election_date', 'national_lists', 'main_poll_index_candidates', 'localities', 'ballot_boxes'],
              'coverage': coverage, 'input_sha256': hashes,
              'validation': 'passed; see scripts/build_database.py for exact checks',
              'poll_warning': 'Candidate rows are not deduplicated releases or verified historical publication information sets.'}
    if 'cbs_sources' in tables:
        report['cbs_profiles_by_year'] = connection.execute('SELECT reference_year,COUNT(*) FROM cbs_locality_profiles GROUP BY reference_year ORDER BY reference_year').fetchall()
        report['cbs_warning'] = 'Descriptive locality-level context. Historical release availability is unverified; no individual voter demographics or automatic feature eligibility.'
    connection.close()
    destination.with_suffix('.coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    return report


def add_cbs_views(db):
    db.executescript('''
    CREATE INDEX cbs_census_lookup ON cbs_census_records(source_id,sheet,locality_code,statistical_area);
    CREATE VIEW cbs_locality_profiles AS
      SELECT reference_year,reference_date,locality_code,locality_name_he,population,
        100.0*male_population/NULLIF(population,0) AS male_percent,
        100.0*(json_extract(age_bands,'$.age_65_69')+json_extract(age_bands,'$.age_70_74')+json_extract(age_bands,'$.age_75_up'))/NULLIF(population,0) AS age65_plus_percent,
        100.0*(json_extract(age_bands,'$.age_0_4')+json_extract(age_bands,'$.age_5_9')+json_extract(age_bands,'$.age_10_14')+json_extract(age_bands,'$.age_15_19'))/NULLIF(population,0) AS age0_19_percent,
        NULL AS median_age,NULL AS median_male_age,NULL AS median_female_age,source_id
      FROM cbs_population_2018
      UNION ALL
      SELECT t.reference_year,t.reference_date,t.locality_code,t.locality_name_he,t.population,
        100.0*m.population/NULLIF(t.population,0),
        100.0*COALESCE(json_extract(t.age_bands,'$.age_65_plus'),json_extract(t.age_bands,'$.age_65_69')+json_extract(t.age_bands,'$.age_70_74')+json_extract(t.age_bands,'$.age_75_79')+json_extract(t.age_bands,'$.age_80_84')+json_extract(t.age_bands,'$.age_85_plus'))/NULLIF(t.population,0),
        100.0*(json_extract(t.age_bands,'$.age_0_4')+json_extract(t.age_bands,'$.age_5_9')+json_extract(t.age_bands,'$.age_10_14')+json_extract(t.age_bands,'$.age_15_19'))/NULLIF(t.population,0),
        NULL,NULL,NULL,t.source_id FROM cbs_age_sex t LEFT JOIN cbs_age_sex m
        ON t.reference_year=m.reference_year AND t.locality_code=m.locality_code AND m.sex='male' WHERE t.sex='total'
      UNION ALL
      SELECT reference_year,reference_date,locality_code,NULL,
        json_extract(attributes,'$.pop_approx'),NULL,json_extract(attributes,'$.age65_pcnt'),
        json_extract(attributes,'$.age0_19_pcnt'),json_extract(attributes,'$.age_median'),
        json_extract(attributes,'$.m_age_median'),json_extract(attributes,'$.w_age_median'),source_id
      FROM cbs_census_records WHERE source_id='census-selected.xlsx' AND statistical_area IS NULL;
    CREATE VIEW cbs_locality_vote_shares AS SELECT g.geo_id,g.knesset,e.election_date,
        CAST(CAST(g.locality_code AS INTEGER) AS TEXT) AS locality_code,g.locality_name_he,
        g.valid,g.ballots,g.electorate,l.ballot_code,l.party_name_he,l.party_name_en,
        COALESCE(v.votes,0) AS votes,100.0*COALESCE(v.votes,0)/NULLIF(g.valid,0) AS vote_share_percent
      FROM geography_totals g JOIN official_lists l ON l.knesset=g.knesset
      LEFT JOIN geographic_votes v ON v.geo_id=g.geo_id AND l.ballot_code=v.ballot_code
      JOIN elections e ON e.knesset=g.knesset WHERE g.granularity='locality';
    CREATE VIEW cbs_locality_election_context AS SELECT v.*,p.reference_year AS demographic_year,
        p.reference_date AS demographic_reference_date,p.population,p.male_percent,
        p.age65_plus_percent,p.age0_19_percent,p.median_age,p.median_male_age,p.median_female_age,
        c.district_code,c.subdistrict_code,p.source_id AS demographic_source_id,
        1 AS descriptive_only,0 AS historical_availability_verified,
        p.reference_date>v.election_date AS demographic_reference_after_election
      FROM cbs_locality_vote_shares v JOIN cbs_locality_profiles p USING(locality_code)
      LEFT JOIN cbs_locality_geography c ON c.locality_code=p.locality_code AND c.reference_year=p.reference_year;
    CREATE VIEW cbs_ballot_locality_links AS SELECT g.geo_id,g.knesset,g.locality_code,
        g.ballot_number,p.reference_year AS demographic_year,p.source_id AS demographic_source_id,
        'locality context only' AS match_resolution
      FROM geography_totals g JOIN cbs_locality_profiles p
      ON p.locality_code=CAST(CAST(g.locality_code AS INTEGER) AS TEXT) WHERE g.granularity='ballot';
    ''')


def validate(db):
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok', 'SQLite integrity')
    for k, valid, ballots, invalid, electorate, turnout in db.execute('SELECT knesset,valid,ballots,invalid,electorate,turnout FROM elections'):
        sums = db.execute('SELECT SUM(votes),SUM(seats) FROM official_lists WHERE knesset=?', (k,)).fetchone()
        require(sums == (valid, 120), f'National list totals {k}: {sums} != {(valid,120)}')
        require(valid + invalid == ballots, f'Ballot identity {k}')
        require(abs(100 * ballots / electorate - turnout) < (.051 if k == 20 else .011), f'Turnout {k}')
        for granularity in ['locality', 'ballot']:
            actual = dict(db.execute('''SELECT v.ballot_code,SUM(v.votes) FROM geographic_votes v
                JOIN geographies g USING(geo_id) WHERE knesset=? AND granularity=? GROUP BY v.ballot_code''', (k, granularity)))
            expected = dict(db.execute('SELECT ballot_code,votes FROM official_lists WHERE knesset=?', (k,)))
            require(all(actual.get(party, 0) == expected.get(party, 0) for party in actual.keys() | expected.keys()), f'Geographic/national reconciliation {k} {granularity}')
    for child, parent, key in [('geographic_votes','geographies','geo_id'), ('poll_values','polls','poll_id'),
                                ('polls','poll_rows','row_id'), ('poll_rows','poll_tables','table_id')]:
        require(db.execute(f'SELECT COUNT(*) FROM {child} c LEFT JOIN {parent} p USING({key}) WHERE p.{key} IS NULL').fetchone()[0] == 0, f'Orphan {child}')
    require(db.execute('SELECT COUNT(*) FROM geographic_votes WHERE votes<0').fetchone()[0] == 0, 'Negative votes')
    require(db.execute('''SELECT COUNT(*) FROM geography_totals g LEFT JOIN
        (SELECT geo_id,SUM(votes) AS n FROM geographic_votes GROUP BY geo_id) v USING(geo_id)
        WHERE g.valid!=COALESCE(v.n,0) OR g.valid+g.invalid!=g.ballots
        OR g.valid IS NULL OR g.invalid IS NULL OR g.ballots IS NULL''').fetchone()[0] == 0, 'Geographic row totals')
    if db.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='cbs_sources'").fetchone()[0]:
        require(db.execute('SELECT COUNT(*) FROM cbs_socioeconomic WHERE cluster<1 OR cluster>10').fetchone()[0] == 0, 'CBS clusters')
        require(db.execute('SELECT COUNT(*) FROM cbs_locality_profiles WHERE population<0 OR male_percent<0 OR male_percent>100 OR age65_plus_percent<0 OR age65_plus_percent>100').fetchone()[0] == 0, 'CBS population bounds')
        require(db.execute('SELECT COUNT(*) FROM (SELECT reference_year,locality_code,COUNT(*) n FROM cbs_locality_profiles GROUP BY reference_year,locality_code HAVING n>1)').fetchone()[0] == 0, 'Duplicate CBS locality profiles')
        for table in CBS_TABLES[1:]:
            require(db.execute(f'SELECT COUNT(*) FROM {table} c LEFT JOIN cbs_sources s USING(source_id) WHERE s.source_id IS NULL').fetchone()[0] == 0, f'CBS source orphan {table}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=ROOT / 'data/database')
    parser.add_argument('--out', type=Path, default=ROOT / 'output/elections.sqlite')
    args = parser.parse_args()
    print(json.dumps(build(args.inputs, args.out), indent=2))
