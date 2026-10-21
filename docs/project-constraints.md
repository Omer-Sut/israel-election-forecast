# Project constraints and working principles

E001 update: the user approved the [cloud screening implementation](model-screening.md), prioritizing today's one-hour availability and soft limits. Three configurations for each of six lightweight families are implemented in a separate optional scientific environment. This supersedes the earlier one-improvement scope, while preserving the approximate eight-hour total budget, no heavy training, online portability and no final model selection without historical evidence.

Confirmed with the user on October 21, 2026. These constraints govern planning and implementation; proposed methods are not implemented models.

## Time and computation

- Total available hands-on effort is approximately **eight hours**. Track actual effort from the next execution phase and revise scope if earlier planning/setup must also count toward that total.
- Do not train a heavy model from scratch, conduct broad model searches, or build infrastructure disproportionate to the forecast.
- Prefer transparent numerical/statistical methods that run on an ordinary hosted CPU. Cheap estimation of a few parameters is permissible if it earns its setup and validation time.
- Off-the-shelf pretrained open-source models may be considered, but lack of training does not imply low setup cost or useful election forecasts. They must beat the simple baseline on appropriate historical checks and fit the remaining budget.

## Solution space and uncertainty

Latest user direction: anchor predictions to recent polls and investigate conservative refinements around them; defer locality forecasting. Discuss per-party buffers and a joint adjustment budget before choosing numerical limits. The user's belief that current mean/L1 forecasts are close is not verified future accuracy. Keep historical election accuracy primary, current-poll agreement auxiliary, and predictive uncertainty separate from a chosen operational bound. See [poll-centered-modeling.md](poll-centered-modeling.md). Existing narrow poll agreement does not by itself establish narrow election uncertainty.

The user's working intuition is that only a small part of mathematically possible election outcomes is plausible. Use evidence to concentrate effort on this region. Do not treat an intuitive example, such as Likud falling below the threshold being extremely unlikely, as a verified fact or an automatic hard constraint.

The raw combinatorial space is still large: distributing 120 indistinguishable seats among ten named lists with nonnegative integer counts gives `C(129, 9) = 20,492,404,684,400` vectors, before electoral rules. This is an illustrative mathematical count, not a count of legally attainable or plausible outcomes. We can avoid enumeration through optimization or sampling.

Verified structural impossibilities can be excluded. A user-chosen operational search cap is a separate modeling assumption, not proof of impossibility or a calibrated probability statement; no numerical cap has been selected yet. Use documented probability assumptions, bounds, and sensitivity checks for unlikely events. Retain threshold uncertainty for genuinely borderline lists. Record how pruning changes the forecast rather than silently assigning zero probability.

## Data and evidence

- Explain each source before adopting it: what it measures, coverage, units, provenance, limitations, and intended role.
- Use current polls for current support and historical polls/results for error assessment and validation. A large number of ballot boxes is not a large number of independent national elections.
- Inspect historical party splits, mergers, and hypothetical poll lineups. Do not transfer old party labels or vote shares mechanically to current lists.
- Prefer original poll releases and official results over aggregator transcriptions when they conflict. Flag unresolved discrepancies instead of choosing whichever number suits the model.

## Online collaboration and reproducibility

- Keep authoritative code, configuration, small shareable inputs, source metadata, decisions, and report material in GitHub.
- Aim for a fresh hosted CPU session to reproduce the forecast from a specific commit and input snapshot. No required paths, packages, files, or manual state may live only on one person's computer.
- Implemented first execution surface: a small GitHub Actions CPU job running standard-library Python 3.12 against committed inputs. This avoids extra notebook setup; a Colab wrapper remains optional later. Check the workflow's actual run result before claiming successful remote reproduction.
- Keep reproducibility-critical inputs durable. Session disks and expiring workflow artifacts are not the only copy of a final submission.

## Documentation while working

Update the experiment log, decisions, source inventory, and method-report draft as work happens. A short run record should make the final 500-word method description an editing task, not a reconstruction from memory. Describe only methods actually executed and validated.

See [the execution plan](project-plan.md), [source review](data-sources.md), and [report draft](method-report.md).
