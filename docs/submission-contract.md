# Submission form contract

Source: user-supplied transcription of all form sections, received October 21, 2026. This records the form as shown to the user, not a direct authenticated inspection by the agent. The user's entered numbers and method text were explicitly dummy navigation inputs; they are **not predictions, model results, or final responses**. Personal/account details are not reproduced here or in the machine-readable configuration.

Canonical field order and labels: [config/submission-fields.json](../config/submission-fields.json). Stable IDs are project identifiers, not official ballot identifiers. English names are working translations; Hebrew labels preserve the supplied form wording.

## Forecast outputs

The form requires **15 seat entries: 14 named lists and one combined other-qualifying-parties entry**, plus national turnout. Its header explicitly states that seats must sum to **120**. Preserve the following order:

| # | Project ID | English working name | Hebrew list label |
| --- | --- | --- | --- |
| 1 | `likud` | Likud | הליכוד |
| 2 | `yashar` | Yashar! (Eisenkot) | ישר! (איזנקוט) |
| 3 | `beyachad` | Beyachad / Together (Bennett) | ביחד (בנט) |
| 4 | `democrats` | The Democrats | הדמוקרטים |
| 5 | `yisrael_beiteinu` | Yisrael Beiteinu | ישראל ביתנו |
| 6 | `shas` | Shas | ש"ס |
| 7 | `united_torah_judaism` | United Torah Judaism | יהדות התורה |
| 8 | `otzma_yehudit` | Otzma Yehudit | עוצמה יהודית |
| 9 | `religious_zionism` | Religious Zionism | הציונות הדתית |
| 10 | `raam` | Ra'am | רע"ם |
| 11 | `hadash_taal` | Hadash-Ta'al | חד"ש-תע"ל |
| 12 | `blue_and_white` | Blue and White | כחול לבן |
| 13 | `amcha_yisrael` | Amcha Yisrael | עמך ישראל |
| 14 | `reservists_economic` | Reservists-Economic | מילואימניקים כלכלית |
| 15 | `other_qualifying_lists` | Other parties passing the threshold, combined | מפלגות אחרות שעוברות את אחוז החסימה |

Turnout is a separate required percentage field: `national_turnout_pct`, labeled `אחוז הצבעה ארצי צפוי (%)`. The user subsequently confirmed the form requires **40.00 <= turnout <= 100.00**, inclusive. This is a hard constraint on the model's reported point prediction and final export. Read the bounds from the field configuration, validate before export, and display two decimal places. The exact permitted decimal increment/precision remains unverified; two-decimal output is our presentation convention. Other hidden Google Forms validation remains unverified. Use nonnegative integer seats.

Apply the turnout constraint during prediction/decision selection as well as final output validation. If an intermediate unconstrained estimate lies outside the range, retain it for diagnostics and review/document the constrained estimate; do not silently alter it at submission time. The form bound is an admissible-output rule, not evidence that historical or real-world turnout outside that range is impossible. No forecasting model or executable export validator has been implemented yet.

The required zero-seat entries must remain in the export. Do not drop a named form field because it is missing from a poll, expected to win no seats, or reported elsewhere as withdrawn. Verify status and mapping, then forecast accordingly.

## Meaning of the other-parties entry

Interpret the supplied label as the combined seats of qualifying lists not represented by the 14 named entries. It is **not** a vote-share bucket for below-threshold parties, undecided respondents, or invalid ballots.

If modeling individual other lists, apply the threshold and allocation to each separately, then aggregate their seats for this output field. Do not pool several sub-threshold parties to invent a qualifying list. Export all 15 entries with a total of 120. Resolve any ambiguous official-to-form mapping before finalizing the forecast.

## Other form sections

The supplied first section has required email, full name, and track fields; degree/year/program and team name/other members were shown without a required marker. The two track options are community guessing and systematic competitive. Record actual participant responses only at final entry preparation, outside the public repository. Inspecting the systematic section is not itself confirmation of the user's final track or team.

The systematic section requires:

- Method description: method, model, data, assumptions.
- Data sources.
- Code link.
- Agreement to present the method if selected as winner.

A document link is shown as preferred, without a required marker. The PDF supplies the **500-word** description limit; it is not visible as validation in this transcription. Do not infer the user's presentation agreement from dummy form navigation.

The header repeats election day **October 27, 2026** and deadline **October 26, 2026 at 23:59**. No explicit timezone is shown. Asia/Jerusalem remains a planning assumption.

## Outstanding mapping and scoring questions

1. Poll labels such as **Joint List** and the form's **Hadash-Ta'al** must not be treated as identical without verifying the actual constituent lists and relevant date. Check whether any separately contesting list belongs in the other-parties output instead.
2. Combined poll labels, including Religious Zionism/Zehut or changing Reservists/Economic lineups, require explicit date-specific mappings. Similar names alone are insufficient.
3. The form includes Blue and White even if some sources omit it or report a status change. Verify current status; keep the field.
4. The PDF defines absolute error by list, while this form combines other qualifying parties. Working output-level scoring uses the 15 form entries, aggregating other-list truth before taking absolute error. The organizer's precise treatment of multiple other qualifiers is not independently confirmed; retain disaggregated internal outcomes so alternative scoring can be checked.
5. Exact decimal increment/precision, other hidden field validation, exact timezone, eligibility, team, and final track/presentation consent remain to be confirmed. Turnout bounds of 40.00-100.00 are confirmed by the user. None prevents starting poll collection with the known field inventory.

### Joint List / Hadash-Ta'al source check (October 21, 2026)

The user proposed treating these as the same form target and asked for online validation. Sources support a relationship, but **not literal or historical equivalence**:

- The [current alliance's own website](https://jointlist.org.il/en/) identifies its three constituent parties as Hadash, Ta'al, and Balad.
- [N12's August 19, 2026 reporting](https://www.mako.co.il/news-israel-elections/2026/Article-cb92eb7e0f910a1026.htm) describes Hadash, Ta'al, and Balad agreeing to a joint run, without Ra'am.
- [Official 2022 results](https://votes25.bechirot.gov.il/nationalresults) list Hadash-Ta'al and Balad separately. Historical series must retain that election-specific composition.

The form may use an older Hadash-Ta'al label for the current Joint List output slot; this is a plausible **form-mapping interpretation**, not organizer-confirmed intent. Current Joint List polling can be mapped to that slot only with this assumption made explicit and its source label/composition retained. No automatic alias or historical merger has been encoded in the field configuration. In particular, do not add a separate Balad forecast on top of a current poll already including it in the Joint List. Verify each poll's date and lineup.

## Stage-one status

The form inventory, labels, required markers, total-seat rule, and narrative-field requirements are now recorded. Structural electoral-rule verification and official/poll/form mappings remain open. No real forecast has been entered or submitted by the agent.
