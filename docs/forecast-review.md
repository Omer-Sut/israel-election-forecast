# E010: current forecast review

October 24, 2026. User authorized moving from research diagnostics to current-source review, a small final decision set, threshold sensitivities and a submission package. This produces a concrete review package; source conflicts prevent calling the input freeze complete. No competition entry is submitted.

## Source review

`data/snapshots/polls-2026-10-24.json` preserves all ten E007 poll records unchanged and adds five complete reviewed allocations: N12 October23, Channel13 October23, Maariv via Walla October23, Israel Hayom/Kantar October22 (updated23), i24NEWS/Direct Polls October23 (fieldwork22). It supplies seven reporting groups, using the latest reviewed release per group. The other two anchors remain Channel14 and Zman October22. Current source versions are conservatively available October24; this is not a claim of an actual edit that day.

- N12 reports actual N1018 versus initial sample1000 and margin4.4%. Preserve the inconsistency without estimating effective N or sample weighting.
- Channel13 reports N1875; fieldwork and mode not established. Relative Friday/yesterday dating is corroborated by its original homepage and dated graphic caption.
- Walla's dated Maariv report supplies a complete120-seat vector and partial threshold percentages. Do not copy N1048 or fieldwork dates from an aggregator when absent in this retrieved report. Replaces the older Walla/Lazar anchor, not another independent firm.
- Israel Hayom explicitly identifies Kantar, N1110, internet interviewing October21–22. Its group is shared with Kan; a later verified Kan release replaces it. Its bloc prose groups Reservists inconsistently with some external summaries; only the complete party vector enters calculations.
- i24 identifies Direct Polls/Tzuriel Sharon, N5124, October22 fieldwork and digital/panel method. Publication23 is supported by the original four-days-before-election wording and dated index linking the exact article. Separate from Next Data/Filber for current reporting; common lineage and potential dependence remain a limitation. Omission sensitivities include both.

Kan October23 remains excluded from the main panel: Skarim/Zman report Democrats8 and a120-seat table; Ynet reports9 and a121-seat table. No silent repair. An explicit secondary sensitivity uses the separately attributed8-seat vector in place of Kantar, never in addition. Channel16 October22 remains an unverified aggregate-source sensitivity; original complete graphic not retrieved. Exact sample size stays missing when described only as more than5000. Neither variant enters the recommended reference.

## Status, rules and mappings

Zman October21 reports completion of all Blue and White candidate withdrawals, quoting CEC; Ynet October19 reports Gantz's own announcement. The direct official candidate page remains403. All selected complete polls already allocate zero; its required form field remains and no withdrawal-based support redistribution is invented. Current mapping aliases remain explicit user-accepted assumptions, especially Joint List to the form's Hadash-Ta'al slot and Religious Zionism/Zehut to Religious Zionism.

Indexed Knesset primary text supports3.25% of valid votes and120seats; direct lexicon access redirects to geographic restriction. Full operative2026 rules, surplus agreements, final candidate inventory and blackout text remain unverified. The competition PDF's Friday cutoff is retained as a document requirement. Inputs use pre-election releases; no newly measured post-cutoff polls are introduced.

## Decision protocol

Run `python scripts/forecast_review.py`. Standard-library only. Round the equal-group mean using the existing exact rational largest-remainder rule. Keep empirical L1 consensus as a comparison. Four seat-space sensitivities minimize either squared distance to the mean or absolute poll disagreement, with each individual named list restricted to zero or at least3/4seats. The combined other-list form field is exempt: applying one threshold to that aggregate would be incorrect. These restrictions are modeling assumptions, not a verified Bader-Ofer allocator. Exact integer dynamic programming maintains total120; ties use the stated second loss then field order.

Four additional scenarios fix Amcha and Reservists independently to0or4seats and adjust other fields by squared-distance minimization under zero-or-4 assumptions. They are conditional numerical illustrations, with no assigned probabilities or claimed legal feasibility. Partial percentages cannot reconstruct full vote shares or party-specific threshold probabilities.

The same six decision rules run on the unchanged six-election T−1 panel. Outcomes have already been inspected; this is a retrospective sensitivity, not untouched model selection. Retain the established rounded-mean reference provisionally. Do not adopt a new threshold correction merely because its historical score improves.

All options are checked against the actual field configuration, exact120seat total and inclusive turnout bounds. Turnout stays at the official2022 persistence70.63%, displayed to two decimals. Self-reported intentions are descriptive only. The package includes CSV, full JSON, plot, input hashes and a method draft below500words; no personal responses or presentation consent is recorded.

Five tests cover exhaustive small-decision comparison, scenario constraints, aggregate-other treatment, preservation of earlier records and source-version cutoffs. Hosted `Prepare forecast review` runs the package twice and compares saved results when present. Check the PR execution record before claiming success. Preserve original frozen baseline/model reports.
