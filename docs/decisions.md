# Decisions and open questions

## Accepted

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

## Provisional choices

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
