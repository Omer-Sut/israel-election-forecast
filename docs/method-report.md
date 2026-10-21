# Method report working draft

Status: structure only. No model has run, no prediction exists, and no validation scores are available. Do not submit this scaffold as the method description.

The competition's systematic track requires a method description of at most 500 words, data sources, a code link, and agreement to present if selected as winner. Keep the final submission description within 500 words; this working file can hold supporting evidence separately.

## Submission description scaffold

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
- [ ] Baseline run and selected method recorded in experiment log.
- [ ] Validation results and rejected alternatives recorded.
- [ ] Final output generated from frozen inputs and a recorded code revision.
- [ ] Fresh online reproduction checked.
- [ ] Final method paragraph <=500 words, with no unimplemented claims.
- [ ] User/team agrees to presentation requirement and reviews final entry.

Code repository: https://github.com/Omer-Sut/israel-election-forecast

Final code revision, input manifest, forecast output, chosen method, and submission status: **pending**.
