# Current project state

Last updated: October 21, 2026 (cloud model screening implementation).

## Current handoff — lightweight cloud screening (E001)

The user approved implementation of a narrow all-family screen, prioritizing cloud setup within today's one-hour availability and soft correction limits before hard caps. Implemented 18 candidate configurations (recency, ridge Gaussian GLM, forest, XGBoost, dynamic Kalman, ensemble; three each) plus unchanged mean/L1 references. Read [model-screening.md](model-screening.md) for exact inputs, features, weights, reconciliation, evidence tiers and execution.

`Screen lightweight forecast models` is a separate GitHub Actions CPU workflow: Python 3.12, locked optional scientific dependencies, no secrets/GPU/local training. It runs all tests, real historical diagnostics, synthetic checks for all configurations, deterministic reruns and artifact upload. Baseline inputs/code/reports and current 2026 forecasts are unchanged. Audit tier is explicit: only the existing original-source-audited 2021/2022 panel is used, not bulk poll indexes/CBS/INES.

Work started from clean main on `feat/cloud-model-screening`, published through [PR #12](https://github.com/Omer-Sut/israel-election-forecast/pull/12). Final code commit `12d19d5e13ff5f226321fda8e5a3ab07102b95cf` passed [screen run 39622248851](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39622248851): all 43 tests with scientific dependencies, all 20 configurations exercised, deterministic reruns, artifact upload. Experiment runtime was 2.720 seconds; hosted job approximately 60 seconds including setup/tests. [Baseline run 39622248780](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39622248780) also succeeded with original reports/database checks. Earlier implementation e650619 passed both workflows too. A new boundary test caught ambiguous older syndicated trajectory copies; the runner rejects them without changing the baseline.

Verified artifact 12356255608 (38,185 compressed bytes) was downloaded and its consumed code/input hashes all matched current files. Five compact outputs (331,703 bytes total) are preserved in [reports/screening-2026-10-21](../reports/screening-2026-10-21/): summary, full JSON/provenance, per-list CSV, synthetic smoke result and installed package environment. The JSON's code_commit is the tested GitHub PR merge ref `4fc96087caa1bb86c0e7df969c556c81dc47bc1b`, not a claim that the topic branch was already merged. This evidence/continuity update is a later report/documentation commit; inspect actual Git/PR state for subsequent publication/merge status.

Publication checkpoint: report/documentation commit `31324b17ad3fb1012f64dc5a5bf3f6632a565093` was pushed. Both final PR checks succeeded: [screen 39622977662](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39622977662) and [baseline 39622977663](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39622977663); PR merge state was CLEAN. Automatic approval review rejected merging PR #12 into main because it requires explicit user approval for that shared-branch mutation. No merge or main-branch synchronization was executed. Work remains published on `feat/cloud-model-screening`, with this additional handoff update committed afterward. Do not retry or bypass that rejection without user authorization. The manual Run workflow button awaits merge into the default branch; PR runs and committed reports already work. Next operational action: obtain explicit approval for PR #12's merge, then verify main and workflow availability.

Initial real results: for 2022, all fitted candidates tie error 12 at T−6; at T−1, candidates score 12 or 14 versus both references at 12. No candidate improves on those references on this observed election. This is a one-training-election preview, not evidence to select/discard a family. Optimized ensembles have no real fit; synthetic optimization is software evidence only.

Next: audit earlier election polling panels, then run the unchanged grid with strict chronological folds. Supervised 2022 fits use only 2021 and are diagnostics; optimized real ensembles remain unavailable until two earlier strict OOF elections exist. No model is selected, no hard bound/CI is calibrated, and no competition submission is made. Hands-on effort remains unmeasured; the eight-hour total budget is not reset.

## Latest direction — refine recent polls, defer locality forecasting

The user wants recent polls to anchor the forecast, with historical/auxiliary data used to polish the result conservatively. They believe current mean/L1 forecasts may already be close; this remains an intuition about an unobserved future outcome. Locality forecasting is deferred as a possible future direction; preserve the collected CBS/geographic tables, without prioritizing a bottom-up model.

Read [poll-centered-modeling.md](poll-centered-modeling.md) before implementing models. It records the user's five points, explains dynamic polls, and proposes benchmark-plus-correction, shrinkage, per-party buffers and joint adjustment budgets. Agreement with current polls is an auxiliary consistency metric; independent forward-poll evaluation requires withholding those releases and any anchor using them. Historical election error remains the main competition evidence. Poll scatter, predictive intervals and chosen hard search limits are distinct; shared polling error, correlated parties, the total of 120 and threshold discontinuities need explicit handling. No numerical buffer, confidence level, model choice, new forecast or uncertainty estimate is implemented.

Documentation-only work started on `docs/poll-centered-modeling` from clean main bc829d9. Markdown links/code fences passed across 18 files and Git whitespace checks passed. No runtime code, data or reference report changed; no new model tests were written or run locally. Published commit 746cd14 was verified remotely through [PR #11](https://github.com/Omer-Sut/israel-election-forecast/pull/11). The unchanged hosted reproduction pipeline is [run 39616331613](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39616331613), still queued when this checkpoint was written; do not claim hosted success for this discussion. Inspect live Git/PR/run state for later documentation commits and merge/completion status. The 31-test implementation evidence below belongs to D002, not a new model experiment.

Next active work: audit the polling panel/publication dates, select a benchmark/calibration policy on chronological development data, then test a small conservative correction or dynamic update. RF/XGBoost/GLM remain candidates; locality modeling is a backlog item.

## Previous handoff — CBS area context (D002)

The user requested broad age/sex/socioeconomic data from the CBS census site that can be associated with ballot locations across years. The dataset is extended in the same SQLite file with eight tables and four views. Sources: CBS official census downloads, annual population workbooks/GIS ZIP, socioeconomic tables/official linked GIS map, and the government CBS locality catalog. Full [CBS integration guide](cbs-demographics.md) covers schema, sources, units, joins, coverage, dates, missingness and examples.

Actual coverage: 1,218 / 1,218 / 1,217 / 1,218 / 1,185 locality profiles for 2018/2019/2020/2021/2022; 10,959 annual locality/year/sex rows for 2019–2021; 4,765 socioeconomic locality/year rows for 2015/2017/2019/2021; 8,896 annual 2017–2022 geographic mappings; 5,085 census records, 1,132 variable definitions, 56,714 raw rows, 19 source responses archived/hashed. CBS input archives are approximately 28.2 MB. Age 2015–2017 remains uncollected; no annual interpolation or future-census backcasting was added.

Ballots inherit locality context through CBS/CEC locality codes. No neighborhood/statistical-area voter assignment is verified; code 0/unlocated votes stay unmatched. Views retain demographic year, future-reference and descriptive-only flags. All historical publication availability remains unverified. Census sources are under a 2025 publication path despite a 2022 reference date; the 2017 rural index explicitly records a March 4, 2021 replacement. Rank scopes differ across socioeconomic sources. Do not interpret an area relationship as an individual age/sex party preference.

Validated descriptive example: April 2019 Likud share in 235 matched Central District localities is 319,095 / 1,121,237 = 28.4592%. Matched 2018 population=2,192,404; male measure covers 2,050,825 people (234 localities), giving 49.5010% male in that subset. Age summaries use their own exposed denominators. CBS directly publishes 2022 district median ages 33 overall, 32 male, 35 female; these are not mean ages. `scripts/cbs_report.py` regenerates examples/coverage; no forecasting method was changed.

Branch `feat/cbs-demographics` began from clean main at c53d23f (merged database PR #9). All 31 local tests passed in 29.0 seconds, including eight new CBS checks; links/fences, whitespace and both unchanged forecast reproductions passed. Implementation `f007367948c77e205a3a1d9711c7bb94db0dfd53` was pushed and verified through [PR #10](https://github.com/Omer-Sut/israel-election-forecast/pull/10). [Hosted run 39610830289](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39610830289) succeeded: all tests, both original forecast report comparisons, expanded offline database, exact combined coverage/hash manifest, CBS descriptive report and artifact uploads passed. The unexpired `historical-election-database` artifact ID 12349988642 was verified (28,365,093 compressed bytes). This handoff records the checked implementation run; inspect live Git/PR state for subsequent documentation commits and merge status.

Retrospective 2022-profile linkage covers 99.51–99.72% of valid votes assigned to ordinary localities across the six elections, or 89.93–94.20% including national special/unlocated votes in the denominator. The special source codes change: 2015=0; April 2019=99999; September 2019–2022=9999. None is allocated demographics.

Rebuild offline with `python scripts/build_database.py` and `python scripts/cbs_report.py`. Latest combined manifests/reports are frozen at `reports/cbs-2026-10-21/`; the earlier D001 manifest is preserved. Next: verify historical source release/revision dates and choose a small feature panel, fill useful earlier age gaps, review unmatched codes/boundary changes. Original polls, six-election outcomes and forecast reports remain unchanged.

## Previous handoff — database first

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
