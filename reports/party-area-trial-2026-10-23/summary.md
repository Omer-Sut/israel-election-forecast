# E006: expanded party-area context trial

No current forecast, turnout, poll weights, merge or submission changed.
Only three fixed existing learners, one expanded audited history, T-1 and earlier-election training. No new model/hyperparameter grid.

## Fixed 25% corrections: final comparison elections

| Features | Method | 2021 integer / continuous error | 2022 integer / continuous error |
|---|---|---:|---:|
| original | ridge_10 | 24 / 22.428 | 12 / 13.761 |
| original | forest_3_5 | 26 / 23.011 | 14 / 13.598 |
| original | xgb_2_50 | 22 / 22.200 | 14 / 13.388 |
| cities_continuity | ridge_10 | 24 / 22.583 | 14 / 14.053 |
| cities_continuity | forest_3_5 | 24 / 23.319 | 12 / 13.402 |
| cities_continuity | xgb_2_50 | 22 / 22.206 | 14 / 13.096 |
| cities_pooled | ridge_10 | 24 / 22.491 | 14 / 13.989 |
| cities_pooled | forest_3_5 | 24 / 23.346 | 12 / 13.323 |
| cities_pooled | xgb_2_50 | 24 / 22.687 | 12 / 13.409 |
| edition2015_continuity | ridge_10 | 24 / 22.512 | 14 / 13.687 |
| edition2015_continuity | forest_3_5 | 24 / 23.264 | 12 / 13.407 |
| edition2015_continuity | xgb_2_50 | 22 / 21.791 | 14 / 13.310 |
| edition2015_pooled | ridge_10 | 24 / 22.472 | 14 / 13.472 |
| edition2015_pooled | forest_3_5 | 24 / 23.038 | 12 / 13.301 |
| edition2015_pooled | xgb_2_50 | 20 / 22.004 | 14 / 13.110 |

Reference integer errors: 2021=20; 2022=12. Lower is better.

See selection.csv for correction fractions chosen using continuous OR integer loss on at least two earlier OOF elections. Feature sets and model IDs themselves are NOT selected by this inner rule.

City profiles use the dated 2018 release. Full 2015 edition (1183 localities) begins only after2019-08-31, falling back to the city subset before then. Its dated publication/table linkage and spot checks do NOT authenticate an archived workbook or prove absence of revisions; remains separately labeled retrospective sensitivity. No CBS historical_availability flag changed.

Continuity means an explicit retained-party/whole-alliance geographic proxy, not unchanged voters. Pooled mode adds five explicit predecessor pools. Splits/new lists remain missing. Previous votes are pooled BEFORE averaging characteristics; no seats or target-election votes enter geographic features. Coverage is matched predecessor votes / predecessor NATIONAL votes, not target votes.

All appended features are exported by target in contexts.csv with source election, codes, labels, date, vintage tier and missing reason. Four feature names: prior_area_index, matched_prior_vote_fraction, area_missing, pooled_lineage_proxy.

Age/sex remain outside historical fitting pending date audit. 2017 SES release/revision was located but is not fitted here. No individual voter demographic inference; no ballot-neighborhood claim. Previously inspected national outcomes are exploratory, not blind validation.

Runtime seconds=6.231; code_commit=93e1e7dd2592a72466b3007943bf032dddf542b7. Seed=20261021. User hands-on/cumulative effort unmeasured; no local setup required.
