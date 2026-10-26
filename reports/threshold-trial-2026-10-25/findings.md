# E018 findings: threshold decisions need better evidence

The user reopened research and identified Reservists-Economic and AmchaYisrael as the concern. This trial directly tests a representation-first alternative, rather than choosing a current vector by intuition. Implementation1d765e82b1ebdbfbd2d324f61711cfeb9b6063c7 / PR30, stacked on PR29. Hosted40189471181 passed five new tests and fixed-tolerance fresh repeats. No forecast, turnout, poll input or historical identity changed.

## What changed conceptually

For a poll-defined borderline list, learn p(represented) from earlier campaigns using two features: fraction of polling firms projecting seats and mean positive projection. A separate conditional positive branch retains the empirical positive seat projections. Choose all lists jointly to minimize expected total absolute seat error under total120 and0-or-at-least3. Marginal loss addition does not assume independent parties, but these are not a coherent joint electoral distribution or a vote-based Bader–Ofer simulation.

This addresses a real structural distinction: an average between zero and four seats is not itself a threshold-crossing probability. It does not guarantee an improved estimate. Joint constraints can still produce a three-seat compromise, including in the existing empirical-L1 control.

## Results and decision

On the same four learned outer campaigns, the existing squared-distance control has mean total seat error13.0; empirical-L1 control13.5; each of the three learned models13.5. Equal-period scores(2019–21 as one period,2022 another) are12.667 versus13.0. None earns adoption.

| Election | Squared-distance control | Weak penalty.01 | Middle penalty.1 | Strong penalty1 |
|---|---:|---:|---:|---:|
| September2019 | 12 | 10 | 10 | 14 |
| 2020 | 8 | 8 | 8 | 8 |
| 2021 | 20 | 24 | 24 | 20 |
| 2022 | 12 | 12 | 12 | 12 |

The weak/middle models correctly remove OtzmaYehudit in September2019, but incorrectly exclude Raam in2021. All models still predict Meretz representation in2022. Thus this trial trades a false inclusion for a false exclusion rather than solving the threshold problem. Weak/middle models have one false positive and one false negative over these folds; the reference has two false positives and no false negatives. The strict earlier-campaign selector chooses a weak model before2021 and incurs24error, then returns to the reference before2022; its four-fold seat error is13.5. Its current choice remains the reference.

**Effective threshold sample is smaller than the four-fold seat table suggests.**2020 has no candidate list under the frozen poll-only definition, so it supplies no threshold probability test. There are13candidate predictions across only three informative outer campaigns, with Brier means.166/.149/.151 for penalties.01/.1/1. Current fitting uses25candidate rows across five campaigns;2020 contributes no candidate training row. These are not25independent elections.

A post-hoc descriptive audit of the saved middle-penalty fits compares their Brier.149 with the earlier campaign-balanced base-rate-only Brier.165. This audit is not a new selected model or a prespecified significance test. By campaign, middle-model Brier.049/.240/.157 versus base-rate.222/.111/.162: a gain in September2019 and a sharp loss in2021. It cannot certify calibration.

## Current parties of concern

| Fixed penalty | Reservists projected seats | Exploratory model p | Amcha projected seats | Exploratory model p |
|---|---:|---:|---:|---:|
|.01|0|.168|0|.059|
|.1|0|.280|0|.135|
|1|4|.619|0|.549|

These numerical probabilities are **not calibrated crossing probabilities**. Regularization alone changes the Reservists branch from zero to four. At the strongest penalty, Amcha's marginal estimate exceeds.5 yet its joint decision is zero because satisfying the120-seat constraint changes the total expected-loss tradeoff. Marginal probability>.5 is not an independent instruction for every party once all outputs must sum120.

All three learned point vectors give Amcha zero, but that does not establish certainty. Historical training has three selected firms per election versus seven current firms; the precision/dependence shift is not calibrated. Parties with all-zero projections have no learned probability estimate in this trial. No all-zero winner occurs in the six reviewed panels, which does not prove it cannot happen elsewhere. Conditional positive seat distributions also omit possible outcomes beyond the published projections.

The current partial percentage evidence remains available in results.json, with exact poll IDs, original URLs and missing entries. Six selected releases put Amcha outside parliament and one gives four; four put Reservists outside and three give four. Frequencies are descriptive, not outcome probabilities. No reported seat projection is converted into a vote share.

## Data finding and next research step

The existing first four campaign snapshots contain no stored below-threshold percentages.2021 has two such releases, both for NewEconomic(1.4/1.3%), not the close Raam case.2022 has percentages in all six audited releases, mainly for Balad/JewishHome and smaller lists. Polls that publish seats for a qualifying projection often do not report its vote percentage, so missingness is informative/censored rather than random.

The useful next data work is comparable original-source historical percentages around3.25%, including lists that later passed and failed, and documented undecided treatment/denominators. Collect by a frozen inclusion rule, not by selecting examples that support a preferred current party outcome. Preserve publication availability and source tiers; current full vote vectors remain unavailable. More rows can improve coverage but do not create more independent elections.

Keep the two-stage machinery and reject its current adoption. Preserve Reservists3/Amcha0 and adopted turnout69.86 as the working reference, with0/4Reservists scenarios visible. This is a reference pending better research, not a claim that three is its most probable actual outcome. No source promotion, weights, merge or submission. Research remains open under the user's direction. Final report-commit checks are on PR30; local Git metadata remains stale. Actual cumulative user effort is unmeasured; no budget reset or new broad grid.
