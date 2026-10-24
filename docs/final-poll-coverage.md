# E009: final-poll coverage diagnostic

User requested checking whether2021 was harder because of the available data. This diagnostic broadens final-release coverage and compares common polling firms before considering any new model.

Read [analysis and plot](../reports/final-poll-coverage-2026-10-24/analysis.md). Reproduce with `node scripts/final_poll_coverage.mjs`; run five tests with `node --test tests/test_final_poll_coverage.mjs`. No external packages or fitting. Sources in `data/snapshots/final-poll-coverage-2026-10-24/audit.json` are separate from frozen historical/model inputs.

Original three-firm means are reproduced exactly (integer20/12; continuous20.667/12.667). Expanded six-firm means are20/14 and19.333/13. Common original-publisher firms (Midgam/Fuchs/Maagar) give20/18 and20.667/16.667. All five-firm omission sensitivities retain a larger2021 continuous error. This supports both selection sensitivity and persistent shared misses, not causal identification.

One added release has complete original-publisher evidence, one is an attributed republication, and four have complete dated secondary reports. Show each tier separately; never silently train on the secondary additions. Direct2021 may incorporate trend adjustments; matched exclusion in both years is reported. Smith2021's primary graphic and Smith2022's final publisher source remain unverified. Unknown sample size stays missing; no estimated sample size from reported margins of error. No current forecast, learned weights, turnout, baseline or historical model panel changes.

The result is retrospective with previously inspected outcomes, a limited source set and unverified archive vintage. It does not prove all polls failed or that late movement caused the errors. Adding polls can change cancellation between opposing errors, so more coverage need not improve a particular historical score. Avoid hindsight pollster exclusion.
