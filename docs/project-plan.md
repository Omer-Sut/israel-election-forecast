# Eight-hour forecasting plan

Planning date: October 21, 2026. User constraints: [project-constraints.md](project-constraints.md). This is a proposed implementation sequence, not a claim that any method has run.

Execution update: [the first preliminary baseline](baseline-method.md) is now implemented with six stored poll records, five selected groups, an official historical turnout reference, nine correctness tests, and committed outputs. A GitHub Actions CPU workflow replaces the initially proposed notebook to minimize setup. Historical forecast validation and additional source audits remain open; planned methods below are not all implemented.

## Target deliverable

A reproducible forecast of seats for every list in the competition form and national turnout (%), an accessible code link, and an honest method description of no more than 500 words. Optimize total absolute seat error. Preserve code revision, input cutoff, source versions, assumptions, and final output.

The official 2022 results provide a concrete historical fixture: votes, shares, seats, turnout, and valid/invalid counts are available in the [Central Elections Committee national results](https://votes25.bechirot.gov.il/nationalresults). Form fields are now recorded from the user's transcription in [submission-contract.md](submission-contract.md); hidden validation and electoral rules still need verification.

## Effort budget

These are proposed timeboxes, not measured timings or runtime guarantees. Use the experiment log to record actual effort. If the eight-hour budget includes effort already spent on setup/planning, subtract it before execution.

| Work | Hands-on cap | Deliverable / stopping condition |
| --- | --- | --- |
| 1. Define the exact task | 0.5 h | Form field inventory, list mapping, cutoff, constraints, rule sources |
| 2. Assemble minimum useful data | 2 h | Audited current polls, official historical outcomes, a small historical poll sample |
| 3a. Produce a baseline | 1 h | Valid seat vector and turnout baseline from a fresh run |
| 3b. Add one numerical improvement | 1.5 h | Uncertainty/scenario method, or retain baseline if data is insufficient |
| 3c. Validate and choose | 1 h | Same-cutoff historical comparison and sensitivity table |
| Online reproduction check | 0.5 h | Fresh hosted CPU run using committed inputs/code |
| Final output and method description | 1 h | Frozen forecast package and <=500-word explanation for user review |
| Contingency | 0.5 h | Resolve missing fields, data mismatches, or failed reproduction |
| **Total** | **8 h** | Stop adding features when a timebox is exhausted |

## 1. Understand the exact task

Read [competition-brief.md](competition-brief.md), then resolve the remaining contract with the form and official sources:

Update: the user supplied all form sections. There are 14 named-list seat fields, one combined other-qualifying-parties field, a 120-seat total, and turnout. Use `config/submission-fields.json` as the ordered export contract. Poll/official-list mappings, hidden validation, turnout precision, timezone, and final track/team choices remain open. Dummy responses are not predictions or consent. Preserve individual other lists internally; aggregate their allocated seats only when exporting/scoring at form level.

- Confirm systematic track, eligibility, and team size (up to four).
- Record the exact list fields, including lists expected to win zero seats, spelling, units, validation rules, and turnout precision. Do not infer the submission list from a polling website.
- Confirm the deadline/timezone and the permissible input/publication cutoff. The PDF states October 26 at 23:59 and election day October 27; live official pages encountered access restrictions during initial review.
- Verify the 120-seat total, integer constraints, threshold denominator, Bader-Ofer allocation, and current surplus agreements. Official search results identify 120 seats and a 3.25% threshold; full Knesset rule pages were geo-blocked. Verify the complete procedure before implementing it.
- Distinguish legal outcomes from form validation. Do not assume a universal four-seat minimum or hard-code any party's survival based on intuition.

**Exit:** one documented output schema, party mapping, cutoff, and explicit unresolved questions. If the form requires university authentication, the user inspects it; never submit an entry during inspection.

## 2. Learn the available data and collect only what we need

Use [data-sources.md](data-sources.md) as the source guide. Prioritize:

1. Recent polls with the actual current lineup. Aim for the latest independent polls from several polling organizations, using a short, documented recent window. Start with roughly 10-20 usable releases if available; this is a cap on collection effort, not a claim about availability.
2. Original releases for below-threshold percentages, dates, pollster identity, sample sizes, and denominator definitions. Record unknown values as unknown, not zero.
3. Official national results and turnout for recent elections, initially 2022 and 2021; add 2020 or 2019 only if easy to obtain with compatible pre-election polls.
4. Final pre-election polls from those elections, at a cutoff comparable to this competition. Use them to measure aggregate poll-to-result error and threshold misses. Later public data must not enter earlier forecasts.

Suggested logical tables: `polls` with one row per poll/list/measurement and source ID; `lists` with election-specific names/IDs and validity dates; `results` with official votes/seats/turnout; `sources` with URL, dates, snapshot path/hash, and rights notes. The first implementation uses small versioned JSON snapshots plus an explicit mapping configuration instead of a database. Separate seats from below-threshold percentages; full vote-share data is not yet available. Keep population and undecided handling explicit.

Do not mix hypothetical lineups, repeat articles reporting the same poll, or replace missing entries with zero. Missing and below-threshold are different. Check source totals and mapping conflicts. Distinguish pollster from publisher so frequently published polls do not dominate merely through repetition.

Historical data has three jobs: produce an honest baseline comparison, estimate the scale/structure of forecast error, and inform turnout. It does not justify pretending new alliances match old parties exactly. Start nationally; ballot-level demographics and vote-transfer estimation are stretch work.

**Exit:** a small versioned dataset that another computer can access, provenance records, and a list of exclusions. If comparable history cannot be assembled in time, use explicitly assumption-based sensitivity scenarios and do not call them calibrated probabilities.

## 3. Compose and compare lightweight methods

| Candidate | Work required | Role in this budget |
| --- | --- | --- |
| Latest poll per organization, equally weighted | Basic cleaning and coherent integer output | Mandatory reference baseline |
| Recent poll consensus with recency weighting | One transparent weighting rule; cap repeat-poll influence | Main starting candidate |
| Small uncertainty/scenario model plus constrained decision | Error scale or clearly labeled assumptions; numerical sampling/optimization | Preferred single improvement |
| Small shrinkage/historical pollster correction | Compatible historical errors and validation | Only if easy; avoid per-party overfitting |
| Pretrained time-series model | Installation, regularized series, lineage alignment, validation | Optional challenger, not the critical path |
| Ballot-level transfer/demographic model | Geographic harmonization and additional assumptions | Defer under the eight-hour budget |

### Baseline first

Use a pollster-balanced consensus, preserving the latest poll per organization as a reference. If comparing a recency rule, predefine a small set (for example 3-, 7-, or 14-day half-lives), rather than searching a large grid. Those values are candidates, not selected parameters. Equal or capped weights are a safer starting point than claiming precise historical pollster quality from a few elections.

Two data routes must stay distinct:

- **Vote-share route:** if compatible shares are available, normalize according to the documented denominator, retain support for lists below the threshold, and convert to seats using verified allocation rules and agreements. Missing-party mass and undecideds need explicit treatment.
- **Seats-only route:** aggregate reported seat estimates directly, then find a coherent integer forecast. Do not divide seats by 120 and label the result raw vote share. A zero-seat poll result does not reveal how close that list is to the vote threshold. Use original releases or documented pass/fail scenarios if possible.

For turnout, start with an official recent-election reference and a simple historical summary. Add a current adjustment only when supported by comparable turnout-intention evidence. A PM-preference or issue-importance question is not a turnout measure.

The form's user-confirmed admissible turnout range is **40.00-100.00% inclusive**. Constrain the reported point forecast to this interval and validate against `config/submission-fields.json` before export, displaying two decimals. Keep an unconstrained estimate as a diagnostic if applicable, and document any boundary adjustment. Do not alter historical observations or assume the submission bound proves the true outcome cannot lie outside it. Actual model/export validation is still to be implemented.

### Preferred improvement: numerical uncertainty, no heavy training

Generate a modest number of coherent vote/seat scenarios (start with thousands, not millions). Include shared election-level error, disagreements across pollsters, and threshold alternatives where data supports them. Repeated polls from one organization are not independent draws of election error. Verify stability with a second seed or sample size; do not promise calibrated probabilities without sufficient history.

Use legal constraints to keep outcomes coherent. Concentrate on plausible ranges around polling evidence, but test wider ranges. A boundary assumption that removes an outcome is a modeling choice, not a verified fact. Enumerating all seat vectors is unnecessary.

The decision should match the competition loss. Given scenario weights `w[j]` and scenario seats `s[j,i]`, choose a feasible forecast `x` to minimize:

```text
sum over scenarios j of w[j] * sum over lists i of abs(x[i] - s[j,i])
```

For unconstrained coordinates the optimum is a median, not necessarily a mean. Separate party medians may fail to total 120 or violate structural constraints. A small dynamic program over list index and seats allocated can minimize the additive cost under a total-seat constraint and verified allowed seat sets; alternatively evaluate only scenario-generated legal vectors. More complex cross-list constraints need additional checks. Do not round each party independently and assume the result is valid.

This is the key numerical opportunity: optimize a small constrained decision problem under a useful uncertainty model, rather than train a large predictor or enumerate the full outcome space.

### Pretrained option, with a strict stop rule

[Amazon's Chronos project](https://github.com/amazon-science/chronos-forecasting) offers pretrained forecasting models, including zero-shot inference. This verifies availability, not election forecasting skill. Irregular polls, changing list identities, threshold discontinuities, and jointly constrained vote shares require extra work. We have not checked a particular checkpoint's suitability, license, training-data cutoff, or historical leakage risk. Consider one small model only after the numerical pipeline works, only if unused contingency remains, and drop it if it cannot be fairly evaluated quickly. No pretrained model has been downloaded or evaluated.

### Validation and selection

- Compare against the mandatory baseline on identical historical elections, cutoffs, list mapping, and scoring.
- If historical elections inform parameters/error scales, leave the evaluation election out of that estimation. Several cutoffs from one election are not several independent elections.
- Report absolute seat error per election, threshold misses, turnout error, and sensitivity to recency/error/threshold assumptions. Do not hide a loss behind an averaged improvement.
- Validate allocator arithmetic on official historical votes/seats and check integer seats, complete form coverage, total seats, nonnegative values, and turnout bounds.
- Prefer the simpler method unless the improvement is credible across the limited checks. If calibration evidence is weak, say so and present scenarios as sensitivity analysis.

## Online execution and stopping rule

The first implementation uses Python 3.12 standard-library code and a small GitHub-hosted CPU workflow, with committed inputs and output hashes. A [Colab](https://research.google.com/colaboratory/faq.html) wrapper is deferred because the simple command already runs online without package installation. Keep method logic independent of any hosted surface.

The [GitHub-hosted Actions runner](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job) is configured to run tests, reproduce the baseline, compare committed outputs, and expose a summary/artifact. Inspect actual run status; configured is not the same as successfully executed. Do not duplicate this setup without a concrete need.

Stop once there is a checked baseline, an evaluated decision about the single improvement, a fresh hosted reproduction, and a frozen forecast/report package. Do not spend the reporting reserve on adding models.

## Submission preparation as ongoing work

Append each consequential run to [experiment-log.md](experiment-log.md). Update [method-report.md](method-report.md) after data/method choices, not only at the deadline. Each final run must identify code revision, input hashes, cutoff/timezone, configuration, seed (if applicable), runtime, outputs, validation, and the actual selected method.

The first methods and outputs are preliminary baselines only. Next audit missing latest sources and assemble historical pre-election polls for evaluation. Operative electoral rules/agreements are still needed for a vote-share allocation model; unresolved hidden form validation need not block collection.
