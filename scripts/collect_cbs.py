"""Collect CBS area statistics, never individual voter demographics.

Optional refresh dependencies: requests/openpyxl; GDAL for the 2018 geodatabase.
Frozen tables and database rebuilds do not require any of these packages.
"""
import gzip
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

import openpyxl
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / 'tmp/cbs'
OUT = ROOT / 'data/cbs-2026-10-21'
SOURCES = []
RAW_ROWS = []


def fetch(name, url, kind, expected=None):
    path = CACHE / name
    if not path.exists():
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        path.write_bytes(response.content)
    data = path.read_bytes()
    if expected:
        assert data.startswith(expected), (name, 'Unexpected response content')
    archive = OUT / 'raw-sources'
    archive.mkdir(parents=True, exist_ok=True)
    (archive / (name + '.gz')).write_bytes(gzip.compress(data, mtime=0))
    SOURCES.append(dict(source_id=name, url=url, retrieved_date='2026-10-21',
                        sha256=hashlib.sha256(data).hexdigest(), bytes=len(data), kind=kind,
                        publisher='Israel Central Bureau of Statistics',
                        historical_availability_verified=False,
                        known_revision_date='2021-03-04' if name == 'ses2017.xlsx' else None,
                        rights='CBS published aggregate statistics; source rights retained; transformed numerical tables attributed to CBS'))
    return path


def save(name, rows):
    payload = ''.join(json.dumps(row, sort_keys=True, ensure_ascii=False) + '\n' for row in rows).encode('utf-8')
    (OUT / (name + '.jsonl.gz')).write_bytes(gzip.compress(payload, mtime=0))
    print(name, len(rows), flush=True)


def code(value):
    if value is None or value == '':
        return None
    try:
        return str(int(float(value)))
    except (ValueError, TypeError):
        return str(value).strip()


