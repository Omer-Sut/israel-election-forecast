# Data sources and provenance

No datasets have been downloaded or reviewed. The following links are starting points from the competition PDF, not validated data dependencies.

| Candidate source | Intended use | Review status |
| --- | --- | --- |
| https://en.wikipedia.org/wiki/Opinion_polling_for_the_2026_Israeli_legislative_election | Poll inventory; follow citations to original poll releases | Not reviewed |
| https://www.idi.org.il/articles/66233 | Background on threshold and wasted votes | Not reviewed |
| https://www.idi.org.il/articles/66114 | Israeli Voice Index | Not reviewed |
| https://www.gov.il/he/departments/units/elections-26 | Official election lists and information | Not reviewed |
| https://kolot-nodedim.netlify.app | Additional election resource | Not reviewed |

## Record for every dataset

- Publisher, original URL, retrieval timestamp/timezone, and license or usage restrictions.
- Historical election identifier or pollster, commissioning body, fieldwork dates, publication date, sample size, population, and collection mode where available.
- Stable party/list identifiers, original names, alliances/splits, and documented mapping decisions.
- Units (votes, vote share, seats, or percent turnout), schema, missing values, and any below-threshold/other-party treatment.
- Immutable raw snapshot location and checksum; transformation code and resulting version.
- Earliest public availability and forecast cutoff eligibility, so backtests cannot use future information.
- Reproduction/access instructions for data not stored in Git.

Do not silently treat poll seat estimates as vote shares, or invent methodological metadata missing from a source. Prefer official results and original poll releases for substantive claims. Detailed collection design remains open.
