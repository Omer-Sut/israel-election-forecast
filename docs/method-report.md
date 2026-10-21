# Method report working draft

Status: the preliminary baseline and a limited 2021/2022 historical backtest have run; broader validation and final method selection remain pending. The following draft describes executed work only. It is not a final competition entry.

The competition's systematic track requires a method description of at most 500 words, data sources, a code link, and agreement to present if selected as winner. Keep the final submission description within 500 words; this working file can hold supporting evidence separately.

## Submission description scaffold

### Current implemented-method draft (under 500 words)

We compiled a small audited sample of published national seat projections, preserving source URLs, dates, sample metadata, original list labels, and separate below-threshold percentages. Six stored records yield five active polling groups after retaining the latest audited release from each group in a 14-day window as of October 21, 2026. This is not an exhaustive set of all latest releases.

We compare two transparent references: equal-weight mean seat estimates rounded to total 120 using largest remainders, and an integer consensus minimizing total absolute deviation from the selected polls under the same total. A small dynamic program computes the latter; no heavy training or pretrained model is used. Current alliance labels map explicitly to the form's fields. These are output-label assumptions and do not equate historical party compositions.

Turnout is initially the official 2022 rate, 70.63%, checked against the form's 40.00-100.00% range. A current self-reported turnout-intention measure is retained separately, without assuming it predicts actual participation.

Software checks cover allocation arithmetic, inclusive turnout bounds, group deduplication, cutoff eligibility, optimizer correctness, and historical target separation. Leaving out one current polling group changes the consensus by 4-8 in total absolute seat difference; this is sensitivity, not a confidence interval.

A retrospective pilot uses 12 original-source historical releases across 2021/2022. With three equal-weight groups per election, total absolute seat errors at six days before voting were 24/22 (mean/L1) in 2021 and 12/12 in 2022; final cutoffs gave 20/20 and 12/12. Prior-election turnout persistence missed by 4.08 and 3.19 percentage points. We did not fit weights or tune methods on these results. Two elections, incomplete poll coverage and unauthenticated historical page versions limit conclusions. Neither method is selected as final. Inputs, code, and outputs are versioned in GitHub with hosted reproduction.

### Finalization structure

Replace each item with the method actually implemented; remove placeholders before submission.

1. **Target and cutoff:** seats by the form's lists, turnout, forecast timestamp/timezone, information cutoff.
2. **Data:** polls and official historical results actually used, dates, source links, deduplication, list mapping, and units.
3. **Method:** aggregation rule, threshold/allocation handling, uncertainty assumptions, seat-decision rule, turnout calculation.
4. **Validation:** historical cutoffs, baseline comparison, achieved seat errors, sensitivity, and limitations. Explain limited evidence honestly.
5. **Reproduction:** code revision, accessible input snapshot, configuration/seed, hosted notebook or command, output link.

## Evidence checklist maintained during work

- [x] Submission party field inventory and total-seat rule recorded from the user's transcription; hidden validation/precision remain unverified.
- [ ] Official/poll/form mappings and other-qualifier scoring interpretation resolved.
- [ ] Data provenance, rights, cutoff eligibility, and source discrepancies resolved/documented.
- [x] First baseline run recorded in experiment log; final method selection remains pending.
- [x] Initial historical reference comparison recorded as R002; broader evaluation and final selection remain pending.
- [ ] Final output generated from frozen inputs and a recorded code revision.
- [x] First baseline reproduced exactly in a fresh hosted CPU run: [39572969093](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39572969093), implementation commit `aee2f11`. Final chosen method still needs its own frozen reproduction.
- [ ] Final method paragraph <=500 words, with no unimplemented claims.
- [ ] User/team agrees to presentation requirement and reviews final entry.

Code repository: https://github.com/Omer-Sut/israel-election-forecast

Preliminary input/config/code hashes and outputs: `reports/baseline-2026-10-21/`. Final code revision, chosen method, final forecast, validation results, and submission status: **pending**.
