# Experiment and effort log

## E006 - Explicit party-area context, October23 (verified)

Implementation1fcca3da08f4c6a66bdf55c20f345db351b1c961 / PR17. Screen39921492239 and baseline39921492335 succeeded:60tests, frozen references, repeated E006contexts/coverage/scores/selections/SVG identical. E006runtime6.231s; seed20261021. Input hashes/configs in reports/party-area-trial-2026-10-23/manifest.json and full artifact12486559561 (138283bytes, unexpired throughNovember22). Tested output PR merge ref93e1e7dd is not a merge claim. Initial770065d run39921070292 failed on wrong-module import; corrected, no failed results used.

Expanded27audited releases, six elections T-1, previous-election locality votes only. Fixed ridge_10/forest_3_5/xgb_2_50; five ablations, seven existing strengths; per-fixed-learner/feature-set selection on >=2earlier OOF elections by continuous or integer L1. Dated15cities versus full2015edition after2019-08-31, explicitly archive-unverified sensitivity. Five pools are context proxies; splits/new entrants missing.2022profiles11/16with pools, conditional unweighted mean predecessor coverage39.6%→90.0%;2021only4/14despite52.3%→93.9%coverage. All420scalar scores/180selection rows preserved. No fixed25% or selected integer improvement in2021/2022over20/12. Hindsight2022edition+pools ridge5% continuous12.576vs12.667 ties integer12, not chosen earlier; not adoption evidence. Keep lineage/audit tooling, reject correction adoption now; prioritize current polls/threshold inputs. No age/sex/current forecast/turnout/merge change. Local Python unavailable; user hands-on/cumulative effort unmeasured, budget not reset.

## E005 - poll quality and feature trial (verified)

Final4275c5484ccd2525923d89c9f45e13b7dce2b272 / PR #16. Screen39776060120 and baseline39776062476 succeeded:55tests and frozen/deterministic reproduction. New trial37.133s; outputsfrozen at tested PR merge refefb6675 (not a merge claim).324mapped exploratory index rows/466exclusions,27audited releases,22known sizes. Source2018-11-28CBS2015index15city table transcribed and matched to official city codes/names; previous-election vote profiles for three explicit cores enter two additional ablations. Broad209profiles remain descriptive; age/sex/lineage integration still gated. Fourfeature sets/twohistory variants; correction0/.025/.05/.1/.25/.5/1 and existing family parameters selected on>=2earlier OOF elections. No selected2021/2022improvement, oftenzero corrections. Audited-only quality MAE9.233vs prior-campaign-average8.668, reject weight adoption for now. Compact report preserves CSV/SVG/HTML/provenance; artifact12424098121 verified203126bytes/unexpiredthroughNovember21, full2MBparameterCSV rebuildable. No current forecast/turnout/final model/merge change. Hands-on effort unmeasured/not reset.

Protocol poll-quality-feature-trial.md. Separate audited27/index error tiers, campaign means/sample variances/creator/horizon patterns, audited-only earlier-campaign expected-error/severity prototype. Original/expanded history,8versus9dynamic-gap features, fixed small grid; fractions0/.025/.05/.10/.25/.5/1 selected from>=2earlier OOF elections. Descriptive209party-area profiles with CBS date/lineage gate closed to historical fitting. Explicit final rounding assertions. User authorized trying ideas, no final weight/model/forecast. Hosted validation pending; hands-on budget unmeasured/not reset; turnout later.

## E004 - correction and forest-seed robustness (October 22, 2026)

