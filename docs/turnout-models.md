# E015: turnout regression and GLM time-series screen

User explicitly requested fitting many linear/GLM configurations using time-series data. This supersedes the earlier no-broad-search limit for this bounded turnout screen. There are264 configurations:8 feature groups x3 training windows x(4 level-linear penalties +4 change-linear penalties +3 fractional-logit penalties). No forests/heavy training/new data collection. Hosted CPU uses optional pinned NumPy2.2.6/SciPy1.15.3, separate from the dependency-free baseline.

Input is the unchanged E01425-election turnout history. First3 elections warm up lag features. Fit only after6 earlier lag-complete rows:16 common outer targets,1981–2022. Training windows are all earlier rows or last12/8. Feature groups: AR1, AR3, level/momentum, mean/momentum/gap, election spacing, calendar/post2000 sensitivity, annualized momentum and expanding-level summaries. All scalers are trained per fold; current-date gap/year are known calendar features. Last-three means last three elections, not years. The competition-provided2026-10-27 date is used without claiming new independent verification.

Linear models fit level T/100 or change(T−previous)/100, with alpha0/.01/.1/1. Objective is average squared fraction error/2 plus alpha times squared standardized slopes/2; intercept/drift is not penalized. The fractional-logit GLM uses mean logistic quasi-likelihood plus the same slope penalty at alpha.001/.01/.1. Election rows are equally weighted; registered voters/ballots are not treated as independent GLM trials. No naive voter-count standard errors.

At each target, select using only earlier completed OOF errors, never that target's truth. Four predefined policies compare all models using last6/all earlier folds, linear-only last6 and GLM-only last6; all include three simple references. Require3 earlier OOF folds; otherwise use persistence. Form bounds40–100 inclusive and convergence apply before point selection. Invalid/unconstrained outputs remain diagnostic, never clipped. Hindsight full-grid rankings are labeled as such and kept separate from chronological policy scores. Numerical ties at8-decimal MAE favor references then fixed IDs.

Recent six-election and equal-three-block scores retain the2019–2021 dependence caveat. All outcomes and the post2000 level break have already been inspected; this is not a fresh holdout. Many configurations are algebraically equivalent or correlated. Report distinct prediction vectors, every fit's coefficients/training IDs/scaler, nested choices, convergence, forecasts and bounds. Current war and poll-intention predictors are omitted because audited comparable inputs are insufficient, as E014 records. No automatic current turnout replacement.

Reproduce with requirements-turnout.txt then python scripts/turnout_models.py. Outputs include full JSON, prediction/configuration CSVs, chronological error and stability plots, analysis and hashes. Dedicated workflow runs twice and compares numeric JSON/CSV values within absolute1e-7, exact text/plots and exact configuration/selection IDs. The same tolerance is fixed before execution; meaningful changes or discrete selection changes fail. Five tests cover feature boundaries, past-only selection/admissibility, known linear fit/train-only scaling, fractional-logit constant-response fit and comparator sensitivity. Baseline skips optional fits when dependencies are absent.

No final model, vote/seat change, merge or competition entry is selected by preparing this screen. Read the topic PR for executed results and validation.

## Method references

The [Papke–Wooldridge original fractional-response paper](https://www.nber.org/papers/t0147) motivates a logistic conditional mean with quasi-likelihood for proportions. Our small-election sample does not justify its large-sample inference claims; we report chronological prediction errors. Implementation uses [NumPy2.2 least squares](https://numpy.org/doc/2.2/reference/generated/numpy.linalg.lstsq.html) and [SciPy1.15.3 minimize](https://docs.scipy.org/doc/scipy-1.15.3/reference/generated/scipy.optimize.minimize.html), with exact objectives documented above. No statsmodels dependency is installed.

## Executed evidence

Read reports/turnout-models-2026-10-24/findings.md for numerical findings and keep/reject reasoning. The saved coefficients/scalers are for current fits; historical rows preserve training IDs, status and predictions and are reproducible from the code. No claim is made that every historical fit’s coefficient array is stored.