def numeric(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    return None  # Suppression/absence tokens are never zero-filled.


def crosswalks():
    path = CACHE / 'locality-catalog.json'
    if not path.exists():
        result = requests.get('https://data.gov.il/api/3/action/package_show?id=localities-in-israel', timeout=30).json()
        path.write_text(json.dumps(result['result'], ensure_ascii=False), encoding='utf-8')
    catalog = json.loads(path.read_bytes())
    output = []
    for year in range(2017, 2023):
        resource = next(r for r in catalog['resources'] if str(year) in r['name'])
        name = f'localities{year}.json'
        url = f"https://data.gov.il/api/3/action/datastore_search?resource_id={resource['id']}&limit=10000"
        data = json.loads(fetch(name, url, 'annual CBS locality-code catalog').read_bytes())['result']
        assert data['total'] == len(data['records'])
        for index, row in enumerate(data['records']):
            RAW_ROWS.append(dict(source_id=name, sheet='API records', row_number=index, attributes=row))
            locality = code(row.get('סמל יישוב', row.get('סמל')))
            if not locality or locality == '0':
                continue
            output.append(dict(reference_year=year, locality_code=locality,
                               locality_name_he=row.get('שם יישוב', row.get('שם יישוב -A')),
                               district_code=code(row.get('סמל מחוז', row.get('מחוז'))),
                               district_name_he=row.get('שם מחוז'),
                               subdistrict_code=code(row.get('סמל נפה', row.get('נפה'))),
                               population=numeric(row.get(f'סך הכל אוכלוסייה {year}')),
                               source_id=name))
    save('cbs_locality_geography', output)


def annual_age_sex():
    output = []
    for year in [2019, 2020, 2021]:
        name = f'annual{year}.xlsx'
        path = fetch(name, f'https://www.cbs.gov.il/he/publications/doclib/2017/population_madaf/population_madaf_{year}_7.xlsx', 'annual year-end population by age and sex', b'PK')
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        grouped = defaultdict(list)
        for sheet in workbook:
            if year == 2019 and sheet.title not in ['סה"כ אוכלוסייה', 'זכרים', 'נקבות']:
                continue
            if year != 2019 and sheet.title not in ['יישובים יהודיים', 'יישובים לא-יהודיים', 'יישובים מעורבים']:
                continue
            age_columns = {}
            for rn, row in enumerate(sheet.iter_rows(max_col=25, values_only=True), 1):
                RAW_ROWS.append(dict(source_id=name, sheet=sheet.title, row_number=rn, attributes=list(row)))
                if '4-0' in row:
                    for index, label in enumerate(row):
                        if not isinstance(label, str):
                            continue
                        if re.fullmatch(r'\d+-\d+', label):
                            low, high = sorted(map(int, label.split('-')))
                            age_columns[index] = f'age_{low}_{high}'
                        elif re.fullmatch(r'\+?\d+\+?', label) and '+' in label:
                            age_columns[index] = f"age_{label.replace('+','')}_plus"
                    continue
                if year == 2019:
                    locality, locname, area, total = row[1:5]
                    sex = {'סה"כ אוכלוסייה': 'total', 'זכרים': 'male', 'נקבות': 'female'}[sheet.title]
                else:
                    locality, locname, area = row[:3]
                    mixed = sheet.title == 'יישובים מעורבים'
                    if mixed and row[3] != 'סה"כ':
                        continue
                    raw_sex, total = row[4:6] if mixed else row[3:5]
                    sex = {'סה"כ': 'total', 'גברים': 'male', 'נשים': 'female', 'זכר': 'male', 'נקבה': 'female'}.get(raw_sex)
                if not isinstance(locality, (int, float)) or not sex or numeric(total) is None:
                    continue
                assert age_columns, (name, sheet.title)
                ages = {label: numeric(row[index]) for index, label in age_columns.items()}
                grouped[(code(locality), sex)].append(dict(locality_name_he=locname, area=area,
                                                           population=total, age_bands=ages))
        for (locality, sex), rows in grouped.items():
            totals = [r for r in rows if r['area'] in (None, '', 'סך הכל', 'סה"כ')]
            assert len(totals) <= 1, (year, locality, sex, 'duplicate locality totals')
            selected = totals or rows
            assert len({str(r['area']) for r in selected}) == len(selected), (year, locality, sex, 'duplicate reporting areas')
            fields = selected[0]['age_bands']
            ages = {}
            for field in fields:
                values = [r['age_bands'].get(field) for r in selected]
                ages[field] = sum(values) if all(v is not None for v in values) else None
            output.append(dict(reference_year=year, locality_code=locality, locality_name_he=selected[0]['locality_name_he'],
                               sex=sex, population=sum(r['population'] for r in selected), age_bands=ages,
                               source_id=name, contributing_records=len(selected),
                               method='published locality total' if totals else 'sum unique reporting areas; total population group only',
                               reference_date=f'{year}-12-31'))
        workbook.close()
    save('cbs_age_sex', output)


def population_2018():
    # Extract only attribute records. Original geometry stays in the archived source ZIP.
    from osgeo import ogr
    ogr.UseExceptions()
    name = 'demo2018.zip'
    fetch('demography2018-readme.pdf', 'https://www.cbs.gov.il/he/Documents/שכבות גיאוגרפיות/readme%20_demographic_project_2018_29Mar_1414.pdf', 'official field definitions, suppressed/referenced areas and geographic vintage', b'%PDF')
    path = fetch(name, 'https://www.cbs.gov.il/he/Documents/שכבות גיאוגרפיות/yishuv_stat11_demografy_18_29Mar_1414.zip', '2018 year-end demographic attributes on 2011 statistical-area geography', b'PK')
    import zipfile
    extraction = CACHE / 'extract2018'
    if not extraction.exists():
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                assert (extraction / member).resolve().is_relative_to(extraction.resolve())
            archive.extractall(extraction)
    data = ogr.Open(str(next(extraction.glob('*.gdb'))))
    layer = data.GetLayer(0)
    grouped = defaultdict(list)
    for index, feature in enumerate(layer):
        row = feature.items()
        row = {k: v for k, v in row.items() if k.lower() not in ('shape_length', 'shape_area')}
        RAW_ROWS.append(dict(source_id=name, sheet=layer.GetName(), row_number=index, attributes=row))
        if row['Pop_Total'] is not None and row['Pop_Total'] > 0:
            grouped[code(row['SEMEL_YISHUV'])].append(row)
    output = []
    for locality, rows in grouped.items():
        def complete_sum(field):
            values = [numeric(row[field]) for row in rows]
            return sum(values) if all(v is not None for v in values) else None
        record = dict(reference_year=2018, locality_code=locality,
                      locality_name_he=next((r['SHEM_YISHUV'] for r in rows if r['SHEM_YISHUV']), None),
                      population=complete_sum('Pop_Total'), male_population=complete_sum('Male_Total'),
                      female_population=complete_sum('Female_Total'),
                      age_bands={field: complete_sum(field) for field in rows[0] if field.startswith('age_')},
                      source_id=name, contributing_records=len(rows),
                      method='sum populated statistical-area/unified reporting records; referenced empty polygons excluded',
                      reference_date='2018-12-31')
        output.append(record)
    save('cbs_population_2018', output)


def socioeconomic():
    output = []
    definitions = [
        (2015, 'ses2015.xlsx', 'https://www.cbs.gov.il/he/publications/doclib/2019/1765_socio_economic_2015/t08.xlsx', (3, 4, 5, 6, 7, 8, 9)),
        (2017, 'ses2017.xlsx', 'https://www.cbs.gov.il/he/mediarelease/doclib/2020/403/24_20_403t2.xlsx', (5, 6, 7, 9, 10, 11, 12)),
        (2017, 'ses2017-muni.xlsx', 'https://www.cbs.gov.il/he/mediarelease/doclib/2020/403/24_20_403t1.xlsx', (1, 2, 10, 3, 4, 5, 6)),
        (2019, 'ses2019.xlsx', 'https://www.cbs.gov.il/he/publications/doclib/2023/socio_eco19_1903/t08.xlsx', (5, 6, 7, 9, 10, 11, 12)),
        (2019, 'ses2019-muni.xlsx', 'https://www.cbs.gov.il/he/publications/doclib/2023/socio_eco19_1903/t02.xlsx', (1, 2, 11, 4, 5, 6, 7)),
    ]
    for year, name, url, columns in definitions:
        path = fetch(name, url, 'CBS socioeconomic index: reference year differs from release year', b'PK')
        sheet = openpyxl.load_workbook(path, read_only=True, data_only=True).active
        for rn, row in enumerate(sheet.iter_rows(max_col=15, values_only=True), 1):
            RAW_ROWS.append(dict(source_id=name, sheet=sheet.title, row_number=rn, attributes=list(row)))
            loc, he, en, population, index, rank, cluster = [row[i] for i in columns]
            if not isinstance(loc, (int, float)) or not isinstance(cluster, (int, float)) or not 1 <= cluster <= 10:
                continue  # Regional council authority codes are not locality codes.
            output.append(dict(reference_year=year, locality_code=code(loc), locality_name_he=he,
                               locality_name_en=en, index_population=population, index_value=index,
                               rank=rank, cluster=cluster, source_id=name,
                               rank_scope='all localities' if year == 2015 else ('local authorities' if 'muni' in name else 'localities within regional councils')))
    base = 'https://services2.arcgis.com/xMRYm7cNgdR5RN6F/arcgis/rest/services/אשכולחברתיכלכלי2021לפייישוב_ExportFeatures/FeatureServer/26'
    url = base + '/query?where=1%3D1&outFields=SETL_CODE,HEB_NAME,INDEX_VALUE_2021,RANK_2021,CLUSTER_2021&returnGeometry=false&f=json&resultRecordCount=2000&orderByFields=OBJECTID'
    name = 'ses2021-localities.json'
    response = json.loads(fetch(name, url, 'CBS-owned GIS layer linked from official socioeconomic map').read_bytes())
    assert not response.get('exceededTransferLimit') and 'error' not in response
    for rn, feature in enumerate(response['features']):
        row = feature['attributes']
        RAW_ROWS.append(dict(source_id=name, sheet='GIS attributes', row_number=rn, attributes=row))
        if numeric(row['CLUSTER_2021']) is None:
            continue
        output.append(dict(reference_year=2021, locality_code=code(row['SETL_CODE']), locality_name_he=row['HEB_NAME'],
                           locality_name_en=None, index_population=None, index_value=row['INDEX_VALUE_2021'],
                           rank=row['RANK_2021'], cluster=row['CLUSTER_2021'], source_id=name,
                           rank_scope='CBS locality GIS map; consult source ranking definitions'))
    save('cbs_socioeconomic', output)


def census():
    # Preserve published fields and their definitions, with no false precision or imputation.
    records, variables = [], []
    names = {
        'census-selected.xlsx': 'https://www.cbs.gov.il/he/publications/LochutTlushim/2025/Selected%20data%2C%20by%20localities%20and%20statistical%20areas%20-%20the%202022%20Census.xlsx',
        'census-broad.xlsx': 'https://www.cbs.gov.il/he/publications/LochutTlushim/2025/Summarized%20file%20of%20broad%20geographical%20units%20-%20census%202022.xlsx'}
    for name, url in names.items():
        path = fetch(name, url, '2022 Census estimates; source workbook published under 2025 path, not a historical pre-election release', b'PK')
        workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
        # Full selected locality/stat-area data; broad geographic comparisons and local geography.
        sheets = list(workbook) if name == 'census-selected.xlsx' else [workbook[x] for x in ['Big Localities', 'Little Localities', 'District Sub-District Natural  ']]
        for sheet in sheets:
            headers = None
            previous = None
            for rn, row in enumerate(sheet.iter_rows(max_col=min(sheet.max_column, 500), values_only=True), 1):
                RAW_ROWS.append(dict(source_id=name, sheet=sheet.title, row_number=rn, attributes=list(row)))
                if 'LocalityCode' in row or 'DistrictCode' in row:
                    headers = list(row)
                    for index, field in enumerate(headers):
                        if field:
                            variables.append(dict(source_id=name, sheet=sheet.title, variable=field, label=str(previous[index]).strip() if previous and previous[index] else None))
                    continue
                if headers:
                    attributes = {str(h): value for h, value in zip(headers, row) if h}
                    loc = attributes.get('LocalityCode')
                    district = attributes.get('DistrictCode')
                    if isinstance(loc, (int, float)) or isinstance(district, (int, float)):
                        records.append(dict(record_id=f'{name}:{sheet.title}:{rn}', source_id=name, sheet=sheet.title,
                                            reference_year=2022, reference_date='2022-04',
                                            locality_code=code(loc), statistical_area=code(attributes.get('StatArea')),
                                            quarter=code(attributes.get('Quarter')), subquarter=code(attributes.get('SubQuarter')),
                                            district_code=code(district), subdistrict_code=code(attributes.get('SubDistrictCode')),
                                            natural_area_code=code(attributes.get('NatRegCode')), attributes=attributes))
                previous = row
        workbook.close()
    save('cbs_census_records', records)
    save('cbs_census_variables', variables)


if __name__ == '__main__':
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    crosswalks()
    annual_age_sex()
    population_2018()
    socioeconomic()
    census()
    save('cbs_raw_rows', RAW_ROWS)
    save('cbs_sources', SOURCES)