Verified: implementationbe272a4d923b2921faa8da529d4b8d72d5debc95, PR #15, screen39750449237 and baseline39750449205 succeeded.50 tests, full-grid repeat equality, forest-only adapter equality,3080 score rows across both variants/five fractions/20 forest seeds. Compute51.396seconds. Artifact12413786085 contains83files/1,156,262bytes, verified unexpired; tested PR merge commitf5ce233aa2544550f6107250aecd057b820959e9. Initial run39750028287 identified a real diagnostic assumption error: exact-integer reference and floating reconciliation can break tied remainders differently even at0%. Regression test/CSV flag retain both, frozen algorithms unchanged. April2019 differing0% vectors both score40. Original seed/25% still yields no2021/2022 improvement;2022 identical mean vectors16/18 original and12/18 expanded. Preserve batch, inspect all correction/seed curves next session, don't select by best retrospectively tuned cell. No method selected or forecast altered. Hands-on/cumulative usage remains unmeasured.

User approved unattended computation during approximately two-hour absence. Protocol: docs/robustness-batch.md. Original/expanded history; fractions0/.10/.25/.50/1; full fixed grid at20261021 and three forests at20 seeds20261021-20261040. All eligible T-1 chronological folds; unchanged gates/dates/features/targets/weights. Inspected outcomes are descriptive, no best-seed/fraction selection. Local Python unavailable; tests/execution pending on GitHub at preparation. Artifact preserves raw fits, predictions, plots, score/seed CSVs and manifest. Record actual commit/run/runtime after verification. Hands-on/cumulative usage unmeasured; no budget reset or current forecast change.

## E003 - Repeated-release and source-age sensitivity (October 22, 2026)

- User authorized next data/coverage work and online-first collaboration. Source selection frozen before fitting: three reviewed earlier releases within existing groups,24 to27 total, latest-group anchors unchanged. Four variants: reference, Walla publication age, expanded history, combined. Fixed model grid/correction/seed/cutoffs/outcomes, chronological gates preserved.
- Audit/protocol: `data/snapshots/campaign-history-2026-10-22/audit.json`, `docs/campaign-history.md`. Missing2015 primary access and possible Walla copy metadata explicitly retained; no index-only numerical promotion. No final model/L0/2026 forecast selected.
- Reproduce on hosted CPU with `python scripts/campaign_history.py` and `node scripts/compare_campaign_diagnostics.mjs output/campaign-history`. Node source mapping/diagnostic checks pass locally. Scientific fitting, new Python tests, reference reproduction and deterministic repeated fits pending at this checkpoint. Actual run/commit/results will be appended after verification; hands-on/cumulative effort unmeasured.
- Verified31b58712593b3db492b20e27ef3fb1728baaf858, PR #14, screen39741972606 and baseline39741972643:46 tests and all reference/data-variant/determinism checks pass. Runtime per variant(reference/age/history/both)=3.012/2.390/2.399/2.411s; every prediction CSV reproduced on repeat. Four hosted data variants reuse the same inspected outcomes, not four independent replications.
- New results: no candidate beats reference20/12 on2021/2022. Combined equal/strong-penalty ensembles tie20/12; two forest configurations worsen2021 to26 and middle forest2022 to14. Training trend-missing rows for2021 drop44 to11, confirming the new feature coverage without proving predictive usefulness. Keep controls/no final selection; do not choose metadata by best score.
- Durable `reports/campaign-history-2026-10-22/` holds compact all-fold stage/representation/provenance archive,CSV,SVGs,PNG and summary; full artifact12408824706 verified877,889bytes/unexpired.12 stable consumed file hashes match. Results derived from hosted output, no local refitting. Remote report/documentation publication follows checked implementation; actual latest SHA belongs in live PR state.

## A002 - Four-stage diagnostics over every available E002 fold (October 22, 2026)

