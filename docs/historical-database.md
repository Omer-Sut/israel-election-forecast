# Historical research database

Snapshot: October 21, 2026. User requested a substantial dataset first, covering every election back to the 20th Knesset (2015), before further model selection. This collection does not change or retrain the existing baseline or its audited pilot backtest.

## Coverage

| Knesset | Election | All national lists | Main-table pre-election poll candidates | Locality records | Ballot-box records |
| --- | --- | ---: | ---: | ---: | ---: |
| 20 | 2015-03-17 | 25 | 176 | 1,196 | 10,414 |
| 21 | 2019-04-09 | 43 | 127 | 1,214 | 10,765 |
| 22 | 2019-09-17 | 32 | 68 | 1,214 | 10,901 |
| 23 | 2020-03-02 | 30 | 94 | 1,214 | 11,179 |
| 24 | 2021-03-23 | 39 | 169 | 1,215 | 12,926 |
| 25 | 2022-11-01 | 40 | 156 | 1,216 | 12,545 |

Total: 209 national list results, 75,999 geographic records, and 899,195 positive geographic/list vote counts. Sparse vote rows omit zeros; a missing list in a geography means zero only within that election's complete official list inventory. Locality and ballot tables represent the same votes at two granularities: never add them together. Special/double-envelope aggregate rows are retained, including code 0 and blank locality names; not every geographic record is an ordinary municipality or physical station. Ballot and locality identifiers remain strings.

Poll extraction retains 167 tables, 2,171 source rows, 1,197 date-bearing poll/reference/scenario records and 16,150 measurement cells. The 790 main-table candidates above are **not 790 verified independent published polls**. They include polling between elections as well as formal campaign periods. Alternative-lineup tables, student/other context tables, election outcomes, and exit/reference rows are retained separately. Dated events without numeric measurements remain source context, not polls. Dates sometimes describe fieldwork rather than publication. All bulk `publication_date` values are null; `date_proxy` is a parsed source date endpoint. Retrospective Wikipedia snapshots are not contemporary archived releases.

## Build and use on any computer

```sh
python scripts/build_database.py
python -m unittest discover -s tests -v
```

Python 3.12, no packages or network required. Outputs: `output/elections.sqlite` and `output/elections.coverage.json` with table counts, coverage and hashes of every canonical input. The SQLite file is generated, not committed. The small compressed source tables and inputs are in Git at [data/database](../data/database/); they are sufficient to rebuild offline.

