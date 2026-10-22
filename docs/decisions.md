# Decisions and open questions

## Accepted

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

