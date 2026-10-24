# Method report working draft

E008 verified: poll-level source/methodology features and strictly past-only reliability training weights were tested with three fixed learners and aggregate/poll-basic controls.70 scientific tests, frozen checks and deterministic repeats passed (screen39952455330/baseline39952455404). No incremental25% integer gain on2021/2022; chronological fraction selection did not earn adoption. Keep research machinery, do not describe metadata weights/corrections as the selected forecasting method. See poll-metadata-trial.md and reports/poll-metadata-trial-2026-10-23/analysis.md. Final draft remains unchanged.

E007 verified current-source refresh: four newer original releases, five latest audited equal-weight groups, unchanged mean/L1, partial threshold plot and conservative October23 source-version cutoff. Baseline39948181011/screen39948181004 passed64 scientific tests, frozen checks and deterministic audit repeats. Both outputs sum120; Amcha1/0 and Reservists2/3 remain arithmetic references rather than a selected final vector. No calibrated threshold model, learned weight or turnout change. See current-poll-audit.md and reports/current-poll-audit-2026-10-23/analysis.md. Original final-method draft remains unchanged pending selection.

E006 verified October23:60hosted tests and deterministic repeats passed. Broader prior-list area proxies and separately labeled1183locality2015edition sensitivity did not produce fixed25% or earlier-OOF-selected integer gains over mean20/12. Do not adopt into the forecast/submission draft. Full workbook archive uncertainty and2021split/new-list missingness remain material; age/sex dates and2026lineage unresolved. See party-area-trial.md and reports/party-area-trial-2026-10-23/analysis.md. Final method draft remains unchanged.

E005 verified:55hosted tests passed. Chronological parameter/blending validation, dynamic-gap features and a dated prior-election geographic subset were tried; no selected2021/2022configuration beat the mean. Broad CBS profiles remain descriptive. Audited-only expected-poll-error prototype MAE9.233versus8.668simple baseline, so no quality weights adopted. These are research diagnostics, not a change to the final forecasting method. Turnout/war/economics later. See poll-quality-feature-trial.md and project-state.

E004 preparation: user approved hosted correction-strength/forest-seed sensitivity on unchanged audited inputs. Diagnostic work, not an adopted forecasting method; final description remains unchanged until evaluated selection. See robustness-batch.md/project-state for actual execution status.

October22 continuation: A002 adds independently checked pre-rounding plots over all saved historical folds. E003 adds three earlier original-source-reviewed releases (24 to27) and runs four fixed data sensitivities while preserving latest-group anchors, model settings, outcomes and the preliminary2026 forecast. All46 hosted tests and deterministic repeats passed; none beats reference20/12 on2021/2022. Some ensembles improve to ties, some forests worsen. See [campaign-history.md](campaign-history.md) and project-state for checked run/provenance evidence. No L0 penalty or final model is adopted. The final submission description remains the baseline draft until a method is selected.

E002 analysis: [screening-results-analysis.md](screening-results-analysis.md) explains why matching reference scores often means reproducing its rounded vector, why the earlier four panels do not train a within-group trend effect, and which party-level misses dominate. No candidate improved either comparison outcome, and larger unshrunk supervised corrections worsened both. Treat this as limited retrospective evidence; retain references and audit source/trajectory coverage before adopting an adjustment. No final method or uncertainty interval is selected.

E002 execution update: [six-election screening](six-election-screening.md) now uses T−1 panels from 2015, both 2019 elections and 2020 as earlier training/OOF history, with complete 2021/2022 comparisons for all 20 configurations. All 45 hosted tests and deterministic reruns passed; [durable results](../reports/screening-six-elections-2026-10-21/summary.md) show no improvement: references 20/12 versus candidates20–24/12–14 total absolute seat error. These are two already-inspected evaluation outcomes, not an untouched holdout. Source-vintage/coverage/metadata limits remain explicit; no challenger or final current forecast is selected.

