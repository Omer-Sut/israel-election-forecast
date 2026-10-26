# Decisions and open questions


## E010 — current forecast review, October 24

User authorized preparing final options. Added five complete current releases in a separate snapshot, preserving all ten old records: N12/C13/Maariv/i24 October23 and IsraelHayom/Kantar October22. Seven reporting groups. Kan23 Democrats8/9 source conflict and Channel16 original-graphic gap stay excluded from the main reference, with explicit secondary sensitivities. Official CEC403/Knesset geo-block persist. Completed BlueandWhite list withdrawal is news-reported, not direct-official verified; all selected polls already allocate zero. Existing current form mappings retained.

Standard-library scripts/forecast_review.py prepares rounded mean, L1, zero-or-3/4 sensitivities, four fixed0/4 scenarios, omission checks, six-election retrospective threshold diagnostics, validated outputs, plot and<=500word method draft. Rounded mean remains provisional; no learned correction or threshold policy adopted. No probability/official allocator claim. Turnout persistence70.63%, configured bounds enforced. See [forecast-review.md](forecast-review.md). Initial implementation13e15d5 / PR21: forecast-review40070762691 passed five tests and exact repeats; baseline40070762676 passed frozen checks. Results preserved in reports/forecast-review-2026-10-24, including a validated provisional export and221word method draft. All six rules tie2021error20/2022error12; April2019 improves40to38 under restrictions while September2019 zero-or-4 worsens12to14. No threshold policy adopted. Small export/plot-axis addition and committed-reference reproduction pending on the report commit. Source freeze remains incomplete; next resolve Kan/Channel16 source gaps and direct official verification, then user review of a concrete final vector. No merge/submission; localGitHEAD3055db4 stale; cumulative user effort unmeasured.


## E009 — final-poll coverage comparison, October 24

User requested testing whether2021's larger error is due to available polls. Separate diagnostic adds six factual transcriptions: one original publisher, one attributed republication, four dated secondary reports. Both broader panels have the same six firms; secondary records remain excluded from training/frozen inputs. [Analysis and plot](../reports/final-poll-coverage-2026-10-24/analysis.md), [protocol](final-poll-coverage.md). Continuous error2021/2022: old different three-firm sets20.667/12.667; same six19.333/13; same original-publisher trio20.667/16.667; matched five excluding Direct20.4/15.2. Selection therefore matters, but shared2021 party misses persist. All single-firm deletion continuous errors remain higher for2021. No causal attribution to late movement or turnout; no hindsight best-firm exclusion or learned correction adopted.

Direct2021 may include trend adjustment; explicit exclusion sensitivity retained. Smith missing primary allocation/source remains excluded. Dates are historically reported, archive vintage unverified. Unknown metadata stays missing. Local Node-tool execution reproduced four output files exactly and original E008 vectors; full five-test hosted workflow pending at preparation. Inputs/code/results stay on a topic branch stacked on PR19 head58faf83; local GitHEAD3055db4 remains stale. No current forecast, turnout, merge or submission change. User cumulative hands-on effort remains unmeasured. Next: review diagnostic, then final current-poll/lineup audit; further historical expansion needs original-source recovery rather than another model sweep.

## E008 training-quality decision (verified)

Poll quality now enters individual-poll learners as source/methodology features and a separately tested past-only training weight. Four ablations isolate representation versus metadata effects; no outcome leakage or raw poll count as independent campaign evidence. Retain this machinery, but do not adopt learned corrections/weights now: no incremental25% integer improvement over poll-basic on2021/2022, and earlier-selected metadata Ridge worsens2021. Small continuous differences are insufficient adoption evidence. Further research needs better audited historical methodology coverage; no more same-data parameter sweep selected. Current forecast/turnout unchanged. See poll-metadata-trial.md and dated analysis.

October23 E006 decision: keep explicit prior-election continuity/pooling context machinery, reject forecast correction adoption now because no fixed25% or earlier-OOF-selected integer gain in2021/2022. Full2015edition-linked data stays separate archive-unverified sensitivity; coverage is not individual demographic identification. Preserve tiny hindsight-only continuous gain without selecting it. Next prioritize current polls/threshold measurements rather than enlarging this matrix; age/sex/2026lineage still audited separately. No merge/submission authorized. See party-area-trial.md and its verified report.

