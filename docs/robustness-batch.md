# E004: unattended robustness batch

Authorized October 22, 2026 while the user is away for approximately two hours. Bounded sensitivity, not broader hyperparameter search or final model selection.

- Fixed inputs: E003 `reference` and `expanded_history` only; original printed Walla fieldwork retained. Do not choose source metadata by its score.
- Full original grid including ensembles at seed20261021. Two identical fits must reproduce every case prediction.
- Fractions0/.10/.25/.50/1 applied to saved unshrunk predictions before continuous simplex projection and unchanged integer reconciliation. No refitting/re-optimizing ensembles by fraction.
- Three forests at20 seeds20261021-20261040. Other families/ensembles are not repeatedly fitted; no ensemble seed-stability claim. Forest-only reconstruction must exactly reproduce full-grid raw predictions at the original seed.
- Every available chronological fold; missing early fits remain explicit. Whole earlier elections train later forecasts with unchanged equal-election weights. Outcomes were inspected previously; earlier OOF results also fit later ensembles. Seeds/list rows are not independent elections.
- Score projected continuous/final integer outputs against official seats. Retain mean/L1 integer controls and continuous mean. Check0% equals pipeline reconciliation of the anchor and25% equals the original fitted pipeline. Exact-integer mean rounding can break tied remainders differently from floating-point reconciliation; preserve and flag this zero-correction discrepancy rather than altering frozen code.

Hosted command: `python scripts/robustness.py`. Workflow: `Screen lightweight forecast models`; artifact: `robustness-correction-seeds`, retained30days. Extract and open `index.html`. Shared-scale SVGs show correction sensitivity for every candidate and forest seed plots at25%/100%. CSVs hold every eligible fit, prediction and seed range; raw compressed reports/manifest preserve inputs, hashes, packages, config, commit and runtime. Summary also appears in GitHub's job summary.

No new packages, L0, threshold mechanism, turnout/current forecast change, automatic merge or competition submission. Code/config/audit remain reproducible after artifact expiration; preserve compact checked results in Git after execution.

Preparation adds projection/fraction contract tests. Local Python3.12 is unavailable; hosted tests/full batch are authoritative. Actual run status and verified links belong in project-state/session-log after publication. Configured is not completed.

First hosted run39750028287 passed49 tests and unchanged reference/campaign-history reproduction, then intentionally failed the original assumption that floating reconciliation must equal exact-integer mean rounding at0%. A regression fixture with three equal one-third remainders demonstrates the difference. Revised batch records this caveat while leaving both forecasting algorithms unchanged; the failed run's partial artifact is not a completed result.

Verified completion: implementationbe272a4, [PR #15](https://github.com/Omer-Sut/israel-election-forecast/pull/15), [successful screen39750449237](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39750449237) and [baseline39750449205](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39750449205). All50 tests passed; batch51.396seconds,3080score rows. [Full artifact](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39750449237/artifacts/12413786085) verified1,156,262bytes/83files/unexpired throughNovember21. Extract and open index.html; summary is also on the run page. Outputs identify tested PR merge reff5ce233, not a completed merge. No final model selected; inspect correction/seed plots next session.

