# Analysis of the six-election screening results

Analysis date: October 21, 2026. This analyzes the saved E002 results; no models were refitted, parameters changed or new 2026 forecast produced. Read [the experiment protocol and source limits](six-election-screening.md), [comparison report](../reports/screening-six-elections-2026-10-21/summary.md) and [reproducible numerical analysis](../reports/screening-six-elections-2026-10-21/analysis.json).

## Main finding

**No candidate improved on the mean or L1 reference in either comparison election.** Retain both references as controls and do not replace the current forecast on this evidence. This is a recommendation from a small screen, not a final method choice or a finding that forests, boosting or GLMs can never help.

The score is total absolute seat error, summed across historical lists; lower is better. A one-seat transfer contributes two points when both affected list errors move by one. Means below weight the two elections equally.

| Family | 2021 error across configurations | 2022 error across configurations | Two-election mean across configurations |
| --- | ---: | ---: | ---: |
| Rounded mean / L1 references | 20 | 12 | 16 |
| Recency weighting | 20 | 12 | 16 |
| Gaussian GLM / ridge | 22–24 | 12 | 17–18 |
| Random forest | 24 | 12 | 18 |
| XGBoost | 24 | 12–14 | 18–19 |
| Dynamic polling | 20–22 | 12 | 16–17 |
| Ensemble | 22–24 | 12 | 17–18 |

All 18 candidates plus two references ran successfully for both comparison elections. There are no unavailable fits in these comparison cells. Early-history gaps remain visible in the full JSON/CSV: those elections supply training and earlier out-of-fold predictions, rather than a complete all-family comparison.

There are only **two comparison outcomes**, both already inspected before this run. The other four elections supply chronological history, not four additional blind comparisons. Eighteen related candidates and repeated settings are not eighteen independent pieces of evidence. Do not attach significance claims or precise confidence coverage to these results.

## What went wrong at the party level

### 2021: corrections usually moved seats in the wrong direction

The mean reference's largest errors were:

| Historical list | Predicted | Actual | Signed error |
| --- | ---: | ---: | ---: |
| Blue and White | 4 | 8 | −4 |
| New Hope | 10 | 6 | +4 |
| Joint List | 9 | 6 | +3 |
| Meretz | 4 | 6 | −2 |
| Yamina | 9 | 7 | +2 |

The first three contribute 11 of the total 20 error points. The pooled residual learners did not correct this pattern sufficiently. For example, `ridge_10` changed Labor 6→5, Likud 30→31, Religious Zionism/Otzma 5→4 and Yamina 9→10. Each change added one error point, taking total error from 20 to 24. Likud was already exact in the mean reference.

The mean and L1 references had the same total error but different allocations. L1 moved one seat from Joint List to Yamina: one error improved and another worsened. Equal score does not mean the same forecast.

Of the 18 candidates, four tied the mean's error and fourteen worsened it; none improved it. All changed at least one integer allocation. Across all 20 configurations there were only eight distinct final vectors.

### 2022: a representation miss dominates the remaining error

The mean reference predicted Meretz=4 versus actual=0 and Shas=8 versus actual=11. Those two lists contribute seven of the twelve absolute-error points. Every configuration still predicted Meretz representation. No method repaired this failure.

Sixteen of the eighteen candidates returned exactly the mean reference's integer vector. The exceptions were `xgb_2_50` and `xgb_2_100`, each worsening total error to 14. Across all 20 configurations there were only three distinct final vectors.

**Inference:** this implementation's smooth seat corrections do not directly address uncertain representation. Before imposing narrow party buffers, inspect threshold-sensitive outcomes: a small buffer around four can exclude zero. This motivates a later representation/scenario experiment, not a hindsight rule forcing Meretz or any current party below threshold. Published seat counts are not raw vote shares, and no verified vote-to-seat allocator has been implemented.

## Shrinkage and rounding explain many apparent ties

Every candidate is blended 25% toward its proposed adjustment, then jointly projected and integer-rounded. Matching the benchmark can therefore mean a correction was damped below an integer boundary; it does not mean the fitted model learned a zero correction.

For example, `ridge_10` proposed a continuous 2022 vector about 10.32 seats away from the unrounded anchor in total L1 distance. After 25% blending, the distance was about 2.58, yet the final integer vector exactly matched the rounded mean. Its fully unshrunk integer diagnostic had error 18, worse than the reference's 12.

Those continuous distances are measured before joint simplex projection. Projection can also remove an incoherent common shift across parties; do not attribute all disappearing movement to rounding alone.

All nine supervised configurations' fully unshrunk diagnostics were worse than the reference in both comparison elections: errors 24–32 in 2021 and 14–20 in 2022. This supports retaining conservative shrinkage for now; it does not establish that 25% is optimal or rule out every intermediate fraction.

Conversely, very small continuous corrections can change integer allocation near rounding ties. In 2021 `recency_14` moved only about 0.038 seats in continuous total L1 distance after blending, but rounding shifted one seat between lists (integer total movement=2). Record continuous and integer movements separately; an integer difference is not necessarily a strong change in estimated support.

## The feature panel is still sparse

The supervised fit for 2021 had **44 party rows from four earlier elections**. The 2022 fit had **58 rows from five earlier elections**. These rows share national election errors; they are not 44 or 58 independent elections.