Implementation update (E001, October 21): a separate [cloud screening pipeline](model-screening.md) now implements six candidate families with three configurations each, anchored to polls with 25% corrections. This is exploratory work; no challenger is selected or substituted into the preliminary forecast. Only audited 2021/2022 polls enter real diagnostics; synthetic checks are software tests, not predictive evidence. See the experiment log and project state for verified execution status. Retain the baseline description below until a method is actually selected.

The first hosted screen passed all 43 tests and deterministic reruns. On the one 2022 evaluation election, fitted candidates tie the 12-seat reference error at T−6 and tie or worsen it to 14 at T−1. These results do not establish a family ranking. The remaining four elections need audited poll panels before strict chronological screening and learned real-data ensemble weights are supported.

Status: the preliminary baseline and a limited 2021/2022 historical backtest have run; broader validation and final method selection remain pending. The following draft describes executed work only. It is not a final competition entry.

The competition's systematic track requires a method description of at most 500 words, data sources, a code link, and agreement to present if selected as winner. Keep the final submission description within 500 words; this working file can hold supporting evidence separately.

## Submission description scaffold

### Current implemented-method draft (under 500 words)

We compiled a small audited sample of published national seat projections, preserving source URLs, dates, sample metadata, original list labels, and separate below-threshold percentages. Six stored records yield five active polling groups after retaining the latest audited release from each group in a 14-day window as of October 21, 2026. This is not an exhaustive set of all latest releases.

We compare two transparent references: equal-weight mean seat estimates rounded to total 120 using largest remainders, and an integer consensus minimizing total absolute deviation from the selected polls under the same total. A small dynamic program computes the latter; no heavy training or pretrained model is used. Current alliance labels map explicitly to the form's fields. These are output-label assumptions and do not equate historical party compositions.

Turnout is initially the official 2022 rate, 70.63%, checked against the form's 40.00-100.00% range. A current self-reported turnout-intention measure is retained separately, without assuming it predicts actual participation.

Software checks cover allocation arithmetic, inclusive turnout bounds, group deduplication, cutoff eligibility, optimizer correctness, and historical target separation. Leaving out one current polling group changes the consensus by 4-8 in total absolute seat difference; this is sensitivity, not a confidence interval.

A retrospective pilot uses 12 original-source historical releases across 2021/2022. With three equal-weight groups per election, total absolute seat errors at six days before voting were 24/22 (mean/L1) in 2021 and 12/12 in 2022; final cutoffs gave 20/20 and 12/12. Prior-election turnout persistence missed by 4.08 and 3.19 percentage points. We did not fit weights or tune methods on these results. Two elections, incomplete poll coverage and unauthenticated historical page versions limit conclusions. Neither method is selected as final. Inputs, code, and outputs are versioned in GitHub with hosted reproduction.

### Finalization structure

Replace each item with the method actually implemented; remove placeholders before submission.

1. **Target and cutoff:** seats by the form's lists, turnout, forecast timestamp/timezone, information cutoff.
2. **Data:** polls and official historical results actually used, dates, source links, deduplication, list mapping, and units.
3. **Method:** aggregation rule, threshold/allocation handling, uncertainty assumptions, seat-decision rule, turnout calculation.
4. **Validation:** historical cutoffs, baseline comparison, achieved seat errors, sensitivity, and limitations. Explain limited evidence honestly.
5. **Reproduction:** code revision, accessible input snapshot, configuration/seed, hosted notebook or command, output link.

## Evidence checklist maintained during work

