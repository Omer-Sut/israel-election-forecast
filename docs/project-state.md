# Current project state

Last updated: October 21, 2026 (constraints, source review, and execution plan).

## Goal and user preferences

Build a model predicting Israeli election results for the departmental competition. Work in English. Support multiple computers, collaborators, and future agents through Git and maintained Markdown handoffs.

User has approximately **eight hours total hands-on effort**. No heavy model training from scratch. Favor lightweight numerical methods, consider pretrained models only if worthwhile, keep work online and portable, explain data sources, and document work continuously. See `project-constraints.md` and `project-plan.md`. Earlier setup/planning effort was not timed; confirm whether it must count before assuming eight hours remain.

Public repository: https://github.com/Omer-Sut/israel-election-forecast

## Completed

- Read and visually checked both Hebrew guideline pages; preserved the original PDF unchanged.
- Created the English competition brief, README, agent instructions, collaboration workflow, decision log, session log, source inventory, Git text/ignore settings, and bootstrap helper.
- User installed Git and GitHub CLI and authenticated as Omer-Sut.
- Verified authentication outside the sandbox, initialized Git on main, and created the public GitHub repository.
- Configured repository-local author Omer-Sut with 162723325+Omer-Sut@users.noreply.github.com, using the authenticated account's public ID. Global author identity was not changed.
- Recorded the six user constraints, eight-hour timeboxes, task/data/method plan, experiment/effort log, and final-method-report scaffold.
- Inspected the PDF's linked sources and additional official 2021/2022 results and original poll publications. Source inventory now explains intended use and access/quality limitations.
- Found that Kolot Nodedim's K26 scenario is simulated, and that one Wikipedia poll row conflicts with the original release's text. No data ingestion has occurred; reconcile before use.

## Publication status

Initial publication succeeded; `a1bf22d` was the verified synchronized main before this planning update. The planning update uses topic branch `docs/lightweight-project-plan` and a pull request; inspect Git/PR state for its latest publication status. Public visibility and default branch main were verified previously.

## Environment notes

- The inherited PATH did not expose installed Git/gh. Executables: C:\Users\omersu\AppData\Local\Programs\Git\cmd\git.exe and C:\Program Files\GitHub CLI\gh.exe.
- In-sandbox authentication checks failed; approved outside-sandbox commands successfully used the keyring login. Do not ask the user to repeat login based solely on sandbox failure.
- The sandbox created .git under CodexSandboxOffline, triggering Git's ownership check. Added an approved global safe.directory exception for this exact project path only. No wildcard exception was added.
- Network operations and Git metadata writes may require approved outside-sandbox commands.
- QGIS Python 3.12, pypdf, and Ghostscript were PDF inspection tools, not project dependencies. tmp/pdfs/ contains ignored render intermediates.

## Next actions

1. Follow stage 1 of `project-plan.md`: confirm track/team, exact form party list/field rules, cutoff, timezone, and operative electoral rules/agreements. Form retrieval failed in web tools; several official pages were blocked or empty. Do not infer the output list from Wikipedia and do not submit the form.
2. Within the data timebox, collect a small audited recent-poll set and official national results plus comparable historical polls. Resolve the recorded source discrepancy and separate seats from vote percentages.
3. Choose a minimal portable runtime, produce a poll-consensus and turnout baseline, then evaluate one numerical uncertainty/optimization improvement if data and time allow. Keep the pretrained option off the critical path.
4. Record actual effort/runs, maintain the method-report draft, and reserve time for a fresh hosted reproduction and final output review. No notebook or Actions workflow exists yet.

## Validation and modeling position

Both PDF pages were reviewed. Initial documentation links and publication-script syntax were checked. Git/GitHub publication was verified. The latest planning session reviewed source pages, checked all 12 Markdown files for local links/code fences, checked Git whitespace, verified that timeboxes sum to eight hours, and computed the illustrative combinatorial count with Python. Official search excerpts support 120 seats/3.25%, but full operative allocation rules and current agreements are not yet verified. No model, collected modeling dataset, forecast, or modeling tests exist. Turnout remains required as the tie-breaker.
