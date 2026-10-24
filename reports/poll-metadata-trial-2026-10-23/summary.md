# E008: poll metadata in training

All fits use earlier elections only. Four eligible OOF elections; 2021/2022 are previously inspected comparisons.
Aggregate control; individual polls with seats/zero/lead time; added source metadata; added past-only training weights.
Reliability alters training weights only. Target latest-group predictions are averaged equally. Missing metadata stays explicit.
No party-identity continuity is inferred. Creator-by-seat-size interactions are not a party-specific house-effect model.

| Inputs | Learner | 2021 fixed25% / selected | 2022 fixed25% / selected |
|---|---|---:|---:|
| aggregate | ridge_10 | 24 / 30 (fraction 1) | 12 / 12 (fraction 0) |
| aggregate | forest_3_5 | 26 / 26 (fraction 0.25) | 14 / 12 (fraction 0) |
| aggregate | xgb_2_50 | 22 / 22 (fraction 0.05) | 14 / 12 (fraction 0) |
| poll_basic | ridge_10 | 24 / 20 (fraction 0) | 12 / 12 (fraction 0) |
| poll_basic | forest_3_5 | 22 / 20 (fraction 0) | 14 / 12 (fraction 0) |
| poll_basic | xgb_2_50 | 20 / 20 (fraction 0) | 14 / 12 (fraction 0) |
| poll_metadata | ridge_10 | 24 / 22 (fraction 0.05) | 12 / 12 (fraction 0) |
| poll_metadata | forest_3_5 | 22 / 20 (fraction 0) | 14 / 12 (fraction 0) |
| poll_metadata | xgb_2_50 | 20 / 20 (fraction 0) | 14 / 12 (fraction 0) |
| poll_metadata_weighted | ridge_10 | 24 / 22 (fraction 0.05) | 12 / 12 (fraction 0) |
| poll_metadata_weighted | forest_3_5 | 22 / 20 (fraction 0) | 14 / 12 (fraction 0) |
| poll_metadata_weighted | xgb_2_50 | 20 / 20 (fraction 0) | 14 / 12 (fraction 0) |

Reference errors: 2021=20, 2022=12. Lower is better. Full continuous errors and vectors are in results.json.
Correction fractions {0,5,25,100}% chosen on at least two strictly earlier OOF campaigns; ties prefer zero/smaller corrections. Families/ablations are not automatically selected.
No claim of independent poll/party samples, calibrated reliability or superiority from a hindsight best cell. Training balances campaigns and firms before bounded reliability adjustment.
Sampling design, effective sample size, panel provider, likely-voter and undecided rules require additional audited metadata; they are not invented from publisher names.
