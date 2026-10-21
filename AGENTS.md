# Instructions for project agents

## Read before working

Read `README.md`, `docs/competition-brief.md`, `docs/project-state.md`, and `docs/decisions.md`. Consult `docs/session-log.md` for history and `docs/data-sources.md` before collecting data. The original Hebrew PDF remains the requirements source of truth.

Also read `docs/project-constraints.md` and `docs/project-plan.md`. The user has approximately **eight hours total hands-on effort**: prioritize a baseline and one lightweight numerical improvement; no heavy training or broad model search. Record actual effort and narrow scope when time runs out. Keep execution portable to a hosted CPU session and all required inputs/code/results in GitHub or a documented shared store.

Use `docs/submission-contract.md` and `config/submission-fields.json` for the user-transcribed form: 14 named lists plus one combined other-qualifying-lists seat field (sum 120), and turnout. Dummy form inputs are not forecasts. Never copy personal/account form responses into the public repository. Verify poll/official/form mappings; Joint List and Hadash-Ta'al are not automatically interchangeable. Apply thresholds to individual other lists before aggregating their seats.

Turnout predictions must satisfy the user-confirmed form bound **40.00 <= national_turnout_pct <= 100.00**, inclusive. Read these bounds from configuration and enforce them during point-prediction selection and export validation; display two decimal places. Preserve diagnostics for any unconstrained out-of-range estimate rather than silently clipping at submission. Exact accepted decimal increments and other form validation remain unverified.

The first implementation is documented in `docs/baseline-method.md`: Python 3.12 standard library, audited JSON inputs, and a GitHub-hosted CPU workflow. Run `python -m unittest discover -s tests -v` and `python scripts/baseline.py --out-dir output/baseline`. When changing consumed inputs/code, regenerate the committed `reports/baseline-2026-10-21/` reference deliberately or create a new dated report; CI compares it with fresh output. Empirical poll disagreement is not historical forecast accuracy or calibrated uncertainty. The accepted current Joint List form mapping is explicit in `config/poll-mappings.json`; historical identities remain separate.

## Working conventions

- Communicate and document in English. Preserve original Hebrew identifiers alongside stable English/internal identifiers when necessary.
- Inspect working-tree changes before editing; do not overwrite another contributor's work.
- Treat the competition as a forecasting task: optimize and evaluate total absolute seat error, with turnout as the tie-breaker.
- Distinguish PDF requirements, independently verified facts, modeling assumptions, and proposed work. Do not present an unimplemented method as implemented.
- Verify current election details, electoral rules, party lists, and publication restrictions against appropriate primary sources before relying on them. Preserve the date and provenance of that verification.
- Preserve raw source data and record URLs, retrieval dates, fieldwork/publication dates where relevant, transformations, and usage restrictions.
- Use historical time cutoffs in backtests. Do not let later polls, revised data, or election results leak into earlier forecasts.
- Do not select a model or add dependencies merely because they are mentioned as possibilities in the notes.
- Treat improbable-outcome pruning as a documented assumption with sensitivity checks, not a mathematical impossibility. A named-party example in user intuition is not a verified hard constraint.
- Inspect the reviewed-source caveats: Kolot Nodedim K26 data is simulated, and an initial aggregator/original-poll mismatch remains unresolved. Never use simulated future results as observations.
- Never commit secrets, credentials, university login information, personal submission responses, local environments, or large generated artifacts.
- Do not submit the competition entry or send messages to people without explicit authorization.

## Session completion and continuity

After meaningful changes, update `docs/project-state.md` with what changed, what was validated, what remains blocked, and the next concrete actions. Add a concise entry to `docs/session-log.md`; add durable decisions to `docs/decisions.md`. Keep these records consistent and self-contained so a new session can resume without chat history.

For consequential experiments, update `docs/experiment-log.md` with inputs/cutoff, commit, configuration, seed, results, effort, and keep/reject reasoning. Maintain `docs/method-report.md` during implementation so the final <=500-word description can be assembled quickly. Never fill it with planned-but-unrun methods as though executed.

Review diffs, run checks appropriate to the change, and commit coherent work on a topic branch once Git is available. Push authorized project work to the configured remote when authenticated and reachable; otherwise explicitly record uncommitted/unpushed status in the handoff and final response. Never claim a commit, push, test, or remote creation succeeded without verification. Do not force-push shared branches or merge conflicting work blindly.

The public repository is https://github.com/Omer-Sut/israel-election-forecast. Initial sandbox restrictions were resolved using approved outside-sandbox commands. If an in-sandbox authentication check fails, do not assume the user's login is invalid; retry with the available approval mechanism. Use `docs/project-state.md` and actual Git state for current status.