- [x] Submission party field inventory and total-seat rule recorded from the user's transcription; hidden validation/precision remain unverified.
- [ ] Official/poll/form mappings and other-qualifier scoring interpretation resolved.
- [ ] Data provenance, rights, cutoff eligibility, and source discrepancies resolved/documented.
- [x] First baseline run recorded in experiment log; final method selection remains pending.
- [x] Initial historical reference comparison recorded as R002; broader evaluation and final selection remain pending.
- [ ] Final output generated from frozen inputs and a recorded code revision.
- [x] First baseline reproduced exactly in a fresh hosted CPU run: [39572969093](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39572969093), implementation commit `aee2f11`. Final chosen method still needs its own frozen reproduction.
- [ ] Final method paragraph <=500 words, with no unimplemented claims.
- [ ] User/team agrees to presentation requirement and reviews final entry.

Code repository: https://github.com/Omer-Sut/israel-election-forecast

Preliminary input/config/code hashes and outputs: `reports/baseline-2026-10-21/`. Final code revision, chosen method, final forecast, validation results, and submission status: **pending**.


E009 research-only diagnostic (October24): broader source-tiered final-poll and common-firm comparison executed without fitting. The2021/2022 continuous-error gap falls from8 to6.333 with six matched firms and to4 with three matched original publishers. Shared directional party misses persist; this does not identify a cause or change the forecast method. See final-poll-coverage.md.


E010 preparation: seven-group current reference refresh and explicit seat-space threshold sensitivities; no new learned correction. Standard-library hosted run will export a concrete<=500word method draft alongside decisions and validation. Do not call the package final or source freeze complete: Kan/Channel16 source gaps and direct official verification remain. Check PR execution before treating prepared diagnostics as run.


E010 executed: initial forecast-review40070762691 passed five tests and exact repeats. Seven-group reference and six-election threshold sensitivities are preserved; all rules tie2021/2022, mixed earlier outcomes. Retain mean provisionally. A221word executed-method draft is in reports/forecast-review-2026-10-24/method-draft.txt, alongside source gaps and an explicit provisional export. Final committed-reference comparison is checked on the PR head.


## E011 — electoral allocation, October 24, 2026

User requires excluding 1/2-seat predictions. E010's archived submission draft is superseded; earlier continuous scores remain diagnostics. Active entry point: python scripts/electoral_review.py. New constrained mean decision uses each list0or3+ and total120, changing Amcha1→0 and Reservists2→3; turnout70.63%. This is interim seat-space projection, not an exact current Bader–Ofer outcome. A separate exact vote allocator implements threshold, integer quota, surplus pairing, remainder quotients, half-seat safeguard and unresolved lottery errors. Complete2022 votes and reported historical agreements are used only for calculation verification, not forecasting. Current full vote-share inventory and official agreements remain missing; no votes inferred from published seats. Other qualifiers must be disaggregated. Hosted tests/report reproduction pending on implementation commit; inspect PR for verified results. Preserve frozen reports. Local HEAD3055db4 remains stale; publish on a new branch stacked on PR21 after verifying remote parent. Cumulative user effort unmeasured.


E011 implementation e90478b322615c0b8a2827536f1efe73e9219863 / PR22 (stacked on PR21): hosted allocation run40089831676 passed all seven new tests, reproduced the complete 2022 official allocation and generated identical reports twice. Baseline run40089831626 passed the full standard-library suite and frozen baseline/backtest/database/current-audit checks. Reports are preserved in reports/electoral-review-2026-10-24; the report commit must pass comparison against committed files. Current draft remains provisional; no full current vote-share allocation is possible with present inputs. No merge/submission. Local Git HEAD3055db4 is stale; use the live topic branch and verified PR checks.


## E012 — bounded vote-share audit, October 24, 2026

Checked all seven selected publisher releases and a new original HaMadad final release. No complete matching vote-share vector recovered; this does not prove reports do not exist. CEC dynamic poll index exposes a template, parameterized index and four older PDF leads return403; do not substitute older waves or secondary reconstructions. Indexed CEC text updatedSeptember15 explicitly corroborates3.25% forK26 and120seats/Bader–Ofer, but full legal/official agreement inventory remains unverified. Five current pairs are original-news reported only. See reports/vote-input-audit-2026-10-24/analysis.md and data/snapshots/vote-input-audit-2026-10-24/audit.json.

