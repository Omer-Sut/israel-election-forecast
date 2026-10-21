# Method report working draft

Status: a first preliminary baseline has run; historical forecast validation and final method selection remain pending. The following draft describes executed work only. It is not a final competition entry.

The competition's systematic track requires a method description of at most 500 words, data sources, a code link, and agreement to present if selected as winner. Keep the final submission description within 500 words; this working file can hold supporting evidence separately.

## Submission description scaffold

### Current implemented-method draft (under 500 words)

We compiled a small audited sample of published national seat projections, preserving source URLs, dates, sample metadata, original list labels, and separate below-threshold percentages. Six stored records yield five active polling groups after retaining the latest audited release from each group in a 14-day window as of October 21, 2026. This is not an exhaustive set of all latest releases.

We compare two transparent references: equal-weight mean seat estimates rounded to total 120 using largest remainders, and an integer consensus minimizing total absolute deviation from the selected polls under the same total. A small dynamic program computes the latter; no heavy training or pretrained model is used. Current alliance labels map explicitly to the form's fields. These are output-label assumptions and do not equate historical party compositions.

Turnout is initially the official 2022 rate, 70.63%, checked against the form's 40.00-100.00% range. A current self-reported turnout-intention measure is retained separately, without assuming it predicts actual participation.

Software checks cover allocation arithmetic, inclusive turnout bounds, group deduplication, cutoff eligibility, and optimizer correctness. Leaving out one polling group changes the consensus by 4-8 in total absolute seat difference. This is sensitivity, not a confidence interval. Historical poll-to-election validation has not yet been performed; lower disagreement with polls is not proof of improved election accuracy. Inputs, code, and reference outputs are versioned in GitHub, with a hosted CPU reproduction workflow.

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
- [ ] Validation results and rejected alternatives recorded.
- [ ] Final output generated from frozen inputs and a recorded code revision.
- [x] First baseline reproduced exactly in a fresh hosted CPU run: [39572969093](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39572969093), implementation commit `aee2f11`. Final chosen method still needs its own frozen reproduction.
- [ ] Final method paragraph <=500 words, with no unimplemented claims.
- [ ] User/team agrees to presentation requirement and reviews final entry.

Code repository: https://github.com/Omer-Sut/israel-election-forecast

Preliminary input/config/code hashes and outputs: `reports/baseline-2026-10-21/`. Final code revision, chosen method, final forecast, validation results, and submission status: **pending**.
