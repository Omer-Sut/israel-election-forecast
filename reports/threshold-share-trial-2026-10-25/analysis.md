# E020: matched reported-percentage ablation

Research only; no adopted forecast, source promotion, merge or submission

Primary: T−1/latest, fixed alpha0.1. Missingness-only isolates selective coverage; other panels/penalties are sensitivity diagnostics, not a new grid-selected winner.

## t1_latest

| Method | Matched folds | Mean seat L1 | Equal-period L1 | Brier | FP/FN |
|---|---:|---:|---:|---:|---:|
|square_0or3|4|13.0000|12.6667|—|2/0|
|absolute_0or3|4|13.5000|13.0000|—|2/0|
|seat_a0.1|4|13.5000|13.0000|0.0722|2/0|
|missing_a0.1|4|13.5000|13.0000|0.0691|2/0|
|share_a0.1|4|15.0000|14.0000|0.3204|3/0|
|share_a0.01|4|15.0000|14.0000|0.3310|2/1|
|share_a1|4|15.0000|14.0000|0.2755|3/0|

Earlier-OOF-only selector: [{'election': 'knesset_20_2015', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 22}, {'election': 'knesset_21_2019apr', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 38}, {'election': 'knesset_22_2019sep', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 12}, {'election': 'knesset_23_2020', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': ['2019-09-17'], 'seat_l1': 8}, {'election': 'knesset_24_2021', 'id': 'square_0or3', 'status': 'earlier_campaign_selection', 'validation_dates': ['2019-09-17', '2020-03-02'], 'seat_l1': 20}, {'election': 'knesset_25_2022', 'id': 'square_0or3', 'status': 'earlier_campaign_selection', 'validation_dates': ['2019-09-17', '2020-03-02', '2021-03-23'], 'seat_l1': 12}]

## t1_eligible_history

| Method | Matched folds | Mean seat L1 | Equal-period L1 | Brier | FP/FN |
|---|---:|---:|---:|---:|---:|
|square_0or3|4|13.0000|12.6667|—|2/0|
|absolute_0or3|4|13.5000|13.0000|—|2/0|
|seat_a0.1|4|13.5000|13.0000|0.0722|2/0|
|missing_a0.1|4|13.5000|13.0000|0.0680|2/0|
|share_a0.1|4|13.5000|13.0000|0.0735|1/1|
|share_a0.01|4|13.5000|13.0000|0.0823|1/1|
|share_a1|4|12.5000|12.3333|0.0970|1/0|

Earlier-OOF-only selector: [{'election': 'knesset_20_2015', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 22}, {'election': 'knesset_21_2019apr', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 38}, {'election': 'knesset_22_2019sep', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 12}, {'election': 'knesset_23_2020', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': ['2019-09-17'], 'seat_l1': 8}, {'election': 'knesset_24_2021', 'id': 'share_a0.01', 'status': 'earlier_campaign_selection', 'validation_dates': ['2019-09-17', '2020-03-02'], 'seat_l1': 24}, {'election': 'knesset_25_2022', 'id': 'share_a1', 'status': 'earlier_campaign_selection', 'validation_dates': ['2019-09-17', '2020-03-02', '2021-03-23'], 'seat_l1': 12}]

## t8_latest

| Method | Matched folds | Mean seat L1 | Equal-period L1 | Brier | FP/FN |
|---|---:|---:|---:|---:|---:|
|square_0or3|4|17.0000|16.0000|—|2/1|
|absolute_0or3|4|17.0000|16.0000|—|2/1|
|seat_a0.1|4|16.5000|15.6667|0.1345|2/0|
|missing_a0.1|4|16.5000|15.6667|0.1387|2/0|
|share_a0.1|4|16.5000|15.6667|0.3349|2/0|
|share_a0.01|4|16.5000|15.6667|0.3263|2/0|
|share_a1|4|16.5000|15.6667|0.3629|2/0|

Earlier-OOF-only selector: [{'election': 'knesset_20_2015', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 24}, {'election': 'knesset_21_2019apr', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 38}, {'election': 'knesset_22_2019sep', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 14}, {'election': 'knesset_23_2020', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': ['2019-09-17'], 'seat_l1': 12}, {'election': 'knesset_24_2021', 'id': 'absolute_0or3', 'status': 'earlier_campaign_selection', 'validation_dates': ['2019-09-17', '2020-03-02'], 'seat_l1': 28}, {'election': 'knesset_25_2022', 'id': 'missing_a0.1', 'status': 'earlier_campaign_selection', 'validation_dates': ['2019-09-17', '2020-03-02', '2021-03-23'], 'seat_l1': 14}]

## t8_eligible_history

| Method | Matched folds | Mean seat L1 | Equal-period L1 | Brier | FP/FN |
|---|---:|---:|---:|---:|---:|
|square_0or3|4|17.0000|16.0000|—|2/1|
|absolute_0or3|4|17.0000|16.0000|—|2/1|
|seat_a0.1|4|16.5000|15.6667|0.1345|2/0|
|missing_a0.1|4|16.5000|15.6667|0.1223|2/0|
|share_a0.1|4|18.5000|17.0000|0.1951|2/2|
|share_a0.01|4|18.5000|17.0000|0.2787|2/2|
|share_a1|4|16.5000|15.6667|0.1875|2/0|

Earlier-OOF-only selector: [{'election': 'knesset_20_2015', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 24}, {'election': 'knesset_21_2019apr', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 38}, {'election': 'knesset_22_2019sep', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': [], 'seat_l1': 14}, {'election': 'knesset_23_2020', 'id': 'square_0or3', 'status': 'warmup_control', 'validation_dates': ['2019-09-17'], 'seat_l1': 12}, {'election': 'knesset_24_2021', 'id': 'absolute_0or3', 'status': 'earlier_campaign_selection', 'validation_dates': ['2019-09-17', '2020-03-02'], 'seat_l1': 28}, {'election': 'knesset_25_2022', 'id': 'missing_a0.1', 'status': 'earlier_campaign_selection', 'validation_dates': ['2019-09-17', '2020-03-02', '2021-03-23'], 'seat_l1': 14}]

## Current diagnostic (T−3, latest sources only)

| Method | Reservists seats / p | Amcha seats / p |
|---|---:|---:|
|seat_a0.1|4 / 0.4445|0 / 0.3279|
|missing_a0.1|0 / 0.2047|0 / 0.1436|
|share_a0.1|0 / 0.2594|0 / 0.1799|
|share_a0.01|0 / 0.3963|0 / 0.1891|
|share_a1|0 / 0.4115|0 / 0.3738|

![Matched campaign errors](matched-errors.svg)

![Training support and extrapolation](support-diagnostics.svg)

## Limits

- Repeated campaigns/firm/list outcomes are dependent; no untouched holdout or calibrated crossing probabilities.
- Reported percentages have unknown denominator/undecided treatment, not valid-vote shares.
- Percentage reporting is selective. Candidate roster includes all-zero lists with any observed share in the chosen mode, identically in all arms.
- For all-zero candidates, conditional representation is assigned four seats as an explicit assumption, not inferred votes.
- Latest-firm seat projections are identical across arms; eligible-history shares are a separately labelled source-age sensitivity, never backfilled latest values.
- History averages within firm then across observed firms; coverage averages within every eligible firm. No independent-sample weight for repeated releases.
- T-8 may have one firm and different campaign coverage; compare arms only within a panel, not panel averages as model gains.
- Current percentages are only the audited seven latest releases; its October24 cutoff is T-3, not historical T-1.
- Current/history firm count and reporting patterns differ. Combined other is fixed at zero; no new unmapped list is predicted.
- Sum120 and zero-or-at-least3 are seat-space decision assumptions, not a complete Bader–Ofer simulation.
