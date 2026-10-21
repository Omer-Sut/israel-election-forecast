# Poll-centered modeling direction

Recorded October 21, 2026. This document distinguishes the user's modeling preferences from proposed experiments. No new model, constraint, uncertainty interval or forecast has been implemented by this discussion.

## User direction

- Treat recent 2026 polls as the primary picture of current support. Historical/auxiliary data should help make modest, evidence-supported refinements around that picture.
- The user believes the existing mean/L1 forecasts may already be close to the eventual outcome. Record this as an intuition, not verified future accuracy or proof that a narrow error band is sufficient. The frozen baseline is only the latest audited five-group sample, not all latest polls.
- Defer the locality forecasting route as a possible future direction. Retain the geographic/CBS database and its documented limits, but do not prioritize a new bottom-up locality model now.
- Consider agreement with recent polls as another diagnostic for models estimated from older data. Clarify independent future-poll evaluation versus agreement with the same anchor/input polls.
- Focus the accepted prediction space near the benchmark, avoiding extreme adjustments. Discuss per-party buffers, uncertainty-based ranges and an overall adjustment budget. The user has not selected a numerical width, confidence level, hard cap or particular benchmark vector.
- RF, XGBoost, GLMs and numerical weighting remain candidates from the preceding brainstorming. No learner, target construction or hyperparameter grid has been approved as a final method.

## Working architecture: benchmark plus constrained correction

Proposed structure:

```text
prediction = current poll benchmark + conservative adjustment
```

Benchmark candidates are the existing rounded mean/L1 and a recency-weighted consensus. Audit missing current releases and list changes before freezing a new anchor; preserve the October 21 snapshot and reports. Choose the benchmark and calibration policy on historical development data, not by which current vector feels most plausible.

Possible models estimate poll-consensus errors or update polling trajectories rather than replacing recent polls with historical outcomes. One option is `prediction = benchmark + alpha * correction`, with small/shrunken alpha selected through chronological validation. Corrections must be reconciled jointly across lists; independently clipping/rounding parties can break the total of 120. Defining a usable national/list-level training panel remains prerequisite. Thousands of geographic records do not create thousands of independent national elections, and current/history party identities are not automatically interchangeable.

Historical demographic correlations alone do not identify how far current national polls should move. Defer a new locality pipeline. Auxiliary sources can enter a correction only when a defensible national input/target and historical availability can be established. No new pretrained model or dependency is selected merely because it is available.

## What a dynamic poll model means

A dynamic model treats support as a quantity that can change through the campaign. Each poll is a noisy observation, potentially with a persistent polling-organization effect. A conceptual model is:

```text
support_today = support_yesterday + possible movement
observed_poll = current_support + polling-group effect + observation noise
```

It combines a dated sequence of polls, discounts stale information and asks whether new changes are a persistent trend or ordinary noise. It can update whenever a new release arrives and project from the cutoff to election day. The movement/noise assumptions govern responsiveness; excessive smoothing can miss changes and excessive responsiveness can chase noise. House effects are proposed components, not identified automatically from a few releases. Shared election-wide error also needs uncertainty beyond organization-specific effects.

A small state-space/Kalman implementation is a possible first version; a fuller Bayesian implementation is optional. A recency-weighted average is the simpler comparison. Our collected polls are largely published seat projections rather than vote shares: these must remain correctly labeled, and smoothing seat expectations does not itself implement threshold/seat allocation. A dynamic seat-projection model and a vote-share model require different observation/constraint handling.

