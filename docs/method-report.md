# Method report working draft

E007 prepares a separate October23 current-source refresh using unchanged equal-group mean/L1. Four newer original releases, partial threshold-support plot, preserved unknowns and conservative source-version cutoff. Hosted execution pending; no calibrated threshold model, learned weighting or final forecast selected. See current-poll-audit.md. Original method draft remains unchanged.

E006 verified October23:60hosted tests and deterministic repeats passed. Broader prior-list area proxies and separately labeled1183locality2015edition sensitivity did not produce fixed25% or earlier-OOF-selected integer gains over mean20/12. Do not adopt into the forecast/submission draft. Full workbook archive uncertainty and2021split/new-list missingness remain material; age/sex dates and2026lineage unresolved. See party-area-trial.md and reports/party-area-trial-2026-10-23/analysis.md. Final method draft remains unchanged.

E005 verified:55hosted tests passed. Chronological parameter/blending validation, dynamic-gap features and a dated prior-election geographic subset were tried; no selected2021/2022configuration beat the mean. Broad CBS profiles remain descriptive. Audited-only expected-poll-error prototype MAE9.233versus8.668simple baseline, so no quality weights adopted. These are research diagnostics, not a change to the final forecasting method. Turnout/war/economics later. See poll-quality-feature-trial.md and project-state.

E004 preparation: user approved hosted correction-strength/forest-seed sensitivity on unchanged audited inputs. Diagnostic work, not an adopted forecasting method; final description remains unchanged until evaluated selection. See robustness-batch.md/project-state for actual execution status.

October22 continuation: A002 adds independently checked pre-rounding plots over all saved historical folds. E003 adds three earlier original-source-reviewed releases (24 to27) and runs four fixed data sensitivities while preserving latest-group anchors, model settings, outcomes and the preliminary2026 forecast. All46 hosted tests and deterministic repeats passed; none beats reference20/12 on2021/2022. Some ensembles improve to ties, some forests worsen. See [campaign-history.md](campaign-history.md) and project-state for checked run/provenance evidence. No L0 penalty or final model is adopted. The final submission description remains the baseline draft until a method is selected.

E002 analysis: [screening-results-analysis.md](screening-results-analysis.md) explains why matching reference scores often means reproducing its rounded vector, why the earlier four panels do not train a within-group trend effect, and which party-level misses dominate. No candidate improved either comparison outcome, and larger unshrunk supervised corrections worsened both. Treat this as limited retrospective evidence; retain references and audit source/trajectory coverage before adopting an adjustment. No final method or uncertainty interval is selected.

E002 execution update: [six-election screening](six-election-screening.md) now uses T−1 panels from 2015, both 2019 elections and 2020 as earlier training/OOF history, with complete 2021/2022 comparisons for all 20 configurations. All 45 hosted tests and deterministic reruns passed; [durable results](../reports/screening-six-elections-2026-10-21/summary.md) show no improvement: references 20/12 versus candidates20–24/12–14 total absolute seat error. These are two already-inspected evaluation outcomes, not an untouched holdout. Source-vintage/coverage/metadata limits remain explicit; no challenger or final current forecast is selected.

Implementation update (E001, October 21): a separate [cloud screening pipeline](model-screening.md) now implements six candidate families with three configurations each, anchored to polls with 25% corrections. This is exploratory work; no challenger is selected or substituted into the preliminary forecast. Only audited 2021/2022 polls enter real diagnostics; synthetic checks are software tests, not predictive evidence. See the experiment log and project state for verified execution status. Retain the baseline description below until a method is actually selected.

The first hosted screen passed all 43 tests and deterministic reruns. On the one 2022 evaluation election, fitted candidates tie the 12-seat reference error at T−6 and tie or worsen it to 14 at T−1. These results do not establish a family ranking. The remaining four elections need audited poll panels before strict chronological screening and learned real-data ensemble weights are supported.

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
