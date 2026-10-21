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


def records(path):
    with gzip.open(path, 'rt', encoding='utf-8') as stream:
        for line in stream:
            yield json.loads(line)


def quote(name):
    return '"' + name.replace('"', '""') + '"'


def build(inputs, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    connection = sqlite3.connect(destination)
    counts, hashes = {}, {}
    for table in TABLES:
        path = inputs / (table + '.jsonl.gz')
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
    connection.close()
    destination.with_suffix('.coverage.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    return report


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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, default=ROOT / 'data/database')
    parser.add_argument('--out', type=Path, default=ROOT / 'output/elections.sqlite')
    args = parser.parse_args()
    print(json.dumps(build(args.inputs, args.out), indent=2))
