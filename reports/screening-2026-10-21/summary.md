# Lightweight model screen — exploratory, no model selected

Real historical diagnostics below; synthetic smoke results are separate and contain no accuracy ranking.
The audited panel covers 2021/2022 only. Supervised 2022 predictions train on 2021; this is one training election, not sufficient validation.
25% correction around the latest-group mean; T−6 and T−1 remain separate. No current-election forecast is changed.

## T−6: real-data diagnostics

Each cell: total absolute seat error / total movement from rounded anchor. Missing fits are explicit.

| Configuration | knesset_24_2021 | knesset_25_2022 |
| --- | ---: | ---: |
| rounded_mean_reference | 24 / 0 | 12 / 0 |
| empirical_l1_consensus | 22 / 2 | 12 / 0 |
| recency_3 | 24 / 0 | 12 / 0 |
| recency_7 | 24 / 0 | 12 / 0 |
| recency_14 | 24 / 0 | 12 / 0 |
| ridge_1 | insufficient data | 12 / 2 |
| ridge_10 | insufficient data | 12 / 2 |
| ridge_100 | insufficient data | 12 / 0 |
| forest_2_5 | insufficient data | 12 / 2 |
| forest_3_5 | insufficient data | 12 / 2 |
| forest_3_10 | insufficient data | 12 / 0 |
| xgb_1_50 | insufficient data | 12 / 2 |
| xgb_2_50 | insufficient data | 12 / 6 |
| xgb_2_100 | insufficient data | 12 / 6 |
| dynamic_001 | 24 / 0 | 12 / 0 |
| dynamic_01 | 24 / 0 | 12 / 0 |
| dynamic_1 | 24 / 0 | 12 / 0 |
| ensemble_equal | insufficient data | 12 / 2 |
| ensemble_1 | insufficient data | insufficient data |
| ensemble_5 | insufficient data | insufficient data |
## T−1: real-data diagnostics

Each cell: total absolute seat error / total movement from rounded anchor. Missing fits are explicit.

| Configuration | knesset_24_2021 | knesset_25_2022 |
| --- | ---: | ---: |
| rounded_mean_reference | 20 / 0 | 12 / 0 |
| empirical_l1_consensus | 20 / 2 | 12 / 0 |
| recency_3 | 20 / 2 | 12 / 0 |
| recency_7 | 20 / 2 | 12 / 0 |
| recency_14 | 20 / 2 | 12 / 0 |
| ridge_1 | insufficient data | 14 / 2 |
| ridge_10 | insufficient data | 12 / 2 |
| ridge_100 | insufficient data | 12 / 0 |
| forest_2_5 | insufficient data | 14 / 4 |
| forest_3_5 | insufficient data | 14 / 4 |
| forest_3_10 | insufficient data | 12 / 0 |
| xgb_1_50 | insufficient data | 14 / 2 |
| xgb_2_50 | insufficient data | 14 / 2 |
| xgb_2_100 | insufficient data | 14 / 2 |
| dynamic_001 | 22 / 2 | 12 / 0 |
| dynamic_01 | 22 / 2 | 12 / 0 |
| dynamic_1 | 20 / 2 | 12 / 0 |
| ensemble_equal | insufficient data | 14 / 2 |
| ensemble_1 | insufficient data | insufficient data |
| ensemble_5 | insufficient data | insufficient data |

## Common-case summaries (descriptive, not a model ranking)

Compare each candidate with both references on exactly the same elections, separately by horizon.

| Method | Horizon | Elections | Mean error | Worst error | Mean reference | L1 reference |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| rounded_mean_reference | 6 | 2 | 18.00 | 24 | 18.00 | 17.00 |
| rounded_mean_reference | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| empirical_l1_consensus | 6 | 2 | 17.00 | 22 | 18.00 | 17.00 |
| empirical_l1_consensus | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| recency_3 | 6 | 2 | 18.00 | 24 | 18.00 | 17.00 |
| recency_3 | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| recency_7 | 6 | 2 | 18.00 | 24 | 18.00 | 17.00 |
| recency_7 | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| recency_14 | 6 | 2 | 18.00 | 24 | 18.00 | 17.00 |
| recency_14 | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| ridge_1 | 6 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| ridge_1 | 1 | 1 | 14.00 | 14 | 12.00 | 12.00 |
| ridge_10 | 6 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| ridge_10 | 1 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| ridge_100 | 6 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| ridge_100 | 1 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| forest_2_5 | 6 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| forest_2_5 | 1 | 1 | 14.00 | 14 | 12.00 | 12.00 |
| forest_3_5 | 6 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| forest_3_5 | 1 | 1 | 14.00 | 14 | 12.00 | 12.00 |
| forest_3_10 | 6 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| forest_3_10 | 1 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| xgb_1_50 | 6 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| xgb_1_50 | 1 | 1 | 14.00 | 14 | 12.00 | 12.00 |
| xgb_2_50 | 6 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| xgb_2_50 | 1 | 1 | 14.00 | 14 | 12.00 | 12.00 |
| xgb_2_100 | 6 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| xgb_2_100 | 1 | 1 | 14.00 | 14 | 12.00 | 12.00 |
| dynamic_001 | 6 | 2 | 18.00 | 24 | 18.00 | 17.00 |
| dynamic_001 | 1 | 2 | 17.00 | 22 | 16.00 | 16.00 |
| dynamic_01 | 6 | 2 | 18.00 | 24 | 18.00 | 17.00 |
| dynamic_01 | 1 | 2 | 17.00 | 22 | 16.00 | 16.00 |
| dynamic_1 | 6 | 2 | 18.00 | 24 | 18.00 | 17.00 |
| dynamic_1 | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| ensemble_equal | 6 | 1 | 12.00 | 12 | 12.00 | 12.00 |
| ensemble_equal | 1 | 1 | 14.00 | 14 | 12.00 | 12.00 |

## Turnout reference

- knesset_24_2021 T−6: persistence 71.52%; error 4.08 percentage points.
- knesset_24_2021 T−1: persistence 71.52%; error 4.08 percentage points.
- knesset_25_2022 T−6: persistence 67.44%; error 3.19 percentage points.
- knesset_25_2022 T−1: persistence 67.44%; error 3.19 percentage points.

## Synthetic software smoke checks

All 20 configurations (including two references) exercised; nonnegative integer totals verified.
Synthetic outcomes are used only to exercise code paths, including optimized ensemble weights. They are never election evidence.

## Limits and next steps

- Only two original-source-audited elections currently available; both outcomes already inspected.
- One-election supervised fits are diagnostic only; no final model ranking or current forecast.
- Bulk poll indexes, CBS and INES data are not model inputs; historical availability remains unaudited.
- Polls/party rows and repeated horizons are dependent; only elections count as independent outcomes.
- Dynamic filter variances and 25% shrinkage are experimental defaults, not calibrated uncertainty.
- Integer sum-120 arithmetic is enforced; no vote-to-seat allocator or electoral attainability claim.
- Optimized ensemble real-data fitting awaits two earlier strict OOF elections.
- Next: audit three-group panels for 2015, April/September 2019 and 2020; enable strict chronological comparisons before narrowing models.
- Full provenance, configurations, statuses, continuous corrections, representation errors and unshrunk diagnostics: `experiments.json`; per-list output: `predictions.csv`.
- Excluded historical cases: 0.