## E007 source refresh

Preserve October21 baseline; separate October23 research reference uses unchanged equal-group methods. Conservative current-version cutoffOctober23 retains original publication dates. Keep partial support/unknown percentages. No crossing probability inferred from poll frequency/sample size, no official-unverified withdrawal hard constraint, no pooled failed-list votes. Complete current sources/lineup before final selection; no wider feature/grid expansion.

## Accepted

- E005 checked outcome: preserve the dated geographic/dynamic ablation and chronological-selection results; no feature configuration establishes2021/2022gains. Do not adopt prototype poll-quality weights: OOF expected-error MAE9.233loses to8.668prior-campaign-average baseline. These are working evidence-based keep/reject decisions for this trial, not a permanent family exclusion or user-selected final forecast. Broader dated demographics/lineages are the next information-gathering step; turnout remains later.

- E005 October22: user requested another bounded geographic/party-identity and dynamic-feature trial, chronological regularization validation and campaign poll accuracy/severity analysis before adopting weights. Supersedes prior blanket locality/active-tabular deferral, not data availability safeguards. Party votes first; turnout/war/economics later. No final method/weight/forecast change selected.

- E004 (October22): user approved bounded unattended sensitivity: correction strengths0/10/25/50/100%, original versus expanded campaign history, every eligible chronological fold, and20 forest seeds. No additional families, L0, final model selection or forecast changes. Hosted CPU, plots and downloadable provenance/results.

- October22: user reaffirmed online-first work and collaboration across people/agents/sessions, with guidance in AGENTS.md. Use connected GitHub publication when local Git metadata/networking is unavailable, isolated topic branches, expected-parent updates and verified hosted checks. Local restrictions do not revoke authorized project publication; respect machine access controls and retain a precise remote/local handoff.
- E003: user authorized the recommended source/history expansion. Keep the grid, correction strength and outcomes fixed while comparing the frozen reference, a publication-age assumption, three repeated original-source releases, and their combination. Review all available folds and continuous stages; do not call repeated old outcomes new blind evidence. L0/representation modeling remains a proposal, not an adopted method.

- A001 (October 21): analysis of E002 does not support replacing either poll reference or choosing a final model. Preserve all candidate results and pause wider configuration search until source/coverage and missing trajectory features are reviewed. This is an evidence-based working recommendation, not a user-selected final method, permanent family exclusion or approval of hard bounds.

- E002 (October 21): user requested using earlier years with sufficient history. Prepare a six-election T−1 panel from original-source-reviewed releases and existing national results. Use 2015/April2019 as initial history, September2019/2020 as strict OOF history and 2021/2022 for complete all-model comparison. Preserve chronological isolation, the original model grid and the fact that both evaluation outcomes were previously seen. Do not lower minimum-history gates merely to remove missing cells.

- October 21, E001: user approved the implementation plan and chose cloud setup/screening first, with soft limits rather than hard movement caps. Use a separate GitHub Actions CPU environment and three fixed configurations each for recency, ridge, forest, XGBoost, dynamic and ensemble; preserve both original references. This supersedes the earlier one-improvement implementation scope, while retaining lightweight compute and the total effort constraint.
- E001 experimental defaults: 25% correction around the unrounded latest-group mean, no hard bounds, deterministic sum-120 reconciliation. Numerical defaults are test settings, not historically selected parameters or calibrated confidence claims. Restrict real inputs to audited snapshots; one-election fits are diagnostics, strict fits need two prior elections and optimized ensembles need two prior strict OOF elections. No final model or replacement 2026 forecast is selected.

