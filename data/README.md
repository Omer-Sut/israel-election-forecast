# First audited input snapshot

Historical update: [snapshots/historical-2026-10-21/](snapshots/historical-2026-10-21/) now contains 12 audited 2021/2022 poll records and official seat/turnout targets for the [historical backtest pilot](../docs/historical-backtest.md). Its sources, residual derivation, missing metadata and historical-vintage limitations are documented separately. The current 2026 snapshot below remains unchanged.

`snapshots/polls-2026-10-21.json` contains six factual poll transcriptions from five declared polling groups. These are seat projections, with separate below-threshold percentage measurements. The newer Walla/Lazar release replaces the older Maariv/Lazar release; both remain traceable in the snapshot. Selection is the latest **audited** publication per group in a 14-day window, not a claim of exhaustive coverage.

## Source audit

| Release | Positive seats checked against | Role |
| --- | --- | --- |
| N12, October 19 | Original article's complete seat list and metadata | Active |
| Channel 14, October 19 | Original publisher's complete seat list and metadata | Active; possible later release unaudited |
| Channel 13, October 19 | Original dated graphic, visually inspected | Active; source-body conflict retained |
| Walla, October 20 | Original article, including fieldwork/sample metadata | Active; latest audited Lazar group release |
| Zman / Times of Israel, October 15 | Commissioning group's article, first poll described | Active; avoid confusing it with the other poll in the same article |
| Maariv / Lazar, October 16 | Pollster-authored report page 1, visually inspected, with sibling publication corroboration | Archived by group selection |

Each record contains the source URL, publication date, available fieldwork/sample metadata, original source-list keys, measurements, and audit decisions. Unknown metadata is null. The common review date is recorded; per-request second-level timestamps were not captured. Full article prose/images are not redistributed. Numerical transcriptions preserve attribution and do not claim a new license over publisher material.

Channel 13's graphic shows Likud=18 and a complete allocation summing to 120. Its article body says 17 and omits UTJ. We use the graphic consistently, with the conflict disclosed. The graphic's URL and downloaded-file SHA-256 (`ef9b577719f8852da394f345de34e1375d4bfa6d6e32db9455769558569c90cd`) are recorded in the poll snapshot. A future publisher correction should trigger an explicit new snapshot, not a silent edit.

Kan's page returned no readable poll text, and the original October 20 i24 Telegram post could not be retrieved. Several additional October 20 releases were discovered through aggregators but are not audited inputs. See `not_ingested` in the snapshot. Next data collection should address these coverage gaps, not treat the current five-group sample as all available evidence.

## Mapping and zeros

[The mapping configuration](../config/poll-mappings.json) preserves current Joint List and Religious Zionism/Zehut labels and maps them to the form slots explicitly. The user accepted proceeding with Joint List -> Hadash-Ta'al as a form-label assumption, not an assertion of historical identity. Other allocated individual-list seats aggregate only at export; below-threshold vote shares are never pooled into one qualifying party.

Zero seats for omitted form fields follow only from a source audited as a complete 120-seat allocation. Missing percentages remain missing. This is different from treating an unmentioned party as zero support.

## Official historical reference

`snapshots/results-2022.json` preserves the official 2022 totals, all seat-winning lists, and selected below-threshold lists. Its vote table is partial and is labeled accordingly. Old alliances keep election-specific IDs. Only official 2022 turnout is used in this first baseline; the seat outcomes are saved for later validation and are not treated as current-party priors.

## Reproduction and updating

Inputs are small, committed, and usable without live scraping. A new collection should create a dated/versioned snapshot, preserve old records, reconcile source conflicts, and update `config/baseline.json`. Generated `baseline.json` includes SHA-256 hashes of each consumed input/configuration and the implementation file. It should never be reported as a historical backtest merely because historical outcome data is present.
