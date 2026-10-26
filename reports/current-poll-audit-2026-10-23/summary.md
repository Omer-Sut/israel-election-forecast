# Preliminary baseline - not submission ready

As-of date: 2026-10-23. Latest audited release per group; 5 selected groups.

| Form field | Rounded-mean reference | Empirical L1 consensus |
| --- | ---: | ---: |
| Likud | 22 | 19 |
| Yashar! (Eisenkot) | 22 | 22 |
| Beyachad / Together (Bennett) | 13 | 14 |
| The Democrats | 9 | 9 |
| Yisrael Beiteinu | 8 | 8 |
| Shas | 8 | 8 |
| United Torah Judaism | 8 | 8 |
| Otzma Yehudit | 8 | 8 |
| Religious Zionism | 6 | 6 |
| Ra'am | 5 | 6 |
| Hadash-Ta'al | 8 | 9 |
| Blue and White | 0 | 0 |
| Amcha Yisrael | 1 | 0 |
| Reservists-Economic | 2 | 3 |
| Other parties passing the electoral threshold (combined seats) | 0 | 0 |
| **Total** | **120** | **120** |

Turnout persistence baseline: **70.63%**, within the configured form bounds.

Empirical L1 minimizes disagreement with these polls, not validated error against the future election. Neither column is a final submission recommendation.

## Sources

- 2026-10-21 [Channel 13](https://13tv.co.il/item/news/politics/politics/ksgoq-905411865/) (c13_consortium)
- 2026-10-20 [Walla](https://www.walla.co.il/news/politics/383958175) (lazar_panel4all)
- 2026-10-21 [N12](https://www.mako.co.il/news-israel-elections/2026/Article-bf175ad340f51a1027.htm) (midgam_rc)
- 2026-10-22 [Channel 14](https://www.c14.co.il/article/1750553) (next_data)
- 2026-10-22 [Zman Yisrael](https://www.zman.co.il/735649/) (tatika_adgenda)

## Limitations

- Bounded original-source update, not all final Friday polls. New Maariv release remains unaudited; Lazar anchor is October 20 Walla.
- Four newer releases are current article versions reviewed October 23; conservative update dates prevent claiming earlier historical availability.
- Equal-group weights retained; sample sizes do not establish independence or remove systematic bias.
- Previously inspected historical backtests are limited retrospective evidence; current consensus disagreement is not future accuracy.
- Published partial vote percentages cannot supply a full vote-share allocation or calibrated threshold-crossing probability.
- Arithmetic averages/consensus can give small positive seats to borderline lists; no official electoral feasibility allocator implemented.
- Official current eligibility, withdrawal notice and operative publication restriction remain unverified; indexed official threshold text supports 3.25%.
- Joint List/form mapping is the existing user-accepted slot assumption, not organizer verification or historical identity equivalence.
- No learned correction, poll-quality weighting, withdrawal redistribution or turnout-intention adjustment adopted. Turnout remains 70.63% persistence.

Detailed input/code hashes, method diagnostics, and leave-one-group-out results are in `baseline.json`.
