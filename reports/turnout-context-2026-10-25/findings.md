# E016 executed findings

The approved extension is implemented and tested, with a narrower source-compatible scope.48configurations use12common outer targets(K14-K25,1996-2022),8minimum training rows, two families, three penalties, two windows and four feature blocks. Seven new tests and fresh repeated-output comparison passed on hosted run40168196842 at implementationeccf3a6df77259f7a18ecc0a7aff9705055b5884. Raw-source collection40167831419 and12source SHA256 checks passed. This is deterministic fitting, no random seed. Actual cumulative user hands-on effort is unmeasured; source audit/implementation stayed within the approximately one-hour collection timebox.

## What the experiment says

Past-only selected policies have recent-six MAE history2.684, demographics2.663, conflict2.634, both2.500percentage points. Simple last-three mean remains better at2.059. All12fold MAE respectively4.212/3.999/3.770/3.703 versus mean3=3.607. Equal2015/2019-21/2022block MAE3.068/2.740/3.058/2.487 versus mean3=3.032. The combined selector helps on the block metric but does not consistently beat the simpler reference.

[Chronological error plot](chronological-errors.svg) shows why the apparent gain is fragile. All four selectors choose persistence for2015, April2019, September2019 and2020. Differences in the recent-six selected-policy errors come only from2021/2022, not six independent demonstrations of feature value. For2021, errors history/demographics/conflict/both=2.302/3.441/1.943/3.152pp; for2022,2.372/1.106/2.434/.418. Thus demographic/combined gains are driven by2022, while they worsen2021 relative to the matched history selector. The four2019-21events are correlated.

Paired contrasts hold family, penalty, window and all rows fixed. Demographics improve recent MAE in10/12pairs, all-fold MAE in6/12 and all three reported metrics in4/12. Conflict alone improves recent in2/12, all-fold in0/12. Both improve recent in5/12 and all-fold in2/12, all three metrics in1/12. These dependent, inspected contrasts are not independent significance tests. Demographic context deserves better source-vintage coverage; this onset index has no robust standalone case for adoption.

The hindsight-best fixed recent configuration is fractional-logit/both/last8/alpha.01: recentMAE1.466, block1.124 but all-fold5.702pp. Selecting it after inspecting these outcomes would be hindsight tuning. Its favorable recent score does not establish a reliable current model.

Four linear configurations produce inadmissible2006estimates128.64-179.00%. They converge numerically but extrapolate badly with small training windows/context. All remain visible in CSV and are rejected before point selection, never clipped or silently dropped from diagnostic error summaries. Fractional-logit bounds its mean to0-100, but must still pass the form minimum40 and convergence checks.

## What we actually fed the models

- History: previous Knesset turnout and years since previous election.
- Demographics:65+share of total resident population;20-29share of female resident population(sum of two same-denominator age bands). These are national context, not age-specific turnout or registered-voter composition.
- Conflict: count of13curated named onsets in preceding365days; time since latest onset capped10years. This is not active-war duration, severity or peace. Three additional original IDF onsets were reviewed before fitting; gaps remain explicit.

Every block uses exactly the same eligible training/evaluation elections. Each model/scaler sees only earlier numerical outcomes; each selector uses only earlier OOF errors. Reference-year minus2 and current cap2022 prevent future-year backfill but do not repair revised historical source vintages. Raw WDI metadata identifies later updates, and original real-time releases are unverified. All context results are therefore **retrospective sensitivities**, not certified historical forecast gains. Existing CBS local/census tables remain excluded from national fitting for coverage/vintage/denominator reasons. The collected female-total weight additionally cites WPP2022; it is not multiplied into the age shares across unverified revisions.

## Current decision and limits

No learned model adopted; working turnout70.63 and all seat forecasts unchanged. The chronological history selector currently estimates68.95%, demographic sensitivity69.25%. These are exploratory candidates, not replacements. Current conflict/both model estimates are unavailable because the post2022catalogue is incomplete. Their selector output69.86% is explicitly the unadjusted last-three-mean fallback, not a conflict-informed forecast. All shown candidates display two decimals and pass configured40-100bounds.

Do not run another same-grid search to chase2022. If extending this line, prioritize historically released national age composition and a predefined conflict inclusion/duration/severity dataset, with uncertainty/current coverage preserved. Otherwise retain the simple turnout candidates for a deliberate final choice. No merge, submission, poll/seat reallocation or causal war/COVID conclusion.

Final report-commit verification is recorded on PR28; do not infer a later successful check solely from this implementation-run record. Local Git HEAD3055db4 is stale; topic branch and verified remote head are authoritative.
