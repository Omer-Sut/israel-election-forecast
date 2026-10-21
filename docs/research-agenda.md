# User feedback and research agenda

Recorded October 21, 2026. This is a handoff for collaborators and agents; proposals below are not selected models or completed experiments. See [implemented baseline](baseline-method.md), [research review](forecasting-research.md), and [current state](project-state.md).

Subsequent execution update: the user authorized proceeding with the historical backtest. The [initial 2021/2022 pilot](historical-backtest.md) is now implemented and run; its four horizon cases are two outcomes. The sections below preserve the earlier research-stage feedback/proposals. Broader history, war/turnout analysis and alternative models remain pending.

## Why this review exists

The user asked how the autonomous preliminary results were calculated, including their data, assumptions, and methods. The explanation established that these were two poll-consensus references, not a trained prediction model: equally weighted latest audited groups, rounded mean versus empirical absolute-deviation consensus, plus unchanged 2022 turnout. The 14-day window and aggregation choices were agent-selected starting points, not user-selected or historically validated decisions. In-sample disagreement of 14.4/12.4 is not future election error. Software checks establish correctness and reproducibility, not prediction skill.

The user now requests: preserve all feedback and progress, study existing election forecasting work, and identify useful data beyond published polls. Keep the existing outputs frozen while investigating; no replacement forecast, additional model, backtest, war adjustment, or dependency is implemented in this research update.

## Feedback to preserve

- Explain the electoral threshold, smallest possible positive seat allocation, and whether the competition expects results before or after threshold exclusion and seat allocation. Check the PDF and actual official published outcomes.
- Test candidate methods against previous elections using the polls and parallel inputs actually available before each election; official results are ground truth. Decide the historical range and account for the exceptional cluster of repeated elections.
- Explain precisely what the baseline's 14-day window measures and what an omitted submission category means.
- Explore whether elections after wars have systematically different turnout, using decades of Israeli history. Treat the direction as an open question. The user suggested starting around statehood; the first national election in the inspected official table is January 25, 1949.
- Explore alternative numerical and ML approaches, explicitly including random forests/decision trees and accessible pretrained models. Research is requested; no specific method has been selected.
- Continue to honor the approximately eight-hour total hands-on budget, portable online execution, and continuous report preparation.

## Clarifications grounded in existing code

The 14-day parameter is a **recent-poll eligibility window**, not a training period or 14 observations. `select_polls` requires publication and recorded source-update dates to be no later than the as-of date. It measures age using fieldwork end when recorded and publication as an explicit fallback. The lower bound is inclusive: as-of October 21 minus 14 elapsed days is October 7. Within this eligible set it selects the latest audited publication per declared group and weights selected groups equally. There is no further recency decay. The previous conversational shorthand of a publication-only window was incomplete.

An **omitted form category** is a list required by our output schema but absent from a source's seat table. For example, if a source gives an audited, complete 120-seat allocation without Blue and White, it can imply zero allocated seats for that category. It does not imply zero voting support or explain distance from the threshold. An incomplete table, an unresolved alliance mapping, or an unexplained aggregated other bucket does not justify this inference. Preserve missing percentages as missing. Original source labels and the accepted current Joint List/form mapping remain explicit.

## Competition target and threshold implications

