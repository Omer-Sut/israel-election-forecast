# Data sources and provenance

Initial web review and first data collection: **October 21, 2026**. The first [audited input snapshot](../data/README.md) now stores six poll records, five active groups, and a partial official 2022 outcome table. The sections below preserve the broader source inventory and its limitations; not every reviewed source has been ingested.

## Sources supplied in the competition guidelines

### S1. Wikipedia poll compilation

[2026 opinion polling](https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Israeli_legislative_election) contains dated poll tables, polling organizations/publishers, sample sizes where reported, seat projections, some below-threshold percentages, and references. Lineups vary; a separate section reports vote-intention percentages.

Use as a discovery index and a starting transcription, then reconcile important values against original releases. Do not count a syndicated poll twice or treat mixed seat/percentage cells as one numeric unit. Keep publication and fieldwork dates distinct. Party names and hypothetical lineups need mapping before aggregation. This is not the authoritative submission list.

### S2. Israel Democracy Institute: threshold and wasted votes

[Threshold and wasted votes](https://www.idi.org.il/articles/66233), dated September 14, 2026, discusses threshold history and votes cast for lists that fail to enter parliament. It identifies the current threshold as 3.25%.

Use to understand why small-party uncertainty changes the seat allocation of other parties and to motivate pass/fail sensitivity scenarios. It is explanatory analysis, not a current voting-intention dataset or a complete allocation implementation. Confirm operative rules with official sources before coding them.

### S3. Israel Democracy Institute: Israeli Voice Index

[August 2026 index report](https://www.idi.org.il/articles/66114), published September 8, concerns public attitudes, election-related concerns, and voting considerations. Its methodology reports 755 adult respondents, Hebrew/Arabic interviewing, and fieldwork spanning August 31-September 3. It links to [Data Israel](https://dataisrael.idi.org.il) for fuller data; that database has not been inspected.

Use as context or a source of a precisely relevant variable only after checking the questionnaire. This linked report is not a full party-vote-share or turnout forecast. Issue preferences, confidence, and perceived election integrity cannot be directly converted into seat changes. Access and reuse conditions for underlying respondent data remain unreviewed.

### S4. Official Knesset 26 election information

The PDF's [CEC unit page](https://www.gov.il/he/departments/units/elections-26) returned HTTP 403 in this review. The [official candidate-list link](https://www.gov.il/en/pages/candidates-lists-26), discovered through S1, returned no readable content. The form may include a particular subset or naming scheme, so official lists do not replace inspecting it.

Use official pages for definitive list identifiers, candidate-list status, agreements, and election information when accessible. **Current list mapping and surplus agreements are not verified yet.** The [Interior Ministry election-date page](https://www.gov.il/he/pages/knesset-elections-2026?chapterIndex=3) has an indexed title matching October 27, 2026, but direct retrieval also returned 403. Treat that as partial corroboration, not a complete live verification.

### S5. Kolot Nodedim (Wandering Votes)

[The interactive site](https://kolot-nodedim.netlify.app) explores Israeli election data. Its [source repository](https://github.com/harelc/elections-vote-transfer) describes historical ballot data, vote-transfer analysis, and preprocessing. It explicitly labels its K26 feature as a **simulated scenario**, not observed results.

Use historical data/code as a convenience after checking provenance against official totals. Transfers inferred from aggregate ballots are estimates, not observed individual voter movements. Never use generated K26 ballots as real evidence or validation targets. Geographic harmonization and transfer modeling are deferred under the eight-hour budget. The site's footer displays CC BY-NC-SA 4.0; inspect the relevant code/data licensing before copying, and preserve attribution.

## Additional sources inspected

### S6. Official historical results (highest priority)

- [2022 / Knesset 25 national results](https://votes25.bechirot.gov.il/nationalresults): final official party votes, vote shares, seats, electorate, valid/invalid ballots, and turnout (70.63%); links to locality/ballot views. This is ground truth for a historical evaluation, not a 2026 forecast.
- [2021 / Knesset 24 national results](https://votes24.bechirot.gov.il/nationalresults): another accessible official results page, including national results and geographic-view links.
- [CEC historical archive](https://www.gov.il/he/pages/election-committee-history?chapterindex=7): discovered as an official index; direct retrieval yielded no readable content. Older election datasets remain to be checked.

Use recent national outcomes first to evaluate same-election pre-election poll errors and establish a turnout reference. Only a few independent elections are available; hundreds of polls or thousands of ballot boxes do not create hundreds of independent national election outcomes.

### S7. Original current poll publications (spot checks)

- [Channel 13 release linked by S1](https://13tv.co.il/item/news/politics/politics/jw3wm-905406894/): page includes seat estimates, polling organizations, sample size (1,016), and notes about the lineup/timing. The article text reports Likud at 17 while the corresponding October 19 row in S1 showed 18 during review. **Unresolved source discrepancy: flag before ingestion; do not silently select a value.** Images/corrections may need inspection.
- [Channel 14 release](https://www.c14.co.il/article/1745051): reports seats, explicit support percentages for some below-threshold lists, fieldwork date (October 19, 2026), polling organization, and sample size (454).

These demonstrate available measurements and the need to audit sources. Both are now ingested in the first snapshot: Channel 13 uses the original graphic's Likud=18 and UTJ=7 after visual inspection, preserving the body-text conflict; Channel 14 uses its complete publisher seat list. Sample size alone is not a complete quality measure or a justified weight. PM-preference questions are separate from list voting intention.

### S8. Official allocation references (access incomplete)

[Knesset Bader-Ofer explanation](https://m.knesset.gov.il/en/about/lexicon/pages/seats.aspx) and [Hebrew version](https://main.knesset.gov.il/About/Lexicon/pages/seats.aspx) appeared in official-domain search results with 120-seat allocation, a 3.25% valid-vote threshold, and surplus agreements, but redirected to a geographic-access restriction. An [official CEC English booklet for Knesset 25](https://www.gov.il/BlobFolder/guide/knesset25-elections-info/he/info-pages_english.pdf) also appeared in search, but direct fetching returned 403.

Use them to locate the official rule specification; detailed mechanics, tie handling, current agreements, and rule currency remain verification tasks. Do not describe the full allocator as verified based solely on a search excerpt.

## Collection priority and exclusions

The user has now supplied the form inventory: see [submission-contract.md](submission-contract.md) and [ordered output configuration](../config/submission-fields.json). Treat this as source S9 (user transcription, October 21, 2026), not direct authenticated inspection. Personal/account details and dummy inputs are excluded. Check Joint List versus Hadash-Ta'al and other changing lineup labels before mapping poll rows to form fields. Keep individual other lists internally; the form's combined other-qualifiers field is a seat output, not a pool of votes to threshold together.

1. Audit several original current polls against the now-known form inventory and verify official-list mappings.
2. Collect small national result tables for 2022/2021 and matching historical pre-election polls at comparable cutoffs. Historical poll availability and completeness have not yet been audited.
3. Collect below-threshold shares and missing metadata from original releases where possible.
4. Only then consider additional attitude/demographic data or transfer estimates. No paid source or person-specific data is needed for the proposed baseline.

Published seat estimates and vote percentages require separate fields. Missing values remain missing. Store actual source-specific denominators and population definitions, not guessed conversions. Preserve uncertainty when the source cannot resolve it.

## Record for every dataset

- Publisher, original URL, retrieval timestamp/timezone, and license or usage restrictions.
- Historical election identifier or pollster, commissioning body, fieldwork dates, publication date, sample size, population, and collection mode where available.
- Stable party/list identifiers, original names, alliances/splits, and documented mapping decisions.
- Units (votes, vote share, seats, or percent turnout), schema, missing values, and any below-threshold/other-party treatment.
- Immutable raw snapshot location and checksum; transformation code and resulting version.
- Earliest public availability and forecast cutoff eligibility, so backtests cannot use future information.
- Reproduction/access instructions for data not stored in Git.

## S10. Joint List composition check (October 21, 2026)

The [alliance's own website](https://jointlist.org.il/en/) names Hadash, Ta'al, and Balad as its constituents. [N12, August 19, 2026](https://www.mako.co.il/news-israel-elections/2026/Article-cb92eb7e0f910a1026.htm), reports their agreement to run jointly without Ra'am. [Official 2022 results](https://votes25.bechirot.gov.il/nationalresults) list Hadash-Ta'al and Balad separately. These sources support a changed alliance composition, not unconditional equivalence of labels over time. After the user accepted proceeding, the current poll-to-form mapping is encoded explicitly in `config/poll-mappings.json`. Historical identities remain separate; organizer intent is still an interpretation.

## Online storage policy

GitHub is the durable source of truth. Prefer small redistributable input snapshots and a source manifest in a tracked path such as `data/snapshots/` (the existing `data/raw/` and `data/processed/` paths are ignored). Review rights before copying data; do not accidentally force-add a restricted source. For larger or restricted inputs, record a shared store, access procedure, version/hash, and a reproducible retrieval path. Nothing required to reproduce the final run should exist only on one laptop or a temporary Colab disk.
