# Forecasting methods and useful additional data

Research date: **October 21, 2026**. Primary research, authors' code, original publishers, and official data pages were inspected. This is a bounded research review, not an exhaustive literature search. All transferability judgments and priorities are project proposals. No new model/data ingestion or predictive validation was run. The [user feedback and validation agenda](research-agenda.md) preserve the requested direction.

## Electoral rules and the scored target

**Competition requirement:** the original PDF, page 1, uses the final official CEC outcome after double-envelope counting. The form requests a 120-seat allocation. We therefore interpret the target as final seats after eligibility and allocation, not pre-threshold support. This interpretation does not establish hidden form validation or the organizer's exact treatment of multiple other qualifiers.

**Official source evidence:** the Knesset's [allocation explanation](https://main.knesset.gov.il/About/Lexicon/pages/seats.aspx) and the CEC's [voter information](https://www.gov.il/en/pages/knesset25-elections-info?chapterIndex=12) have indexed official text specifying **at least 3.25% of valid votes** for participation in allocation. Invalid ballots and nonvoters do not enter that denominator. Eligible lists share all 120 seats under Bader-Ofer, with applicable surplus agreements. Votes for excluded lists are not assigned to a designated party; excluding them from the allocation denominator indirectly increases representation for qualifying lists.

Example: with 1,000,000 valid votes, the threshold is 32,500. A list receiving 30,000 has 3.0% and zero seats. Its votes are not rescued by simply pooling all failed lists into "other". Do not confuse a surplus agreement with automatic transfer of a failed list's votes.

The usual smallest observed qualifying-list projection is **four seats**; a universal four-seat hard constraint is too strong. The Knesset Research and Information Center's [comparative threshold review](https://main.knesset.gov.il/EN/activity/mmm/The%20NationalElectoralThreshold.pdf), footnote 36 in indexed text, notes that 3.25% of 120 is 3.9 and that three seats are theoretically possible. One or two are not supported by this full-list allocation framework. This concerns electoral lists, not parliamentary factions created by later splits.

**Verification limitation:** direct retrieval of those Knesset pages/PDF redirected to a geographic-access block and the CEC information page returned 403; the evidence above is official-domain indexed text, not a successful full-document or operative 2026 law review. Do not claim the complete current allocator, tie handling, or 2026 surplus agreements have been verified. An allocator remains unimplemented. The [2022 official results](https://votes25.bechirot.gov.il/nationalresults) were fully readable and show both votes and final seats: Meretz received 3.16% and zero seats; Balad 2.91% and zero; Labor 3.69% and four. These are concrete post-threshold ground-truth examples.

The frozen rounded mean can output one/two seats because it summarizes poll projections. That does not simulate an actual allocation. The PDF does not explicitly prohibit an unattainable point estimate, but any future outcome simulation should produce coherent allocations and label decision summaries separately.

## Existing forecasting work: what can we borrow?

### 1. Spain, 2015: multiparty forecasting with new entrants

Garcia Montalvo, Papaspiliopoulos, and Stumpf-Fetizon combine a hierarchical fundamentals model with poll information and update it as new evidence arrives. Their application addresses two major new parties. This makes it a useful conceptual match for changing Israeli lists. Borrow the separation of prior structure and polling evidence; do not import Spanish coefficients or district rules. [Authors' paper, abstract and metadata](https://arxiv.org/abs/1612.03073), European Journal of Political Economy (2019). The full implementation/replication package was not audited.

### 2. United States, 2020: fundamentals, polls, and correlated uncertainty

The Economist's model combines economic/political predictors with dynamic polling estimates and allows related outcomes to share uncertainty. Its public [methodology](https://projects.economist.com/us-2020-forecast/president/how-this-works) describes regularization and validation; its [authors' repository](https://github.com/TheEconomist/us-potus-model) contains R/Stan code under MIT, with separate terms for generated and third-party data. Borrow shared-error scenarios and simple regularized covariates; a full US state model is disproportionate here. It is reusable source code, not a pretrained Israeli checkpoint. Our proposed backtest must remain chronological even where other research uses leave-one-election-out validation.

### 3. United Kingdom, 2019: demographics plus population weighting

YouGov's [original model explanation](https://yougov.com/en-gb/articles/26534-faqs-about-yougovs-2019-general-election-mrp-model) describes multilevel regression and post-stratification (MRP): model preferences by demographic/political characteristics and combine group estimates using population composition. The transferable idea is differential support and turnout across groups. It requires suitable respondent data and joint population counts; headline poll totals alone are insufficient. Rebuilding constituency MRP is a stretch task under our budget. Public explanation does not establish availability or reuse rights for its respondent data or fitted model.

### 4. India, 2019: a concrete random forest election application

Cerina and Duch replace the regression learner in a post-stratification approach with random forests, using online respondent samples and population information assembled from census/auxiliary sources. Their [peer-reviewed original study](https://pmc.ncbi.nlm.nih.gov/articles/PMC8629219/) demonstrates an election use of the user's suggested model family. Borrow the approach only if compatible Israeli respondent or area-level inputs are available. Its predictive performance in that setting does not establish transportability here. A pretrained reusable election checkpoint was not verified.

### 5. A pretrained option: TabPFN, with a different role

The [2025 original paper](https://www.nature.com/articles/s41586-024-08328-6) presents a pretrained tabular foundation model for classification/regression. It is not a random forest or election-specific forecaster. It could be an optional challenger on a historical labeled table, but cannot infer Israeli party support without appropriate inputs and examples. The [maintainer repository](https://github.com/PriorLabs/TabPFN) distinguishes code and checkpoint licenses and recommends GPU use for best performance. Version, weight license, CPU feasibility, dependency cost, and historical cutoff eligibility must be pinned before adoption; none was installed or benchmarked. Do not rely on the moving default or treat all weights as unrestricted open source.

## Data beyond published headline polls

Priority is a project judgment reflecting the remaining budget. Survey microdata and attitude surveys below still involve surveying; they are additional to public seat projections, not independent proof of them.

| Data and inspected primary source | Potential role | Priority and main qualification |
| --- | --- | --- |
| [CEC national, locality and ballot results](https://votes25.bechirot.gov.il/nationalresults), [2021 national results](https://votes24.bechirot.gov.il/nationalresults) | Historical targets; prior turnout; group/geographic participation and support | High. Some national data already stored; no geographic model implemented. Harmonize geography and election-specific lists; aggregate results do not reveal individual transfers. |
| [CBS Knesset turnout history](https://www.cbs.gov.il/he/publications/DocLib/2022/ShnatonElectionsTheKnessetandGovernment.27/st27_02.pdf) | Long-run turnout, election spacing and repeat-election indicators | High for the proposed turnout check. Table published August 2, 2022 actually ends at March 2021 despite its 1949-2022 heading; append official 2022 separately. Historical turnout uses the source's eligible-electorate denominator. |
| [Israel National Election Studies](https://socsci4.tau.ac.il/mu2/ines/data/) | Turnout determinants, past vote, attitudes and demographic relationships where questionnaires support them | Medium. Design inventory includes pre/post-election waves from 1969 onward and a 2025 off-cycle survey. Access, questionnaires and reuse terms require inspection. Historical post-election answers are not pre-election inputs for that same election; files released later also cannot enter a strict historical information set. |
| [CBS 2022 census portal](https://census.cbs.gov.il/) | Age, population-group and geographic composition for weighting or locality models | Medium/stretch. Join on documented geography, use eligible-voter counts where possible, and avoid treating total residents as eligible voters. Marginals do not automatically supply joint post-stratification cells. Only the portal was identified, not a model-ready table. |
| [Bank of Israel price indices](https://www.boi.org.il/en/economic-roles/statistics/real-economic-activity/price-indices/) and [labor market](https://www.boi.org.il/en/economic-roles/statistics/real-economic-activity/labor-market-and-demography/) | Inflation, real wages and unemployment as a small set of economic covariates | Medium/low near election day. Series catalog reviewed; values not collected. Preserve original release dates/vintages so revised macro data cannot leak into backtests. Test incremental benefit over polls. |
| [UCDP downloads and codebooks](https://ucdp.uu.se/downloads/) | Prespecified conflict exposure for exploratory turnout comparisons | Medium for the user's hypothesis. Annual state-based conflict series begins in 1946; exact timing requires suitable chronology/event data. Check actors and codebook, not only geographic location. Annual releases can lag the forecast; preserve versions/publication dates. No Israeli subset or war labels have been constructed. |
| [IDI Israeli Voice report](https://www.idi.org.il/articles/66114), [Data Israel](https://dataisrael.idi.org.il) | Trust, issue priorities, security/economic assessments, potentially intention to vote if actually asked | Optional. Existing report reviewed in the earlier source inventory; database/microdata not audited. Do not translate attitudes directly into seats or assume respondent access. |
| Official finalized list registrations, withdrawals and surplus agreements; [CEC K26 entry point](https://www.gov.il/he/departments/units/elections-26) | Define feasible alternatives and allocate seats correctly | High structural importance. Current official page access remains incomplete; no 2026 agreement set verified. These constrain scenarios rather than independently measuring support. |

Additional optional signals include search interest, social-media activity, market prices and campaign spending, **if** a reproducible historical source and cutoff can be verified. This review did not establish usable Israeli coverage. Attention is not vote share, and market prices may target a coalition/prime minister rather than party seats; defer these before crowding out validation.

## Cheap ways to use the extra information

**Turnout composition:** aggregate group turnout using eligible-electorate weights: `national_turnout = sum(eligible_g * turnout_g) / sum(eligible_g)`. If vote choice among participants is also known, combine group participation and preferences to obtain party votes, then apply allocation. This explains why a national turnout number alone cannot determine which party gains. No group-rate estimates have been fitted.

**Small tree model:** define rows as election/list or election/locality with a handful of pre-cutoff features, predict vote share or the error of a poll consensus, and evaluate on entire later elections. A modest forest is computationally cheap. Its critical bottlenecks are comparable labels, few independent elections, alliance changes and geographic joins. A generic pretrained forest from another country is not a drop-in solution to these issues.

**War hypothesis:** historical turnout can be assembled separately from the more demanding party-level backtest. Predefine which conflicts and lag windows count; compare changes rather than just raw post-war turnout, allowing for trend and election spacing. Do not infer causation or set an adjustment direction from a few selected wars. See [the proposed design](research-agenda.md#proposed-war-and-turnout-check).

## Provenance, scope and next evidence

All links above were retrieved or identified on October 21, 2026; access limitations are stated in place. No full articles, respondent records, model weights, or newly collected datasets were copied into this repository. This document's source descriptions are research notes, not a machine-ready dataset. Before ingestion, follow [the source manifest conventions](data-sources.md#record-for-every-dataset), inspect rights, and preserve public-availability and transformation records.

A readable **original historical poll** was located: [Channel 13, March 19, 2021](https://13tv.co.il/item/news/politics/politics/elections-survey-1225553/). It contains a complete projected seat allocation and reported sample metadata. It is a starting source for collection, not an already balanced historical dataset or a completed backtest. Audit its graphics and release/version dates before use, as with current sources.

Recommended next work is a tiny historical poll/result dataset and a written candidate comparison, followed by one justified improvement. The research supports exploring uncertainty/allocation and forests; it does not select either as the final model.
