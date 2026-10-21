# Lightweight model screen — exploratory, no model selected

Real historical diagnostics below; synthetic smoke results are separate and contain no accuracy ranking.
Earlier elections provide training and chronological out-of-fold history; every displayed comparison configuration must run successfully. Both 2021/2022 outcomes were previously inspected.
25% correction around the latest-group mean; T−6 and T−1 remain separate. No current-election forecast is changed.

## Historical coverage and roles

Warm-up elections train models and generate earlier strict out-of-fold (OOF) predictions. Missing early fits are expected and never appear as failed comparison cells.

| Election | Horizon | Groups | Earlier training elections | Role |
| --- | ---: | ---: | ---: | --- |
| knesset_20_2015 | 1 | 3 | 0 | training_and_oof_history |
| knesset_21_2019apr | 1 | 3 | 1 | training_and_oof_history |
| knesset_22_2019sep | 1 | 3 | 2 | training_and_oof_history |
| knesset_23_2020 | 1 | 3 | 3 | training_and_oof_history |
| knesset_24_2021 | 1 | 3 | 4 | comparison |
| knesset_25_2022 | 1 | 3 | 5 | comparison |

## T−1: real-data diagnostics

Each cell: total absolute seat error / total movement from rounded anchor. Missing fits are explicit.

| Configuration | knesset_24_2021 | knesset_25_2022 |
| --- | ---: | ---: |
| rounded_mean_reference | 20 / 0 | 12 / 0 |
| empirical_l1_consensus | 20 / 2 | 12 / 0 |
| recency_3 | 20 / 2 | 12 / 0 |
| recency_7 | 20 / 2 | 12 / 0 |
| recency_14 | 20 / 2 | 12 / 0 |
| ridge_1 | 24 / 4 | 12 / 0 |
| ridge_10 | 24 / 4 | 12 / 0 |
| ridge_100 | 22 / 2 | 12 / 0 |
| forest_2_5 | 24 / 4 | 12 / 0 |
| forest_3_5 | 24 / 4 | 12 / 0 |
| forest_3_10 | 24 / 4 | 12 / 0 |
| xgb_1_50 | 24 / 4 | 12 / 0 |
| xgb_2_50 | 24 / 6 | 14 / 2 |
| xgb_2_100 | 24 / 6 | 14 / 2 |
| dynamic_001 | 22 / 2 | 12 / 0 |
| dynamic_01 | 22 / 2 | 12 / 0 |
| dynamic_1 | 20 / 2 | 12 / 0 |
| ensemble_equal | 24 / 4 | 12 / 0 |
| ensemble_1 | 22 / 2 | 12 / 0 |
| ensemble_5 | 24 / 4 | 12 / 0 |

## Common-case summaries (descriptive, not a model ranking)

Compare each candidate with both references on exactly the same elections, separately by horizon.

| Method | Horizon | Elections | Mean error | Worst error | Mean reference | L1 reference |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| rounded_mean_reference | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| empirical_l1_consensus | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| recency_3 | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| recency_7 | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| recency_14 | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| ridge_1 | 1 | 2 | 18.00 | 24 | 16.00 | 16.00 |
| ridge_10 | 1 | 2 | 18.00 | 24 | 16.00 | 16.00 |
| ridge_100 | 1 | 2 | 17.00 | 22 | 16.00 | 16.00 |
| forest_2_5 | 1 | 2 | 18.00 | 24 | 16.00 | 16.00 |
| forest_3_5 | 1 | 2 | 18.00 | 24 | 16.00 | 16.00 |
| forest_3_10 | 1 | 2 | 18.00 | 24 | 16.00 | 16.00 |
| xgb_1_50 | 1 | 2 | 18.00 | 24 | 16.00 | 16.00 |
| xgb_2_50 | 1 | 2 | 19.00 | 24 | 16.00 | 16.00 |
| xgb_2_100 | 1 | 2 | 19.00 | 24 | 16.00 | 16.00 |
| dynamic_001 | 1 | 2 | 17.00 | 22 | 16.00 | 16.00 |
| dynamic_01 | 1 | 2 | 17.00 | 22 | 16.00 | 16.00 |
| dynamic_1 | 1 | 2 | 16.00 | 20 | 16.00 | 16.00 |
| ensemble_equal | 1 | 2 | 18.00 | 24 | 16.00 | 16.00 |
| ensemble_1 | 1 | 2 | 17.00 | 22 | 16.00 | 16.00 |
| ensemble_5 | 1 | 2 | 18.00 | 24 | 16.00 | 16.00 |

## Turnout reference

- knesset_24_2021 T−1: persistence 71.52%; error 4.08 percentage points.
- knesset_25_2022 T−1: persistence 67.44%; error 3.19 percentage points.

## Synthetic software smoke checks

All 20 configurations (including two references) exercised; nonnegative integer totals verified.
Synthetic outcomes are used only to exercise code paths, including optimized ensemble weights. They are never election evidence.

## Limits and next steps

- 6 audited election panels; convenience poll coverage and retrospective source vintages remain limited.
- 2021/2022 outcomes already inspected; this is not a pristine blind holdout or a final model choice.
- Bulk poll indexes, CBS and INES data are not model inputs; historical availability remains unaudited.
- Polls/party rows and repeated horizons are dependent; only elections count as independent outcomes.
- Dynamic filter variances and 25% shrinkage are experimental defaults, not calibrated uncertainty.
- Integer sum-120 arithmetic is enforced; no vote-to-seat allocator or electoral attainability claim.
- Optimized weights require earlier strict OOF elections; unavailable warm-up fits are not comparison failures.
- Next: inspect stability and source-metadata sensitivities before narrowing the shortlist; six elections remain a small history.
- Full provenance, configurations, statuses, continuous corrections, representation errors and unshrunk diagnostics: `experiments.json`; per-list output: `predictions.csv`.
- Excluded historical cases: 0.
