# E004: unattended robustness batch

Authorized October 22, 2026 while the user is away for approximately two hours. Bounded sensitivity, not broader hyperparameter search or final model selection.

- Fixed inputs: E003 `reference` and `expanded_history` only; original printed Walla fieldwork retained. Do not choose source metadata by its score.
- Full original grid including ensembles at seed20261021. Two identical fits must reproduce every case prediction.
- Fractions0/.10/.25/.50/1 applied to saved unshrunk predictions before continuous simplex projection and unchanged integer reconciliation. No refitting/re-optimizing ensembles by fraction.
- Three forests at20 seeds20261021-20261040. Other families/ensembles are not repeatedly fitted; no ensemble seed-stability claim. Forest-only reconstruction must exactly reproduce full-grid raw predictions at the original seed.
- Every available chronological fold; missing early fits remain explicit. Whole earlier elections train later forecasts with unchanged equal-election weights. Outcomes were inspected previously; earlier OOF results also fit later ensembles. Seeds/list rows are not independent elections.
- Score projected continuous/final integer outputs against official seats. Retain mean/L1 integer controls and continuous mean. Check0% equals mean and25% equals the original fitted pipeline.

Hosted command: `python scripts/robustness.py`. Workflow: `Screen lightweight forecast models`; artifact: `robustness-correction-seeds`, retained30days. Extract and open `index.html`. Shared-scale SVGs show correction sensitivity for every candidate and forest seed plots at25%/100%. CSVs hold every eligible fit, prediction and seed range; raw compressed reports/manifest preserve inputs, hashes, packages, config, commit and runtime. Summary also appears in GitHub's job summary.

No new packages, L0, threshold mechanism, turnout/current forecast change, automatic merge or competition submission. Code/config/audit remain reproducible after artifact expiration; preserve compact checked results in Git after execution.

Preparation adds projection/fraction contract tests. Local Python3.12 is unavailable; hosted tests/full batch are authoritative. Actual run status and verified links belong in project-state/session-log after publication. Configured is not completed.