[Votamatic's original explanation](https://votamatic.org/2012-how-it-works/) illustrates time-varying polling forecasts and increasing reliance on current polls. This is methodological inspiration; its US-specific historical predictors and assumptions are not adopted here.

## How to use recent-poll agreement

Keep three separate questions:

| Diagnostic | Target | Interpretation |
| --- | --- | --- |
| Historical election accuracy | Final allocated seats, using inputs available before the historical cutoff | Primary evidence for competition usefulness; sum absolute seat error |
| Current-poll consistency | Current audited poll consensus | Shows how far a candidate departs from the anchor; useful plausibility/adjustment diagnostic |
| Forward poll prediction | Later original poll releases withheld from a dated forecast | Tests ability to anticipate later polling, not necessarily the election outcome |

Agreement with the same polls used to build the anchor is not independent validation. A method that copies the benchmark has zero benchmark disagreement by construction; this metric alone cannot establish that a correction helps. A model predicting withheld recent polls must not consume those releases, revised copies, syndicated duplicates or an anchor constructed from them. Freeze its input cutoff first and define evaluation against later releases/polling groups explicitly. Poll errors can be correlated, so even independent publication withholding is weaker evidence about election truth than observing another election.

Use historical election error as the main selection criterion, poll agreement as an auxiliary diagnostic, and inspect stability across elections/cutoffs. Turnout remains separate and the competition tie-breaker. The 2021/2022 pilot and outcomes have already been inspected; a later 2022 comparison cannot be called a pristine blind test. No composite metric weights are selected in this discussion.

## Options for limiting the space

Let `b[p]` be the chosen benchmark's seats and `s[p]` a candidate final seat vector.

1. **Soft shrinkage toward the benchmark.** Penalize large corrections or blend a candidate toward the anchor. A larger deviation must earn its complexity on historical development elections. This is the proposed first defense against unstable historical fits.
2. **Per-party operational buffers.** Require `lower[p] <= s[p] <= upper[p]`. A uniform `b[p] +/- X` is a simple experimental reference; party-specific/asymmetric widths can reflect differing historical errors and threshold risks. Widths remain unselected and should not be tightened solely because the current polls agree.
3. **A total adjustment budget.** Require `sum(abs(s[p]-b[p])) <= B`, in addition to any party bounds. A one-seat transfer from one party to another costs two in this metric. This prevents modest individual changes from accumulating into a very different national picture. B is unselected.
4. **Joint predictive scenarios.** Generate correlated error vectors around the benchmark using historically calibrated polling-to-outcome residuals, accounting for shared error and late movement. Preserve the 120-seat constraint and use a verified allocator if generating from vote shares. Individual-party intervals alone do not define a calibrated simultaneous region.

Hard arithmetic constraints apply in every case: nonnegative integer seats, total 120, explicit list/form mappings, and final turnout within the form's bounds. Do not describe arithmetic validity alone as verified electoral attainability. A party near the threshold can have a discontinuous seat outcome; a narrow band around zero must not automatically remove its possibility of representation. A joint feasible set must be checked, and every excluded scenario/threshold assumption documented. No fixed safe-party exclusion or party-specific lower bound was authorized.

Separate three kinds of ranges:

- **Poll disagreement band:** how far current published polls differ. Useful descriptive evidence; may be very narrow even if polls share the same bias.
- **Predictive interval/region:** uncertainty about final election outcomes, including sampling/nonsampling error and remaining movement. Historical coverage should be checked at the intended horizon. With only six elections, party mappings and dependent rows, precise 95% coverage cannot be claimed from a large poll count.
- **Operational search bound:** a chosen limit on model adjustments. This can be stricter than a predictive region if the user deliberately adopts it, but is not thereby a statistical confidence statement or proof that excluded outcomes are impossible.

Concrete project evidence: the existing 2022 pilot's mean and L1 forecasts each have total absolute seat error 12. A total adjustment cap B=6 around either of those historical forecasts would exclude the actual seat vector; at least B=12 would be needed to contain it. This is an illustration, not a proposed 2026 budget. The pilot also predicts Meretz representation when the official result is zero. These cases motivate testing caps and threshold branches rather than assuming that a consensus-centered narrow region necessarily contains the outcome.

A confidence interval for current estimated support is not the same target as a predictive interval for final seats. Poll sample margins of error cannot simply be reinterpreted as seat bounds, and repeated polls are not independent new elections. [Shirani-Mehr et al. (2018)](https://sites.stat.columbia.edu/gelman/research/published/polling-errors.pdf) document shared election-level error and nonsampling error; their US numerical error magnitudes are not transferred to Israel. Sampling polls naively and treating the resulting spread as full election uncertainty would miss these components.

Possible calibration approach: recreate comparable historical poll benchmarks at fixed cutoffs, measure outcome-minus-benchmark errors, shrink sparse party-specific scales toward a pooled scale, and compare a few correction strengths/budgets on chronological development folds. Preserve whole-election dependence when assessing uncertainty or resampling residual vectors; do not treat polls/parties within an election as independent calibration elections. Benchmark selection, bounds and all fitted corrections must be estimated without a fold's held-out targets. Report sensitivity to tighter/wider bounds and whether they exclude actual held-out outcomes. No confidence level or calibration algorithm is finalized.

## Proposed next experiment, not yet executed

1. Freeze an audited, mapped historical/current poll panel at common forecasting horizons.
2. Reproduce the existing mean/L1 references and a small recency-weighted candidate.
3. Compare a small regularized error correction/dynamic update, keeping the existing references available. Treat RF/XGBoost as optional constrained correction challengers only if the cleaned training panel and remaining time justify them.
4. Evaluate election error, anchor distance, withheld-poll prediction where genuinely independent, and sensitivity to correction/buffer budgets. Do not select using current-poll agreement alone.
5. If the user chooses explicit hard caps, keep those separate from predictive uncertainty and record their calibration/coverage limitations. No numerical caps or new forecast are set by this document.
