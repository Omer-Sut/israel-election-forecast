# Current project state

Last updated: October 21, 2026 (six-election research database assembled).

## Latest handoff — database first

The user now explicitly requests a substantial historical dataset before further model selection. The completed collection covers all six 2015–2022 elections: 209 national list outcomes, 75,999 geographic records and 899,195 positive geographic vote cells. Both locality and ballot-box totals reconcile to national party votes for every election. All final seat vectors sum to 120. The 2015 votes use official government data; final seats/names/turnout use IDI's secondary table because the old CEC national page is unavailable.

Broad poll indexes retain 2,171 source rows and 1,197 date-bearing poll/scenario/reference records; 790 are main-table pre-election candidates. These are lower-tier index transcriptions, not audited independent releases. Publication dates remain null; party mappings, duplicates, alternative scenarios and date provenance need review before backtesting. No existing forecast, audited snapshot or pilot score was changed.

INES integration covers six files (2015, combined 2019, 2020, 2021, 2022, auxiliary off-cycle 2025): 1,047 variable records, 8,377 code labels and 8,614 unweighted marginal-frequency rows. Raw respondent data is excluded from the public repo because explicit redistribution terms were not verified. Frequencies suppress counts below five, preserve special codes, and are not population estimates or certified pre-election features.

Run `python scripts/build_database.py` with Python 3.12, no packages/network, to obtain `output/elections.sqlite` plus hashed coverage. Frozen compressed inputs and raw public official/Wikipedia source archives are committed under `data/database/`. Read [historical-database.md](historical-database.md) for schema, examples, rights, coverage and exact audit limits. GitHub Actions now builds a downloadable `historical-election-database` artifact. Local/hosted validation and publication evidence for this branch are recorded below after verification.

Current work started from clean synchronized main at 7238f4c on `feat/historical-database`. All 23 local tests pass, including seven new database integration checks. Both frozen forecasting reports reproduce (normalized Windows text newlines), documentation links/fences and Git whitespace checks pass. Database inputs/source archives total approximately 12.2 MB; no generated SQLite or raw INES respondent data is committed.

