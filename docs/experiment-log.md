# Experiment and effort log

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
