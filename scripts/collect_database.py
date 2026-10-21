"""Refresh historical source tables. Optional collection dependencies: pandas, lxml, requests.

This script uses a local cache; the offline database builder needs only Python.
"""
import csv
import gzip
import hashlib
import io
import json
import re
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests
from lxml import html

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'tmp/database'
OUT = ROOT / 'data/database'
DATES = {20: '2015-03-17', 21: '2019-04-09', 22: '2019-09-17',
         23: '2020-03-02', 24: '2021-03-23', 25: '2022-11-01'}
KEYS = dict(zip(DATES, ['2015', '2019apr', '2019sep', '2020', '2021', '2022']))
SESSION = requests.Session()
SESSION.headers['User-Agent'] = 'IsraelElectionForecastResearch/0.1 (+https://github.com/Omer-Sut/israel-election-forecast)'
SOURCES = []


def fetch(name, url, rights):
    path = CACHE / name
    if not path.exists():
        response = SESSION.get(url, timeout=45)
        response.raise_for_status()
        path.write_bytes(response.content)
    data = path.read_bytes()
    if name.startswith('wiki-') or re.fullmatch(r'cec\d+\.html|cec\d+-(locality|ballot)\.csv\.json', name):
        archive = OUT / 'raw-sources'
        archive.mkdir(parents=True, exist_ok=True)
        (archive / (name + '.gz')).write_bytes(gzip.compress(data, mtime=0))
    source_id = name
    SOURCES.append(dict(source_id=source_id, url=url, retrieved_date='2026-10-21',
                        sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), rights=rights))
    return data


