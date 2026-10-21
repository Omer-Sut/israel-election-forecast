# CBS geographic context for election results

Collected October 21, 2026 after the user requested broad age, sex and socioeconomic statistics linkable to ballot locations across years. This is an extension of the historical database, not a new forecasting model. The existing six-election inputs and forecast outputs remain unchanged.

## What was obtained

The supplied [2022 census site](https://census.cbs.gov.il/he) is a census snapshot, not an annual 2015–2022 series. Its linked CBS workbooks provide locality/statistical-area measures and broad geographic comparisons. Complementary official annual population and socioeconomic releases supply historical context.

| Data | Reference years | Actual integrated coverage |
| --- | --- | --- |
| Population, male/female counts and broad age bands | 2018 | 1,218 locality aggregates from official GIS reporting areas |
| Population and age bands by sex | 2019, 2020, 2021 | 10,959 locality/year/sex records; 1,218 / 1,217 / 1,218 total-population profiles |
| Census age/sex/household profiles | April 2022 | 1,185 locality profiles, plus published statistical-area records |
| Census broader geography and social/economic measures | April 2022 | Selected locality/statistical-area workbook plus big-locality, small-locality and district/subdistrict/natural-area sheets of broad workbook; 5,085 source records and 1,132 variable definitions in total |
| Socioeconomic index, rank and cluster | 2015, 2017, 2019, 2021 | 1,183 / 1,191 / 1,196 / 1,195 locality records; 4,765 total |
| Locality-to-district/subdistrict and population catalog | 2017–2022 | 8,896 locality/year rows |

Nineteen source responses, raw workbooks/API JSON/2018 GIS ZIP and field-definition PDF are archived with SHA-256. There are 56,714 retained raw tabular rows. Frozen CBS inputs/source archives total approximately 28.2 MB. No individual respondent/voter information is collected. Source-specific CBS rights are retained; attribution does not assert a new license over CBS material.

Age profiles for 2015–2017 are **not collected** in this extension; socioeconomic 2015 does not substitute for 2015 age data. No annual socioeconomic interpolation or census-age backcasting is performed. A 2016 government locality resource was inspected but lacked the district fields needed here and is not integrated. Failed legacy annual URLs sometimes returned HTML with HTTP 200; content signatures are checked so these are not mistaken for workbooks. The non-CBS-owned 2018 ArcGIS mirror discovered during research is not an input; the 2018 data comes from CBS's own ZIP.

## How locations are linked

1. CEC election rows contain a locality code (`סמל ישוב`). Normalize its integer-like representation to a string and match the CBS locality code.
2. Attach a selected reference year's locality profile. Both demographic reference year/date and election date remain visible.
3. Use the **same reference year's** CBS locality catalog for district/subdistrict grouping. Do not silently reuse a later district classification.
4. Ballot rows inherit their locality's context through the same code. This is a **locality-level association**. Ballots in one city receive the same city profile.

No address-to-neighborhood/statistical-area crosswalk was constructed. A polling building's neighborhood does not prove that its assigned voters live in that neighborhood. Ballot numbers are not assumed to identify a stable population across elections. Code-based historical matches are not certified historical-boundary harmonization; locality splits/mergers and unmatched codes remain review items.

Special or unlocated ballots are not assigned to a locality, district or demographic group. The CEC source codes vary: 0 in 2015, 99999 in April 2019, and 9999 in September 2019–2022. Later rows explicitly carry the external-envelope label; the 2015 row has a blank name. Residential origin is unavailable in these tables. The coverage report distinguishes national-vote coverage from coverage of votes already located to ordinary localities. Retrospectively linking 2022 census codes to old elections measures linkage coverage only; it does not make 2022 features available for forecasting those elections.

## Tables and views

All are inside the same generated `output/elections.sqlite` file.

| Table/view | Row and main fields |
| --- | --- |
| `cbs_sources` | One source response: URL, retrieval date, hash, type, rights and availability flag |
| `cbs_locality_geography` | One locality/year: locality code/name, district/subdistrict, published population, source |
| `cbs_population_2018` | One locality: population, male/female counts, JSON age bands, contributing-area count and aggregation method |
| `cbs_age_sex` | One locality/year/sex: population, JSON age bands and aggregation method |
| `cbs_socioeconomic` | One locality/reference year: index value, cluster 1–10, rank, **rank scope**, index population and source |
| `cbs_census_records` | One published geographic record: locality/statistical-area/quarter/district identifiers, original variable values in JSON `attributes` |
| `cbs_census_variables` | One source/sheet/variable: original internal code and readable label |
| `cbs_raw_rows` | One original tabular row: source, sheet/layer, row number and full values/attributes |
| `cbs_locality_profiles` | Derived convenient profile for each locality/year: population, available male percentage, 0–19/65+ percentages and published 2022 age medians |
| `cbs_locality_vote_shares` | One locality/election/list: votes, all valid votes and vote share; includes zero-vote list rows |
| `cbs_locality_election_context` | Join vote shares to every available locality profile, with explicit demographic year, geography vintage, future-reference and descriptive-only flags |
| `cbs_ballot_locality_links` | One ballot/profile-year link, explicitly labeled `locality context only` |

Examples of available census codes: `age_median`, `m_age_median`, `w_age_median`, `age0_19_pcnt`, `age65_pcnt`, `sexRatio`, `size_avg`, `Vehicle0_pcnt`, `own_pcnt` and `rent_pcnt`. Broader sheets also retain education, labor and economic fields; inspect `cbs_census_variables` for their actual definitions, populations and units before use. Availability and detail differ by sheet and geography. The original English selected workbook confusingly calls its locality-name variable `LocNameHeb`; its values are English. These values stay raw, but are not exported as Hebrew names in the profile view. Original Hebrew names remain available from CEC/annual CBS catalogs.

## Meaning, dates and aggregation

**Area characteristics do not identify who voted for a party.** A city with an older population and a high party vote share establishes a geographic association. It does not establish the age of that party's voters. CBS resident populations include children and residents who may not be eligible Knesset voters. They are not interchangeable with the electoral register or actual turnout denominators. The source classifies sex; no additional gender identity variable is inferred.

**Median is not mean.** CBS's April 2022 broad workbook directly reports Central District median age 33, male median 32 and female median 35. These are published district medians, not averages of city medians. No exact mean age is inferred from five-year age bands or open-ended oldest groups, and no exact male mean for 2018 is claimed. Averaging locality medians would not yield the regional median.

**Reference year is not publication year.** The census workbooks are served under a 2025 publication path and cannot be treated as known before the 2022 election. The 2015 socioeconomic workbook is under the 2019 publication path, the 2017 rural release explicitly says replaced March 4, 2021, the 2019 final tables are under a 2023 path, and the 2021 index is from a later official map. A directory year alone is not a verified exact release date. All CBS sources remain `historical_availability_verified=false`. Context views are `descriptive_only=1`; no automatic historically eligible feature matrix is created. Even a prior year-end figure needs release/revision verification before a backtest cutoff. Future reference dates are flagged separately from unknown publication availability.

**Preserve source units and suppression.** Census percent fields are on the 0–100 scale. Annual population bands are counts, with raw suppression markers retained; unknown cells remain null. The 2018 GIS readme describes 2011 statistical-area identifiers and boundaries at the end of 2017. Some areas are unified for publication, with other polygons only referencing them; only populated reporting records are aggregated. Annual workbooks change format: 2019 has separate sex sheets and published city totals; 2020/2021 have sex rows, an extra population-group column in mixed cities and a combined 65+ band. The parser follows actual headers. Published locality totals take precedence; otherwise unique reporting areas for the total population group are summed. City totals and their subdivisions are never added together. Raw rows and aggregation method/count remain traceable.

Independent population/sex/age estimates and small-area rounding can differ. For example, 383 of the 2018 locality GIS population sums differ from the independently published locality-catalog figure, often by one person. They are not overwritten to force agreement. Missing components make the corresponding aggregate age/sex measure unavailable rather than silently zero-filled. Consequently a regional age summary may cover fewer residents than a regional sex summary; the report exposes each denominator. Its 2018 Central District 65+ figure has limited complete-measure coverage and must not be described as an estimate for the entire district.

**Aggregate the correct numerator and denominator.** Regional party share is `100 * SUM(party_votes) / SUM(valid_votes)`, retaining localities with zero party votes. It is not the unweighted average of locality percentages. Demographic percentages use population-weighted averages over only localities with that measure, with that same cohort's population in the denominator. Do not repeat population once for every ballot/party and then sum it. Do not add locality and ballot-level results together.

**Socioeconomic position is a composite area measure.** The index combines demographic, education, living-standard and employment characteristics; cluster 1 is low, 10 high. Clusters are not equally sized population deciles or individual income brackets. Rank populations differ between tables (all localities, local authorities, or localities within regional councils); `rank_scope` prevents treating all ranks as one nationwide scale. Classification year/method changes and local-boundary changes need review before interpreting changes as social mobility. No missing index is filled from its regional council automatically.

## Reproduce and query

```sh
python scripts/build_database.py
python scripts/cbs_report.py
python -m unittest discover -s tests -v
```

No packages/network needed for the frozen build, queries or reports. The workflow publishes the expanded SQLite database, coverage and `cbs-linkage.json` in `historical-election-database`. The new full coverage manifest and descriptive report are frozen under [reports/cbs-2026-10-21](../reports/cbs-2026-10-21/); the earlier D001 manifest is preserved. Locality code 3000 remains a string, not a shared historical party identifier.

Example: pair **2018 demographics with April 2019 votes** in the Central District (code 4). This is a deliberate descriptive pair, not a certified historical feature policy:

```sql
SELECT locality_name_he, demographic_year, election_date,
       population, male_percent, age65_plus_percent, vote_share_percent
FROM cbs_locality_election_context
WHERE knesset=21 AND demographic_year=2018
  AND district_code='4' AND ballot_code='מחל';
```

For a socioeconomic comparison, explicitly choose the index's year rather than implicitly selecting the newest available table:

```sql
SELECT v.locality_name_he, v.knesset, s.reference_year AS index_year,
       s.cluster, s.index_value, v.vote_share_percent
FROM cbs_locality_vote_shares v
JOIN cbs_socioeconomic s USING(locality_code)
WHERE v.knesset=25 AND s.reference_year=2017 AND v.ballot_code='מחל';
```

The first report example finds 319,095 Likud votes / 1,121,237 valid votes = **28.4592%** across 235 matched Central District localities in April 2019. The 2018 population profiles for that matched cohort total 2,192,404. The male-share measure is available for 2,050,825 of those residents (234 localities), giving **49.5010% male** within that subset. These are different population/vote denominators, not a claim that 28.46% of men voted Likud. The sample is geographically matched; historical publication eligibility is unverified.

Online refresh is optional: `scripts/collect_cbs.py` uses requests/openpyxl and GDAL for one official 2018 geodatabase. It ran using the existing QGIS Python environment; no GDAL installation is needed for normal cross-device use. A refresh requires a fresh cache and a deliberately new version/date; the current script reuses `tmp/cbs` and writes the frozen directory. Review source-format changes, rights and diffs, then regenerate the new manifest/report. No need to install a heavy GIS stack merely to use this database.

## Primary sources and next work

- [CBS Census survey and download links](https://www.cbs.gov.il/en/Surveys/Pages/Population-Census.aspx): selected data and broad-geography workbooks.
- [CBS official geographic layers](https://www.cbs.gov.il/he/cbsNewBrand/Pages/geo-layers.aspx): 2018 demographic ZIP and field definitions. Later 2019/2020 GIS layers were inspected but not duplicated into the integrated annual series.
- [CBS population components publication](https://www.cbs.gov.il/he/publications/Pages/2017/אוכלוסייה-ומרכיבי-גידול-ביישובים-ובאזורים-סטטיסטיים-2017.aspx): annual age/sex workbooks; the page is currently labeled 2014–2024, not evidence of original publication vintage.
- [Government CBS locality-code catalog](https://data.gov.il/dataset/localities-in-israel): annual geographic crosswalks, queried through the public API.
- [CBS socioeconomic topic/map](https://www.cbs.gov.il/he/subjects/Pages/מדד-חברתי-כלכלי-של-הרשויות-המקומיות.aspx): official 2021 map links to CBS-owned GIS services; older workbook URLs and exact response hashes are in `cbs_sources`.

Next: review original annual source availability/revisions, fill the 2015–2017 age gap if useful, investigate unmatched localities and changed boundaries, and define a small historically available feature panel. Neighborhood-level ballot matching would require an independently validated assignment crosswalk. No model, partisan demographic assumption or individual voting inference was added.
