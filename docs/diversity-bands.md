# E022: diverse forecasts and minimum-width scenario bands

User approved proceeding after proposing the sum of prediction-band widths as an objective. Preserve the adopted forecast and69.86% turnout. This experiment separates diversity from uncertainty diagnostics and does not turn a small hypothetical-model region into a calibrated confidence interval. It reuses audited E021 artifact12645121746/run40311428283, with checkpoint SHA25672c95783b04d0af0b0b8e2a8a24e82a84dff4a7250c4b7f2ce813f4af8fffe55. No new polls, E021 rerun, current vote reconstruction or automatic forecast change.

The new topic explicitly stacks on PR35 because its independent source auditor and E021 implementation are still unmerged dependencies. Live main remains49c9534; parent PR35head a848b37fcdebc0fb0b75f4167f310dc8abdf6b3a was read before publication. Local Git metadata is protected/stale at3055db4. Publish only intended files. The user's prior unattended-run preference applies: confirm a queued/running job, give the run link and stop rather than spending tokens polling. Launch is not execution success. User can return with run ID.

## Part1: minimum total band width with coverage constraints

For each current/historical case and target80%/90%, CP-SAT minimizes:

    sum across parties of (upper bound - lower bound)

Each model from E021 must put at least the target fraction of its **joint whole-vector scenario mass** inside the region. Exact rational weights are scaled to integer constraints; masses are independently recomputed from final bounds. Invalid source scenarios cannot count as covered or be silently renormalized. Their mass can make a target infeasible. Report this rather than shrinking uncertainty dishonestly.

The region contains the existing constrained-mean anchor, hence at least one feasible vector. Bounds have legal integer endpoints; feasible vectors also satisfy sum120 and each list0or>=3. The current other field remains fixed0 as a documented roster assumption. Bounds spanning0to4 represent allowed values0,3,4, not possible1/2-seat results. Coordinate ranges cannot be independently combined into a valid election. A count-DP reports the number of feasible vectors inside each box as a decimal string; neither this count nor width is a probability.

After minimum width is solved, a fixed secondary rule minimizes total absolute distance of interval midpoints from the anchor (implemented on twice-midpoints). This rule is predeclared, not selected from historical outcomes. Primary/secondary solver statuses remain separate; primary optimality does not imply a unique set of endpoints. All intervals are labelled **scenario-coverage bands**, not confidence intervals. Zero-width bands for unmeasured lists describe this scenario family, not verified real-world certainty.

Join actual historical results only after constructing bands. Report whole-election coverage, descriptive marginal coverage, width, largest miss and a sum of standard marginal interval scores:

    score = width + 2/(1-target) × distance outside the interval

This summed marginal score is an auxiliary diagnostic, not a proper joint-region score. Joint model coverage and marginal score target different aspects. A poll-disagreement envelope is descriptive context, not a calibrated comparator. All six historical elections were inspected earlier; these are retrospective diagnostics.

## Earlier-campaign inflation diagnostic

For each historical raw band, define one calibration miss per entire election: the maximum distance of any actual party outside its band. For a later target use earlier misses only, sorted chronologically by original cutoff. No historical/current party alias transfer is required for this scalar maximum. All parties in an election remain one calibration unit; a long party table is not many independent elections.

    rank = ceil((number of earlier campaigns + 1) × target)

If rank exceeds the available campaign count, mark the correction unavailable; do not invent a finite estimate. Otherwise inflate each coordinate by the corresponding ranked previous miss, preserving the fixed roster scope and legal domain. This minimizes inflation within that simple expansion family at the selected empirical rank; it is not a new fitted voter model. Only certified raw-band cases enter the earlier pool. With six earlier campaigns, the90%rank is7and no finite diagnostic is available;80%rank is6. Historical finite80%diagnostics begin only after four earlier campaigns. Empty/incomplete cells stay explicit.

This is **not a claimed conformal guarantee**. Chronological campaigns, especially2019–2021, are dependent and their exchangeability with2026is unverified. The dataset and outcomes have been inspected. Report coverage limitations and do not sell80%/90%as certified election probabilities. Background: [Angelopoulos–Bates tutorial](https://arxiv.org/abs/2107.07511), [HTML](https://arxiv.org/html/2107.07511v6), and [Gneiting–Raftery interval scoring](https://sites.stat.washington.edu/raftery/Research/PDF/Gneiting2007jasa.pdf), consulted October26. These papers do not establish the assumptions for this election dataset.

## Part2: deliberately diverse valid alternatives

For current E021budget12and unrestricted, consider regret tolerances1and3above each budget's certified optimum. Start from the adopted constrained mean. At each step CP-SAT maximizes the minimum total absolute seat distance to the already selected vectors. Add at most12vectors; stop if the certified maximum new distance is zero. Every vector is independently checked for total120, integer/zero-or3plus, fixed roster, budget and exact regret cap.

This is **sequential greedy max-min diversity**, not a globally optimized batch of12and not random sampling. Each step's status/bound is reported. A feasible/time-limited step is not a proven farthest point. A tolerance3set intentionally permits worse assumed regret than tolerance1to show additional alternatives; it is not a claim that the extra alternatives are equally likely or improve the competition's point loss. Existing source-derived passing weights and stresses remain assumptions. No new constraint forcing Amcha/Reservists to zero.

## Execution and user instructions

Workflow **Explore diverse forecasts and prediction-band widths** first runs six new boundary/exhaustive tests, audits the original E021artifact independently and reproduces the frozen baseline. The research job starts only if validation passes. Reuses pinned optional requirements-numerical-search.txt. Job limit180minutes, soft deadline150minutes, checkpoints throughout, finishes earlier when complete. It runs Python/CP-SAT with no AI/model calls or automatic commits/merge/submission. The agent ends after verifying launch, without waiting/polling.

The30-day artifact **diversity-bands-E022** contains START_HERE.md, results.json, diversity.csv, current-bands.svg, diversity.svg, source/code hashes, environment and run.log. It includes complete/partial/infeasible/unavailable statuses. Ordinary failures preserve partial files where possible; a hard runner termination may prevent upload. Full outputs remain artifact-only until a reviewed compact report is published.

Open the supplied run link → inspect validation/research status → Summary → Artifacts → diversity-bands-E022. Extract into `output/diversity-bands-2026-10-26` within the repo; read START_HERE.md and open both SVGs. Return with the run ID for analysis. No personal/team/form information is collected. No adoption, new≤500word method claim or submission is authorized by launching this experiment.


## Executed analysis

Run40317447939succeeded12.485s; six tests/source audit/baseline and all14primary/14secondary/44greedy optima passed. Raw scenario80/90coverage does not calibrate actual elections:0/6whole-vector coverage; auxiliary marginal interval scores improve on descriptive envelopes. Prior80inflation6is very wide and90rank unavailable. Four diversity batches produce41unique math vectors; one BlueWhite3 conflict with working withdrawal assumption is flagged. Wider tolerance includes additional threshold cases; audited Amcha4witness exists despite greedy-sample omission. Read reports/diversity-bands-2026-10-26/findings.md, independent audit, plots and review CSV. Full detail artifact-only. PR37stacksPR36 and holds final head/checks; no adopted forecast/turnout change, merge or submission.
