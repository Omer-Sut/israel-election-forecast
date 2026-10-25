# E019: what the extended data now adds

The user asked to extend/improve the threshold data after E018. This collection adds eight complete original-publisher poll releases and percentages to two existing releases, as a separate overlay. Frozen inputs/database and adopted forecasts remain unchanged. No model was fitted.

Implementation7fcfdb599d32472948bac1d3f79457dec8dc5757 / PR31, stacked on PR30. Hosted40192307814 passed five data-boundary tests and byte-identical repeats. Source discovery/review was bounded; cumulative user hands-on effort remains unmeasured, with no new budget invented. Final report-commit checks are recorded on PR31.

## Concrete extension

| Measure | Original | Extended |
|---|---:|---:|
| Audited releases |24|32|
| Exact reported party percentages |20|37|
| Campaigns containing exact percentages |2|5|
| Percentage observations for eventual winners |0|7|

The most important improvement is the last row. The original stored exact-percentage subset contained only eventual failures. It could not by itself teach a model that a list reported below the threshold might eventually qualify. New data include both directions:

- [PanelsPolitics/Mako, April1,2019](https://www.mako.co.il/tv-morning-news/articles/Article-caa965cb707d961006.htm): Raam–Balad2.1% ultimately won seats; Gesher2.2% did not. This is also a fourth reviewed firm in that campaign, rather than treating the Mako brand as Midgam.
- [Midgam/N12, March2,2021](https://www.mako.co.il/news-israel-elections/2021-election_polls/Article-0ef19cf03d3f771027.htm): Raam2.8%, Meretz2.5% and NewEconomic1.8%; the first two eventually qualified, the last did not.
- [Midgam/N12, March10,2021](https://www.mako.co.il/news-israel-elections/2021-election_polls/Article-40e76c2962d1871026.htm): Raam3.1% still reported outside parliament, thirteen elapsed days before election; it eventually qualified.
- Original Walla and N12 releases add Otzma2019Sep/2020 observations that ultimately failed. Existing2022below-threshold evidence is retained unchanged.

These are not seven independent successful threshold tests: they concern only three election/list outcomes in two campaigns. Overall37exact observations cover12unique election/list outcomes across five campaigns; campaigns, firms, parties and repeated releases remain dependent. New2021coverage is concentrated in Midgam.2015numeric-share coverage remains missing in the inspected originals.

## Data quality improved alongside quantity

Publication and fieldwork dates are separate, with horizon bands1–7,8–14,15–28 and the original T−1 effective-age gate exported independently. N12March7was fieldedMarch4; the release cannot be backdated. Known revisions are retained. Original-source metadata supplies sample/invited counts, collection method and undecided context where reported.

Two Walla2020articles print identicalFeb16–17fieldwork,N502/invited3486 despite different publication dates/results. Both factual publication records are preserved with unresolved wave-linkage warnings; neither is certified an independent sample. Percentages describing a previous wave are not copied as another release. Secondary rounded/conflicting tables and unavailable original graphics remain excluded.

Reported-share denominators and allocation of undecided voters remain unknown. The13.7%undecided in PanelsApril2019 and approximately40%in the finalYnet report are retained as context, not used to renormalize percentages. **None of the37observations is certified on a common valid-vote denominator.** They can support a later exploratory reported-share model with source/horizon/missingness controls; they do not identify a complete vote-to-seat allocation. Positive projected seats are not converted into measured shares or numerical percentage bounds.

One Maan2021.8%observation is retained separately pending official identity/lineup mapping and receives no invented outcome label. Primary PDF/graphic access failures, secondary contradictions and missing-percentage checks are durable in the source audit. Raw publisher page bytes were unavailable through the reader; no raw-response hashes are invented. Numerical transcriptions/code/inputs are hashed, and publisher prose/images are not redistributed.

## Usable outputs and next model test

The report contains complete release JSON, an observation CSV with evaluation labels, a separate pre-election predictor whitelist, coverage JSON/figure, unmapped evidence and input hashes. The exporter validates identity, dates, complete120-seat tables, conflicting enrichments, duplicate URLs/IDs, missingness and source preservation.

The next model test should compare the seat-only representation learner with a reported-percentage-plus-missingness version on matched chronological campaigns/sources/horizons, preserving equal campaign/firm mass. Do not fit only the newly successful cases, silently treat blank percentages as zero, count repeated waves as independent outcomes or claim a new untouched holdout. Firm-count shift to the current seven-firm panel and sparse successful outcomes remain unresolved.

Adopted Reservists3/Amcha0 and turnout69.86%remain the working reference. No model/weight/source promotion, merging or competition submission. User-directed research remains open. Local Git metadata is stale; PR31 final verification and live topic SHA are authoritative.