| Date | Decision | Basis |
| --- | --- | --- |
| 2026-10-21 | Use English for communication, code, and project documentation. Retain Hebrew sources where needed. | Explicit user request |
| 2026-10-21 | Maintain Git history and repository-based context for other computers, people, and agents. | Explicit user request |
| 2026-10-21 | GitHub owner is `Omer-Sut`; repository can be public. | Explicit user reply and profile link |
| 2026-10-21 | Preserve the original guidelines PDF and keep a separate English summary. | Project setup choice for traceability |
| 2026-10-21 | Evaluate primarily with total absolute seat error; include turnout. | Competition requirements |
| 2026-10-21 | Created public repository `Omer-Sut/israel-election-forecast`; use a repository-local GitHub noreply author for setup commits. | User authorized public GitHub publication; authenticated public account ID verified |
| 2026-10-21 | Budget approximately eight total hands-on hours; exclude heavy training from scratch and avoid expensive searches. | Explicit user constraints and time-budget clarification |
| 2026-10-21 | Prioritize lightweight numerical/statistical methods; consider pretrained open-source models only as optional candidates. | User preference; no particular model approved or selected |
| 2026-10-21 | Keep required code/data/context online and portable across devices; maintain documentation during work to minimize final-report effort. | Explicit user requirements |
| 2026-10-21 | Organize execution around exact task definition, available-data review, and method comparison. | Explicit user requested sequence |
| 2026-10-21 | Preserve the supplied form order as 14 named lists plus combined other qualifying parties (120 seats total), with turnout separately. Store no personal form responses or dummy forecast values. | User-supplied full form transcription and explicit dummy-input clarification |
| 2026-10-21 | Turnout's reported point prediction and export must lie in [40.00, 100.00] percent, inclusive; use two-decimal presentation. | User explicitly confirmed form bounds; display precision is a project convention, not a verified input step |
| 2026-10-21 | Proceed with current Joint List polling mapped to the form's Hadash-Ta'al field as an explicit assumption; retain historical distinctions. | User accepted proceeding after the three-party composition was explained |
| 2026-10-21 | Use standard-library Python 3.12 and a small hosted GitHub Actions CPU job for the first baseline; defer notebook/dependencies. | Minimal setup and direct cross-device reproduction |
| 2026-10-21 | Proceed with the historical backtest, initially 2021/2022; retain the unchanged reference methods while evaluating. | Explicit user instruction following the proposed initial scope |
| 2026-10-21 | Center the active modeling direction on recent polls; investigate modest refinements around a benchmark. Defer bottom-up locality forecasting to a possible future direction. | Explicit user feedback; belief that current mean/L1 is close remains unverified |
| 2026-10-21 | Discuss bounded/conservative adjustments and recent-poll consistency as an auxiliary diagnostic. No buffer width, hard cap, confidence level or final model is selected yet. | Explicit user request to discuss solution-space limits and another possible metric |

## Provisional choices

- Read [poll-centered-modeling.md](poll-centered-modeling.md) for the latest user direction, dynamic model explanation, independent withheld-poll evaluation, and proposed shrinkage/per-party/joint bounds. Historical election error remains primary; agreement with an input benchmark cannot establish independent accuracy. Predictive uncertainty and operational search caps must stay distinct. No new model or bound is implemented by this discussion.

- User requested broad CBS age/sex/socioeconomic statistics linkable to election locations across years. Link by locality code, preserve both demographic reference year and election date, and retain actual geographic resolution. Do not infer individuals' voting choices or a precinct catchment from a polling building's location.
- Keep CBS source availability uncertified until release/revision dates are verified; a 2022 census reference date is not a 2022 publication date. Preserve suppression as missing, use aligned population/vote denominators, retain socioeconomic rank scope, and do not backcast/interpolate missing years automatically.

- User explicitly expanded data collection to all six elections from the 20th Knesset (2015) through 2022, with as many accessible campaign polls as feasible and easy CEC/INES tabular integration, **before further model selection**.
- Use a portable generated SQLite database with versioned compressed inputs/source archives and GitHub Actions downloads. This avoids a machine-specific dependency or shared mutable binary; ordinary offline rebuild/query uses Python's standard library. Optional pandas/lxml/requests are confined to collection.
- Retain bulk poll indexes as lower-tier transcriptions with unknown publication dates and unresolved party identities; do not silently replace the audited pilot panel. Raw INES respondent files are not republished without verified rights; integrate dictionaries and unweighted marginal aggregates first.

