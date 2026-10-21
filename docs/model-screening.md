# Cloud model screening

Implemented October 21, 2026 following the approved plan. This is exploratory screening, not a final model selection or a new 2026 forecast. Frozen baseline/backtest files remain unchanged.

Verified first milestone: [durable real-data report](../reports/screening-2026-10-21/summary.md), [successful cloud execution](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39622248851). All 43 tests and deterministic reruns passed. Experiment runtime=2.720s; full hosted job about 60s. Results do not establish an improvement: 2022 candidate errors=12 at T−6, 12–14 at T−1, versus references=12 at both. The full JSON identifies the exact tested PR merge ref and consumed file hashes; report-generation code/input files matched after download.

## Run from any computer

Open [GitHub Actions](https://github.com/Omer-Sut/israel-election-forecast/actions), select **Screen lightweight forecast models → Run workflow** after merge to the default branch. Before merge, relevant pull requests run automatically. Write access is needed for manual dispatch. No local runtime, secrets, university account or extra cloud service is needed.

Reference environment: Ubuntu 24.04, Python 3.12 and locked `requirements-experiments.txt`: NumPy 2.2.6, SciPy 1.15.3, scikit-learn 1.7.2, CPU-only XGBoost 3.0.5, joblib 1.5.2 and threadpoolctl 3.6.0. These are reproducibility pins, not latest-version claims. [CPU-only XGBoost](https://pypi.org/project/xgboost-cpu/3.0.5/) avoids GPU dependencies; the original baseline stays standard-library only.

The single-thread CPU job has a 20-minute timeout. It installs binary packages, runs tests, executes the screen twice and compares predictions, smoke results and summaries. Its summary and `lightweight-model-screen` download contain full provenance JSON, per-list CSV, readable report and installed packages. Artifacts expire after 30 days; preserve compact milestone outputs in reviewed `reports/` commits. Standard hosted runners are free for public repositories ([GitHub policy](https://docs.github.com/en/actions/concepts/billing-and-usage)).

Optional equivalent commands in ordinary Python 3.12:

```sh
python -m pip install -r requirements-experiments.txt
python -m unittest discover -s tests -v
python scripts/experiments.py --out-dir output/experiments
```

## Fixed initial grid

Settings are explicit in `config/experiments.json`; no automated search occurs.

| Family | Three configurations |
| --- | --- |
| Recency | Poll-age half-life 3 / 7 / 14 days |
| Gaussian GLM (ridge) | Training-standardized features; alpha 1 / 10 / 100; SVD solver |
| Random forest | 100 trees; depth/leaf (2,5) / (3,5) / (3,10) |
| XGBoost | Squared-error residuals; depth/trees (1,50) / (2,50) / (2,100); learning rate .05 |
| Dynamic polling | Daily process/observation variance ratio .01 / .1 / 1 |
| Ensemble | Equal weights / optimized weights with equal-weight L1 penalties 1 / 5 |

The unchanged rounded mean and empirical L1 are two additional references. Seed=20261021; trees use one CPU thread. No locality learner or pretrained model is selected.

## Data and prediction contract

Only configured original-source-audited snapshots enter. Bulk index date proxies, CBS and INES are excluded pending audits. No 2026 forecast is produced or changed.

Reuse the historical configuration's 14-day effective-age window, latest publication per group and end-of-day Asia/Jerusalem T−6/T−1 cutoffs. Filter later publications/known revisions before feature extraction. Recover eligible older releases for trajectories, rejecting ambiguous same-group/publication-day duplicates even in older history. Poll age uses fieldwork end or publication when unknown; dynamic observations use publication day.

Anchor: unrounded equal-group mean. Features: anchor seats, population standard deviation and range across groups, mean poll age, group count, fraction of groups reporting zero allocated seats, average within-group endpoint slope in seats/day, missing-trend flag. With no repeat observations, slope=0 with missing flag=1. Within-group trends avoid confounding changes in pollster composition. Complete audited 120-seat projections permit residual seat zeros under the existing policy; incomplete tables/unknown positive list labels are rejected. Outcome/list coverage must match.

Supervised target: actual final seats minus anchor. Pool election-specific list rows without cross-election party aliases or identity features. Equal total training weight per election across horizons/lists, normalized to mean row weight one. Fit weighted ridge scaling on training rows only; trees use the same row weights. Repeated horizons/party rows are dependent.

Dynamic model: per-list random-walk Kalman filter, observation variance=4 squared seats. Initialize from the first daily mean with variance=4. Average same-day polls with fixed observation variance rather than claiming independent errors. Add `days × ratio × 4` process variance between observations. Forecast the filtered level forward without drift; no fitted house effects or calibrated interval is claimed.

Apply `anchor + .25 × (candidate − anchor)`, Euclidean-project onto the nonnegative sum-120 simplex, then round by deterministic largest remainder using historical list order. Preserve continuous and full/unshrunk diagnostic outputs. No hard movement caps or party-specific floors. Report total/max movement, changed representation and one/two-seat warnings; arithmetic validity is not electoral attainability.

Ensemble members: recency_7, ridge_10, forest_3_5, xgb_2_50, dynamic_01. Combine continuous unshrunk predictions and shrink once. Optimized weights are nonnegative, sum to one, and minimize equal-election mean total absolute continuous/unshrunk error plus `penalty × sum(abs(weight − 1/5))` using a linear program. Rounded/shrunk scores remain separate. Use only earlier strict OOF predictions to fit weights; synthetic outcomes never fit real weights.

Turnout remains previous-election persistence, separately validated within 40.00–100.00% and reported to two decimals. No new turnout/war model.

## Evidence and evaluation

1. **Synthetic smoke:** six artificial elections exercise every configuration, including learned ensembles. No synthetic accuracy ranking; software evidence only.
2. **Current historical diagnostic:** four cases from audited 2021/2022 snapshots. No supervised fit for 2021; 2021-trained 2022 fits are explicitly `one_training_election_diagnostic`. Equal ensemble can run there; optimized ensembles are `insufficient_data`. Both outcomes were already inspected.
3. **Strict screen after audit:** at least two completed earlier elections for supervised fits, with training election dates before the target cutoff. Same-election horizons never train one another. At least two earlier strict OOF elections for optimized ensembles. Missing fits stay explicit.

Reports separate T−6/T−1, show absolute seat error and benchmark movement, and compare each candidate with both references on identical eligible cases. Mean/worst errors are descriptive, not a final ranking. JSON includes per-list representation errors, training elections, dates/URLs, selected/excluded releases, audit tier, input/code hashes, packages, seed, runtime and GitHub commit. The target case's result is used only after its predictions; only earlier outcomes enter training.

## Next steps and acceptance

- Audit at least three groups at both cutoffs for 2015, April/September 2019 and 2020: original values, publication/revision dates, duplicates and lineups. Preserve provenance; never silently promote index date proxies.
- Add audited snapshots/outcomes through a new historical configuration rather than rewriting frozen pilot files. With six elections, strict supervised evaluation can start September 2019; optimized ensembles wait for two earlier strict OOF elections.
- Run the fixed grid; inspect equal-election loss, worst cases and repeated-election-period sensitivity. Retain at most two challengers plus references; prefer simpler references if gains are small/inconsistent. Never choose by preferred-looking current results.
- Later tasks: independently withheld later-poll prediction, calibrated uncertainty/hard bounds, verified vote-to-seat allocation and turnout research. Locality forecasting remains deferred.
- Today prioritizes cloud setup/screening with soft limits. The one-hour schedule is a timebox, not a completed six-election-validation promise. Record runtime separately from actual hands-on effort; prior effort is unmeasured and the approximate eight-hour budget is not reset.

Acceptance checks cover target/future-feature leakage, revision cutoffs, duplicate history, missing lineups, insufficient coverage, equal-election weights, rounding, every adapter, optimizer shrinkage and deterministic reruns. Cloud tests require scientific dependencies, so optional model tests cannot silently skip there; the dependency-free baseline job may skip them.
