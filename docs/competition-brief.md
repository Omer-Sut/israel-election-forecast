# Competition requirements (English summary)

Reviewed on October 21, 2026. Source: the two-page Hebrew PDF `תחרות תחזית בחירות לכנסת ה26.pdf` in the repository root, visually checked against both rendered pages. This is a faithful working summary, not a certified translation. The PDF is authoritative.

Source SHA-256: `ab0902cda5df7d3ef89cf88dabd5bd2a7590622932ae7aca6bf04ff94a42dd9e`.

## Purpose and eligibility (page 1)

The Department of Statistics and Data Science invites students, staff, and departmental alumni to forecast the results of the 26th Knesset election. The PDF states that the election will take place on **October 27, 2026**.

## Tracks (page 1)

- Community/guessing track: individual prediction, with no requirement to explain its basis.
- Systematic/competitive track: a method-based prediction by an individual or a team of **up to four participants**. The model, data, and assumptions must be explained. The winning team must present its method at the award ceremony.

Working assumption for project planning: develop an entry suitable for the systematic track. The user has not yet explicitly selected a track or team.

## Submission and deadline (page 1)

- Submit through the university's [Google Form](https://forms.gle/tSX7cYLPwKD86HdM7), using a university account.
- Deadline: **October 26, 2026 at 23:59**. Responses may be edited until that deadline.
- Each participant may submit once in each track.
- The PDF does not explicitly state a timezone. Use Asia/Jerusalem as a planning assumption pending confirmation.
- On October 21 the user supplied a full form transcription. Its 15 seat fields (14 named lists plus combined other qualifying parties), required narrative fields, and explicit total of 120 are documented in [submission-contract.md](submission-contract.md). Hidden numeric validation, turnout precision, and timezone remain unknown. The user's entries were dummy navigation values, not a forecast.

## Forecast targets and scoring (page 1)

1. Seat counts for the form's **14 named lists plus combined other qualifying parties**, totaling **120** according to the form header. Preserve disaggregated internal list outcomes; scoring of multiple other qualifiers is not independently confirmed.
2. National voter turnout, in percent.

The main score is the sum of absolute differences between predicted seats and official seats across lists. Lower scores are better. If scores tie, turnout accuracy determines the ranking. The PDF does not specify a more detailed turnout-error formula or further tie-breakers.

The reference outcome is the Central Elections Committee's **final official result after double-envelope ballots have been counted**.

## Additional systematic-track requirements (pages 1-2)

- A method description of **up to 500 words**, covering the model, data, and assumptions.
- Data sources, such as polls and historical data.
- A **link to code**, preferably also a document describing it.
- Confirmation that the team agrees to present its method if it wins.

Ranking is based solely on prediction accuracy. The committee can disqualify a submission whose explanation is incomplete or whose described method clearly was not actually implemented. The winning systematic-track team commits to presenting the method at the award ceremony.

## Other conditions (page 2)

- Winners in the leading places in each track will be announced.
- Systematic-track winners also receive a symbolic prize at the ceremony; its date will be announced later.
- Committee decisions are final.
- Submitted data will be retained and used only for the competition and statistical analysis, and published in aggregate or with the participant's consent.

## Resources listed in the PDF (page 2)

These URLs are transcribed from the source. An initial October 21 review, source explanations, access limitations, and data-quality findings are recorded in [data-sources.md](data-sources.md); they are not yet audited input datasets.

| Resource | Link |
| --- | --- |
| Aggregated polls | https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Israeli_legislative_election |
| Wasted votes and electoral threshold, Israel Democracy Institute | https://www.idi.org.il/articles/66233 |
| Israeli Voice Index, Israel Democracy Institute | https://www.idi.org.il/articles/66114 |
| Official lists, Central Elections Committee | https://www.gov.il/he/departments/units/elections-26 |
| Additional site | https://kolot-nodedim.netlify.app |

The PDF states that election law prohibits publishing polls from the end of Friday **October 23, 2026** until polls close, and that polls published before then remain available for participants to use. This is a statement in the competition document, not independently verified legal advice. Verify the applicable official rules before planning collection or publication.

## Modeling implications (project interpretation)

- Model selection and validation should match absolute seat error; a turnout forecast is still required even though it is a tie-breaker.
- A forecast needs an explicit data cutoff, party/list mapping, and reproducible processing.
- Electoral thresholds, seat allocation, surplus-vote agreements, list alliances, and integer/total-seat constraints need official verification before implementation. Their detailed mechanics are not specified in this PDF.
- The explanation must describe the method actually run. Preserve the code revision, inputs, assumptions, and output for the submitted forecast.

## Submission readiness checklist

- [ ] Confirm track, eligibility, and team membership (maximum four in systematic track).
- [x] Record the user-transcribed form party fields and required fields (see submission contract); hidden validation remains unverified.
- [ ] Confirm current deadline/timezone and relevant official electoral rules.
- [ ] Produce and validate seat predictions for every required list.
- [ ] Produce national turnout prediction in the form's required precision.
- [ ] Record forecast cutoff, input versions, code revision, and reproduction steps.
- [ ] Write a method description of no more than 500 words and cite sources.
- [ ] Provide an accessible code link and preferably a method document.
- [ ] Confirm the team's agreement to present if it wins.
- [ ] Have the user review and explicitly authorize the actual competition submission.
