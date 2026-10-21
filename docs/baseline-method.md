# Implemented preliminary baseline

This is the first runnable reference, not a submission-ready forecast or a validated probability model. No heavy training, pretrained model, third-party Python dependency, or GPU is used.

## Run on any computer or hosted CPU

Python **3.12** is the reference runtime. The implementation uses only the standard library; no package installation is required.

```sh
python -m unittest discover -s tests -v
python scripts/baseline.py --out-dir output/baseline
```

The commands work from the repository root on Windows/Linux. The program resolves inputs relative to its repository location and writes no machine-specific input paths. Committed reference outputs are under [reports/baseline-2026-10-21](../reports/baseline-2026-10-21/summary.md).

The GitHub Actions workflow `Reproduce preliminary baseline` runs the same commands in a fresh hosted Linux CPU job, compares generated outputs byte-for-byte with the committed reference, displays the summary, and uploads downloadable artifacts. It can be manually rerun from the repository's Actions tab after it is on main. The durable inputs and outputs remain committed even after workflow artifacts expire. Check the run result before claiming remote reproduction succeeded.

Verified: [hosted run 39572969093](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39572969093) passed for implementation commit `aee2f11`, including nine tests and exact output comparison. This verifies portability and software behavior, not election forecasting accuracy.

## Poll selection

Use the latest eligible audited release per configured polling group in the 14 days preceding the as-of date, with one equal weight per selected group. Six stored observations produce five active groups because Walla and Maariv share Lazar/Panel4All. This avoids simple repeat-publication overcounting, but it does not prove independence across organizations or shared panels/methods.

Publication date and any recorded source-update date must precede the cutoff. Use known fieldwork end for age; where unavailable, use publication date as an explicit proxy. An earlier cutoff must not reuse a source version updated later. The current snapshot is an audited convenience sample, not every latest poll. No numerical house-effect correction or sample-size weighting has been estimated.

Map source-list labels through `config/poll-mappings.json`. For complete audited tables summing to 120, residual zero seats are inferred for omitted form fields. Missing vote percentages are not imputed. Below-threshold percentages are retained for future analysis and do not enter this seats-only consensus.

## Two seat references

1. **Rounded mean:** average the selected seat vectors, take floors, and distribute remaining seats by largest fractional remainders; ties use form order. This gives a transparent total-120 numerical reference. It may produce small positive seat counts that are arithmetic averages of pass/fail outcomes; it is not claimed to be an attainable election result.
2. **Empirical L1 consensus:** minimize the sum of absolute deviations from the selected poll vectors, over nonnegative integer form outputs totaling 120. A dynamic program over list index and allocated seats solves this small problem. Equal-cost solutions minimize squared distance to the poll mean, then lexicographic form order.

The second objective matches the *shape* of the competition loss but treats the observed polls as equally weighted reference scenarios. Polls are not independent election outcomes, so lower disagreement with them is not evidence of better predictive accuracy. It is not a calibrated expected-loss forecast. Neither method implements an official Bader-Ofer allocator or verifies full electoral feasibility; constraints are currently the form's field coverage, integer arithmetic, and total.

## Turnout

The first turnout baseline simply repeats the official 2022 turnout, **70.63%**. It is validated against the form's inclusive **40.00-100.00%** bounds and displayed to two decimals. An out-of-range input raises an error rather than silently clipping. N12's reported **72% intention to vote** is stored as a separate diagnostic and has not been calibrated or blended into actual-turnout prediction.

## Diagnostics and checks

Generated JSON includes source selection, input/code hashes, both methods, observed poll ranges, and leave-one-group-out results. Poll ranges and omission scenarios are **not confidence intervals**. The first run found an L1 distance of 4-8 seats after omitting one active group (sum of absolute changes across lists, equivalent to 2-4 seats reassigned), with small-party outcomes particularly sensitive. Those diagnostics quantify this input sample's sensitivity only.

Tests cover turnout endpoints/nonfinite rejection, missing/invalid seats, total preservation, other-list mapping, group deduplication, future source-revision exclusion, and an independent brute-force check of the dynamic program on a small problem. These are software correctness checks, not historical forecast validation.

## Next before choosing a final method

Audit the omitted latest releases, collect comparable historical pre-election polls, evaluate against same-election official outcomes using time-respecting cutoffs, resolve remaining mappings/agreements as needed, and evaluate whether a vote-share/scenario method earns its complexity. Keep the baseline results frozen for comparison. No final submission has been prepared or sent.
