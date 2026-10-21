# Israeli Election Forecast

Build a reproducible model to forecast the results of Israel's 26th Knesset election for the departmental forecasting competition. All project discussion, documentation, and code should be in English; Hebrew source material and party names may be retained where needed.

## Start here

1. Read [the competition brief](docs/competition-brief.md).
2. Read [the current project state](docs/project-state.md) before starting work.
3. Follow [the collaboration guide](CONTRIBUTING.md).
4. Agents should also read [AGENTS.md](AGENTS.md).
5. Follow the [eight-hour plan](docs/project-plan.md) and [user constraints](docs/project-constraints.md) before choosing methods.

The original Hebrew guidelines are preserved unchanged as [the source PDF](תחרות%20תחזית%20בחירות%20לכנסת%20ה26.pdf). They are authoritative if the English summary is ambiguous.

## Objective

Predict seats for every electoral list in the submission form and national turnout (%). The primary competition loss is:

```text
seat_error = sum(abs(predicted_seats[list] - official_seats[list]))
```

Lower is better. Turnout accuracy breaks ties. Final official results, including double-envelope ballots, determine the outcome. The PDF gives a submission deadline of **October 26, 2026 at 23:59** and an election date of October 27, 2026. These are document statements, not independently verified current information; the deadline's timezone is not explicitly specified.

## Status

Requirements review, initial source inspection, and an eight-hour execution plan are documented. Prefer lightweight numerical methods, one baseline and one justified improvement, online reproduction, and documentation during experiments. No modeling dataset has been collected, no final method has been selected, and no forecast has been produced. See `docs/project-state.md` for the latest handoff and next actions.

## Repository and setup

Public repository: [Omer-Sut/israel-election-forecast](https://github.com/Omer-Sut/israel-election-forecast).

Git and GitHub authentication are configured on the original computer. To work on another computer, install Git and clone the repository:

```sh
git clone https://github.com/Omer-Sut/israel-election-forecast.git
cd israel-election-forecast
git switch -c work/short-description
```

Authenticate with `gh auth login` and configure your own Git author identity before contributing. See [the collaboration guide](CONTRIBUTING.md) for other computers and collaborators. The publication script is the original bootstrap helper; use normal commits, pushes, and pull requests for ongoing work.

No programming language, dependency set, or runtime version has been selected yet. The QGIS Python installation used to read the PDF is a local inspection tool, not a project dependency.

Online work is the priority: GitHub holds durable project state; a hosted CPU notebook is proposed for the first implementation, with optional GitHub Actions automation later. These execution surfaces are not configured yet. Each run should work from versioned inputs/code and save its results to a shared durable location.

## Project records

| File | Purpose |
| --- | --- |
| `docs/competition-brief.md` | English requirements, scoring, source links, and submission checklist |
| `docs/project-state.md` | Latest handoff, completed work, blockers, and next actions |
| `docs/decisions.md` | Durable decisions and unresolved choices |
| `docs/session-log.md` | Concise chronological history |
| `docs/data-sources.md` | Source inventory and provenance conventions |
| `docs/project-constraints.md` | User requirements, eight-hour budget, and scope limits |
| `docs/project-plan.md` | Task/data/method stages, timeboxes, validation, and stopping rules |
| `docs/experiment-log.md` | Run, effort, evidence, and decision records |
| `docs/method-report.md` | Continuously maintained scaffold for the final explanation |
| `CONTRIBUTING.md` | Branch, review, synchronization, and handoff workflow |
| `AGENTS.md` | Instructions for future coding agents |

No open-source license has been selected. Public visibility alone does not grant an open-source license.
