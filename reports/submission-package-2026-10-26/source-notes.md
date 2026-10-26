# Data and interpretation notes

The copy sheet uses the active forecast in [`forecast.json`](../forecast-decision-2026-10-25/forecast.json), whose SHA-256 is checked in `validation.json`. It is a provisional individual systematic-entry draft, not a submitted response. It has 15 integer fields totaling 120, no one- or two-seat list, and 69.86% national turnout. Neither this package nor the accompanying method PDFs changes the forecast.

## Inputs used by the point forecast

- [Reviewed current poll releases](../../data/snapshots/polls-2026-10-24.json): published seat tables, source URLs, dates, revisions and selected polling groups. The selection cutoff is 24 October 2026. The seven-group current review is documented in [`docs/forecast-review.md`](../../docs/forecast-review.md).
- [2020, 2021 and 2022 official turnout records](../../data/snapshots/turnout-history-2026-10-24/inputs.json): 71.52%, 67.44% and 70.63%, from the [23rd](https://votes23.bechirot.gov.il/nationalresults), [24th](https://votes24.bechirot.gov.il/nationalresults) and [25th](https://votes25.bechirot.gov.il/nationalresults) Knesset national results. Their arithmetic mean is 69.8633...%, displayed as 69.86%.
- [Current poll-to-form mappings](../../config/poll-mappings.json) and [form field order](../../config/submission-fields.json). The current Joint List is placed in the form's Hadash-Ta'al field as an accepted, unconfirmed mapping assumption; historical identities are kept separate. The zero in other qualifying lists is a current forecast, not pooling of below-threshold votes.

## Reproduction and limits

The adopted point decision is implemented in [`scripts/forecast_decision.py`](../../scripts/forecast_decision.py), with input review in [`scripts/forecast_review.py`](../../scripts/forecast_review.py). An [exact vote-based Bader-Ofer implementation](../../scripts/bader_ofer.py) reproduced the complete official 2022 allocation but is not the current point allocator. Current complete vote shares and official surplus agreements have not been verified. Do not describe the submitted seats as an exact Bader-Ofer simulation.

The source freeze is incomplete: the Kan seat-table discrepancy, Zman corroboration link, Channel 16 original graphic, and official candidate/agreement access remain open. The form field inventory is based on the user's 21 October transcription and the original competition PDF; this session did not authenticate the live Google Form. User-specific responses, presentation consent and submission remain private and pending.

Separate numerical-search and prediction-band diagnostics in [PR 35](https://github.com/Omer-Sut/israel-election-forecast/pull/35) and [PR 37](https://github.com/Omer-Sut/israel-election-forecast/pull/37) have not changed this point forecast; the bands are not calibrated confidence intervals.