Implementation `f81a22c4339c23fe908414780b5a1ae08d2644ae` was pushed and verified through [PR #9](https://github.com/Omer-Sut/israel-election-forecast/pull/9). [Hosted run 39602185506](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39602185506) completed successfully at 12:46:16 UTC: all 23 tests, offline database build/reconciliation, exact coverage/hash manifest, and both unchanged forecast report comparisons passed. Artifact `historical-election-database` (ID 12346532323, approximately 19.9 MB compressed) was verified available and unexpired. This handoff records that verified implementation run; inspect actual Git/PR state for subsequent documentation commits and merge status. A successful artifact can be downloaded from the run page; authentication may be needed. Agent time from first recorded research timestamp to hosted success was 26m32s, not measured user hands-on effort.

Next: audit a useful panel of original releases around fixed cutoffs, review election-specific mappings and INES wave/weight/availability metadata, then compare models. The prior two-election pilot below remains a limited reference, not evidence that the bulk database has been evaluated.

## Goal and constraints

Forecast the 26th Knesset competition outputs in English, using approximately eight total hands-on hours, lightweight CPU methods, shared online execution, and continuous documentation. User's hands-on effort is not the same as agent/tool wall-clock time; earlier setup was not timed. Do not reset the budget each session.

Repository: https://github.com/Omer-Sut/israel-election-forecast

Collaboration access update (October 21): the user authorized adding `IdoRavid` with all permissions. GitHub rejected an `admin` invitation for this personal-account repository. A `write` invitation was sent and verified pending; access awaits IdoRavid's acceptance. Do not claim admin rights or accepted membership. See CONTRIBUTING.md and inspect live GitHub access for later changes. No repository transfer/migration was authorized or performed.

## Earlier implemented forecasting work (unchanged)

- Preserved and reviewed the original Hebrew PDF and the user-transcribed form. Contract: 14 named-list seat fields plus combined other qualifying parties, total 120, and turnout within [40.00, 100.00] percent inclusive.
- Recorded the user's accepted current Joint List -> Hadash-Ta'al form mapping as an explicit assumption, preserving historical distinctions. Current Religious Zionism/Zehut uses the Religious Zionism slot with its combined source label retained.
- Collected six factual, original-source-audited poll records, selecting five latest audited polling groups. Older Maariv/Lazar is replaced by newer Walla/Lazar, avoiding double counting. This is not exhaustive latest-poll coverage.
- Checked Channel 13's original graphic: Likud=18, UTJ=7, full total=120. Its body says Likud=17; conflict is retained, with the graphic used consistently. Original graphic URL/hash are recorded.
- Stored partial official 2022 results with election-specific IDs. Turnout persistence reference is 70.63%; current self-reported voting intention remains a separate diagnostic.
- Implemented standard-library Python 3.12: latest-group selection, explicit mappings, rounded-mean reference, empirical L1 consensus via a small dynamic program, output validation, hashes, and omission sensitivity.
- Generated durable preliminary reports at reports/baseline-2026-10-21/. Both outputs pass form arithmetic. They are not final, historically validated, or proven electorally attainable forecasts.
- Added 12 original-source-audited historical poll releases, three groups per election and horizon, plus official 2021/2022 targets and earlier-election turnout references. Historical list identities remain separate; a documented N12 National Unity residual=13 and unknown metadata are preserved.
- Implemented `scripts/backtest.py` using the unchanged baseline functions, 14-day window, six-day and day-before cutoffs. Predictions are generated before targets are loaded. Per-list errors, source selection/exclusions and input/code hashes are in `reports/backtest-2026-10-21/`.
- Sixteen meaningful software checks pass locally, including seven new tests for time boundaries, historical identity, target separation and scoring. A retrospective two-election backtest has run; probability calibration has not.
- Configured and verified a small GitHub Actions CPU workflow: all tests and byte-for-byte report reproduction passed in hosted run 39572969093 for implementation commit aee2f11. Run: https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39572969093 . A notebook is deferred to avoid duplicate setup.

## Important results and limits

The user requested an explanation of the autonomous baseline, then documentation/research, and subsequently authorized the historical backtest. Read [research-agenda.md](research-agenda.md) for feedback and the broader agenda, [forecasting-research.md](forecasting-research.md) for the literature/data inventory, and [historical-backtest.md](historical-backtest.md) for the newly executed pilot. The existing 2026 configuration, poll snapshot, baseline code and numerical forecasts remain unchanged. No alternative model or war-effect calculation has run.

Historical results (total absolute seat error): at T-6, 2021 rounded mean=24/L1=22 and 2022=12/12; at T-1, 2021=20/20 and 2022=12/12. Equal-election means are 18/17 at T-6 and 16/16 at T-1. Turnout persistence misses by 4.08 pp in 2021 and 3.19 pp in 2022. Both seat methods falsely predict Meretz representation in 2022 and materially miss Blue and White/New Hope in 2021. Two elections and a convenience source panel do not establish a final ranking; the four cutoffs are not four independent elections.

Known historical publication/update dates are enforced; separately authenticated historical archive copies were not obtained. This is a retrospective pilot, not a certified reconstruction of every historical information set. Three-group coverage differs by election and omits some known releases. The repeated-election-period sensitivity needs more elections; only 2021 currently represents 2019-2021.

Both PDF pages were rechecked: the target is interpreted as final allocated seats after threshold exclusion, using the stated final official outcome. Readable official 2022 outcomes corroborate this. Official-domain indexed text supports 3.25% of valid votes, and Knesset research notes a theoretical three-seat result rather than a universal four-seat minimum. Full operative 2026 rules/agreements remain unverified because direct official rule retrieval was blocked; no allocator has been built.

Average absolute disagreement with the input polls: rounded mean 14.4; L1 consensus 12.4. These are in-sample descriptive objectives, not forecast accuracy. Omitting a group changes L1 consensus by 4-8 total absolute seat difference. Only form arithmetic is constrained; no official vote-to-seat allocator is implemented. Full vote shares, surplus agreements, predictive error calibration, and support redistribution after reported Blue and White withdrawal are not modeled.

Kan and several October 20 releases (including i24/Direct Polls and Channel 16) remain unaudited. Keep them on the collection list. Do not call the five-group sample all current evidence.

## Publication and reproduction

Baseline PR #5 was merged; before this research update, main was clean and matched origin/main at ec4396e. Research documentation is published through [PR #6](https://github.com/Omer-Sut/israel-election-forecast/pull/6), branch docs/research-methods-and-user-feedback. Initial research commit fcd50c8 was verified on the remote; [hosted run 39580440662](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39580440662) passed all baseline tests and exact report reproduction. This confirms the existing baseline still reproduces, not predictive validation of any researched candidate. This handoff records that verified evidence; inspect Git/PR state for subsequent commits and merge status.

Earlier research validation passed local links/fences/whitespace and hosted baseline reproduction. The prior historical pilot used `feat/historical-backtest`, starting from clean synchronized main at 85fab76. Its 16-test run and initial historical generation passed, and the workflow was extended to reproduce both frozen reports.

Historical implementation `c591c7031d6aebda9a63c38fc4dffabd58ca9d6a` was pushed and verified. [Hosted run 39596526287](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39596526287) passed all 16 tests, byte-for-byte comparison of original baseline and historical reports, and artifact upload, completing at 12:03:15 UTC. This is reproducibility evidence alongside the reported retrospective scores, not proof of a future model ranking. Work is published through [PR #8](https://github.com/Omer-Sut/israel-election-forecast/pull/8); inspect actual Git/PR state for later handoff commits and merge status.

Local historical reproduction is byte-identical. The unchanged baseline matches after newline normalization on Windows; its legacy writer's CRLF behavior was not changed. New historical text uses LF for portable hashes. Documentation checks passed across 17 Markdown files and the method draft remains 286 words; Git whitespace checks passed.

Run from a fresh Python 3.12 session:

    python -m unittest discover -s tests -v
    python scripts/baseline.py --out-dir output/baseline
    python scripts/backtest.py --out-dir output/backtest

See docs/baseline-method.md, docs/historical-backtest.md, data/README.md, and experiment-log.md (R001/R002). Input/code hashes are included in generated JSON; workflow logs record the executed Git revision.

## Next actions

1. Review the initial historical errors and source limitations before selecting a final model. The pilot does not justify tuning many parameters or declaring L1 superior.
2. Six-election data collection is now assembled; audit publication/lineup/deduplication and freeze a model-ready panel before extending the backtest. Separately summarize the repeated 2019-2021 period. Preserve identical horizons and whole-election evaluation. Any method tuned against R002 needs separate later evaluation, not a claim that R002 remains an untouched holdout.
3. If pursuing the user's war/turnout idea, build the official series beginning in 1949 and predefine conflict/lag coding before comparison. The inspected CBS table ends in 2021 despite a 1949-2022 title; official 2022 turnout is already available separately. No directional adjustment is justified yet.
4. Audit omitted current releases/current lineup changes and preserve the original snapshot. Obtain complete operative rules/agreements before implementing vote-share allocation. Consider one justified uncertainty improvement or a small forest challenger only after defining features and validation; no pretrained election-specific checkpoint was verified.
5. Confirm final team/track, timezone, remaining form validation/precision, and other-qualifiers scoring. Keep updating the method report and preserve final-report time; never submit without explicit authorization.

## Environment notes

Git/gh may not appear on the inherited PATH. Executables are C:\Users\omersu\AppData\Local\Programs\Git\cmd\git.exe and C:\Program Files\GitHub CLI\gh.exe. Approved outside-sandbox operations successfully use the existing keyring login; in-sandbox failures do not prove login is invalid. A safe.directory exception exists only for this exact project path because .git was initially created by the sandbox user.

Local checks used QGIS Python 3.12 via PYTHONHOME, but this is not a project dependency: a normal Python 3.12 runtime suffices. Network/Git writes may need approval. Raw source images/renderings under tmp/ are ignored and are not the sole record of any numerical input. No credentials or personal form responses are committed.
