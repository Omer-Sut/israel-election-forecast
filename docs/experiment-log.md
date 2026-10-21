# Experiment and effort log

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
