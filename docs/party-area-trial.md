# E006: explicit party-lineage and dated geographic context

Authorized continuation, October23,2026. Party seats first; turnout/war/economics later. No final model selection, current forecast replacement, merge or submission.

## Question and bounded design

Does expanding geographic context beyond three stable cores make the existing tabular learners useful? Use the expanded27-release audited history, unchanged T-1 cutoffs and training weights, and only existing ridge_10, forest_3_5, xgb_2_50 (same seed20261021). No additional hyperparameter search. Compare original8 features with four explicit area-context features: previous-election vote-weighted SES index, matched predecessor national-vote fraction, missing indicator and pooled-proxy indicator. Model classes still predict poll residuals, not locality vote totals. Age/sex remain excluded pending separate availability audit.

Five ablations: original; dated15cities with continuity only; cities plus pooled proxies; full2015edition sensitivity with continuity only; edition sensitivity plus pools. Full edition starts strictly after2019-08-31 and falls back to dated cities before then. Keep index vintage2015 throughout, rather than confounding geographic coverage with changing SES definitions. Seven existing correction strengths0/.025/.05/.1/.25/.5/1; report fixed25% and select strength per fixed learner/feature set on at least two STRICTLY EARLIER OOF elections. Run separate selection by continuous projected L1 and final integer L1. Tie prefers smaller strength. No random row split or selection of the feature set on the target outcome; the feature comparisons themselves remain exploratory.

All models have earlier training only. First supervised OOF: September2019. First inner-selected result:2021. These national outcomes were previously inspected, not blind holdouts; thousands of localities do not increase their independent count. Both continuous and integer error exported. At zero strength, simplex/largest-remainder floating ties can differ from exact rounded_mean: preserve the earlier documented distinction. Insufficient-history fallback uses the exact reference.

## Explicit list lineage, not automatic aliasing

config/party-area-lineage.json encodes election-specific target IDs, previous election codes, rationale and status. Source labels are taken from preserved CEC result inventories and the original-source-reviewed pre-election label audits; continuity and pooling are MODELING ASSUMPTIONS, not observed transfers. Same ballot code never establishes identity. Example:2022YeshAtid uses standalone2021YeshAtid, never2020BlueWhite.2021BlueWhite/JointList/Labor/Meretz/Raam/YeshAtid stay missing because their combined predecessors cannot be divided from aggregate votes.

The strict continuity arm includes explicitly retained parties/whole alliances, not a claim that their electorate stayed unchanged. Likud2021 retains its core despite NewHope's departure: that is a proxy with an explicit caveat. Five additional pools are separate sensitivity assumptions:2019SepLikud←Likud+Kulanu; JointList←HadashTaal+RaamBalad; LaborGesher←Labor+Gesher;2020LaborGesherMeretz←LaborGesher+DemocraticUnion;2022NationalUnity←BlueWhite+NewHope. Components/new candidates may differ; pools do not predict voter transfers or pool threshold eligibility. Unmapped splits/new entrants fail closed, with a reason for EVERY modeled target in contexts.csv. No 2026 lineage is asserted here.

For target election k and predecessor pool P, calculate from k-1 LOCALITY votes only:

`area = sum_{p in P,l matched} votes[k-1,p,l]*SES[l] / sum_{p in P,l matched} votes[k-1,p,l]`

`coverage = sum matched predecessor votes / sum_{p in P} NATIONAL votes[k-1,p]`.

Pool votes before averaging. Do not average predecessor means equally. Exclude special/unlocated codes0/9999/99999; never add ballot totals to locality totals. No target-election results define features; missing is[0,0,1,0], not a fictitious middle-income electorate. Coverage is conditional on an assumed predecessor, NOT fraction of target voters identified. Geographic characteristics do not reveal individual voters' age/sex/income or neighborhood catchments. Historical code matching is not certified boundary harmonization.

## Source availability tiers

The15city source remains the separately transcribed [CBS November28,2018 release](https://www.cbs.gov.il/he/mediarelease/DocLib/2018/351/24_18_351b.pdf), not a later workbook backcast.

The [full2015publication1765](https://www.cbs.gov.il/he/publications/DocLib/2019/1765_socio_economic_2015/h_print.pdf) dates its cover August2019; table8 contains the locality index. The already frozen t08.xlsx comes from the same publication directory. A separate edition-audit JSON records source hash, URLs, conservative LAST DAY of publication month, index units and four spot checks against the dated book/press release.1183localities. Round values to3published decimals before fitting; do not use rank scopes as one scale.

This is an EDITION-LINKED RETROSPECTIVE ASSUMPTION, not an authenticated archived workbook or exhaustive1183row comparison. Spot checks cannot rule out later revisions. It must stay in separate sensitivity arms; cbs_sources historical_availability_verified remains false. No blanket historical certification of CBS sources. This condition limits any accuracy claim even if its scores improve.

Also located [2017index release403/2020](https://www.cbs.gov.il/he/mediarelease/DocLib/2020/403/24_20_403b.pdf), dated December15,2020, with explicit March4,2021 replacement, and its August2021book. These dates are useful audit leads, NOT an excuse to certify all collected age/sex/SES workbooks.2017index is not fitted in E006. No downloaded PDF byte hash or visual PDF QA is claimed for web-text inspection.

## Reproduction and evidence

`python scripts/party_area_trial.py` runs in the pinned hosted CPU scientific environment. The screen workflow tests all contracts and runs E006 twice, comparing contexts, coverage, all scores/selections and the SVG exactly. Artifact explicit-party-area-trial contains results, generated configs and hashes; no SQLite, new packages, secrets or restricted respondent data. Numerical text is also encoded in logs for connector-readable retrieval. Committed curated results and actual run status are added only after execution is checked. Baseline/frozen references must remain unchanged. Local Python is currently unusable; no local scientific execution is claimed.
