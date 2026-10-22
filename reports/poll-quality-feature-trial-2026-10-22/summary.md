# E005 bounded research trial

All results exploratory; no current forecast/turnout/model/poll-weight change.

Poll rows: audited=27, exploratory mapped index=324. See explicit exclusions; these are not certified independent releases.

## Campaign errors, all retained pre-election rows

| Tier | Election | N | Mean total absolute seat error | Sample variance |
|---|---|---:|---:|---:|
| audited_release | knesset_20_2015 | 3 | 22.667 | 1.3333333333333333 |
| audited_release | knesset_21_2019apr | 4 | 36.500 | 19.666666666666668 |
| audited_release | knesset_22_2019sep | 4 | 13.000 | 12 |
| audited_release | knesset_23_2020 | 4 | 9.500 | 1 |
| audited_release | knesset_24_2021 | 6 | 22.333 | 7.066666666666666 |
| audited_release | knesset_25_2022 | 6 | 15.000 | 6 |
| index_exploratory_not_certified | knesset_20_2015 | 86 | 22.953 | 11.174281805745554 |
| index_exploratory_not_certified | knesset_21_2019apr | 60 | 35.567 | 48.14802259887006 |
| index_exploratory_not_certified | knesset_22_2019sep | 41 | 15.659 | 10.980487804878049 |
| index_exploratory_not_certified | knesset_23_2020 | 42 | 11.286 | 7.379790940766551 |
| index_exploratory_not_certified | knesset_24_2021 | 46 | 29.391 | 45.48792270531401 |
| index_exploratory_not_certified | knesset_25_2022 | 49 | 14.163 | 2.9727891156462585 |

## Chronological parameter selection: 2021/2022

