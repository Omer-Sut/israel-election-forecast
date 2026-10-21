# Historical backtest pilot

Implemented October 21, 2026 following the user's instruction to proceed. Run R002 evaluates the **existing two methods**, not a newly selected model. Results: [readable report](../reports/backtest-2026-10-21/summary.md), [per-list predictions/errors](../reports/backtest-2026-10-21/seat-errors.csv), [machine-readable audit](../reports/backtest-2026-10-21/backtest.json).

## Scope and what was fixed

Start with 2021 and 2022, as proposed in the research agenda. Each has two forecast horizons: **six days** before voting, matching the current 2026 snapshot's lead time, and **one day** before voting using publications already available. These four cases are **two election outcomes**, not four independent validation observations.

Keep the baseline choices fixed: 14 elapsed days of poll age, latest audited release per group, equal group weights, rounded mean and empirical L1 consensus. No weights, time window, house effects, features, or hyperparameters were fitted to these election results. The functions are imported unchanged from `scripts/baseline.py`. There is no random seed or training step.

The source panel was assembled for readable original-source coverage, not to minimize computed errors. It is small and incomplete; do not describe it as every final poll. Expansion to six elections in 2015-2022 is still pending, not implemented by this pilot.

## Inputs and provenance

- `data/snapshots/historical-2026-10-21/polls-2021.json`: six releases, three groups (Camil Fuchs/Channel 13; Midgam/N12; Maagar Mohot/Israel Hayom-i24NEWS).
- `data/snapshots/historical-2026-10-21/polls-2022.json`: six releases, three groups (Camil Fuchs/Channel 13; Midgam/N12; Direct Polls/Channel 14).
- `data/snapshots/historical-2026-10-21/outcomes.json`: [final official 2021](https://votes24.bechirot.gov.il/nationalresults) and [2022](https://votes25.bechirot.gov.il/nationalresults) seats and turnout. This covers all seat-winning lists and modeled zero-seat lists, not every party's vote count. Unmodeled lists have zero seats in both predictions and official results, so adding their zero terms cannot change seat error.
- `config/historical-backtest.json`: horizons, window, minimum three groups, input locations, and turnout references. The 2021 reference is official [2020 turnout](https://votes23.bechirot.gov.il/nationalresults), 71.52%; the 2022 reference is official 2021 turnout, 67.44%. The 2022 target is never a reference for an earlier election.

Each poll records original URL, publication date, known source-update date, fieldwork/sample/mode when established, a complete numerical seat transcription, separate below-threshold percentages, and audit notes. Unknown metadata stays unknown. Only factual transcriptions and provenance are stored; publisher articles/graphics are not redistributed or relicensed. No respondent-level personal data was collected. Review began at 11:47:56 UTC; retrieval date is October 21, 2026.

Original releases were discovered through historical poll indexes, then numerical inputs were checked against the **publishers**, not copied from Wikipedia tables. Original source URLs are also linked individually in the result report. Main exclusions/limits:

- 2021 Panels/103fm/Maariv and Kan releases are not ingested; some original links were unreadable. Other groups were not exhaustively collected.
- 2022 Kan/Maariv and Midgam's Galei Tzahal release referenced around October 26 are not ingested. Our latest-audited Midgam inputs are N12 releases; they are not necessarily its latest publication across every commissioning outlet.
- The N12 October 24, 2022 body reports National Unity's gain but not its absolute level. **13 seats is derived as 120 minus 107 explicitly listed seats for the other qualifying lists**, under the complete-lineup audit. This derivation is recorded separately in the snapshot; no later result or poll supplies it.
- C13 October 25, 2022 uses the publisher's actual 801 respondents. A government-filing search excerpt says 800; that discrepancy is noted rather than mixed into the record. It does not affect equal seat weights.
- Where displayed, actual respondent counts are used rather than initial target sample sizes. No sample-size weighting is applied.

## Information boundaries and identities

Cutoffs are end of the specified day in Asia/Jerusalem: March 17/22, 2021, and October 26/31, 2022. Both publication and any recorded source-update date must be no later than cutoff. Age uses fieldwork end when known, otherwise publication; the 14-day lower bound is inclusive. Exit polls and hypothetical lineups are not admissible pre-election observations.

**Vintage limitation:** these are historical-dated publisher pages inspected in 2026. Independently authenticated archive copies as of each old cutoff were not obtained. Known later revisions are excluded; lack of an unknown revision is not proven. This is a retrospective pilot with date safeguards, not a certified real-time reconstruction. Current pages may have updated navigation or legacy redirects; these are not historical forecasting features.

Each election has its own IDs and Hebrew/English labels. The 2021 Joint List stays separate from 2022 Hadash-Taal/Balad; New Hope and Blue and White in 2021 are not treated as the 2022 National Unity list. There is no 2026 form alias or pooled other category in historical scoring. List order for rounding/optimizer ties is alphabetical by election-specific internal ID, not the later ordering of election winners.

Forecast generation accepts only the poll snapshot/cutoff and fixed method choices. Official outcomes are loaded **after all case predictions exist** and only used to score. Previous-election turnout is passed separately. Tests change future/exit-poll inputs and target outcomes to verify that inadmissible information cannot change earlier predictions.

## Scoring and findings

Main metric is `sum(abs(predicted_seats - official_seats))` over the election's modeled lists. Every vector totals 120. Moving one seat from one list to another contributes two points to this error. Turnout uses absolute percentage-point error as our transparent diagnostic; the competition only specifies turnout accuracy as tie-breaker.

| Election | Horizon | Rounded mean | Empirical L1 | Turnout persistence error |
| --- | --- | ---: | ---: | ---: |
| 2021 | Six days before | 24 | 22 | 4.08 pp |
| 2021 | Day before | 20 | 20 | 4.08 pp |
| 2022 | Six days before | 12 | 12 | 3.19 pp |
| 2022 | Day before | 12 | 12 | 3.19 pp |

Equal-election averages: six-day horizon **18 versus 17**; final horizon **16 versus 16**. These are genuine errors against official outcomes, unlike R001's in-sample disagreement with polls. They do not establish a robust model ranking: only two elections and a convenience panel have been evaluated.

In 2021 both methods materially underpredicted Blue and White and overpredicted New Hope; Yamina was also overpredicted. In 2022 both predicted Meretz seats when it ultimately got zero, and underpredicted Shas. This makes threshold uncertainty a sensible next research target, not evidence that a particular unimplemented fix would improve out-of-sample accuracy. Report representation false positives/negatives as positive-seat versus zero-seat diagnostics, not estimated crossing probabilities.

Neither method independently applies Bader-Ofer or guarantees electoral feasibility. Keep the original methods as references. The 2019-2021 period-group sensitivity cannot be informative with only 2021 from that period; it awaits additional elections. No random forest, pretrained model, war/turnout adjustment, or new 2026 forecast was run.

## Reproduce and extend

Python 3.12, standard library only:

```sh
python -m unittest discover -s tests -v
python scripts/backtest.py --out-dir output/backtest
```

Reference outputs are committed, with hashes of the consumed config, poll/outcome snapshots and code in `backtest.json`. The existing GitHub Actions workflow now runs all 16 tests, regenerates both the original baseline and historical report, compares each byte-for-byte with its reference, and uploads separate artifacts. Local tests passed; hosted execution status must be checked before claiming remote success.

Local validation: all 16 tests passed; the historical report reproduced byte-for-byte; links and balanced code fences passed across 17 root/docs Markdown files; the method-report draft is 286 whitespace-delimited words. New historical inputs and outputs explicitly use LF for stable hashes across Windows/Linux. The unchanged legacy baseline writer emits CRLF on Windows, so its local text comparison was equal after newline normalization; canonical byte-for-byte baseline validation remains the Linux hosted job. No original baseline file was altered to fix that unrelated behavior.

Before adding an election, collect a comparable original-source panel, preserve that election's actual list identities and official outcomes, add a prior turnout reference, and extend configuration. Keep forecast horizons fixed. If fitting new parameters, use earlier elections for each later test and keep an untouched chronological evaluation where feasible. Do not treat this evaluated pilot as an untouched holdout after tuning against its errors.
