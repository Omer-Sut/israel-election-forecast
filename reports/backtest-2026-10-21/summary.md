# Historical backtest pilot - 2021 and 2022

Unchanged rounded mean and empirical L1 consensus; 14-day effective poll-age window, equal latest audited group weights.
Both horizons use end-of-day cutoffs in Asia/Jerusalem. Lower total absolute seat error is better.

| Election | Days before voting | Cutoff | Groups | Rounded mean error | L1 error | Turnout prediction / actual | Turnout error (pp) |
| --- | ---: | --- | ---: | ---: | ---: | --- | ---: |
| knesset_24_2021 | 6 | 2021-03-17 | 3 | 24 | 22 | 71.52% / 67.44% | 4.08 |
| knesset_24_2021 | 1 | 2021-03-22 | 3 | 20 | 20 | 71.52% / 67.44% | 4.08 |
| knesset_25_2022 | 6 | 2022-10-26 | 3 | 12 | 12 | 67.44% / 70.63% | 3.19 |
| knesset_25_2022 | 1 | 2022-10-31 | 3 | 12 | 12 | 67.44% / 70.63% | 3.19 |

## Equal-election averages (keep horizons separate)

- 6 days before voting, 2 elections: rounded mean **18.0**, L1 **17.0** total absolute seat error.
- 1 day before voting, 2 elections: rounded mean **16.0**, L1 **16.0** total absolute seat error.

These are retrospective errors against official results, not in-sample poll disagreement. Two elections cannot establish a reliable model ranking; neither method is selected as final.
Each reassigned seat contributes two to the total absolute error. Turnout error is in percentage points; the same persistence forecast is evaluated at both horizons.

## Largest per-list errors

- knesset_24_2021, T-6, rounded_mean_reference: Blue and White 4 predicted / 8 actual; New Hope 10 predicted / 6 actual; Yamina 11 predicted / 7 actual.
- knesset_24_2021, T-6, empirical_l1_consensus: Blue and White 4 predicted / 8 actual; New Hope 10 predicted / 6 actual; Yamina 11 predicted / 7 actual.
- knesset_24_2021, T-1, rounded_mean_reference: Blue and White 4 predicted / 8 actual; New Hope 10 predicted / 6 actual; Joint List (Hadash, Taal, Balad) 9 predicted / 6 actual.
- knesset_24_2021, T-1, empirical_l1_consensus: Blue and White 4 predicted / 8 actual; New Hope 10 predicted / 6 actual; Yamina 10 predicted / 7 actual.
- knesset_25_2022, T-6, rounded_mean_reference: Meretz 5 predicted / 0 actual; Shas 8 predicted / 11 actual; Hadash-Taal 4 predicted / 5 actual.
- knesset_25_2022, T-6, empirical_l1_consensus: Meretz 5 predicted / 0 actual; Shas 8 predicted / 11 actual; Hadash-Taal 4 predicted / 5 actual.
- knesset_25_2022, T-1, rounded_mean_reference: Meretz 4 predicted / 0 actual; Shas 8 predicted / 11 actual; Hadash-Taal 4 predicted / 5 actual.
- knesset_25_2022, T-1, empirical_l1_consensus: Meretz 4 predicted / 0 actual; Shas 8 predicted / 11 actual; Hadash-Taal 4 predicted / 5 actual.

## Representation diagnostics

- knesset_24_2021, T-6, rounded_mean_reference: false positive lists=[]; false negative lists=[]; one/two-seat point estimates=[].
- knesset_24_2021, T-6, empirical_l1_consensus: false positive lists=[]; false negative lists=[]; one/two-seat point estimates=[].
- knesset_24_2021, T-1, rounded_mean_reference: false positive lists=[]; false negative lists=[]; one/two-seat point estimates=[].
- knesset_24_2021, T-1, empirical_l1_consensus: false positive lists=[]; false negative lists=[]; one/two-seat point estimates=[].
- knesset_25_2022, T-6, rounded_mean_reference: false positive lists=['meretz_2022']; false negative lists=[]; one/two-seat point estimates=[].
- knesset_25_2022, T-6, empirical_l1_consensus: false positive lists=['meretz_2022']; false negative lists=[]; one/two-seat point estimates=[].
- knesset_25_2022, T-1, rounded_mean_reference: false positive lists=['meretz_2022']; false negative lists=[]; one/two-seat point estimates=[].
- knesset_25_2022, T-1, empirical_l1_consensus: false positive lists=['meretz_2022']; false negative lists=[]; one/two-seat point estimates=[].

## Audited source selection

- knesset_24_2021, T-6: [Channel 13, 2021-03-14](https://13tv.co.il/item/news/politics/politics/survey-towards-elections-day-1223224/); [Israel Hayom / i24NEWS, 2021-03-11](https://www.israelhayom.co.il/article/860275); [N12, 2021-03-16](https://www.mako.co.il/news-israel-elections/2021_q1/Article-7394d5f12bb3871027.htm).
- knesset_24_2021, T-1: [Channel 13, 2021-03-19](https://13tv.co.il/item/news/politics/politics/elections-survey-1225553/); [Israel Hayom / i24NEWS, 2021-03-18](https://www.israelhayom.co.il/article/862625); [N12, 2021-03-19](https://www.mako.co.il/news-israel-elections/2021/Article-3288575c4cb4871027.htm).
- knesset_25_2022, T-6: [Channel 13, 2022-10-25](https://13tv.co.il/item/news/politics/politics/m47r5-903303576/); [Channel 14, 2022-10-24](https://www.c14.co.il/article/705525); [N12, 2022-10-24](https://www.mako.co.il/news-israel-elections/2022_q4/Article-989f30b39aa0481027.htm).
- knesset_25_2022, T-1: [Channel 13, 2022-10-28](https://13tv.co.il/item/news/politics/politics/last-survey-903306114/); [Channel 14, 2022-10-27](https://www.c14.co.il/article/707085); [N12, 2022-10-28](https://www.mako.co.il/news-israel-elections/election_2022/Article-afc48a535be1481026.htm).

## Limitations

- Two elections only; repeated horizons do not create additional independent outcomes.
- Three-group original-source convenience panel per election, not all polls; groups differ across elections.
- No model weights, window, or hyperparameters fitted or selected from these outcomes.
- Dated publisher pages and known updates checked; authenticated historical archive versions unavailable.
- Historical list identities are separate; no 2026 form mapping or pooled other bucket is used.
- All official seat-winning lists included; omitted unmodeled lists have zero official and predicted seats.
- Point estimates enforce integer total only; no independent electoral allocator or probability calibration.
- Representation mismatches are seat-positive versus zero diagnostics, not threshold probabilities.
- 2019-2021 repeated-election-period sensitivity needs more elections; this pilot has only 2021 from that period.
- Turnout repeats the preceding election, not a current survey or war-adjusted model.

Per-list predictions/errors are in `seat-errors.csv`; input/code hashes, exclusions, group selections and individual-poll errors are in `backtest.json`.
