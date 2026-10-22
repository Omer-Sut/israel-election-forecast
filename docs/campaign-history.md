# Campaign-history sensitivities (E003)

October 22, 2026. User authorized continuing the earlier data/coverage work and emphasized online collaboration. Work is published on isolated branch `feat/campaign-history-diagnostics`, based on PR #13 head3055db4. PR #13's branch remains unchanged. No main merge is performed.

## Frozen comparison design

Keep the existing 18 candidates plus two controls, 25% correction, seed, T-1 cutoff, 14-day age window, historical identities, outcomes and chronological gates. Execute four variants before selecting any model:

1. `reference`: fresh E002 reproduction.
2. `publication_age`: Walla February26,2020 uses publication as its age fallback. Keep original printed fieldwork in a separate diagnostic field; this is an assumption-based sensitivity, not a certified source correction.
3. `expanded_history`: add three original-source-reviewed earlier releases within existing groups. Keep every latest-group poll/anchor unchanged. This isolates usable history/features from a different current benchmark.
4. `expanded_publication_age`: combine the two changes.

The source-selection policy was frozen before the new scores. Newly reviewed releases are N12 March31,2019; Walla September3,2019; N12 February23,2020. Audit facts, source URLs, dates, numerical transcriptions, explicit Shas residual derivation and attempted-but-unavailable sources are versioned in `data/snapshots/campaign-history-2026-10-22/audit.json`. Raw response hashes were unavailable through the retrieval surface and are not fabricated. These remain retrospective source checks, not authenticated historical archives.

Coverage increases24 to27 reviewed releases. Earlier eligible history counts change3/3/3/3 to3/4/4/4. Three earlier campaigns gain observed within-group trends; 2015 remains missing. None of the 2021/2022 inputs is changed. All six cases and every available model are retained, with missing early fits explicit.

2015 primary video description/newer full commissioned allocation could not be retrieved. Do not replace its old third release from a secondary/index transcription at a falsely upgraded tier. The February17 Walla page has the same printed fieldwork/sample as the inconsistent February26 page; it was reviewed but not added as an independent trajectory observation. Source identities and dates are the limiting factor, not training runtime.

## Hosted execution and durable evidence

The existing `Screen lightweight forecast models` workflow now runs all tests, checks original reports/database, executes the four variants, repeats each for deterministic predictions, and produces independent pre-rounding diagnostics. No local scientific installation/training is required.

```sh
python scripts/campaign_history.py --out-dir output/campaign-history
node scripts/compare_campaign_diagnostics.mjs output/campaign-history
```

The `campaign-history-sensitivities` artifact contains exact generated configs/snapshots, all predictions, provenance, per-list diagnostics, SVG plots and comparison tables. It expires after30days; source audit/code are durable and rebuild offline. Preserve the compact comparison/provenance and checked run links under a dated report once execution is verified. Never claim an unrun variant improved performance. Earlier OOF histories and already inspected comparison outcomes do not create new blind evaluation elections.

## Git and concurrent work

This session can edit source files but cannot create `.git/index.lock`; the terminal also cannot reach github.com. The user's authentication is valid. A connected GitHub client can create topic branches and publish blobs/trees/commits without changing local filesystem permissions. Use expected-SHA updates, verify live remote heads and do not overwrite another contributor. AGENTS.md now records this workflow.

Because remote API commits do not advance local `.git`, local HEAD stays3055db4. A collaborator must fetch and deliberately reconcile local source changes before committing from this checkout; avoid a blind commit/push of the stale tree. Remote branch/SHA and hosted verification belong in project-state after publication.

Verified: implementation31b58712593b3db492b20e27ef3fb1728baaf858, [PR #14](https://github.com/Omer-Sut/israel-election-forecast/pull/14), [screen39741972606](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39741972606), [baseline39741972643](https://github.com/Omer-Sut/israel-election-forecast/actions/runs/39741972643). All46 cloud tests, original reference reproduction, four variant runs and repeated prediction comparisons passed. Runtimes3.012/2.390/2.399/2.411seconds. All12 stable consumed hashes matched. Artifact12408824706 is877,889 compressed bytes and was verified available/unexpired.

Durable [comparison/plots](../reports/campaign-history-2026-10-22/index.html) preserve all variant/fold stage errors and source hashes in `comparison.json.gz`; a standard Node renderer rebuilds CSV/SVGs and base R optionally exports `comparison.png`. The full artifact's generated snapshots and per-list predictions are rebuildable from versioned inputs/code. Source audit and compact results are not dependent on one laptop or expiring workflow storage.

No candidate beats reference20/12 on2021/2022. The combined variant brings equal/strongly penalized ensembles to a2021 tie at20, while forest_2_5/forest_3_5 worsen to26. Middle forest2022 becomes14. The three earlier additions materially change learned corrections; that does not establish reliable gains.2015 remains a genuine primary-source/trajectory gap. No final method, L0 penalty, new2026 forecast or submission is selected. User hands-on effort remains unmeasured and the total budget is not reset.
