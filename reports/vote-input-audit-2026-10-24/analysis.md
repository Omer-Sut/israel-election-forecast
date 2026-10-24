# E012: current vote-input audit

Reviewed October24,2026. Seven selected final releases were checked for the full individual-list vote inputs needed by Bader–Ofer. **No complete matching vote vector was recovered through the inspected routes.** This is an access/coverage finding, not proof that no such report exists. Existing polls, models and forecast numbers are unchanged.

| Selected release | Amcha reported support | Reservists reported support | Complete vote table recovered |
| --- | ---: | ---: | --- |
| [Channel13 / HaMadad consortium](https://13tv.co.il/item/news/politics/politics/survey-905415900/) | 3.1% | 3.0% | No |
| [i24NEWS / Direct Polls](https://www.i24news.tv/he/news/israel-elections-2026/polls/artc-07d162ea) | Not recovered; 4 seats | 2.2% | No |
| [Israel Hayom / Kantar](https://www.israelhayom.co.il/news/politics/article/21687549) | 2.7% | Not recovered; 4 seats | No |
| [Maariv via Walla](https://www.walla.co.il/news/israel/383958572) | 3.0% | 3.5% | No |
| [N12 / Midgam](https://www.mako.co.il/news-israel-elections/2026/Article-8ea5e45ec2961a1027.htm) | 2.5% | 2.4% | No |
| [Channel 14](https://www.c14.co.il/article/1750553) | 1.5% | 1.9% | No |
| [Zman Yisrael](https://www.zman.co.il/735649/) | 3.0% | 3.6% | No |

Percentages are publisher-reported and are not silently normalized: full denominator and undecided/nonresponse treatment remain unverified. Four-seat projections without percentages stay censored observations. Prime-minister preference, turnout intention and party-voter certainty percentages are different questions and must not fill missing vote shares. Six releases put Amcha outside parliament and one gives it4seats; four exclude Reservists and three give it4seats. These are poll outcomes, not estimated election probabilities. Do not average the known percentages over different subsets to infer a common full vote vector.

## Additional source and official checks

The [pollster’s own final HaMadad release](https://themadad.com/סקר-המדד-סקר-אחרון-23-באוקטובר-2026/) corroborates the Channel13 allocation and partial borderline figures; it does not supply a full vote-share table in the retrieved text. Its fieldwork text says22–23October; a relative weekday/date inconsistency remains. No frozen metadata was silently changed.

The [CEC poll-report repository](https://www.gov.il/he/Departments/DynamicCollectors/knesset_election_polls_26) has a readable introduction but exposes an unpopulated dynamic template through the available reader. The parameterized index returns403. Four PDF leads discovered through [Data24](https://data24.co.il/elections/polls) return403 and relate to earlier fieldwork; none is certified as the selected final poll. The public candidate/agreements route remains inaccessible. Full attempts, URLs, associations and exclusions are in the versioned audit JSON. Search results are discovery evidence, not downloaded files; no raw page/PDF hashes are fabricated.

Indexed [CEC explanatory text](https://www.gov.il/he/pages/election-about-info?chapterindex=4), marked updated September15,2026, explicitly applies the3.25% threshold to K26 and describes120 seats and Bader–Ofer. Direct opening yields an empty page. This improves the broad current-rule corroboration; it does not establish the complete operative legal text or agreement inventory.

A [dated original Ynet agreement report](https://www.ynet.co.il/news/elections2026/article/hjextlj2gl) names five pairs: Likud/ReligiousZionism, Yashar/Democrats, Beyachad/YisraelBeiteinu, Raam/JointList, Shas/UTJ. It reports Otzma, Amcha and Reservists without agreements. Preserve these as news-reported current identities, not verified official filings. Historical pairings remain separate.

Secondary model sites do not resolve the input gap. In particular, indexed [LittlePolls](https://littlepolls.com/) material describes some sector recombinations and seat-derived percentages, as well as older releases. Such transformed data are not original final-poll observations and are excluded.

## Working decision

**Retain the E011 constrained forecast unchanged.** It is the closest integer vector to the equal-group mean in squared distance, subject to total120 and each list being0or3+. This rule follows the user’s instruction; it was not selected because of inspected backtest gains. It is an interim seat-space decision, not an exact current Bader–Ofer result or a full feasibility certificate. Three seats for Reservists is a constrained compromise; no selected poll itself reports3seats for that list. This is visible model behavior, not evidence that3is its most probable outcome.

The active draft remains [the E011 submission draft](../electoral-review-2026-10-24/submission-draft.json): Amcha0, Reservists3, all seats sum120; turnout70.63%. No new training, weights, party mappings, withdrawal-based redistribution or source additions are adopted. No merge or competition submission.

Reopen the vote allocator only when a matching full individual-list vote table is recovered, including the denominator, undecided treatment, transformations and original availability, with verified current surplus agreements. Apply the threshold separately before pooling partners or aggregating other qualifiers. Seat estimates must not be treated as observed votes.

For final review, use the existing [rounding/error plot](../electoral-review-2026-10-24/rounding-error.svg) and [method draft](../electoral-review-2026-10-24/method-draft.txt). The wider source freeze remains incomplete because Kan23/Channel16 and official inventory/mapping questions are unresolved. This audit closes the bounded retrieval attempt; it does not label those issues resolved.