For online execution, open [GitHub Actions](https://github.com/Omer-Sut/israel-election-forecast/actions), run **Reproduce preliminary baseline**, then download **historical-election-database** from a successful run. Artifacts expire after 30 days; the committed inputs remain rebuildable. A GitHub Codespace can run the same commands. This is a portable versioned research snapshot, not a multiwriter database server; make changes through branches and pull requests.

```python
import sqlite3
db = sqlite3.connect('output/elections.sqlite')
print(db.execute('SELECT knesset,turnout FROM elections').fetchall())
print(db.execute('SELECT * FROM national_results WHERE knesset=25 ORDER BY votes DESC').fetchall())
print(db.execute('SELECT variable,label FROM ines_variables WHERE study_year=2022').fetchall())
```

## Tables and interpretation

| Table/view | Key and contents |
| --- | --- |
| `sources` | `source_id`; exact URL, retrieval day, downloaded response SHA-256, bytes, rights notes |
| `elections` | `knesset`; date, electorate, ballots, valid/invalid, published turnout and source |
| `official_lists` / `national_results` | `(knesset,ballot_code)`; all lists including zero-seat lists, original Hebrew names where available, votes, published percent, final allocated seats; view adds election date |
| `geographies` | `geo_id`; election, granularity, source, original nonparty fields in JSON `attributes` |
| `geography_totals` | Friendly view of locality names/codes, ballot numbers and turnout/count fields; unusual original attributes remain in `geographies` |
| `geographic_votes` | `(geo_id,ballot_code)`; positive votes; join geography for election and granularity |
| `poll_tables` | `table_id`; source, election, source heading and main/context classification |
| `poll_rows` | `row_id`; original expanded cells, physical cell origins, source row number and linked citation URLs |
| `polls` | `poll_id`; linked row/table, election, original date and date proxy, metadata array, audit/status flags |
| `poll_values` | `(poll_id,value_index)`; source list/combined label, raw value, parsed value/unit and column role |
| `campaign_poll_candidates` | Convenient main-table, pre-election, non-result/non-explicit-exit candidate view; **not a backtest-ready feature table** |
| `poll_seat_diagnostics` | Numeric seat sums and unparsed-cell counts; diagnostic only, not certification of a complete true-lineup poll |
| `ines_studies` | Six study files, respondent/column counts, design and unverified historical availability flag |
| `ines_variables` | `(study_year,variable)`; labels, dtype, observed count, cardinality, frequency eligibility |
| `ines_value_labels` | Original code-to-label dictionary; retain refusal/don't-know and special missing codes |
| `ines_frequencies` | Unweighted one-variable counts; system-missing explicit, cells below five suppressed (`count=null`) |

Election-specific ballot codes are the official result keys. They are not stable party identities across years. Poll labels are deliberately not forced into those codes: alliances, splits, hypothetical scenarios and omitted lists require reviewed mappings. Shared HTML cells spanning several party headers produce one combined measurement, not duplicated seats. Below-threshold percentages remain percentages; strings such as `–`, `<3.25%` or parenthesized percentages remain raw/unparsed rather than being guessed as zero seats. Numeric bloc/lead/comparison columns are flagged separately where their headers identify them; unresolved column roles still require review. Do not assume all parsed numeric cells are party seats or every row sums to 120.

The original-source-audited 12-record pilot stays at [data/snapshots/historical-2026-10-21](../data/snapshots/historical-2026-10-21/). It is not appended into the bulk table, avoiding automatic duplication; its audit tier remains higher. Future integration should link each audited release to its bulk row explicitly.

## Official results provenance and transformations

[CEC 2022 national results](https://votes25.bechirot.gov.il/nationalresults) and the equivalent `votes21` through `votes24` pages supply all 2019–2022 national rows and totals. The CEC's 2022 direct locality/ballot CSVs were inspected; the integrated six-election geographic collection uses the same official CEC archive through [data.gov.il votes-knesset](https://data.gov.il/dataset/votes-knesset). Its CKAN metadata declares **Other (Open)**. Direct archive download URLs returned 403; public `datastore_search` endpoints succeeded. Each request's resource UUID, URL, hash and retrieval day are recorded. A 32,000-row request is accepted only if returned rows equal API `total`; silent truncation fails.

`cec*-*.csv.gz` preserve the returned fields/values as CSV, excluding CKAN's artificial `_id`. They are a CSV projection of API JSON, not byte-identical original CEC files. Party columns after `כשרים` are normalized to sparse positive vote rows; all other fields are retained in geography JSON. Full JSON responses are hashed and archived in `raw-sources/`; hashes apply to those downloaded responses, not the transformed CSV. The compressed canonical JSONL tables are the exact versioned offline inputs, separately hashed by the builder.

The old 2015 CEC national site could not be retrieved reliably. [Israel Democracy Institute's final 2015 table](https://en.idi.org.il/israeli-elections-and-parties/elections/2015/) supplies final seats, English names, rounded shares and national totals. Votes match the official government geographic data list-by-list; unique vote totals link the 25 names to official ballot codes. Hebrew full names for 2015 remain null. The 2015 seat vector is **secondary-source transcribed**, not directly audited from a final CEC allocation document. Its published turnout is 72.3% (one decimal); invalid ballots=total minus valid, 43,854. Later CEC turnout has two decimals. Preserve published precision.

## Poll provenance and reuse

Sources are Wikipedia's election-specific opinion-polling indexes for [2015](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2015_Israeli_legislative_election), [April 2019](https://en.wikipedia.org/wiki/Opinion_polling_for_the_April_2019_Israeli_legislative_election), [September 2019](https://en.wikipedia.org/wiki/Opinion_polling_for_the_September_2019_Israeli_legislative_election), [2020](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2020_Israeli_legislative_election), [2021](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2021_Israeli_legislative_election) and [2022](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2022_Israeli_legislative_election). Attribution: Wikipedia contributors; table transcriptions adapted/normalized here under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Each linked page's **View history** supplies contributor history. Publisher citation links are retained per row where present. Other sources retain their own rights; this attribution does not license the entire repository.

Table-position classification is explicit in the collector and tied to this frozen HTML version; a changed page layout needs review. Header rows, year sections, date ranges and merged cells are preserved. ISO sort attributes provide missing year hints (not replacement month/day values); original sort attributes are retained because some conflict with displayed dates. Original publisher/sample information is sometimes absent or bundled in one metadata cell. No historical publication date, sample size, fieldwork start, weighting, independence or original-source accuracy is fabricated. Re-publications and alternative scenarios can share a poll; deduplicate only after audit. This is broad discovery coverage, not a claim that every poll ever published has been collected.

## INES integration and safe use

The supplied [INES data site](https://socsci4.tau.ac.il/mu2/ines/data/) and [all-data page](https://socsci4.tau.ac.il/mu2/ines/data/our-data/) expose Stata/SPSS data and questionnaires. Downloaded and read: 2015 (1,595 rows/214 variables), combined April–September 2019 (1,614/294), 2020 (873/106), 2021 (1,816/141), 2022 (1,585/160), and optional off-cycle 2025 (1,588/132). The April/September file is a four-wave **panel**, not four independent samples. File rows do not equal every wave's achieved sample.

Integrated: 1,047 variable records, 8,377 value-label entries and 8,614 unweighted frequency rows. These make attitudes, past voting, vote intention, demographics and turnout variables discoverable. A numeric variable with 2–60 observed values is eligible for marginal frequencies unless its name signals identifiers/interview/date/weights; no respondent rows or free text are published. Counts below five are suppressed. Numeric questionnaire missing/refusal codes remain labeled categories; system missing is separately flagged. Frequencies are descriptive and unweighted, with no population estimates or causal interpretation. Code-label mapping uses pandas' Stata reader metadata without categorical conversion because original label texts can repeat.

No explicit microdata redistribution license was verified. Raw `.dta` downloads stay ignored rather than copied into this public repository. Source URLs/hashes and the collector allow collaborators to obtain the same public files themselves. Dictionaries/derived aggregate counts are attributed to INES; no license over underlying data is asserted. Consult original questionnaires and terms before reuse/publication. No multiway respondent profiles are released.

Pre/post waves and historical release availability must be reviewed before extracting features. Post-election turnout and vote reports cannot predict that election. No file is currently certified as available at a historical forecasting cutoff. Unweighted summaries are not ready-made features; election-specific party coding and wave/weight definitions need review. The 2025 study is auxiliary, not a seventh completed election outcome.

## Collection, validation and next work

For an explicitly reviewed refresh, install `requirements-database-collection.txt`, run `python scripts/collect_database.py`, then rebuild/test/review the diff. **The collector reuses `tmp/database` cache and writes the frozen canonical directory**; use a fresh cache/versioned snapshot for a new retrieval date and change its recorded date deliberately. Do not silently overwrite this snapshot or label an old cache as freshly downloaded. pandas/lxml/requests are optional collection tools; collaborators need none of them to query/rebuild the frozen database. The collector was run with pandas 3.0.5/lxml 6.1.1; the Stata metadata mapping is guarded and version-sensitive.

Builder checks: SQLite integrity, unique natural keys, relational orphans, nonnegative votes, ballots=valid+invalid, national seats=120, published-turnout precision, every party's national votes versus each geographic granularity, and every geographic row's party sum/ballot identity. Seven new integration tests additionally cover poll-date audit boundaries, merged party cells, the 2020 Blue & White column and INES aggregate handling. These checks validate ingestion/reconciliation, not poll truth or forecasting skill.

Next: review candidate rows' original references around fixed backtest cutoffs, establish actual publication/update dates, resolve independent polling groups and election-specific lineups, and freeze a model-ready panel. Select INES features only after inspecting wave definitions, weights and historical availability. Model comparison comes after that review; six elections remain six independent national targets regardless of how many poll or precinct rows exist.
