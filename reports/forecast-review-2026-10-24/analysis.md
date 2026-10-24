# Forecast review: refreshed inputs and concrete options

The seven-group rounded-mean reference is ready for review, with turnout70.63%. The package remains provisional because two source gaps and direct official verification are unresolved. It has not been submitted.

![Decision sensitivity](decision-sensitivity.svg)

## Recommended reference

| Form field | Seats |
| --- | ---: |
| Likud | 22 |
| Yashar! | 22 |
| Beyachad | 13 |
| Democrats | 9 |
| Yisrael Beiteinu | 7 |
| Shas | 8 |
| United Torah Judaism | 7 |
| Otzma Yehudit | 8 |
| Religious Zionism | 7 |
| Ra'am | 5 |
| Hadash-Ta'al form slot / current Joint List | 9 |
| Blue and White | 0 |
| Amcha Yisrael | 1 |
| Reservists-Economic | 2 |
| Other qualifying lists combined | 0 |
| **Total** | **120** |

The [small export](submission-draft.json) contains the same seats and formatted turnout, with an explicit provisional status. [All options](seat-options.csv), [summary](summary.md), [full results](review.json) and [221-word method draft](method-draft.txt) are saved alongside it. No personal information or presentation consent is included.

## What the threshold checks establish

Rounded mean, empirical L1 and four explicit zero-or-minimum-seat rules were compared on the unchanged six-election T−1 panel. All give2021 error20 and2022 error12. Zero-or-3/4 rules improve April2019 from40 to38; zero-or-4 rules worsen September2019 from12 to14. The zero-or-3 square rule ties the mean elsewhere, but this is a small, repeatedly inspected retrospective comparison. Do not select it as a proven winner.

The current mean has Amcha0.571 and Reservists1.714 before rounding, yielding1 and2 seats. These are arithmetic point estimates that summarize conflicting zero/four-seat poll projections; they are not simulated feasible outcomes. Restricting named lists to0or3+ changes these to0/3. Restricting them to0or4+ under squared-distance loss chooses0/0 and reallocates seats. Neither assumption can replace a calibrated vote-share/threshold model on the available partial percentages.

Four conditional squared-distance scenarios are provided. If both borderline lists fail, the allocation has Likud23, UTJ8, Ra'am6 and both lists0. If only Reservists qualifies at4, the reference changes Amcha1→0, Reservists2→4 and Religious Zionism7→6. The symmetric Amcha-only scenario swaps the fixed four seats. If both get4, other lists adjust to preserve120. No probabilities are assigned, and fixing four seats does not reproduce Bader-Ofer or certify the whole vector's attainability.

Keep the established rounded mean as the provisional reference, with L1 and threshold scenarios available for the user's final choice. No learned correction earned adoption, and no new threshold rule is adopted merely because it improves an already-inspected historical cell.

## Source coverage and remaining work

The October24 snapshot preserves all ten previous records exactly and adds five complete reviewed final releases. Seven current groups are selected: N12/Midgam, Channel13/consortium, Maariv/Lazar via Walla, IsraelHayom/Kantar, i24/Direct Polls, Channel14/Next Data and Zman/Tatika. Dates, metadata, raw Hebrew labels, partial percentages and caveats remain in the [snapshot](../../data/snapshots/polls-2026-10-24.json). Equal group weight is not a claim of independence or sample-quality calibration.

Kan's October23 source conflict remains unresolved: Zman/Skarim report Democrats8 and a complete120-seat allocation, while Ynet reports9 and a121-seat table. Replacing the older Kantar anchor with the separately attributed8-seat secondary vector changes only Amcha1→0 and UTJ7→8. It is a sensitivity, not an adopted source correction. Kan and Israel Hayom share Kantar and must not be counted as independent polling firms. Channel16's original complete graphic remains unverified; adding its reported aggregate vector leaves the rounded reference unchanged. These small measured effects do not establish that missing sources are irrelevant.

Blue and White's completed list withdrawal is reported by Zman quoting CEC on October21, corroborating the distinction from Gantz's October19 personal announcement. Direct official candidate/withdrawal access remains blocked; every selected complete poll already allocates zero. The form field is retained. Existing accepted Joint List and Religious Zionism alliance mappings remain explicit assumptions.

CEC pages returned403 and the Knesset lexicon redirected to geographic restriction. Indexed Knesset text supports3.25% of valid votes and120 seats, but the complete operative rules, current agreements, final inventory and blackout text have not been retrieved. Thus the source freeze remains incomplete. No public competition entry, final submission or merge was performed.

## Verification

Implementation13e15d5312b66dcaf6bd206f231280acbd299c6a / [PR21](https://github.com/Omer-Sut/israel-election-forecast/pull/21), stacked on PR20. Initial [forecast review run40070762691](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/40070762691) passed all five new tests and exact repeats. [Baseline40070762676](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/40070762676) passed frozen checks. Scientific status and the final committed-report comparison must be verified separately on the latest PR head. A small export and plot tick labels were added after the initial successful model-free computation; the final workflow independently regenerates every saved file.

The source freeze should be completed by resolving Kan/Channel16 and official verification; then review a concrete final vector. Further model tuning on these historical outcomes is not the next priority. User cumulative hands-on effort remains unmeasured; local Git HEAD remains stale and the remote topic tree is authoritative.
