# E005: what the trial changes

The user-directed trial ran on GitHub. All55 tests passed; the frozen baseline, panel rebuild, deterministic model predictions and earlier experiments reproduced. Final implementation4275c5484ccd2525923d89c9f45e13b7dce2b272; [screen39776060120](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39776060120), [baseline39776062476](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39776062476). New trial compute37.133seconds. No current forecast, turnout, final model or poll weights changed. PR #16 is stacked on PR #15; no merge.

## Individual poll errors

Each poll is scored against final allocated seats: `E=sum(abs(poll_seats-final_seats))`. A one-seat reassignment changes this loss by two. Sample variance below is across polls' total errors, in squared seat-error units. This measures election-forecast error, not pure survey quality: real changes in opinion between fieldwork and election day and threshold allocation also contribute.

Of790main-table index candidates,324passed the explicit numerical/final-lineup mapping rules and exact-signature deduplication;466exclusions remain in index-exclusions.json. These are retained lower-tier index rows, NOT324certified independent publications or every poll ever published. Dates are proxies; syndicated duplicates and source-vintage issues remain. Do not pool these with27audited releases as independent evidence or train forecast weights on them.

| Campaign | Retained index N | Mean total absolute seat error | Sample variance | Audited release N | Audited mean error |
|---|---:|---:|---:|---:|---:|
|2015|86|22.95|11.17|3|22.67|
|April2019|60|35.57|48.15|4|36.50|
|September2019|41|15.66|10.98|4|13.00|
|2020|42|11.29|7.38|4|9.50|
|2021|46|29.39|45.49|6|22.33|
|2022|49|14.16|2.97|6|15.00|

[Plot](poll-error-trends.svg), [campaign/window statistics](campaign-summary.csv), [creator/horizon summaries](poll-patterns.csv), [individual rows and original references](poll-errors.csv). All retained dates, last90days and last14days are kept separate. These are different convenience samples across campaigns, not controlled estimates of universal polling quality.

Recency is informative but not universal. Retained2021 index rows average33.56error31-90days out versus20.00in the final7days;2020 averages13.29versus8.73. April2019 reverses that pattern:30.18versus41.17. Different pollster composition, true opinion movement and threshold misses are potential contributors; this analysis does not identify causal effects.

Creators are stratified by campaign/horizon. Audited aliases Midgam/Fuchs are normalized explicitly with creator_raw preserved; broad index combined labels are not certified firm identities. Sample sizes are known for22/27audited releases (500-2087), absent from the bulk metadata. This is too little to establish a reliable sample-size or house-quality multiplier; larger samples do not remove systematic bias.

## Proposed quality/severity score

Prototype predicts a poll's expected final-election absolute error from lead time, sample size/missingness and creator, training on strictly earlier campaigns only. A severity ratio `observed_error/expected_error` is exported, alongside an unnormalized inverse-expected-error weight. These are diagnostic candidates, not calibrated probabilities or adopted weights.

Chronological expected-error prediction MAE=9.233; simply predicting earlier campaigns' average error gives8.668. Lower is better. This first quality model does NOT earn adoption. These MAEs measure prediction of poll errors, not the competition loss of a seat forecast. Final competition scoring must not be rescaled by poll reputation; disagreement with a withheld poll can only be an auxiliary diagnostic.

## Features and chronological regularization

Compared original inputs, dynamic-filter gap, a dated geographic feature, and both together, under original/expanded campaign history. Same small ridge/forest/XGBoost grids; correction fractions0/2.5/5/10/25/50/100%. Parameters and fractions are selected on at least two strictly earlier out-of-fold elections, never the election they are evaluated on. Loss ties prefer smaller corrections. Early cases without enough validation history fall back to the mean. Earlier inspected outcomes remain exploratory, not new blind evidence.

The selector often chooses zero correction. Adding features changes selected parameters/predictions, but no selected configuration improves on reference20/12in2021/2022. Some geographic features reduce a forest's2021loss26to24on original history; that still loses to20. Dynamic features are mixed rather than a demonstrated improvement. This does not establish an optimal universal fraction or disprove richer geographic models.

## Geographic features actually tried versus remaining work

Broad209party-area profiles are exported with age/sex/SES coverage flags, but remain descriptive. These are characteristics of places where votes came from, not individual voters. They cannot use the target election's votes or later CBS releases as historical predictors.

A restricted trial IS fitted: the dated [CBS November28,2018 release](https://www.cbs.gov.il/he/mediarelease/DocLib/2018/351/24_18_351b.pdf) gives2015index values for15large cities. For Shas/UTJ/Yisrael Beiteinu only, use the PREVIOUS election's votes to form a vote-weighted city index, coverage fraction and missing flag. City codes/names are checked against official results.2021vote coverage in those cities is approximately50.4%/64.1%/46.2%, respectively. This is partial coverage and restricted identity continuity, not full national demographic modeling. No age/sex feature or new-alliance lineage has yet been admitted to historical training.

Next useful work: extend dated demographic coverage and explicit prior-party/merger mappings, then rerun the fixed ablation. Do not replace missing lineage with reused ballot codes or post-election outcomes. Turnout/political-war-economic work remains later. Refresh current poll inputs after Friday's final releases as separately planned; no unattended collection schedule is configured.

## Arithmetic and files

Projection first and largest-remainder allocation second preserve120; ordinary independent rounding is not used. Added explicit post-rounding integer/nonnegative/sum120 assertion, in addition to existing score validation. Original numerical forecasts reproduced.

This directory preserves compact results and original-source attribution. The2MBuncompressed full parameter-sensitivity CSV is deliberately left in the [complete artifact](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39776060120/artifacts/12424098121), verified203126compressed bytes/unexpired throughNovember21. Code/config/audits rebuild it; artifact expiry does not erase required inputs. Full raw source archives and restricted INES respondent data are not duplicated here. Manifest commit efb6675 is a tested PR merge ref, not a claim that this PR was merged. Cumulative hands-on effort remains unmeasured/not reset.