All 44 rows from the first four elections have `trend_missing=1` and trend=0, because each earlier panel has only one release per polling group. Thus the 2021 supervised fit cannot learn a relationship between within-group trend and election error from those inputs. The 2022 fit adds fourteen 2021 rows with observed trends, leaving only one historical election with that information. The group-count feature is constant at three in every case.

The dynamic filter can consume the differently dated releases, but without repeated observations from the same group in the earlier panels, changes in the observed sequence can reflect pollster differences as well as time. This version does not fit house effects. Richer trajectory modeling needs more dated campaign releases, not just another model configuration.

**Inference:** insufficient transferable predictors and few election outcomes are plausible reasons for weak residual learning. The screen does not isolate their contribution from model choice, sparse poll coverage, source metadata, shrinkage or rounding. CBS/locality features and INES aggregates were not tested; their availability/target-alignment limits remain unresolved and locality forecasting stays deferred.

## Ensembles did fit, but historical weights did not transfer into gains

For 2021, learned weights use strict out-of-fold predictions from September 2019 and 2020. For 2022 they additionally use the earlier 2021 prediction and outcome. Neither fit sees its own target election result.

The lower-penalty ensemble assigned about 54.4% to the dynamic member, 20% each to recency/forest, 5.6% to XGBoost and zero to ridge before 2021. Before 2022 it shifted to roughly 68.0% recency, 27.3% dynamic and 4.7% ridge, with zero forest/boosting weight. The stronger penalty retained essentially equal weights in both cases.

An earlier forest result did improve on the mean in September 2019 (10 versus 12), but the same middle forest configuration worsened 2021 (24 versus 20). A gain on an earlier fold did not guarantee transfer. Optimized ensemble weights likewise did not beat the references on either comparison outcome.

The weight optimizer minimizes earlier **continuous unshrunk** absolute error, while the competition evaluates the final **shrunk integer** vector. This objective mismatch is a documented design limitation, not proof it caused the observed losses. Avoid interpreting a fitted weight as a causal measure of a model's quality or manually editing weights based on current results.

## Recommendations and next-session order

1. **Keep mean/L1 as controls; pause wider tree/boosting searches.** No challenger earned replacement in this screen. Recency and the responsive dynamic setting are inexpensive tied candidates, not proven improvements. Keep existing outputs frozen and do not permanently discard model families from two outcomes.
2. **Check source/coverage sensitivity before changing model knobs.** Predeclare one alternative using publication-age fallback for Walla 2020's inconsistent printed fieldwork metadata. Compare its features, earlier OOF predictions, ensemble weights and final vectors against the frozen run. Then seek a newer original-source-verified 2015 release for its unusually old third group; preserve minimum group coverage and document any replacement. These are proposed experiments, not completed analyses.
3. **Improve usable campaign history from already collected records.** Prioritize repeated releases per group near the same cutoffs for the earlier four elections, resolving dates/duplicates/lineups. This activates trend information and supports a meaningful dynamic comparison. Do not silently promote all index rows or collect more locality rows as a substitute for national outcomes.
4. **If time remains, predeclare a small shrinkage sensitivity:** alpha=0, 0.10 and 0.25 for a small retained set, using earlier folds for parameter decisions and labeling the already-inspected evaluation outcomes honestly. Report raw and final errors plus integer-vector identity. Do not call this new independent confirmation.
5. **Review representation handling before hard bounds or current deployment.** Audit available vote-share/below-threshold information first; any scenario/allocator must have a documented target and verified rules. Arithmetic-only point estimates can include flagged one/two-seat values. No calibrated CI, hard buffer or safe-party floor is selected.

Turnout remains separate: previous-election persistence missed by 4.08 percentage points in 2021 and 3.19 in 2022 (mean 3.635). This screen did not improve turnout; retain its research task because it is the tie-breaker.

## Resume from another session or device

At this handoff, all E002 work and this analysis are on **`feat/six-election-screening-panel`**, published through [PR #13](https://github.com/Omer-Sut/israel-election-forecast/pull/13), not merged at the last check. Main contains the older E001 screen. Do not assume checking out main gives this expanded panel. Inspect live Git/PR state for later changes.

For a fresh clone:

```sh
git clone https://github.com/Omer-Sut/israel-election-forecast.git
cd israel-election-forecast
git switch feat/six-election-screening-panel
```

Read `AGENTS.md`, README, competition brief, project-state, decisions and this analysis. Use **Actions → Screen lightweight forecast models → Run workflow**, choosing this branch. It installs pinned packages and executes tests/model fits in the cloud; no local training setup is required. The analysis can be regenerated independently with ordinary Python and no scientific packages:

```sh
python scripts/analyze_screening.py --out-dir output/screening-analysis
```

This checks saved per-list scores, derives counts/changes and writes deterministic `analysis.json` without refitting. The committed analysis records its source-report and analysis-code SHA-256. Model parameters, inputs, predictions and runtime provenance are versioned; no machine-specific fitted model file is needed. The verified implementation ran all 45 cloud tests and deterministic prediction checks; this follow-up adds analysis/documentation only. No competition entry was submitted, and the 2026 forecast remains unchanged.