| History | Features | Election | Family | Selected | Fraction | Loss / mean loss |
|---|---|---|---|---|---:|---:|
| reference | original | knesset_24_2021 | dynamic | dynamic_1 | 1 | 20 / 20 |
| reference | original | knesset_24_2021 | forest | forest_3_5 | 0.5 | 26 / 20 |
| reference | original | knesset_24_2021 | recency | recency_14 | 0 | 20 / 20 |
| reference | original | knesset_24_2021 | ridge | ridge_1 | 0.05 | 22 / 20 |
| reference | original | knesset_24_2021 | xgboost | xgb_1_50 | 0 | 20 / 20 |
| reference | original | knesset_25_2022 | dynamic | dynamic_1 | 1 | 12 / 12 |
| reference | original | knesset_25_2022 | forest | forest_2_5 | 0 | 12 / 12 |
| reference | original | knesset_25_2022 | recency | recency_14 | 0 | 12 / 12 |
| reference | original | knesset_25_2022 | ridge | ridge_1 | 0 | 12 / 12 |
| reference | original | knesset_25_2022 | xgboost | xgb_1_50 | 0 | 12 / 12 |
| reference | dynamic_gap | knesset_24_2021 | dynamic | dynamic_1 | 1 | 20 / 20 |
| reference | dynamic_gap | knesset_24_2021 | forest | forest_3_5 | 0.5 | 26 / 20 |
| reference | dynamic_gap | knesset_24_2021 | recency | recency_14 | 0 | 20 / 20 |
| reference | dynamic_gap | knesset_24_2021 | ridge | ridge_100 | 0.25 | 22 / 20 |
| reference | dynamic_gap | knesset_24_2021 | xgboost | xgb_1_50 | 0 | 20 / 20 |
| reference | dynamic_gap | knesset_25_2022 | dynamic | dynamic_1 | 1 | 12 / 12 |
| reference | dynamic_gap | knesset_25_2022 | forest | forest_2_5 | 0 | 12 / 12 |
| reference | dynamic_gap | knesset_25_2022 | recency | recency_14 | 0 | 12 / 12 |
| reference | dynamic_gap | knesset_25_2022 | ridge | ridge_1 | 0 | 12 / 12 |
| reference | dynamic_gap | knesset_25_2022 | xgboost | xgb_1_50 | 0 | 12 / 12 |
| reference | prior_city_core | knesset_24_2021 | dynamic | dynamic_1 | 1 | 20 / 20 |
| reference | prior_city_core | knesset_24_2021 | forest | forest_2_5 | 0.5 | 24 / 20 |
| reference | prior_city_core | knesset_24_2021 | recency | recency_14 | 0 | 20 / 20 |
| reference | prior_city_core | knesset_24_2021 | ridge | ridge_1 | 0.05 | 22 / 20 |
| reference | prior_city_core | knesset_24_2021 | xgboost | xgb_1_50 | 0.1 | 22 / 20 |
| reference | prior_city_core | knesset_25_2022 | dynamic | dynamic_1 | 1 | 12 / 12 |
| reference | prior_city_core | knesset_25_2022 | forest | forest_2_5 | 0 | 12 / 12 |
| reference | prior_city_core | knesset_25_2022 | recency | recency_14 | 0 | 12 / 12 |
| reference | prior_city_core | knesset_25_2022 | ridge | ridge_1 | 0 | 12 / 12 |
| reference | prior_city_core | knesset_25_2022 | xgboost | xgb_1_50 | 0 | 12 / 12 |
| reference | dynamic_plus_prior_city_core | knesset_24_2021 | dynamic | dynamic_1 | 1 | 20 / 20 |
| reference | dynamic_plus_prior_city_core | knesset_24_2021 | forest | forest_2_5 | 0.5 | 24 / 20 |
| reference | dynamic_plus_prior_city_core | knesset_24_2021 | recency | recency_14 | 0 | 20 / 20 |
| reference | dynamic_plus_prior_city_core | knesset_24_2021 | ridge | ridge_100 | 1 | 24 / 20 |
| reference | dynamic_plus_prior_city_core | knesset_24_2021 | xgboost | xgb_1_50 | 0 | 20 / 20 |
| reference | dynamic_plus_prior_city_core | knesset_25_2022 | dynamic | dynamic_1 | 1 | 12 / 12 |
| reference | dynamic_plus_prior_city_core | knesset_25_2022 | forest | forest_2_5 | 0 | 12 / 12 |
| reference | dynamic_plus_prior_city_core | knesset_25_2022 | recency | recency_14 | 0 | 12 / 12 |
| reference | dynamic_plus_prior_city_core | knesset_25_2022 | ridge | ridge_1 | 0 | 12 / 12 |
| reference | dynamic_plus_prior_city_core | knesset_25_2022 | xgboost | xgb_1_50 | 0 | 12 / 12 |
| expanded_history | original | knesset_24_2021 | dynamic | dynamic_001 | 1 | 22 / 20 |
| expanded_history | original | knesset_24_2021 | forest | forest_2_5 | 0.25 | 26 / 20 |
| expanded_history | original | knesset_24_2021 | recency | recency_14 | 0 | 20 / 20 |
| expanded_history | original | knesset_24_2021 | ridge | ridge_1 | 0.5 | 26 / 20 |
| expanded_history | original | knesset_24_2021 | xgboost | xgb_2_100 | 0.05 | 22 / 20 |
| expanded_history | original | knesset_25_2022 | dynamic | dynamic_001 | 1 | 12 / 12 |
| expanded_history | original | knesset_25_2022 | forest | forest_2_5 | 0 | 12 / 12 |
| expanded_history | original | knesset_25_2022 | recency | recency_14 | 0 | 12 / 12 |
| expanded_history | original | knesset_25_2022 | ridge | ridge_1 | 0 | 12 / 12 |
| expanded_history | original | knesset_25_2022 | xgboost | xgb_1_50 | 0.1 | 12 / 12 |
| expanded_history | dynamic_gap | knesset_24_2021 | dynamic | dynamic_001 | 1 | 22 / 20 |
| expanded_history | dynamic_gap | knesset_24_2021 | forest | forest_2_5 | 0 | 20 / 20 |
| expanded_history | dynamic_gap | knesset_24_2021 | recency | recency_14 | 0 | 20 / 20 |
| expanded_history | dynamic_gap | knesset_24_2021 | ridge | ridge_10 | 0.5 | 24 / 20 |
| expanded_history | dynamic_gap | knesset_24_2021 | xgboost | xgb_2_100 | 0.05 | 20 / 20 |
| expanded_history | dynamic_gap | knesset_25_2022 | dynamic | dynamic_001 | 1 | 12 / 12 |
| expanded_history | dynamic_gap | knesset_25_2022 | forest | forest_2_5 | 0 | 12 / 12 |
| expanded_history | dynamic_gap | knesset_25_2022 | recency | recency_14 | 0 | 12 / 12 |
| expanded_history | dynamic_gap | knesset_25_2022 | ridge | ridge_10 | 0.5 | 14 / 12 |
| expanded_history | dynamic_gap | knesset_25_2022 | xgboost | xgb_2_100 | 0.05 | 12 / 12 |
| expanded_history | prior_city_core | knesset_24_2021 | dynamic | dynamic_001 | 1 | 22 / 20 |
| expanded_history | prior_city_core | knesset_24_2021 | forest | forest_2_5 | 0.25 | 26 / 20 |
| expanded_history | prior_city_core | knesset_24_2021 | recency | recency_14 | 0 | 20 / 20 |
| expanded_history | prior_city_core | knesset_24_2021 | ridge | ridge_1 | 0.5 | 26 / 20 |
| expanded_history | prior_city_core | knesset_24_2021 | xgboost | xgb_2_100 | 0.05 | 20 / 20 |
| expanded_history | prior_city_core | knesset_25_2022 | dynamic | dynamic_001 | 1 | 12 / 12 |
| expanded_history | prior_city_core | knesset_25_2022 | forest | forest_2_5 | 0 | 12 / 12 |
| expanded_history | prior_city_core | knesset_25_2022 | recency | recency_14 | 0 | 12 / 12 |
| expanded_history | prior_city_core | knesset_25_2022 | ridge | ridge_1 | 0 | 12 / 12 |
| expanded_history | prior_city_core | knesset_25_2022 | xgboost | xgb_2_100 | 0.05 | 12 / 12 |
| expanded_history | dynamic_plus_prior_city_core | knesset_24_2021 | dynamic | dynamic_001 | 1 | 22 / 20 |
| expanded_history | dynamic_plus_prior_city_core | knesset_24_2021 | forest | forest_2_5 | 0 | 20 / 20 |
| expanded_history | dynamic_plus_prior_city_core | knesset_24_2021 | recency | recency_14 | 0 | 20 / 20 |
| expanded_history | dynamic_plus_prior_city_core | knesset_24_2021 | ridge | ridge_10 | 0.5 | 26 / 20 |
| expanded_history | dynamic_plus_prior_city_core | knesset_24_2021 | xgboost | xgb_2_100 | 0.05 | 20 / 20 |
| expanded_history | dynamic_plus_prior_city_core | knesset_25_2022 | dynamic | dynamic_001 | 1 | 12 / 12 |
| expanded_history | dynamic_plus_prior_city_core | knesset_25_2022 | forest | forest_2_5 | 0 | 12 / 12 |
| expanded_history | dynamic_plus_prior_city_core | knesset_25_2022 | recency | recency_14 | 0 | 12 / 12 |
| expanded_history | dynamic_plus_prior_city_core | knesset_25_2022 | ridge | ridge_1 | 0 | 12 / 12 |
| expanded_history | dynamic_plus_prior_city_core | knesset_25_2022 | xgboost | xgb_2_100 | 0.05 | 12 / 12 |

