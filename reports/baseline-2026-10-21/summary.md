# Preliminary baseline - not submission ready

As-of date: 2026-10-21. Latest audited release per group; 5 selected groups.

| Form field | Rounded-mean reference | Empirical L1 consensus |
| --- | ---: | ---: |
| Likud | 22 | 20 |
| Yashar! (Eisenkot) | 23 | 23 |
| Beyachad / Together (Bennett) | 13 | 14 |
| The Democrats | 9 | 9 |
| Yisrael Beiteinu | 8 | 8 |
| Shas | 8 | 8 |
| United Torah Judaism | 7 | 7 |
| Otzma Yehudit | 7 | 7 |
| Religious Zionism | 7 | 7 |
| Ra'am | 5 | 5 |
| Hadash-Ta'al | 8 | 8 |
| Blue and White | 0 | 0 |
| Amcha Yisrael | 1 | 0 |
| Reservists-Economic | 2 | 4 |
| Other parties passing the electoral threshold (combined seats) | 0 | 0 |
| **Total** | **120** | **120** |

Turnout persistence baseline: **70.63%**, within the configured form bounds.

Empirical L1 minimizes disagreement with these polls, not validated error against the future election. Neither column is a final submission recommendation.

## Sources

- 2026-10-19 [Channel 13](https://13tv.co.il/item/news/politics/politics/jw3wm-905406894/) (c13_consortium)
- 2026-10-20 [Walla](https://www.walla.co.il/news/politics/383958175) (lazar_panel4all)
- 2026-10-19 [N12](https://www.mako.co.il/news-israel-elections/2026/Article-a6eb664b9d451a1026.htm) (midgam_rc)
- 2026-10-19 [Channel 14](https://www.c14.co.il/article/1745051) (next_data)
- 2026-10-15 [Zman Yisrael / Times of Israel](https://www.timesofisrael.com/toi-poll-eisenkot-opens-up-big-lead-on-netanyahu-but-both-blocs-short-of-majority/) (tatika_adgenda)

## Limitations

- Audited convenience sample, not all latest polls; additional October 20 releases remain unaudited.
- No historical poll-to-election backtest or probability calibration has run.
- Poll disagreement is not forecast accuracy or an election-outcome probability.
- Only form arithmetic is enforced; a vote-to-seat allocator and full electoral feasibility are not implemented.
- Current alliance-to-form mappings are explicit assumptions and do not merge historical electorates.
- Unreported seat zeros follow a verified complete 120-seat table, not missing percentage imputation.
- Turnout is a historical persistence baseline; current self-reported intention is diagnostic only.
- No adjustment for support redistribution after Blue and White's reported withdrawal.

Detailed input/code hashes, method diagnostics, and leave-one-group-out results are in `baseline.json`.
