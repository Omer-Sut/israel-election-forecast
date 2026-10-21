# CBS aggregate geographic snapshot

Read [the CBS integration guide](../../docs/cbs-demographics.md) before use. Canonical UTF-8 compressed JSONL tables extend the same historical SQLite database. `raw-sources/` preserves 19 source responses; response hashes and URLs are in `cbs_sources.jsonl.gz`. Sources: Israel Central Bureau of Statistics, including its official government-data catalog and official linked GIS map. Source rights remain distinct; no new blanket data license is asserted.

Age/sex profiles: 2018–2022. Socioeconomic reference years: 2015/2017/2019/2021. Locality geography: 2017–2022. These are locality-level population characteristics and original census geographic records, not individual voter characteristics. Historical release availability is unverified; no backcasting or automatic feature eligibility is implied.

`python scripts/build_database.py` includes these tables automatically when this snapshot directory is present. `python scripts/cbs_report.py` produces descriptive examples with visible reference years, missingness and coverage. Both use the standard library offline. Collection-only dependencies and source-format caveats are documented in the guide.
