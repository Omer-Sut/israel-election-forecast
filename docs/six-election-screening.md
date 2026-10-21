# Six-election screening panel (E002)

Prepared October 21, 2026 after the user requested usable earlier years instead of insufficient-training cells. E001's cloud implementation was merged through PR #12 at main `507fdd8`; this extension starts from that clean state. No final model is selected or new current-election forecast produced.

## Chronological design

Use the same **T−1 cutoff for all six elections**, the existing inclusive 14-day effective-age window and three declared polling groups per election. The grid, features, 25% correction and rounding are unchanged. We chose these roles before inspecting the new model scores:

| Election | Earlier training elections | Role |
| --- | ---: | --- |
| 2015 | 0 | Initial training history |
| April 2019 | 1 | More training history; no supervised diagnostic fit |
| September 2019 | 2 | First strict out-of-fold predictions |
| 2020 | 3 | Second strict out-of-fold predictions |
| 2021 | 4 | Complete comparison, including optimized ensemble weights |
| 2022 | 5 | Complete comparison; may use 2021's earlier OOF result |

2021 and 2022 are evaluation elections for this screen, not untouched blind holdouts: both outcomes were already inspected. Six elections remain six outcomes; party/poll rows do not create independent elections. Earlier four cases stay in the JSON/CSV with role `training_and_oof_history`, including expected early unavailable fits. The readable comparison shows all 20 configurations on 2021/2022. A hard completeness gate fails the run if any requested comparison configuration cannot predict, rather than hiding missing fits. No future election trains an earlier one, and optimized weights use only earlier strict OOF predictions.

The prior E001 configuration is archived as `config/experiments-pilot.json`. Its four-case outputs and original baseline/backtest are preserved. The active `config/experiments.json` points to the new six-election panel with one horizon, turns off one-election diagnostic fitting and requires complete evaluation. This intentionally differs from E001's training on two horizons; do not attribute changed scores solely to adding elections.

## Data prepared

Added twelve reviewed releases from four earlier elections, then reused the existing twelve 2021/2022 releases unchanged: **24 releases across six election snapshots**, three groups selected per T−1 case. This is a small convenience panel from the large database, not every available release or necessarily each group's final release.

The committed `audit.json` under `data/snapshots/screening-six-elections-2026-10-21/` preserves numerical source-label transcriptions, English normalization/Hebrew definitions, URLs, retrieval date, retrieved-page SHA-256/size, publication and known revision dates, fieldwork/sample information, explicit derivations and bulk-row links when available. Publisher prose/pages/videos are not redistributed; retrieved pages remain in ignored audit cache. Raw public poll-index archives stay unchanged. The Knesset Channel 2015 official video description supplies an additional directly verified release without an assigned bulk-row link.

`scripts/prepare_screening_panel.py` deterministically builds four earlier snapshots, a six-election outcome file and historical configuration offline. It joins audited election-specific labels to official ballot codes, rejects unknown/duplicate labels, checks every complete allocation sums to 120, includes all official seat winners, and records omitted official zero-seat lists. Outcomes come from the frozen database; 2015's seats/turnout retain the documented IDI secondary-source tier. The official [2013 CEC result](https://www.gov.il/apps/elections/elections-knesset-19/eng/list/Results_eng.html) supplies the 67.77% previous-election turnout reference for 2015, not additional seat-training data. Other turnout references use completed earlier elections from our database/pilot.

Rebuild generated inputs without downloads/packages:

```sh
python scripts/prepare_screening_panel.py --out-dir output/panel-rebuild
```

The cloud workflow compares that rebuild with committed `prepared/` files before running models. Experiment provenance hashes the audit, preparation script and underlying national-result/source tables as well as consumed snapshots/configs.

## Source audit findings and limits

- **2015:** [Globes/Smith March 12](https://en.globes.co.il/en/article-herzog-opens-four-seat-gap-1001018362), [Ynet/Midgam March 13](https://www.ynetnews.com/articles/0,7340,L-4636623,00.html), [official Knesset Channel/Panels March 3](https://www.youtube.com/watch?v=d0qYlsOyNR0). The last reports March 2 fieldwork, exactly the T−1 window's inclusive lower boundary. It is older than other selected polls. Ynet prose gives Meretz/Yisrael Beiteinu a tie without the numeral: the other 110 seats imply five each, matching the archived index. These are explicitly marked derived values, not silently fabricated transcriptions.
- **April 2019:** [Jerusalem Post/Smith](https://www.jpost.com/israel-news/post-poll-predicts-easy-win-for-right-585821), [Ynet/Midgam](https://www.ynet.co.il/articles/0,7340,L-5489848,00.html), [Channel 13's own contemporaneous companion article](https://13tv.co.il/item/news/opinions/goverment_coalition/). Primary dates are April 5 for all three; the first two index proxies say April 4. Channel 13 was modified April 6, still before cutoff April 8; its original linked poll page now returns a 404 shell, so use its own companion's complete repeated allocation. Keep distinct Hadash–Taal and Raam–Balad lists; do not apply a current Joint List alias. Jerusalem Post's Smith poll differs from Maariv's Smith poll; only the former is selected, not both as independent groups.
- **September 2019:** [Walla/Midgam September 9](https://elections.walla.co.il/item/3311677), [Channel 13/Fuchs September 10](https://13tv.co.il/item/news/politics/state-policy/reelection-2019/survey-election-355016/), [Maariv/Smith September 13](https://www.maariv.co.il/elections2019/polls/article-718968). Maariv's index proxy is September 12 (fieldwork), not publication. The Channel 13 migrated NewsArticle dateline mentions 2020 while visible date/captions/video upload support September 10, 2019; preserve this conflict as a vintage limitation, not a proven numeric revision.
- **2020:** [103FM/Panels February 26](https://103fm.maariv.co.il/programs/media.aspx?ZrqvnVq=HLJMFI&c41t4nzVQ=GJL), [Walla/Midgam February 26](https://elections.walla.co.il/item/3343018), [Channel 13/Fuchs February 28](https://13tv.co.il/item/news/politics/state-policy/2020-elections/2020-election-survey-1016506/). Both February 26 pages appear in the index under February 25. The 103FM page explicitly distinguishes February 26 publication from February 25 fieldwork. Walla instead prints February 16–17 fieldwork and sample 502 despite contextual/date-proxy indications of a newer poll. Preserve its printed metadata rather than guessing; February 17 still qualifies at T−1, but recency-weight sensitivity is needed. Channel 13's migrated dateline mentions 2025 while original visible/video dates support February 2020; no archive-vintage proof is claimed.

These are original-source checks, not authenticated contemporary archives. Unknown fieldwork stays unknown; source publication is then the explicit age fallback. Sample-size weighting is not used. No source is excluded based on whether its poll or model score matches the final result. A nearby Direct Polls release was not selected because its prose totals only 119 seats and disagrees with the index; it is not repaired from election results.

## Running and next steps

Use **Screen lightweight forecast models** on GitHub Actions; optional local command remains `python scripts/experiments.py` in the pinned scientific environment. No new dependency or local model training is required. Cloud results and compact durable reports will be recorded in project-state/experiment-log after verification.

Inspect stability before narrowing candidates. The first source sensitivity should replace Walla 2020's uncertain fieldwork age with publication-age fallback, then compare outputs; also examine older 2015 coverage and repeated-election-period effects. Better campaign coverage is useful later, but additional families/heavier training are not the present bottleneck. T−6 coverage is retained in the old pilot, not claimed complete across the newly prepared years.