- User approved pre-rounding plots and broader reporting. Inputs are unchanged saved E002 predictions and configured six-election outcomes. No fitting, new evaluation data, grid/penalty selection or current forecast changes.
- Outputs: `reports/diagnostics-2026-10-22/` (HTML/SVG/PNG, scores CSV, per-list JSON/provenance). `scripts/screening_diagnostics.mjs` uses Node built-ins; optional `scripts/plot_screening_diagnostics.R` uses base R. Existing Python pipelines remain unchanged.
- Checked all saved final total/signed scores directly against outcomes and reconstructed blended/rounded vectors. Boundary/corruption tests passed and five outputs repeat byte-identically. Exported PNGs were visually inspected. No local original Python suite or new hosted workflow was run; CI diagnostic check is added but remote verification is pending.
- Includes earlier eligible folds with explicit history/OOF roles and matched continuous/integer references. 2022 dynamic_01 improves projected continuous error slightly (11.7895 vs mean12.6667) while retaining mean's integer vector/error12; ridge_10 has worse continuous error but the same rounded vector after 25% correction. Not a family ranking or new independent evidence.
- Actual hands-on/cumulative effort unmeasured; no reset of the eight-hour budget. Keep existing controls; next audit source/trajectory coverage. L0/representation model remains discussion only. Publication status is local until verified.

## A001 - Analysis of saved E002 results (October 21, 2026)

- User requested an analysis and Git handoff. Inputs are the saved E002 report only; no new training, grid search or current prediction. Standard-library `scripts/analyze_screening.py` checks per-list score arithmetic and derives party errors, forecast identity, continuous movement, feature coverage and ensemble weights.
- Outputs: `docs/screening-results-analysis.md` and `reports/screening-six-elections-2026-10-21/analysis.json`, including input/code hashes. Two independent executions produced byte-identical analysis; all saved comparison scores reconcile.
- Interpretation: references remain controls; no challenger earned replacement. 2021 candidate ties/worse=4/14; 2022=16/2, with all 16 ties identical to the rounded mean. Earlier trend coverage is absent in all 44 training rows for 2021. Full unshrunk supervised corrections worsen both outcomes. Meretz representation remains wrong for every 2022 method. Two already-inspected comparison outcomes cannot establish a family ranking or calibrated intervals.
- Recommended next work is source/coverage sensitivity, then repeated earlier campaign releases before wider tuning. No recommendations are claimed implemented. Runtime only analyzes small saved files; hands-on effort/cumulative effort unmeasured. Original E002 prediction artifacts remain unchanged; PR #13 open at inspection.

## E002 - Complete comparison using six-election history (October 21, 2026)