def save(name, rows):
    payload = ''.join(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n' for row in rows).encode('utf-8')
    (OUT / (name + '.jsonl.gz')).write_bytes(gzip.compress(payload, mtime=0))
    print(name, len(rows), 'records', len(payload), 'uncompressed bytes', flush=True)


def clean(node):
    return re.sub(r'\s+', ' ', node.text_content()).strip().replace('\u200e', '').replace('\u200f', '')


def number(text):
    return float(re.sub(r'[, %\s\u200e\u200f]', '', text))


def collect_official():
    metadata = json.loads(fetch('data-gov-search.json', 'https://data.gov.il/api/3/action/package_search?q=elections&rows=50', 'CKAN metadata; Other (Open)'))
    package = next(p for p in metadata['result']['results'] if p['name'] == 'votes-knesset')
    national, lists, geographies, votes = [], [], [], []
    for k, date in DATES.items():
        for granularity, token in [('locality', 'ישוב'), ('ballot', 'קלפי')]:
            candidates = [r for r in package['resources'] if str(k) in r['name'] and token in r['name']]
            if len(candidates) != 1:
                raise ValueError((k, token, [(r['name'], r['url']) for r in candidates]))
            resource = candidates[0]
            name = f'cec{k}-{granularity}.csv'
            api_url = f"https://data.gov.il/api/3/action/datastore_search?resource_id={resource['id']}&limit=32000"
            data = json.loads(fetch(name + '.json', api_url, 'data.gov.il votes-knesset: Other (Open); Central Elections Committee'))['result']
            assert data['total'] == len(data['records']), (name, data['total'])
            stream = io.StringIO()
            columns = [f['id'] for f in data['fields'] if f['id'] != '_id']
            writer = csv.DictWriter(stream, fieldnames=columns, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(data['records'])
            raw = stream.getvalue().encode('utf-8-sig')
            # Preserve all API columns except its artificial _id in a lossless CSV projection.
            (OUT / (name + '.gz')).write_bytes(gzip.compress(raw, mtime=0))
            try:
                text = raw.decode('utf-8-sig')
            except UnicodeDecodeError:
                text = raw.decode('cp1255')
            reader = csv.DictReader(io.StringIO(text))
            fields = reader.fieldnames
            valid_index = fields.index('כשרים')
            totals = {}
            for index, row in enumerate(reader):
                geo_id = f'{k}:{granularity}:{index}'
                meta = {f: row[f] for f in fields[:valid_index + 1]}
                geographies.append(dict(geo_id=geo_id, knesset=k, granularity=granularity,
                                        source_id=name + '.json', attributes=meta))
                for party in fields[valid_index + 1:]:
                    value = int(float(row[party].replace(',', '') or 0))
                    if value:
                        votes.append(dict(geo_id=geo_id, ballot_code=party, votes=value))
                    totals[party] = totals.get(party, 0) + value
            if granularity == 'locality':
                local_totals = totals
            elif totals != local_totals:
                print('Geographic totals differ:', k, {p: totals.get(p, 0)-local_totals.get(p, 0) for p in totals if totals.get(p, 0) != local_totals.get(p, 0)}, flush=True)
        if k >= 21:
            name = f'cec{k}.html'
            tree = html.fromstring(fetch(name, f'https://votes{k}.bechirot.gov.il/nationalresults', 'Official published election results'))
            summary = tree.xpath('//table[contains(@class,"ResultsSummaryTable")]//td')
            values = [number(clean(c)) for c in summary]
            national.append(dict(knesset=k, election_date=date, electorate=int(values[0]), ballots=int(values[1]), turnout=values[2], valid=int(values[3]), invalid=int(values[4]), source_id=name))
            for row in tree.xpath('//table[contains(@class,"TableData")]//tbody/tr'):
                cells = row.xpath('./td')
                if len(cells) < 5:
                    continue
                lists.append(dict(knesset=k, party_name_he=cells[0].get('title') or clean(cells[0]), ballot_code=clean(cells[1]), seats=int(number(clean(cells[2]))), vote_share=number(clean(cells[3])), votes=int(number(clean(cells[4]))), source_id=name))
        else:
            # Historical official CSV supplies votes; independently corroborated final seats.
            raw = fetch('idi2015.html', 'https://en.idi.org.il/israeli-elections-and-parties/elections/2015/', 'Israel Democracy Institute; factual results transcription; no article text redistributed')
            tree = html.fromstring(raw)
            idi_rows = pd.read_html(io.StringIO(raw.decode('utf-8')))[0].fillna('').values.tolist()
            national.append(dict(knesset=k, election_date=date, electorate=5881696, ballots=4254738, turnout=72.3, valid=4210884, invalid=43854, source_id='idi2015.html'))
            for record in idi_rows:
                if not isinstance(record[1], (int, float)):
                    continue
                name_en, count, seats, share = record[:4]
                codes = [code for code, value in local_totals.items() if value == int(count)]
                assert len(codes) == 1, record
                lists.append(dict(knesset=k, ballot_code=codes[0], party_name_he=None,
                                  party_name_en=name_en, votes=int(count), seats=0 if seats == '-' else int(seats),
                                  vote_share=float(share), source_id='idi2015.html',
                                  votes_source_id='cec20-locality.csv.json'))
    save('elections', national)
    save('official_lists', lists)
    save('geographies', geographies)
    save('geographic_votes', votes)


def grid_rows(table):
    """Expand spans while retaining each physical cell's unique origin."""
    carry = {}
    for ri, tr in enumerate(table.xpath('./tbody/tr|./tr')):
        grid = {}
        for col, (remaining, cell, origin) in list(carry.items()):
            grid[col] = (cell, origin)
            if remaining == 1:
                del carry[col]
            else:
                carry[col] = (remaining - 1, cell, origin)
        col = 0
        for ci, cell in enumerate(tr.xpath('./th|./td')):
            while col in grid:
                col += 1
            origin = f'{ri}:{ci}'
            for offset in range(int(cell.get('colspan', '1'))):
                grid[col + offset] = (cell, origin)
                if int(cell.get('rowspan', '1')) > 1:
                    carry[col + offset] = (int(cell.get('rowspan')) - 1, cell, origin)
            col += int(cell.get('colspan', '1'))
        yield ri, [grid.get(i) for i in range(max(grid, default=-1) + 1)], tr


def parse_poll_date(text, default_year):
    """Conservative date endpoint, retained as a date proxy, not verified publication."""
    s = re.sub(r'\[[^\]]*\]', '', text)
    years = re.findall(r'\b20\d{2}\b', s)
    year = int(years[-1]) if years else default_year
    short_year = re.search(r'[A-Za-z]{3}[a-z]*\s+(\d{2})\s*$', s)
    if short_year and not years:
        year = 2000 + int(short_year[1])
    months = {m.lower(): i for i, m in enumerate(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}
    matches = list(re.finditer(r'(\d{1,2})\s*([A-Za-z]{3})[a-z]*', s))
    if not matches:
        return None
    match = matches[-1]
    try:
        return datetime(year, months[match[2].lower()], int(match[1])).date().isoformat()
    except (ValueError, KeyError):
        return None


def collect_polls():
    tables, rows, polls, values = [], [], [], []
    for k, key in KEYS.items():
        target = DATES[k]
        url_key = key.replace('2019apr', 'April_2019').replace('2019sep', 'September_2019')
        raw = fetch(f'wiki-{key}.html', f'https://en.wikipedia.org/wiki/Opinion_polling_for_the_{url_key}_Israeli_legislative_election', 'Wikipedia table data, CC BY-SA 4.0; source page links provide contributor history')
        tree = html.fromstring(raw)
        id_nodes = {node.get('id'): node for node in tree.xpath('//*[@id]')}
        for ti, table in enumerate(tree.xpath('//table[contains(concat(" ",normalize-space(@class)," ")," wikitable ")]')):
            tid = f'{k}:{ti}'
            heading = table.xpath('preceding::*[self::h2 or self::h3 or self::h4][1]')
            title = clean(heading[0]) if heading else ''
            # Explicit table membership: subsequent tables are counterfactual scenarios.
            main_limit = {20: 1, 21: 4, 22: 6, 23: 5, 24: 8, 25: 6}[k]
            kind = 'main' if ti < main_limit else 'context_or_scenario'
            tables.append(dict(table_id=tid, knesset=k, heading=title, kind=kind, source_id=f'wiki-{key}.html'))
            headers = []
            year = int(target[:4])
            for ri, grid, tr in grid_rows(table):
                texts = [clean(item[0]) if item else '' for item in grid]
                distinct = list(dict.fromkeys(texts))
                rid = f'{tid}:{ri}'
                refs = []
                for anchor in tr.xpath('.//sup//a[starts-with(@href,"#")]'):
                    nodes = [id_nodes[anchor.get('href')[1:]]] if anchor.get('href')[1:] in id_nodes else []
                    for node in nodes:
                        refs.extend(node.xpath('.//a[starts-with(@href,"http")]/@href'))
                rows.append(dict(row_id=rid, table_id=tid, row_number=ri, cells=texts,
                                 cell_origins=[item[1] if item else None for item in grid], references=sorted(set(refs))))
                if texts and texts[0].lower() in ('date', 'dates'):
                    if any('likud' in value.lower() for value in texts):
                        headers = texts
                    continue
                if len(distinct) == 1 and re.fullmatch(r'20\d{2}', distinct[0]):
                    year = int(distinct[0])
                if not headers or len(texts) < 4:
                    continue
                sort_date = grid[0][0].get('data-sort-value') if grid[0] else None
                year_hint = int(sort_date[:4]) if sort_date and re.fullmatch(r'20\d{2}-\d{2}-\d{2}', sort_date) else year
                date = parse_poll_date(texts[0], year_hint)
                if not date:
                    continue
                # Exclude final/previous results, seats and exit polls from the poll view.
                description = ' '.join(texts[:3]).lower()
                excluded = any(word in description for word in ['election result', 'final result', 'exit poll', 'outgoing', 'actual result'])
                if not any('likud' in h.lower() for h in headers):
                    continue
                meta_end = 3 if len(headers) > 2 and headers[2].lower() == 'publisher' else 2
                if not any(re.fullmatch(r'\d+(?:\.\d+)?\s*%?', re.sub(r'\[[^\]]*\]', '', value).strip()) for value in texts[meta_end:]):
                    continue  # Dated campaign events remain in raw rows, not poll records.
                pid = rid
                polls.append(dict(poll_id=pid, table_id=tid, row_id=rid, knesset=k,
                                  date_proxy=date, date_raw=texts[0], publication_date=None,
                                  source_sort_date=sort_date,
                                  metadata=texts[1:meta_end], record_kind='result_or_exit_or_reference' if excluded else 'poll_index_row',
                                  audit_status='index_transcription', campaign_main=kind == 'main',
                                  source_id=f'wiki-{key}.html'))
                grouped = {}
                for col in range(meta_end, min(len(headers), len(grid))):
                    item = grid[col]
                    if not item:
                        continue
                    cell, origin = item
                    grouped.setdefault(origin, {'labels': [], 'text': clean(cell)})['labels'].append(headers[col])
                for vi, group in enumerate(grouped.values()):
                    text = re.sub(r'\[[^\]]*\]', '', group['text']).strip()
                    # Numeric seat and percentage values kept distinct; dashes and <threshold are raw only.
                    match = re.fullmatch(r'(\d+(?:\.\d+)?)\s*(%)?', text)
                    numeric = float(match[1]) if match else None
                    label = ' + '.join(dict.fromkeys(group['labels']))
                    values.append(dict(poll_id=pid, value_index=vi, list_label=label,
                                       column_role='aggregate_or_comparison' if re.search(r'bloc|lead|total|coalition|opposition|margin|^(?:L|R|Left|Right|Gap|Diff)$', label, re.I) else 'list_or_unresolved',
                                       value=numeric, unit='percent' if match and match[2] else ('seats' if match else 'unparsed'), raw_value=group['text']))
    save('poll_tables', tables)
    save('poll_rows', rows)
    save('polls', polls)
    save('poll_values', values)


def collect_ines():
    studies, variables, categories, dictionary = [], [], [], []
    names = {2015: '2023/06/2015.dta', 2019: '2023/06/Apr-Sep_2019_update_STATA.dta',
             2020: '2023/06/March_2020_data.dta', 2021: '2023/06/March_2021_data_website_STATA.dta',
             2022: '2023/06/2022_STATA.dta', 2025: '2025/08/2025_STATA.dta'}
    fetch('ines-our-data.html', 'https://socsci4.tau.ac.il/mu2/ines/data/our-data/', 'INES project documentation; metadata only')
    for year, suffix in names.items():
        name = f'ines{year}.dta'
        fetch(name, 'https://socsci4.tau.ac.il/mu2/ines/wp-content/uploads/sites/4/' + suffix, 'INES public download; no explicit microdata redistribution license verified; raw file excluded from Git')
        with pd.io.stata.StataReader(CACHE / name, convert_categoricals=False) as reader:
            labels = reader.variable_labels()
            value_labels = reader.value_labels()
            label_map = dict(zip(reader._varlist, reader._lbllist))
            assert set(label_map) == set(labels)
            # Public API offers variable-to-label mapping through read categorical dtype.
            frame = reader.read()
        studies.append(dict(study_year=year, respondents=len(frame), columns=len(frame.columns), source_id=name, design='four-wave panel spanning April and September elections' if year == 2019 else ('off-cycle survey' if year == 2025 else 'election survey'), availability_before_election_verified=False))
        for col in frame:
            for code, label in value_labels.get(label_map.get(col), {}).items():
                dictionary.append(dict(study_year=year, variable=col, code=float(code), label=label))
            series = frame[col]
            unique = int(series.nunique())
            numeric = pd.api.types.is_numeric_dtype(series)
            # No respondent rows, free text, identifiers, or fine-grained continuous values published.
            eligible = numeric and 1 < unique <= 60 and not re.search(r'(^id$|serial|phone|interview|date|weight|^wgt)', col, re.I)
            variables.append(dict(study_year=year, variable=col, label=labels.get(col, ''), dtype=str(series.dtype), nonmissing=int(series.notna().sum()), distinct=unique, frequencies_published=eligible))
            if eligible:
                for code, count in series.value_counts(dropna=False).items():
                    # Suppress tiny cells rather than expose rare respondent attributes.
                    code_json = None if pd.isna(code) else float(code)
                    label = value_labels.get(label_map.get(col), {}).get(code)
                    categories.append(dict(study_year=year, variable=col, code=code_json, label=label,
                                           count=int(count) if count >= 5 else None, suppressed=count < 5,
                                           weighting='unweighted', missing_system=pd.isna(code)))
    save('ines_studies', studies)
    save('ines_variables', variables)
    save('ines_frequencies', categories)
    save('ines_value_labels', dictionary)


if __name__ == '__main__':
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    collect_official()
    collect_polls()
    collect_ines()
    save('sources', SOURCES)
