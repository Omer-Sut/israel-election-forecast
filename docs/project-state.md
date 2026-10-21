# Current project state

Last updated: October 21, 2026 (GitHub publication).

## Goal and user preferences

Build a model predicting Israeli election results for the departmental competition. Work in English. Support multiple computers, collaborators, and future agents through Git and maintained Markdown handoffs.

Public repository: https://github.com/Omer-Sut/israel-election-forecast

## Completed

- Read and visually checked both Hebrew guideline pages; preserved the original PDF unchanged.
- Created the English competition brief, README, agent instructions, collaboration workflow, decision log, session log, source inventory, Git text/ignore settings, and bootstrap helper.
- User installed Git and GitHub CLI and authenticated as Omer-Sut.
- Verified authentication outside the sandbox, initialized Git on main, and created the public GitHub repository.
- Configured repository-local author Omer-Sut with 162723325+Omer-Sut@users.noreply.github.com, using the authenticated account's public ID. Global author identity was not changed.

## Publication status

Initial publication succeeded. Commit `195022d` was pushed to `main`; local HEAD and GitHub's `refs/heads/main` matched exactly, and the working tree was clean. Public visibility and default branch `main` were verified. This handoff is updated in a subsequent documentation commit; check actual Git state for the latest revision.

## Environment notes

- The inherited PATH did not expose installed Git/gh. Executables: C:\Users\omersu\AppData\Local\Programs\Git\cmd\git.exe and C:\Program Files\GitHub CLI\gh.exe.
- In-sandbox authentication checks failed; approved outside-sandbox commands successfully used the keyring login. Do not ask the user to repeat login based solely on sandbox failure.
- The sandbox created .git under CodexSandboxOffline, triggering Git's ownership check. Added an approved global safe.directory exception for this exact project path only. No wildcard exception was added.
- Network operations and Git metadata writes may require approved outside-sandbox commands.
- QGIS Python 3.12, pypdf, and Ghostscript were PDF inspection tools, not project dependencies. tmp/pdfs/ contains ignored render intermediates.

## Next actions

1. Confirm competition track/team and inspect the university-authenticated form for the exact party list and output format. Do not automate submission.
2. Verify official current dates, electoral allocation rules, surplus agreements, and poll publication restrictions. Record sources and dates.
3. Inventory historical results and polls, choose a reproducible runtime and baseline, and backtest with time-respecting cutoffs and absolute seat error.

## Validation and modeling position

Both PDF pages were reviewed. Documentation links and publication-script syntax were checked. Git initialization, GitHub authentication, public account ID, and repository creation were verified. No model, collected data, forecast, or modeling tests exist yet. Turnout remains required as the competition tie-breaker.
