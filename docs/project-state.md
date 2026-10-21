# Current project state

Last updated: October 21, 2026 (first audited poll dataset and runnable baseline).

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
- Configured a small GitHub Actions CPU workflow to test, reproduce, compare committed reports, and expose a summary/artifact. Actual remote success is pending until a run is verified. A notebook is deferred to avoid duplicate setup.

## Important results and limits

Average absolute disagreement with the input polls: rounded mean 14.4; L1 consensus 12.4. These are in-sample descriptive objectives, not forecast accuracy. Omitting a group changes L1 consensus by 4-8 total absolute seat difference. Only form arithmetic is constrained; no official vote-to-seat allocator is implemented. Full vote shares, surplus agreements, predictive error calibration, and support redistribution after reported Blue and White withdrawal are not modeled.

Kan and several October 20 releases (including i24/Direct Polls and Channel 16) remain unaudited. Keep them on the collection list. Do not call the five-group sample all current evidence.

## Publication and reproduction

Research PR #4 was merged; main was synchronized at 3b56731 before this implementation. Current work uses feat/audited-poll-baseline and a pull request; check Git and workflow status for the latest revision/results.

Run from a fresh Python 3.12 session:

    python -m unittest discover -s tests -v
    python scripts/baseline.py --out-dir output/baseline

See docs/baseline-method.md, data/README.md, and experiment-log.md (R001). Inputs and code hashes are included in generated baseline.json. Workflow logs record the executed Git revision.

## Next actions

1. Verify GitHub-hosted reproduction of this implementation and record its run link/result.
2. Audit omitted latest source releases and reconcile metadata/current lineup changes. Preserve the current snapshot for comparison.
3. Collect comparable historical pre-election polls and evaluate against same-election official outcomes with appropriate cutoffs. Historical outcomes alone are not a backtest.
4. Decide whether to retain this seats-only reference or add the one planned uncertainty/vote-share improvement. Verify operative allocation rules/agreements before implementing a vote-share allocator.
5. Confirm final team/track, timezone, any remaining form validation/precision, and treatment of the other-qualifiers scoring bucket. Keep updating the method report; never submit without the user's explicit authorization.

## Environment notes

Git/gh may not appear on the inherited PATH. Executables are C:\Users\omersu\AppData\Local\Programs\Git\cmd\git.exe and C:\Program Files\GitHub CLI\gh.exe. Approved outside-sandbox operations successfully use the existing keyring login; in-sandbox failures do not prove login is invalid. A safe.directory exception exists only for this exact project path because .git was initially created by the sandbox user.

Local checks used QGIS Python 3.12 via PYTHONHOME, but this is not a project dependency: a normal Python 3.12 runtime suffices. Network/Git writes may need approval. Raw source images/renderings under tmp/ are ignored and are not the sole record of any numerical input. No credentials or personal form responses are committed.
