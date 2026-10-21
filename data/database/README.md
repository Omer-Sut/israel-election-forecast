# Frozen database inputs — October 21, 2026

Read [the database guide](../../docs/historical-database.md) for coverage, schema, provenance, rights and limitations. Build using `python scripts/build_database.py`; generated SQLite stays in `output/` and is downloadable from GitHub Actions.

`*.jsonl.gz` are canonical UTF-8 JSON Lines input tables. `cec*-*.csv.gz` are lossless projections of the official government API response fields, excluding its artificial `_id`. `raw-sources/` preserves compressed original Wikipedia HTML, CEC national HTML and official geographic API JSON responses. Raw-response hashes in `sources.jsonl.gz` must match those archived bytes after decompression. Other raw files (INES microdata and non-CC articles) stay outside the public repository; their provenance/hashes and derived numerical tables are preserved.

Attribution: Central Elections Committee via data.gov.il (`Other (Open)` metadata); Israel Democracy Institute (2015 final seat/name/turnout transcription); Wikipedia contributors (poll-index table adaptations, CC BY-SA 4.0); Israel National Election Studies (variable/value dictionaries and derived unweighted marginal counts). Source-specific rights remain distinct; no blanket repository/data license is asserted.

These are research inputs, not a ready-to-fit forecasting panel. Bulk poll dates/lineups/duplicates and INES historical availability need review. Existing audited poll snapshots remain separate and unchanged.
