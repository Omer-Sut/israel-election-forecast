# Why was 2021 harder? A broader final-poll comparison

The gap survives broader coverage, but our original pollster selection exaggerated it. This is an availability-limited, retrospective diagnostic of two already-inspected elections, not proof of a general election effect or of its cause.

![Coverage and party-level errors](comparison.svg)

## What changed

The old reference uses three final polling groups in each year, with different group composition. We reviewed missing final releases and added three per year to a separate diagnostic snapshot. Both expanded panels contain the same six firms: Midgam, Camil Fuchs, Maagar Mohot, Direct Polls, Kantar and Panels Politics. Each firm receives one equal vote. The original snapshots, trained models, weights and current forecast remain unchanged.

Access limits matter: only the added Maagar2022 release was fully verified at its original publisher. Panels2022 is an attributed Arik Bender republication of Maariv's poll. The other four additions are complete, dated secondary news reports, explicitly labeled and excluded from original-publisher-only comparisons. No bulk index row was promoted to an audited training input. Source selection was based on final-week coverage and source completeness, not measured error.

## Results

| Comparison | Continuous absolute error: 2021 / 2022 | Integer absolute error: 2021 / 2022 |
| --- | ---: | ---: |
| Original three firms (different sets) | 20.67 / 12.67 | 20 / 12 |
| Same six firms, including secondary reports | 19.33 / 13.00 | 20 / 14 |
| Same three firms, original publishers only | 20.67 / 16.67 | 20 / 18 |
| Same five firms, excluding Direct in both years | 20.40 / 15.20 | 20 / 14 |

The common original-publisher set is Midgam, Fuchs and Maagar. Holding that set fixed cuts the continuous gap from8 to4. This is a composition sensitivity, not an estimated causal decomposition. Adding all six reduces the gap to6.33. The original2022 average benefited from its particular mix of firms and cancellation of their signed errors; adding more sources does not guarantee lower error.

Leaving each firm out in turn gives continuous errors18.4–20.4 for2021 and12.0–15.2 for2022. Every five-firm deletion still leaves2021 worse, even comparing the best2021 deletion with the worst2022 deletion. These are sensitivity ranges, not confidence intervals or permission to choose the best deletion retrospectively.

The average individual-poll error in the expanded panels is20 for2021 versus15 for2022; descriptive population variances are12 and6.33 seat-error-squared. The average-vector errors are smaller,19.33 and13, because errors sometimes cancel. Neither quantity is an uncertainty calibration or an independent sample of national elections.

## What remains wrong at party level

Across all six2021 final reports, Blue and White is underestimated (4–7 versus8), while New Hope (7–10 versus6), Joint List (7–10 versus6), and Yamina (8–10 versus7) are overestimated. Labor, Meretz and the Religious Zionism alliance are also underestimated in every report. A nonnegative weighted average cannot reach an outcome lying outside every included poll's range. Pollster weighting alone therefore cannot fully repair these common misses.

The six-firm means are Blue and White4.67, New Hope8.83, Joint List8.17 and Yamina9.33. In2022, the main common misses are Meretz4.5 versus0 and Shas8.5 versus11. Rounding is secondary: the continuous gap persists. Arithmetic totals of120 still do not establish electoral feasibility of every average allocation.

## Provenance and limitations

- [Panels2021, INN](https://www.inn.co.il/news/471452): March19 complete secondary allocation; original Maariv inaccessible.
- [Kantar2021, ICE](https://www.ice.co.il/hotnews/news/article/814601): March18 complete secondary allocation; original Kan migrated page has no readable text.
- [Direct2021, INN](https://www.israelnationalnews.com/news/298828): March19, fieldwork March17–18, reported N6436. Srugim describes trend analysis, so its status as a raw poll versus adjusted projection is unresolved; the exclusion comparison is mandatory.
- [Maagar2022, Israel Hayom](https://www.israelhayom.co.il/news/politics/article/13226572): October27, mixed internet/telephone, reported N1201 (not the aggregator's1200), fieldwork bounds October23–26.
- [Panels2022, Walla republication](https://elections.walla.co.il/item/3537369): October28; fieldwork October26–27; exact sample size unavailable in retrieved text.
- [Kantar2022, Kol Rega](https://www.kore.co.il/viewArticle/116752): October27, complete secondary allocation; also repeated by Walla October28. More than1200 respondents reported; exact N left missing.

All added releases are four or five publication-days before election day, with unchanged T−1 cutoff and14-day eligibility. Historical list IDs and Hebrew labels are preserved. Presently retrieved historical pages are not authenticated as-of archives. Same firm names do not prove identical methodology across years. Source tiers are not numerical quality ratings.

Smith remains excluded in both years. The accessible2021 primary article has only a partial numerical allocation and an inaccessible graphic; its March19 update is explicitly acknowledged. The final2022 publisher social source was not retrieved. Thus this is not a census of all final polls. Full source and exclusion records are in the [audit](../../data/snapshots/final-poll-coverage-2026-10-24/audit.json).

## Decision and reproduction

The evidence supports a narrower answer: **2021 is harder in these comparisons, partly because of source selection and partly because broader reports share larger party misses.** It does not identify how much came from late movement, turnout assumptions or shared polling bias. Do not fit a2021-specific correction from these outcomes or rank pollsters using two elections.

Run `node --test tests/test_final_poll_coverage.mjs` and `node scripts/final_poll_coverage.mjs`. Five contract tests cover dates/revisions, repeated firms, identities, rational rounding and the difference between poll error and average-vector error. The script checks both original vectors against the saved E008 reference. Hosted workflow compares results, plot, summary and input hashes to committed reports and to a second run. See the PR checks for execution evidence; preparation alone is not a hosted pass.