- User requested years with enough earlier history. Predeclared protocol: T−1 across 2015, April/September2019, 2020, 2021, 2022; first four provide training and strict OOF history, final two complete the all-model comparison. Same 18-config grid, two references and 25% shrinkage. Not a blind holdout or a final model selection.
- Inputs: twelve newly original-source-reviewed numerical releases plus unchanged twelve pilot releases, official database outcomes (2015 secondary-seat tier preserved). Explicit original publication-date corrections and unresolved migrated/fieldwork metadata in `docs/six-election-screening.md` and audit facts. Unknowns are not invented.
- Added offline preparation/rebuild check, full source/input/code provenance and a completeness gate for evaluation cases. E001 config/reports preserved. Focused local checkpoint: ten checks passed, four scientific tests deferred to cloud; no model runs locally. Runtime/scores/hosted publication to record after verification. Hands-on effort unmeasured, total budget not reset.
- Verified implementation:6349ac98477bec05bf95cdb076520eb0037bedd4, [PR #13](https://github.com/Omer-Sut/israel-election-forecast/pull/13), [screen39626291280](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39626291280), [baseline39626291139](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39626291139), both successful. All 45 cloud tests, exact panel rebuild, complete 20-config ×2-election comparison and deterministic repeats passed. Local full suite41 passes/four scientific skips.
- Runtime 2.135s (repeat 2.145s), approximately 60s hosted job. Artifact12355914984 verified unexpired,59,305 compressed bytes; downloaded hashes match code/inputs. Durable five-file report at `reports/screening-six-elections-2026-10-21/`,491,970 bytes. Tested PR merge ref982612019e557aa6c4d039414fc0822ad8f1b8e6; no merge of PR #13 claimed.
- Actual T−1 errors: mean/L1 references20 in 2021,12 in 2022. All candidates20–24 and12–14 respectively; no improvement established. Ensemble 2021 weights use2019Sep/2020 strict OOF predictions;2022 adds 2021. No missing comparison methods; expected warm-up gaps retained in full output. Next source/coverage sensitivity before narrowing. No model chosen or current forecast changed.

## E001 - Narrow cloud model screening (October 21, 2026)

- Question: can lightweight poll-centered corrections improve references without large movement? User approved cloud-first implementation and soft shrinkage. Three configurations each for six candidate families; no automated search or final selection.
- Inputs: existing audited 2021/2022 snapshots, T−6/T−1, 14-day window. Each target election uses earlier completed elections only. One-election fits are labeled diagnostics. Bulk indexes/demographics are excluded. Full assumptions and feature/ensemble targets in `docs/model-screening.md`.
- Reproduce: `python scripts/experiments.py --out-dir output/experiments` with pinned `requirements-experiments.txt`, or the dedicated Actions workflow. Reports include code/input hashes, seed, statuses, dates, configs, runtime, errors and movement. Synthetic smoke evidence is separate and never ranked by accuracy.
- Validation checkpoint: 40 local passes, three optional scientific tests skipped (43 total). Cloud requires all dependencies; real scientific outputs and hosted status pending verification. Optimized ensembles have insufficient real history; no weights are borrowed from synthetic tests.
- Hands-on effort/cumulative effort not measured. Runtime will be recorded by the runner, separately from user effort. Next audit earlier election panels, then compare strict folds before narrowing to two challengers.
- First verified execution: implementation e650619, PR #12, [screen run 39621960539](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39621960539), all 43 tests passed, 20 configurations exercised and outputs deterministic. Runtime 2.772s (repeat 2.788s); approximately 66s hosted job including setup/tests. Artifact 12355521369 verified unexpired, 34,852 compressed bytes. Original baseline/database reproduction 39621960596 also passed.
- First real diagnostic: 2022 T−6 all fitted candidate errors=12; T−1=12–14, both references=12. No improvement established; one training/one evaluation election cannot rank families. Optimized real ensemble fits unavailable. Later provenance-only code update is recorded separately after its run succeeds.
- Final code verification: `12d19d5e13ff5f226321fda8e5a3ab07102b95cf`, [screen 39622248851](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39622248851) and [baseline 39622248780](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39622248780), both successful. 43 tests passed; real+synthetic runner=2.720s; job approximately 60s. Artifact 12356255608 verified unexpired (38,185 compressed bytes), downloaded, every input/code hash matched. Durable outputs: `reports/screening-2026-10-21/` (331,703 bytes). Report code_commit is the tested PR merge ref 4fc96087caa1bb86c0e7df969c556c81dc47bc1b. No model chosen; next audit older panels.

## D002 - CBS geographic context integration (October 21, 2026)

- Question: obtain broad official demographic/socioeconomic profiles linkable to historical locality/ballot results. This is data ingestion and descriptive linkage, not a forecasting experiment. User hands-on effort was not measured; the eight-hour budget is not reset.
- Inputs: 19 CBS/government source responses archived under `data/cbs-2026-10-21/`; source URLs, response hashes and revision/availability notes in `cbs_sources`. Counts, schema, units and year coverage are in `docs/cbs-demographics.md`.
- Methods: exact normalized locality-code joins; retain original census geographic records; published city totals before subdivisions, otherwise sum unique total-population reporting rows. Preserve suppression, source vintage, medians and socioeconomic rank scope. Restore zero-party-vote localities when calculating shares. Report population-weighted percentages with measure-specific complete-case denominators.
- Reproduction: `python scripts/build_database.py`; `python scripts/cbs_report.py`; `python -m unittest discover -s tests -v`. Frozen combined coverage/example output in `reports/cbs-2026-10-21/`; earlier reports remain untouched. All 31 local checks passed before publication; hosted evidence is recorded after actual verification.
- Result: broad comparisons work, including 2018 context / April 2019 voting and native 2022 district medians. Limits: no individual demographics, neighborhood ballot mapping, exact male mean age, verified historical source availability or age 2015–2017. No model selection, training, forecast change or accuracy claim.

## D001 - Historical database assembly (October 21, 2026)

- User requested data before model comparison. This is ingestion/validation, not a forecasting experiment or new accuracy claim. Agent work began with recorded research at 12:19:44 UTC; user hands-on effort is not inferred from runtime.
- Snapshot: `data/database/`, 32 source responses with provenance; all six elections 2015–2022. Coverage: 209 list outcomes, 75,999 geographic rows, 899,195 positive geographic/list cells; 790 main-table candidate poll rows from a wider 2,171-row context archive; six INES study dictionaries and marginal summaries.
- Commands: `python scripts/build_database.py`; `python -m unittest discover -s tests -v`. Generated SQLite/coverage go to `output/` and hosted artifact; canonical inputs remain small enough for Git. Report/hash manifest retained under `reports/database-2026-10-21/` after validation.
- Validation: all national/geographic party totals and geographic ballot identities, final 120-seat sums, published-turnout precision, relational integrity, source hashes, mixed party-column layouts, shared cells, year inference and aggregate INES boundaries. Exact executed checks/publication evidence recorded in project-state/session-log.
- Limitations: 2015 seats use secondary-source IDI; bulk polls not original-release audited or deduplicated; no verified publication cutoff panel; INES historical availability/weights/waves need review. No model trained/selected and no existing forecast/backtest input/output changed.

## R001 - First audited-sample consensus (October 21, 2026)

- Question: can a tiny, no-training method reproduce form-valid baseline outputs from original-source seat projections?
- Execution began at 08:39:13 UTC. Agent execution wall-clock duration is recorded in the final session handoff; the user's hands-on effort is not measurable from tool time. Earlier setup/planning was not timed. Do not reset the eight-hour effort budget between sessions.
- Implementation: `scripts/baseline.py`, code commit `aee2f111e1f66f2f52101c5278f0d4a841cd444a`; input/config/code hashes are in `reports/baseline-2026-10-21/baseline.json`.
- Inputs: six audited releases, October 15-20 publication dates; select one latest audited release per declared group within a 14-day window as of October 21, resulting in five equal-weight groups. Older Maariv/Lazar is archived in favor of Walla/Lazar. Further latest releases remain unaudited.
- Mapping: current Joint List -> form Hadash-Ta'al is the user-accepted output-label assumption, not historical equivalence. Preserve current Religious Zionism/Zehut composition.
- Method: largest-remainder rounded mean versus integer total-120 empirical L1 consensus. Turnout repeats official 2022 participation (70.63%); current N12 self-reported intention is diagnostic only. No random seed or model training is involved.
- Results: average total absolute disagreement with input polls is 14.4 for rounded mean and 12.4 for L1 consensus. **These are in-sample consensus diagnostics, not historical forecast errors.** L1 omission sensitivity is 4-8 in sum of absolute seat changes; ranges are not confidence intervals.
- Validation: nine correctness tests passed locally, including a brute-force check of the optimizer, future-data selection, source deduplication, and inclusive turnout bounds. Historical evaluation/calibration: **not performed**.
- Reproduction: Python 3.12 standard library; `python scripts/baseline.py --out-dir output/baseline`. [Hosted CPU run 39572969093](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39572969093) passed all tests and byte-for-byte reference-output comparison, completing at 08:55:49 UTC. Time from execution start to verified hosted reproduction was 16 minutes 36 seconds (agent wall clock, not measured user hands-on effort).
- Decision: retain both references; neither is selected as the final forecast. Next audit missing latest polls and compare against historical pre-election-poll baselines.
- Limitations: convenience sample, source-body/graphic conflict disclosed, some fieldwork metadata missing, no turnout-intention calibration, no vote-to-seat allocator or full legal-feasibility check, and no modeled redistribution after reported Blue and White withdrawal.

## R002 - Initial historical backtest (October 21, 2026)

- User instruction: proceed with the historical backtest, initially the proposed 2021/2022 scope. First recorded research timestamp: 11:47:56 UTC. Agent/tool runtime is distinct from unmeasured user hands-on effort; the eight-hour project budget is not reset.
- Inputs: `data/snapshots/historical-2026-10-21/`, `config/historical-backtest.json`. Twelve original-source audited releases, three groups per election and cutoff. Final official 2021/2022 targets; official 2020/2021 turnout references. Input/code hashes are preserved in `reports/backtest-2026-10-21/backtest.json`. Starting main commit=85fab76; implementation commit/hosted evidence is recorded after publication.
- Fixed methods: existing rounded mean and empirical L1 imported from unchanged baseline.py; equal latest audited group weights, 14-day effective-age window, T-6/T-1 end-of-day cutoffs. Alphabetical election-specific IDs fix ties. No tuning, fitting, random seed or current forecast change.
- Outputs: `reports/backtest-2026-10-21/{backtest.json,seat-errors.csv,summary.md}`. Main metric is total absolute seat error. At T-6, 2021=24/22 and 2022=12/12; equal-election mean=18/17. At T-1, 2021=20/20 and 2022=12/12; mean=16/16. Four cases are two election outcomes.
- Turnout persistence: 71.52 predicted versus 67.44 actual in 2021 (4.08 pp); 67.44 versus 70.63 in 2022 (3.19 pp). Current turnout-intention data and war assumptions are unused.
- Diagnostics: both methods miss Meretz representation in 2022; 2021 includes substantial Blue and White/New Hope/Yamina errors. These motivate investigating uncertainty but do not validate a particular correction. No reliable 2019-2021 block sensitivity with only 2021 in that period.
- Validation: all 16 software checks pass locally, including seven new historical boundary/identity/scoring checks. Mutating later/exit-poll values cannot alter earlier forecasts; mutating targets changes scores but not forecasts. Hosted workflow now reproduces both frozen reports; its status is not assumed before verification.
- Limitations: convenience panel, different third group across elections, some omitted latest publications and missing metadata, one explicitly documented residual seat derivation, no authenticated historical archive versions, no vote-to-seat allocation/probability calibration. This is retrospective evaluation, not a certified real-time reconstruction or a final model choice.
- Decision: retain both references and the frozen current forecast. Review initial failures; extend historical coverage if useful within remaining time, or justify one lightweight improvement with separate evaluation. Once used for tuning, this pilot is no longer an untouched holdout. See `docs/historical-backtest.md`.
- Publication/reproduction verified: implementation commit `c591c7031d6aebda9a63c38fc4dffabd58ca9d6a`, [PR #8](https://github.com/Omer-Sut/israel-election-forecast/pull/8), [hosted run 39596526287](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39596526287). All 16 tests and exact reproduction of both report packages passed at 12:03:15 UTC. First recorded research timestamp to hosted completion=15m19s agent wall clock; user hands-on/cumulative effort remains unmeasured. This evidence update is a later handoff commit; inspect actual Git state for the latest revision.

## Logging conventions

Track actual hands-on effort against the approximate eight-hour budget. Record runtime separately; do not invent elapsed time for earlier sessions.

## Run record (copy for each consequential experiment)

```text
Run ID / author / timestamp / timezone:
Question or hypothesis:
Hands-on effort this run / cumulative effort:
Code commit:
Hosted execution surface and reproduction command/notebook:
Forecast cutoff / input snapshot IDs and hashes:
Method / configuration / random seed:
Historical evaluation elections and their data cutoffs:
Validation separation (what was calibrated on what):
Output locations / runtime:
Absolute seat error by election / turnout error:
Threshold outcomes / sensitivity checks:
Decision and reason (keep, reject, or unresolved):
Limitations / next step:
```

Log failed or rejected approaches briefly too. Keep the authoritative source manifest and outputs durable in GitHub or a documented shared store; a session-only path is insufficient.
