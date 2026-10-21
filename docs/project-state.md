# Current project state

Last updated: October 21, 2026 (user-transcribed submission form contract).

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
- Recorded the user's full form transcription in `submission-contract.md` and `config/submission-fields.json`: 14 named lists, combined other qualifying parties, total 120 seats, turnout, and systematic-track fields. Personal/account details and dummy inputs are excluded. This is an output contract, not a forecast.
- User confirmed turnout bounds of **40.00-100.00% inclusive**. Configuration contract v2 and model/export guidance record this hard output constraint. Two-decimal presentation is specified; exact accepted decimal increments remain unknown. No model/export validator exists yet.

## Publication status

Form-contract PR #2 was merged; `21fe3fe` was verified synchronized main before the turnout-bounds update. This update uses topic branch `docs/turnout-form-bounds` and a pull request; inspect actual Git/PR state for its latest publication status.

## Environment notes

- The inherited PATH did not expose installed Git/gh. Executables: C:\Users\omersu\AppData\Local\Programs\Git\cmd\git.exe and C:\Program Files\GitHub CLI\gh.exe.
- In-sandbox authentication checks failed; approved outside-sandbox commands successfully used the keyring login. Do not ask the user to repeat login based solely on sandbox failure.
- The sandbox created .git under CodexSandboxOffline, triggering Git's ownership check. Added an approved global safe.directory exception for this exact project path only. No wildcard exception was added.
- Network operations and Git metadata writes may require approved outside-sandbox commands.
- QGIS Python 3.12, pypdf, and Ghostscript were PDF inspection tools, not project dependencies. tmp/pdfs/ contains ignored render intermediates.

## Next actions

1. Form inventory is now known. Resolve official/poll/form mappings (especially Joint List versus Hadash-Ta'al), operative rules/agreements, cutoff, timezone, and track/team. Hidden form validation and turnout precision remain unverified. The user's dummy form entries establish neither predictions nor final presentation consent. Do not submit the form.
2. Within the data timebox, collect a small audited recent-poll set and official national results plus comparable historical polls. Resolve the recorded source discrepancy and separate seats from vote percentages.
3. Choose a minimal portable runtime, produce a poll-consensus and turnout baseline, then evaluate one numerical uncertainty/optimization improvement if data and time allow. Keep the pretrained option off the critical path.
4. Record actual effort/runs, maintain the method-report draft, and reserve time for a fresh hosted reproduction and final output review. No notebook or Actions workflow exists yet.

## Validation and modeling position

Both PDF pages and the user-transcribed form sections were reviewed. Prior documentation/link checks and Git/GitHub publication were verified. The form explicitly confirms 120 total seats; full operative allocation rules and current agreements remain unverified. No model, collected modeling dataset, forecast, or modeling tests exist. Turnout remains required as the tie-breaker.