Audited-only error-prediction trial OOF MAE=9.233; prior campaign-mean baseline MAE=8.668. These are poll-error prediction losses, not seat-forecast competition losses. No weighting adopted.

Audited sample-size coverage: 22/27. Index sample sizes are unknown, not imputed.

Geographic footprint rows=209. All descriptive-only: CBS historical release dates unverified; current-election application additionally needs prior-election party/merger lineage. Profiles use2021 area demographics and2019 socioeconomic index. No individual demographic voting inference, no future-CBS historical model fitting.

In contrast to the broad descriptive profiles, the restricted prior-city-core ablation uses the dated November28,2018 CBS2015 press-release table, all15large cities, and only the PREVIOUS election votes for Shas/UTJ/Yisrael Beiteinu. Features: vote-weighted area index, matched-vote coverage, missing flag; no future/same-election outcomes, no new-alliance transfer assumptions. It is a partial geographic trial, not full age/sex/party-identity modeling.

Dynamic-gap ablation adds only a pre-cutoff filtered-level-minus-anchor feature, using fixed Q/R=1; no outcome enters feature extraction. Parameter/fraction selection uses at least two strictly earlier OOF elections; ties prefer smaller corrections. Earlier insufficient selections fall back to mean. Existing inspected outcomes are not new blind evidence.

Final integer allocations now have an explicit post-rounding sum120/nonnegative/integer assertion in addition to score validation. Largest-remainder allocation already preserves the total; independent nearest-integer rounding is not used.

Runtime seconds=37.133; commit=efb6675b548d6a0dc6174ed5b45926486f9a064e. Turnout/political-war-economic features deferred as requested.