Carry forward the E011 constrained draft unchanged: Amcha0, Reservists3, total120, turnout70.63%. Three for Reservists is a constrained compromise, not a poll-reported outcome or calibrated mode. No new model search, learned weights, aliases, source promotion, vote reconstruction, merge or submission. Node reconciliation confirmed7 selected releases, zero complete vectors, Amcha1/7 and Reservists3/7 with positive seats (not probabilities), draft SHA256848b92494e1aeeff3e076c6005508c623827adda655a3bd4d4acaecce9078507, exact120 and no1/2 entries. E011 final checks40090060659/40090060581 passed; PR22 remains unmerged. Publish E012 separately stacked on verified PR22 head3ccfcfb; local GitHEAD3055db4 stale. Next: review retained working forecast and outstanding Kan/Channel16/official-inventory questions. Reopen vote allocation only with source-matched complete shares, denominators, original availability and verified agreements. Cumulative hands-on effort unmeasured; bounded retrieval only, no training.


## E013 — frozen review package, October 24, 2026

User approved preparing one review package: full forecast, conditional Reservists0/3/4 allocations and an actual-method description below500words. New scripts/review_package.py preserves the E011 reference byte-for-byte and derives alternatives from the same seven-group mean, minimum3 and total120, fixing Amcha/BlueandWhite/other qualifiers at zero. It isolates the Reservists assumption rather than mixing minimum3/4 policies. No current forecast change, fitted model, new source, probability, full current Bader–Ofer claim, merge or submission. Source freeze remains incomplete.

Package outputs go to reports/review-package-2026-10-24: full table, signed changes/plot, method text, exact forecast copy, input hashes and validation. Two new tests check scenario redistribution and reference preservation; dedicated hosted workflow runs twice and compares committed results when present. Hosted validation pending at implementation preparation; inspect topic PR for final evidence. PR23 head8bccf36 passed baseline40090777155 and scientific40090777187 (85 scientific tests), with all10 audit/handoff paths verified. E013 stacks on that verified parent; local GitHEAD3055db4 is stale. Cumulative user hands-on effort remains unmeasured. Next: review the package, resolve remaining official inventory/form/source questions if evidence becomes available, and obtain explicit authorization before any actual submission.


E013 implementation05949c6f272bdb3587c1c3e51ac949637bd766de / PR24 (stacked on PR23): hosted package40091489461 passed both new tests and exact repeat. Method309words; reference copy SHA256848b92494e1aeeff3e076c6005508c623827adda655a3bd4d4acaecce9078507 unchanged. Reservists0 redistributes one seat each to Likud/UTJ/Raam; Reservists4 removes one from ReligiousZionism. All options120/no1/2. Reports saved in reports/review-package-2026-10-24; final report-commit comparison pending. Keep reference Reservists3. No merge/submission; source freeze incomplete. Use PR final verification for latest checks and authoritative remote head; local Git remains stale.


## E014 — turnout history work, October 24, 2026

User reopened turnout as a priority and requested past-event analysis. Added separate25-election1949–2022 snapshot, preserving CBS publication/coverage mismatch, recent CEC precision, ballots/eligible denominator and source conflicts (1984 explicit78.8 override; raw retrieved79.8 retained).2001 PM-only excluded. scripts/turnout_history.py compares three fixed past-only references, recent six/equal-three-block sensitivity, curated onset-based conflict context and two2022 turnout-intention observations. No fitted coefficient, calibrated probability, causal war/COVID claim or new turnout/seat decision. Current70.63% remains a placeholder; frozen E013 package unchanged.

Read docs/turnout-history.md. Four new tests and dedicated hosted repeat/reference workflow prepared; execution pending at preparation. E014 stacks on verified PR24 headc31d176, whose package40091721369 and baseline40091721373 passed (87 discovered tests,5 optional skips); all14 report/handoff paths verified, artifact12558789469 available. Source/publication-vintage limitations remain explicit. Publish on a separate topic branch, no merge/submission. Local GitHEAD3055db4 stale. Cumulative user hands-on effort unmeasured; bounded historical diagnostic, no broad model search.


