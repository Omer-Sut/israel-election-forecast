# Turnout fits: findings and decision

We fitted264 time-series configurations over25 elections, using16 outer prediction targets after lag/training warm-up. See the [full fitted-method report](analysis.md), [chronological errors](chronological-errors.svg) and [configuration stability plot](model-stability.svg). All historical outcomes had already been inspected; this is an exploratory screen, not an untouched holdout.

## Best-looking fixed fits

| Candidate | Recent six MAE (pp) | All16 MAE (pp) | Next turnout |
| --- | ---: | ---: | ---: |
| Ridge AR1, last8 training elections, alpha1 | 1.954 | 3.038 | 69.43% |
| Ridge lag/calendar/era, all history, alpha1 | 2.016 | 2.300 | 69.92% |
| Fractional-logit AR1, last8, alpha0.1 | 2.154 | 3.020 | 69.56% |
| Mean of last3 elections | 2.059 | 2.945 | 69.86% |
| Previous election | 3.117 | 2.804 | 70.63% |

The best recent fixed configuration is selected after seeing all six errors; its1.954 is a hindsight score. Its advantage over mean3 is only0.105 percentage points, after examining264 correlated configurations. It is a legitimate candidate for forecasting the next unobserved election, but its rank does not establish dependable superiority. The calendar/era feature was motivated by an already-inspected historical break, another discovery limitation.

The AR1 ridge fit on the last8 lag-complete target elections(2009–2022) is approximately:

T_next = 59.32201 + 0.14311834*T_previous.

Putting T_previous=70.63 gives69.43046%. This largely pulls toward the training period’s turnout level rather than carrying the last turnout through with coefficient1. Alpha1 is a coefficient penalty in a standardized fraction-response objective, not a100% or25% blending weight. Current coefficients/scalers and training IDs are in results.json; historical rows retain training IDs, predictions and fit status.

## What happened when selection was done before each election?

| Predefined chronological selector | Recent MAE (pp) | Three-block MAE (pp) | Current choice |
| --- | ---: | ---: | ---: |
| Linear pool, previous6 OOF errors | 2.885 | 2.334 | Ridge AR1:69.43% |
| All families, previous6 OOF errors | 5.310 | 4.581 | Ridge AR1:69.43% |
| All families, all earlier OOF errors | 3.730 | 3.727 | Calendar ridge:69.92% |
| GLM pool, previous6 OOF errors | 5.318 | 4.597 | Simple mean3:69.86% |
| Simple mean3 | 2.059 | 3.032 | 69.86% |

The linear selector improves the block-weighted score but loses on ordinary recent-election MAE and all16-fold error. None of these selection rules consistently beats the simple mean across evaluation choices. Grouping2019–2021 as one block is a sensitivity, not three truly independent experiments.

A concrete failure: before the March2020 election, the all-family recent6 selector chose a fractional-logit spacing model based on earlier validation errors. It predicted60.83%, versus actual71.52%, an error of10.69 points. Training/selection was numerically past-only; poor extrapolation on a small irregular series remains possible without leakage. This shows why the strongest hindsight score and the error of an operational selection rule are different quantities.

## Stability and limits

There are240 distinct historical prediction vectors at7-decimal precision among264 configurations. Equivalent OLS feature spans and some level/change formulations explain duplicates; they are not264 independent pieces of evidence. All current fits converged and all current point estimates satisfy40–100%;17 configurations had at least one inadmissible historical prediction, preserved diagnostically and gated during selection. Current estimates across all fitted configurations span65.59–73.78%; that spread is model sensitivity, not a confidence interval.

The broad grid is now complete. No second adaptive sweep, war adjustment, current-poll calibration or automatic replacement of the70.63% working forecast is adopted. The learned candidates worth discussing are69.43%(recent AR1 ridge) and69.92%(calendar ridge), alongside the simple69.86% mean. The evidence supports considering a value around69–70%, while the apparent0.105-point hindsight gain is too small and selection-sensitive to claim a forecasting improvement.

All configurations, chronological selections, scalers/current coefficients and invalid diagnostics are preserved; inputs are unchanged from E014. No seat forecast, merge or competition submission.
