# Current project state

Last updated: October 21, 2026 (user review, forecasting literature and additional-data research).

## Goal and constraints

Forecast the 26th Knesset competition outputs in English, using approximately eight total hands-on hours, lightweight CPU methods, shared online execution, and continuous documentation. User's hands-on effort is not the same as agent/tool wall-clock time; earlier setup was not timed. Do not reset the budget each session.

Repository: https://github.com/Omer-Sut/israel-election-forecast

## Implemented

- Preserved and reviewed the original Hebrew PDF and the user-transcribed form. Contract: 14 named-list seat fields plus combined other qualifying parties, total 120, and turnout within [40.00, 100.00] percent inclusive.
- Recorded the user's accepted current Joint List -> Hadash-Ta'al form mapping as an explicit assumption, preserving historical distinctions. Current Religious Zionism/Zehut uses the Religious Zionism slot with its combined source label retained.
- Collected six factual, original-source-audited poll records, selecting five latest audited polling groups. Older Maariv/Lazar is replaced by newer Walla/Lazar, avoiding double counting. This is not exhaustive latest-poll coverage.
- Checked Channel 13's original graphic: Likud=18, UTJ=7, full total=120. Its body says Likud=17; conflict is retained, with the graphic used consistently. Original graphic URL/hash are recorded.
- Stored partial official 2022 results with election-specific IDs. Turnout persistence reference is 70.63%; current self-reported voting intention remains a separate diagnostic.
- Implemented standard-library Python 3.12: latest-group selection, explicit mappings, rounded-mean reference, empirical L1 consensus via a small dynamic program, output validation, hashes, and omission sensitivity.
- Generated durable preliminary reports at reports/baseline-2026-10-21/. Both outputs pass form arithmetic. They are not final, historically validated, or proven electorally attainable forecasts.
- Nine meaningful software checks pass locally. No historical poll-to-result backtest or probability calibration has run.
- Configured and verified a small GitHub Actions CPU workflow: all tests and byte-for-byte report reproduction passed in hosted run 39572969093 for implementation commit aee2f11. Run: https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39572969093 . A notebook is deferred to avoid duplicate setup.

## Important results and limits

The user requested an explanation of the autonomous baseline and then asked to preserve feedback, research established forecasting approaches, and identify useful non-headline-poll data. Read [research-agenda.md](research-agenda.md) for the full feedback, exact window/omission clarifications, proposed historical range and war/turnout design; read [forecasting-research.md](forecasting-research.md) for primary-source examples (Spain, US, UK, India/random forests), TabPFN caveats, additional data and rule evidence. These are research/proposals, not new implemented models. Existing configurations, poll snapshots and forecast outputs are unchanged. No historical backtest or war-effect calculation has run.

Both PDF pages were rechecked: the target is interpreted as final allocated seats after threshold exclusion, using the stated final official outcome. Readable official 2022 outcomes corroborate this. Official-domain indexed text supports 3.25% of valid votes, and Knesset research notes a theoretical three-seat result rather than a universal four-seat minimum. Full operative 2026 rules/agreements remain unverified because direct official rule retrieval was blocked; no allocator has been built.

Average absolute disagreement with the input polls: rounded mean 14.4; L1 consensus 12.4. These are in-sample descriptive objectives, not forecast accuracy. Omitting a group changes L1 consensus by 4-8 total absolute seat difference. Only form arithmetic is constrained; no official vote-to-seat allocator is implemented. Full vote shares, surplus agreements, predictive error calibration, and support redistribution after reported Blue and White withdrawal are not modeled.

Kan and several October 20 releases (including i24/Direct Polls and Channel 16) remain unaudited. Keep them on the collection list. Do not call the five-group sample all current evidence.

## Publication and reproduction

Baseline PR #5 was merged; before this research update, main was clean and matched origin/main at ec4396e. The research/documentation work uses docs/research-methods-and-user-feedback. Publication and documentation checks are recorded below after verification; inspect actual Git/PR state for subsequent changes. The verified baseline hosted run remains evidence for its implementation, not this new research.

Research validation: relative local-file links and code-fence balance passed across 16 Markdown files; Git whitespace checks passed. Reviewed changes are documentation only; executable code, configurations, data snapshots and forecast reports are unchanged. No new predictive tests were claimed or run for this research.

Run from a fresh Python 3.12 session:

    python -m unittest discover -s tests -v
    python scripts/baseline.py --out-dir output/baseline

See docs/baseline-method.md, data/README.md, and experiment-log.md (R001). Inputs and code hashes are included in generated baseline.json. Workflow logs record the executed Git revision.

## Next actions

1. Discuss the documented input tables and candidate methods before selecting a final model. Baseline window/weights remain unvalidated implementation choices, now explicitly classified as provisional in decisions.md.
2. Assemble 2021/2022 pre-election polls plus official targets for an initial historical comparison. An original March 19, 2021 Channel 13 poll was located, not ingested. If time permits, extend to six 2015-2022 elections and separately summarize the repeated 2019-2021 period. Use time-respecting cutoffs and whole-election evaluation.
3. If pursuing the user's war/turnout idea, build the official series beginning in 1949 and predefine conflict/lag coding before comparison. The inspected CBS table ends in 2021 despite a 1949-2022 title; official 2022 turnout is already available separately. No directional adjustment is justified yet.
4. Audit omitted current releases/current lineup changes and preserve the original snapshot. Obtain complete operative rules/agreements before implementing vote-share allocation. Consider one justified uncertainty improvement or a small forest challenger only after defining features and validation; no pretrained election-specific checkpoint was verified.
5. Confirm final team/track, timezone, remaining form validation/precision, and other-qualifiers scoring. Keep updating the method report and preserve final-report time; never submit without explicit authorization.

## Environment notes

Git/gh may not appear on the inherited PATH. Executables are C:\Users\omersu\AppData\Local\Programs\Git\cmd\git.exe and C:\Program Files\GitHub CLI\gh.exe. Approved outside-sandbox operations successfully use the existing keyring login; in-sandbox failures do not prove login is invalid. A safe.directory exception exists only for this exact project path because .git was initially created by the sandbox user.

Local checks used QGIS Python 3.12 via PYTHONHOME, but this is not a project dependency: a normal Python 3.12 runtime suffices. Network/Git writes may need approval. Raw source images/renderings under tmp/ are ignored and are not the sole record of any numerical input. No credentials or personal form responses are committed.