E014 executed: implementation8534a3bc09939a10f3599ae2db0c90d38f08d8ec / PR25, turnout40092873881 passed4 tests and exact repeats; baseline40092873828 passed frozen checks. Recent six MAE previous/mean3/median3=3.117/2.059/2.423pp; equal-three-block3.488/3.032/3.312; all22 common folds2.385/2.530/2.700. Mean3 badly misses2015 (6.98pp), so no automatic selection. Next-election candidate values70.63/69.86/70.63%, all within configured bounds. No current forecast change. Named-war first-election changes average−0.82pp(n5); adding4 specified operations gives+0.84(n8), with duplicate2009 collapsed. Scope/era confounding and non-exhaustive onset definitions prevent a causal or2026 adjustment. Two2022 intention releases69/67 undershoot70.63 by1.63/3.63pp; one election cannot calibrate current questions.

Reports and two SVG plots preserved in reports/turnout-history-2026-10-24; final prose-only polish/report-commit reproduction pending. Scientific regression run40092873836 pending at this preparation; inspect PR for final checks. Old E013 reference forecast hash848b92494e1aeeff3e076c6005508c623827adda655a3bd4d4acaecce9078507 unchanged. No merge/submission; local GitHEAD3055db4 stale. Next: discuss the historical evidence and audit comparable national turnout-intention questions before adopting an adjustment.


## E015 — turnout time-series fitting, October 24, 2026

User requested many linear/GLM configurations. Prepared264 fits across8 strictly historical feature groups,3 training windows and level/change ridge plus fractional-logit penalties. No new observations, war/poll calibration or baseline dependencies. Six earlier lag-complete training rows;16 common outer targets; tune from earlier OOF errors only. Four predeclared chronological selectors retain simple references; hindsight rankings separate. Form bounds applied before point selection, unconstrained/convergence diagnostics preserved. Read docs/turnout-models.md and config/turnout-models.json. Optional hosted NumPy/SciPy workflow and5 tests prepared; execution pending.

Current70.63% remains unchanged at preparation. E014 PR25 head2c5f2e7 passed turnout40093149064, baseline40093149045 and scientific40093149051 (91 scientific tests), with14 final file hashes verified and artifact12560240122 available. E015 stacks on verified PR25. Local GitHEAD3055db4 stale. User's explicit many-configuration request authorizes this bounded screen; cumulative hands-on effort unmeasured. No merge/submission. Record executed results and keep/reject reasoning before any adoption.


E015 implementation0341d79bae678bc40ceb938e779c1acf99414dbb / PR26 executed264 configurations (240 distinct historical vectors),16 outer targets and4 earlier-OOF selectors. Turnout40094456219 passed5 tests and repeat comparison at predeclared1e-7; baseline40094456140/scientific40094456111 also succeeded. Best fixed hindsight AR1 ridge(w8,alpha1) recentMAE1.954/current69.43%; calendar ridge(all,alpha1)2.016/69.92%; best GLM AR1(w8,alpha.1)2.154/69.56%; mean3 baseline2.059/69.86. Linear recent6 selectorMAE2.885, broad recent6=5.310, broad expanding=3.730, GLM recent6=5.318; none consistently beats mean3 across metrics. Broad/GLM selector2020 predicts60.83 vs71.52, showing selection/extrapolation failure despite past-only inputs. No learned model adopted.17 configs have historical out-of-form predictions; all current fits converge and are within40–100. Current grid65.59–73.78 is sensitivity, not uncertainty. Current70.63 and all seat forecasts unchanged. Full findings/outputs in reports/turnout-models-2026-10-24. Final report-commit checks pending; inspect PR final verification. Local Git stale; no merge/submission.
