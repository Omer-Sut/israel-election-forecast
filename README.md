# Israeli Election Forecast

Build a reproducible model to forecast the results of Israel's 26th Knesset election for the departmental forecasting competition. All project discussion, documentation, and code should be in English; Hebrew source material and party names may be retained where needed.

## Start here

1. Read [the competition brief](docs/competition-brief.md).
2. Read [the current project state](docs/project-state.md) before starting work.
3. Follow [the collaboration guide](CONTRIBUTING.md).
4. Agents should also read [AGENTS.md](AGENTS.md).
5. Follow the [eight-hour plan](docs/project-plan.md) and [user constraints](docs/project-constraints.md) before choosing methods.
6. Use the [submission contract](docs/submission-contract.md) and [field configuration](config/submission-fields.json) for forecast outputs.
7. Read the [user feedback and research agenda](docs/research-agenda.md) and [forecasting research review](docs/forecasting-research.md) before extending or selecting a model.
8. Start data exploration with the [2015–2022 historical database](docs/historical-database.md), including official national/geographic results, bulk poll indexes and INES dictionaries/aggregates.
9. Use the [CBS demographic extension](docs/cbs-demographics.md) for age/sex, socioeconomic and geographic context, with explicit reference years and historical-availability limits.
10. Follow the latest [poll-centered modeling direction](docs/poll-centered-modeling.md): conservative refinements around recent polls; locality forecasting deferred; bounds and uncertainty still under discussion.
11. Use [cloud model screening](docs/model-screening.md) for the implemented 18-configuration grid, hosted execution, evidence tiers and remaining historical poll audits. No challenger has been selected.
12. Review [the first screening report](reports/screening-2026-10-21/summary.md): hosted checks passed, but the limited two-election panel does not establish a winning model.
13. The active screen now uses [six-election training history](docs/six-election-screening.md): 2015/both 2019 elections/2020 supply earlier history for complete 2021/2022 comparisons. See project-state for verified run status.

The original Hebrew guidelines are preserved unchanged as [the source PDF](תחרות%20תחזית%20בחירות%20לכנסת%20ה26.pdf). They are authoritative if the English summary is ambiguous.

## Objective

Predict seats for every electoral list in the submission form and national turnout (%). The primary competition loss is:

```text
seat_error = sum(abs(predicted_seats[list] - official_seats[list]))
```

Lower is better. Turnout accuracy breaks ties. Final official results, including double-envelope ballots, determine the outcome. The PDF gives a submission deadline of **October 26, 2026 at 23:59** and an election date of October 27, 2026. These are document statements, not independently verified current information; the deadline's timezone is not explicitly specified.

## Status

The first preliminary baseline is implemented from six audited poll records (five active polling groups). It compares a rounded mean with an absolute-disagreement consensus and uses official 2022 turnout as a persistence reference. A [historical pilot](docs/historical-backtest.md) now tests both unchanged methods on 2021/2022 at two cutoffs, using 12 audited releases. These are **not submission-ready forecasts or a conclusive model comparison**. See the [current baseline results](reports/baseline-2026-10-21/summary.md), [backtest results](reports/backtest-2026-10-21/summary.md), [implemented method](docs/baseline-method.md), and `docs/project-state.md`.

## Repository and setup

Public repository: [Omer-Sut/israel-election-forecast](https://github.com/Omer-Sut/israel-election-forecast).

Git and GitHub authentication are configured on the original computer. To work on another computer, install Git and clone the repository:

```sh
git clone https://github.com/Omer-Sut/israel-election-forecast.git
cd israel-election-forecast
git switch -c work/short-description
```

Authenticate with `gh auth login` and configure your own Git author identity before contributing. See [the collaboration guide](CONTRIBUTING.md) for other computers and collaborators. The publication script is the original bootstrap helper; use normal commits, pushes, and pull requests for ongoing work.

Reference runtime: **Python 3.12, standard library only**. No package installation or model training is required:

```sh
python -m unittest discover -s tests -v
python scripts/baseline.py --out-dir output/baseline
python scripts/backtest.py --out-dir output/backtest
python scripts/build_database.py
python scripts/cbs_report.py
```

For online work, use the repository's [Actions tab](https://github.com/Omer-Sut/israel-election-forecast/actions): `Reproduce preliminary baseline` -> `Run workflow`. The hosted CPU job tests the implementation, reproduces the committed outputs, and provides a summary/downloadable artifact. Check its run status before relying on successful execution. Inputs, code, and reference outputs are committed; no required file exists only on a contributor's machine. A Colab notebook is deferred to avoid duplicating the execution surface.

## Project records

| File | Purpose |
| --- | --- |
| `docs/competition-brief.md` | English requirements, scoring, source links, and submission checklist |
| `docs/submission-contract.md` | User-transcribed form fields, total-seat rule, and mapping questions |
| `config/submission-fields.json` | Ordered machine-readable output labels and stable project IDs; no predictions |
| `docs/project-state.md` | Latest handoff, completed work, blockers, and next actions |
| `docs/decisions.md` | Durable decisions and unresolved choices |
| `docs/session-log.md` | Concise chronological history |
| `docs/data-sources.md` | Source inventory and provenance conventions |
| `data/README.md` | Actual first-snapshot audit, coverage gaps, and update procedure |
| `docs/baseline-method.md` | Implemented methods, reproduction, diagnostics, and limitations |
| `docs/historical-backtest.md` | Implemented 2021/2022 pilot, audited historical sources, information boundaries and results |
| `docs/historical-database.md` | Six-election database, schema, sources, access, coverage and audit limitations |
| `docs/cbs-demographics.md` | CBS age/sex/socioeconomic tables, locality joins, descriptive examples and temporal limits |
| `docs/research-agenda.md` | User feedback, threshold questions, historical validation and war/turnout proposals |
| `docs/forecasting-research.md` | Primary-source forecasting examples, additional data, applicability and limitations |
| `docs/project-constraints.md` | User requirements, eight-hour budget, and scope limits |
| `docs/project-plan.md` | Task/data/method stages, timeboxes, validation, and stopping rules |
| `docs/experiment-log.md` | Run, effort, evidence, and decision records |
| `docs/method-report.md` | Continuously maintained scaffold for the final explanation |
| `CONTRIBUTING.md` | Branch, review, synchronization, and handoff workflow |
| `AGENTS.md` | Instructions for future coding agents |

No open-source license has been selected. Public visibility alone does not grant an open-source license.