- The first implementation uses a 14-day effective poll-age window, one latest audited release per group, equal weights, rounded mean and empirical L1 consensus. These are agent-selected reference choices, not user-selected final methods or settings established through historical model selection. Preserve the original outputs when comparing alternatives.
- R002 now provides a limited retrospective check of those fixed choices: two elections, T-6/T-1 cutoffs, three groups each. It does not establish a final model or an optimal window/weight. Alphabetical election-specific IDs determine historical rounding ties; no post-election winner ordering or current-form mapping is used. Source-vintage and coverage limitations remain explicit.
- Plan for the systematic track because this is a modeling project. Confirm track and participants before preparing submission.
- Plan deadlines using Asia/Jerusalem; the PDF does not explicitly specify the timezone.
- Use topic branches and pull requests for collaboration.
- Use the eight-hour timeboxes in `project-plan.md`; baseline first, then at most one numerical improvement and a historical check.
- A Colab wrapper remains optional later; the first implementation already has a hosted GitHub Actions workflow. Inspect run status before claiming remote success.
- Concentrate on evidence-supported plausible outcomes. The user's small-solution-space intuition motivates efficient sampling/optimization, not exhaustive enumeration or unsupported party exclusions.

## Open

- Historical range is now explicitly 2015–2022 and the research database is assembled. War/turnout analysis and forests/pretrained alternatives remain proposals; no new model is approved or implemented. See the [research agenda](research-agenda.md), [source review](forecasting-research.md) and [database guide](historical-database.md).
- Team members and eligibility; chosen competition track.
- Official/poll/form list mappings, hidden form validation, turnout precision, and exact timezone; form party inventory is now recorded.
- Precise scoring treatment of several lists within the form's other-qualifiers bucket; retain disaggregated internal outcomes.
- Official current election information and verified allocation rules.
- Data sources, rights, coverage, historical validation design, and cutoff policy.
- Model, programming language, supported runtime, dependency management, and experiment tracking.
- Whether the eight-hour budget includes planning/setup effort already spent; actual earlier effort has not been measured.
- Repository license and any external data/artifact storage.
- Collaborator invitations (public read access does not grant write access).

Record decisions here when made, including rationale and relevant evidence. Do not retroactively describe proposals as user-approved decisions.


## E008 cross-run verification follow-up — October 24

Report commit033ef260 passed baseline40066365528; scientific40066365525 passed model tests and exact same-run repeats but failed committed JSON byte comparison. All integer allocations/errors, selected fractions, summary and plot match. Of289 numerical differences, all above1e-10 are weighted-forest continuous outputs, maximum0.016915 seats. No model configuration or saved reference changed. Cross-run comparison now allows absolute0.02 seats only for weighted-forest continuous predictions/errors and1e-10 for other floats; discrete values and structure remain exact. This tolerance was set after observing the discrepancy and is not evidence of bitwise reproducibility. Three comparator regression tests added; hosted rerun pending. No correction adopted; user cumulative effort remains unmeasured.


## E011 — electoral allocation, October 24, 2026

User requires excluding 1/2-seat predictions. E010's archived submission draft is superseded; earlier continuous scores remain diagnostics. Active entry point: python scripts/electoral_review.py. New constrained mean decision uses each list0or3+ and total120, changing Amcha1→0 and Reservists2→3; turnout70.63%. This is interim seat-space projection, not an exact current Bader–Ofer outcome. A separate exact vote allocator implements threshold, integer quota, surplus pairing, remainder quotients, half-seat safeguard and unresolved lottery errors. Complete2022 votes and reported historical agreements are used only for calculation verification, not forecasting. Current full vote-share inventory and official agreements remain missing; no votes inferred from published seats. Other qualifiers must be disaggregated. Hosted tests/report reproduction pending on implementation commit; inspect PR for verified results. Preserve frozen reports. Local HEAD3055db4 remains stale; publish on a new branch stacked on PR21 after verifying remote parent. Cumulative user effort unmeasured.