Rechecked both original PDF pages visually on October 21. Page 1 defines the scored outcome as the CEC's final official result after double-envelope counting; the form asks for seats totaling 120. **Interpretation: predict final allocated seats after the threshold and seat-allocation process**, not raw vote shares or hypothetical pre-threshold seats. The PDF does not prescribe the model's internal method or explicitly require every submitted point estimate to be an electorally attainable scenario. Its aggregation/scoring treatment of several other qualifying lists remains unconfirmed. See [rules review and official examples](forecasting-research.md#electoral-rules-and-the-scored-target).

Any future vote-share scenario generator should apply each list's threshold eligibility before allocating all 120 seats, then map/aggregate outputs into form fields. Surplus agreements and operative allocation rules still need complete current verification before implementing an allocator. Neither existing baseline performs that process. Do not silently repair the frozen reports or describe them as allocation simulations.

## Proposed historical validation design

1. Start with **2021 and 2022** to establish the data pipeline and compare the existing methods without fitting extra parameters. A readable original Channel 13 final 2021 poll has been located; a balanced historical poll dataset has not been collected.
2. If collection fits the remaining budget, extend to **2015, April 2019, September 2019, 2020, 2021, and 2022** (six elections). This is a proposed scope, motivated by the threshold regime and recent polling environment, not an approved final cutoff. Verify rules separately for each election. Earlier history may help turnout without requiring comparable party-level forecasts.
3. Preserve election-specific lists, splits, mergers, poll lineups, source versions, fieldwork/publication timestamps, and valid-vote denominators. Score all actual contesting lists consistently; never merge past identities into today's submission slots. Keep national total absolute seat error as the main metric; also report threshold misses and absolute turnout error.
4. Use the same relative forecast horizon and poll-age rule for each election. The current snapshot is six days before election day; a seven-day horizon is a useful proposed comparison. A deadline-eve forecast is a separate experiment using only publications then available, respecting the applicable publication restrictions. Do not use election-day exit polls or later source revisions.
5. If estimating weights or model parameters, use earlier elections only for each later test election. Reserve a final chronological holdout where feasible. Do not randomly split polls/localities from the same election between training and testing and call that an unseen-election test.
6. Report each election separately, an equal-election average, and a sensitivity summary treating **2019-2021 as one repeated-election period**. This prevents four closely spaced national outcomes from dominating the conclusion. Report uncertainty honestly; six elections remain a small validation set.
7. Compare only a small predefined set. A method earns adoption through held-out performance and manageable data requirements, not fit to current polls. Stop collecting/adding methods when the validation/reporting timebox is threatened.

## Proposed war and turnout check

This is a hypothesis, with no chosen sign or numerical adjustment. Begin with official Knesset turnout history from 1949 and election-to-election changes. Exclude the 2001 prime-minister-only election from a Knesset-turnout series or analyze it separately. The inspected CBS table is labeled 1949-2022 but actually ends at March 2021; append 2022 from the official CEC result rather than inventing a missing row.

Define conflict inclusion, ongoing versus ended conflict, and the meaning of "after" **before** comparing turnout. One affordable proposal is first national election during/after a qualifying conflict episode, with time-since-onset/end and a sensitivity check for alternative windows. A conflict-year dataset cannot supply exact daily war-end dates. Use documented primary chronologies when needed, and account for conflicts outside national borders rather than filtering only by event location.

Plot turnout and its change, then compare post-conflict changes with other changes. If attempting a small regression, limit predictors to time trend/prior turnout, elapsed time since previous election or repeated-election status, and a prespecified conflict measure. Consider special circumstances such as the pandemic and changes in participation/denominators. With few independent cases, this can show historical association, not a causal war effect. Do not automatically add a positive or negative war adjustment to 70.63%.

## Proposed methods to discuss next

- Existing mean and absolute-deviation references remain comparators.
- Highest-priority extension: a lightweight vote-share uncertainty model with explicit threshold alternatives and verified allocation, if compatible shares are obtainable.
- A regularized fundamentals/turnout regression is a cheap alternative once historical covariates exist.
- A small random forest is a legitimate challenger on a well-defined historical feature/target table. Training a modest forest is cheap; assembling valid independent data is the main cost. Respondent/locality rows do not create independent elections.
- A pretrained tabular foundation model is optional. It still needs labeled examples and compatible inputs; pretraining does not provide current Israeli election knowledge. No election-specific, ready-to-run pretrained checkpoint was verified in this review.

Choose the input table and evaluation design before choosing ML software. See [the evidence and prioritized data inventory](forecasting-research.md).
