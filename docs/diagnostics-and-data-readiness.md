# Pre-rounding diagnostics and data readiness

October 22, 2026. User requested evaluation before rounding, plots, broader use of collected data, and an explanation of remaining preparation. L0 sparsity was proposed for discussion, not selected or implemented.

## Implemented A002

[Open the report](../reports/diagnostics-2026-10-22/index.html), [historical plot](../reports/diagnostics-2026-10-22/history.png), and [all-configuration plot](../reports/diagnostics-2026-10-22/stages.png).

The report analyzes saved E002 outputs without refitting. All six elections appear wherever a configuration has an eligible fit. September 2019 and 2020 now appear alongside 2021/2022; earlier OOF outcomes inform later ensemble weights and must not be described as untouched additional ensemble evaluation. Missing fits remain gaps. The six history panels use fixed configurations (recency_7, ridge_10, forest_3_5, xgb_2_50, dynamic_01, ensemble_1), not retrospective winners. CSV/JSON include every available configuration.

Four stages are distinct: full unconstrained estimate; full estimate projected to nonnegative sum 120; 25% correction projected to sum 120; final rounded integer allocation. Continuous comparisons use the unrounded mean as control, and integer comparisons use the rounded mean. Unconstrained scores can benefit from invalid totals, so projected continuous scores are the meaningful coherent pre-rounding comparison. The competition still scores integer seats; continuous performance is diagnostic.

Checks load outcomes directly from the configured outcome snapshot, rather than inferring truth from a saved error. Every saved total and signed per-list error is checked, and saved blending and rounding are independently reconstructed. Corrupted targets/scores/shrinkage are tested. Two executions produced byte-identical JSON, CSV, HTML and SVG outputs. Base-R PNG exports were visually inspected. Original forecasting code/configuration, E002 reports and 2026 predictions are unchanged.

Example: 2022 unrounded mean error=12.6667. Full projected dynamic_01 error=11.7895 but final error=12, the same integer vector as mean. Full projected ridge_10 error=16.8354; its 25%-corrected projected error=13.1813, also rounded to mean's vector/error12. Ties therefore conceal both slightly better and worse continuous estimates. This does not select a method.

Reproduce with Node's built-ins only (optional diagnostic runtime, no npm install):

```sh
node tests/test_screening_diagnostics.mjs
node scripts/screening_diagnostics.mjs --out-dir output/screening-diagnostics
```

The report contains standalone SVG plots. Optional export-quality PNGs use base R, no packages:

```sh
Rscript scripts/plot_screening_diagnostics.R output/screening-diagnostics
```

This host's Python launcher cannot start its registered Windows Store interpreter, so new diagnostics ran in the available JavaScript runtime and optional R 4.5.3. No Python/ML dependencies were installed. The baseline workflow now invokes the diagnostic checks with Node; that workflow modification has not yet been verified in a new hosted run. The original Python test suite was not rerun locally for this analysis-only change.

## What is still needed before using more polls?

Runtime is not the limiting factor. Approximately 790 main-table index candidates exist, but the active historical input has 24 reviewed releases. Twelve earlier releases supply one poll per group/election; 2021/2022 each supply six releases. More rows can improve campaign coverage and trajectories, but cannot create more independent election outcomes.

1. **Availability dates:** index dates often mean fieldwork, not publication. Obtain publication and known update dates before allowing a release at a historical cutoff. Preserve uncertain originals and branch a sensitivity alternative rather than rewriting them.
2. **Poll identity:** reconcile the same poll syndicated by several publishers and distinguish pollster from commissioner. A duplicate cannot count as extra independent evidence.
3. **Actual lineup:** exclude hypothetical alliances; map labels to the lists contesting that election. In April 2019 Hadash-Taal and Raam-Balad are separate; later Joint List and current form mappings cannot be applied backwards.
4. **Measurement/completeness:** distinguish seats, below-threshold percentages, bloc totals and reference/result rows. A dash is not automatically zero. Complete allocations must reconcile to 120 before omitted-seat zeros are inferred.
5. **Coverage and metadata:** replace the unusually old third 2015 poll if a newer verified one is available; test Walla 2020 fieldwork-vs-publication age. Add repeated releases per group inside the configured window so earlier folds have actual trend features.
6. **Evaluation:** keep whole elections chronological. Score the same candidates on the same eligible cutoffs, with matched continuous/integer controls. Multiple cutoffs can diagnose horizon behavior but share one election result; do not randomly split them into independent training/test examples.

These are preparation tasks, not permission to alter official outcomes to improve model scores. Larger CBS/INES tables remain outside this national poll-correction experiment because historical release availability and the connection to the target need a separate design. Locality forecasting remains deferred.

Recommended next expansion: a bounded audit of additional repeated releases in the earlier four campaigns, followed by the unchanged grid and fixed cutoff rules. Choose coverage before inspecting new errors. Keep source-date sensitivity separate from model/shrinkage sensitivity.

## Zero seats: withdrawal, threshold risk, and sparsity

- **Withdrawal/nonparticipation:** use a dated eligibility fact. A confirmed non-running list should have zero seats in current scenarios, while retaining the submission field. Do not automatically redistribute its former supporters or change past-election identities.
- **Running below threshold:** model uncertain representation, ideally from original vote-share/below-threshold evidence and a verified allocator. A zero-or-positive outcome is different from a small smooth correction around four seats. Avoid a hindsight rule specifically trained to erase Meretz in 2022.
- **L0 on regression coefficients:** selects a small set of predictive features. It does not directly set a party's forecast to zero. L1 on coefficients likewise zeros coefficients, not necessarily seat predictions.
- **L0 on the final seat vector:** penalizes the number of represented parties. This can produce zeros, but also favors eliminating small parties without identifying which should fail. Its penalty and target need historical evaluation. It is not inherently a stronger version of ridge; it imposes a different structural preference.
- **L1 on nonnegative seats totaling 120:** equals 120 for every candidate, so adding it cannot induce seat-vector sparsity under those constraints. An L0 term is not constant, but requires a representation-aware decision design and justification.

Current source check: N12 records Gantz's withdrawal announcement on October 19, 2026, updated that evening ([report](https://www.mako.co.il/news-israel-elections/2026/Article-02450f1362451a1026.htm)). Zman Israel reports on October 21 that the CEC said all Blue and White candidates completed withdrawal and its ballot would not be available ([report](https://www.zman.co.il/live/735242/)). These are publisher reports; a directly retrieved CEC notice is not archived here. The user's nonparticipation statement is supported by this reporting. This diagnostic update records the evidence but does not change the frozen current forecast or implement an eligibility constraint.

Hands-on/cumulative effort remains unmeasured; total project budget is not reset. No final method, representation penalty, new forecast or competition submission was selected.
