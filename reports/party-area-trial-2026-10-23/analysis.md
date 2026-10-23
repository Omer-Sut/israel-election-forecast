# Party-area trial: better coverage, no demonstrated forecasting gain

The new features genuinely change the fitted models. They do **not** establish an improvement over the simple poll mean. Retain the mean as the reference; do not adopt a demographic correction from this experiment.

## What we actually tested

We expanded from three party cores to explicit previous-list mappings, leaving splits/new entrants missing. Five separate predecessor pools are optional assumptions, not inferred voter transfers. We compared the original features, dated 15-city context, and a broader 2015 socioeconomic edition-linked sensitivity, each with/without pools. The broader arm covers 1,183 localities; its dated August 2019 publication and spot checks do not authenticate every archived workbook value. It remains a separate retrospective assumption, not a certified real-time reconstruction.

Three existing learners—ridge_10, forest_3_5, xgb_2_50—use the same audited 27-release history, six national elections, T-1 cutoffs and seed 20261021. No new model grid. Earlier completed elections train each later forecast. This is still **seat-residual prediction**, not a newly fitted raw-vote-share or bottom-up locality model.

For target election k, predecessor pool P and locality characteristic z, the appended area feature is

`g[k,P] = sum(votes[k-1,P,locality] * z[locality]) / sum(matched votes[k-1,P,locality])`.

We also append matched/national predecessor-vote coverage, missingness and a pooled-proxy indicator. Pool votes BEFORE averaging. Only previous-election locality results enter; special ballots are excluded, and ballot totals are not added a second time. These characterize areas of earlier support, not individual voters.

## Coverage improved—but identity still limits the experiment

In 2022, continuity mappings supply 10/16 modeled lists; allowing National Unity's explicit Blue and White + New Hope pool gives 11/16. Among those 11 profiles, the unweighted mean predecessor-vote coverage rises from 39.6% in the city subset to 90.0% in the broader arm. This is NOT 90% of target-election voters identified, nor a national vote-weighted coverage estimate.

In 2021, only 4/14 lists have a usable whole-list predecessor: Likud, Shas, UTJ and YisraelBeiteinu. Their average coverage rises 52.3%→93.9%, but more localities do not resolve BlueWhite/YeshAtid, JointList/Raam, Labor/Meretz or newly formed NewHope. We did not invent a division of those earlier combined votes. This is a major limitation precisely where the poll baseline had important misses.

## Accuracy, including before rounding

[Performance plot](performance.svg) shows fixed 25% corrections across the four strict OOF elections. Lower total absolute seat error is better. The lines are different: the new inputs reach the learners. There is no fixed 25% improvement over the mean in either 2021 or 2022.

| Fixed 25% example | 2021 integer / continuous loss | 2022 integer / continuous loss |
|---|---:|---:|
| Poll mean | 20 / 20.667 | 12 / 12.667 |
| Original forest | 26 / 23.011 | 14 / 13.598 |
| Broader edition + pools, forest | 24 / 23.038 | 12 / 13.301 |
| Original XGBoost | 22 / 22.200 | 14 / 13.388 |
| Broader edition + pools, XGBoost | 20 / 22.004 | 14 / 13.110 |

The last row illustrates why rounding diagnostics matter: integer 2021 loss improves to a tie while continuous loss remains worse than the mean. Integer ties alone are not evidence of identical models or equally accurate continuous estimates.

Seven existing correction strengths were also checked. For each FIXED learner/feature set, we selected the strength using at least two strictly earlier OOF elections, separately minimizing continuous or integer L1. Neither selection route beats the mean's integer loss in 2021/2022. In 2022, integer-loss selection chooses zero correction for every ridge/forest arm and four of five XGBoost arms; broader+pools XGBoost instead chooses 25% and worsens to 14. Continuous-loss selection is not a cure: it can prefer stronger corrections that worsen later integer loss. This does not establish that25% is universally excessive or that zero is universally optimal.

There is one small hindsight-only result worth preserving: broader+pools ridge at 5% gives2022 continuous loss 12.576 versus 12.667, with the same 12 integer loss. Earlier-OOF selection did NOT choose 5%. Picking it now because of its2022score would be retrospective tuning, not validation. No nonzero setting improves2021 continuous loss in this bounded trial.

## Decision and next work

Keep the explicit lineage/context machinery and missing-data audit as reusable preparation. Do not add this correction to the current forecast, claim demographics are generally useless, or expand the same tuning exercise on these already-inspected outcomes.

The next practical priority is auditing the final current polls, current list status and original below-threshold measurements. Those directly address the forecast inputs and representation risk. Age/sex features still require a separate historical release-date audit; a census reference year alone is insufficient. A future transfer model must supply defensible information about splits rather than silently subdividing combined votes. Turnout/war/economics remain later as requested.

## Verified execution and files

Implementation **1fcca3da08f4c6a66bdf55c20f345db351b1c961**, [PR17](https://github.com/Omer-Sut/israel-election-forecast/pull/17), stacked on PR16 and unmerged. [Screen39921492239](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39921492239) passed all 60 tests, earlier deterministic checks and two identical E006 context/coverage/score/selection/SVG runs. E006first-run runtime 6.231 seconds. [Baseline39921492335](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39921492335) also succeeded, reproducing frozen forecasts/database/CBS reports. Output code SHA93e1e7dd2592a72466b3007943bf032dddf542b7 is GitHub's tested PR merge ref, NOT a claim that the PR was merged.

[Full artifact](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39921492239/artifacts/12486559561): 138,283 bytes, verified unexpired through November 22. Includes per-list vectors and generated configs; compact tracked files preserve all 420 scalar scores, 180 selection rows, contexts/coverage, plot and provenance. scores-metrics.csv is scores.csv with only the two bulky prediction-vector columns omitted. Logged public text was decoded for curation; no binary artifact-byte download/hash verification or visual image QA is claimed. Input hashes and pinned environment support rebuilds after artifact expiry.

Initial 770065d run 39921070292 failed on an import pointing to the wrong module. Corrected before the successful run; no failed output was used. No local scientific run, current forecast change, merge or submission. User hands-on/cumulative effort remains unmeasured.
