"""Cloud CPU screening; real historical diagnostics are separate from synthetic smoke tests.

No changes to the frozen baseline, no current-election forecast, no fitted hard bounds.
Optional scientific dependencies are loaded only when their methods are used.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import date, timedelta
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.baseline import ROOT, l1_consensus, load_json, rounded_mean, select_polls
from scripts.backtest import historical_vector, score_seats, turnout_prediction

FEATURES = ["anchor_seats", "group_std", "group_range", "mean_poll_age_days",
            "group_count", "fraction_zero", "trend_seats_per_day", "trend_missing"]
SUPERVISED = {"ridge", "forest", "xgboost"}
REFERENCES = ("rounded_mean_reference", "empirical_l1_consensus")


def reconcile(values, total=120):
    """Euclidean simplex projection, then deterministic largest remainder by list order."""
    values = [float(v) for v in values]
    if not values or not all(math.isfinite(v) for v in values):
        raise ValueError("Need finite nonempty seat values")
    ordered = sorted(values, reverse=True)
    cumulative, theta = 0.0, None
    for index, value in enumerate(ordered, 1):
        cumulative += value
        trial = (cumulative - total) / index
        if value > trial:
            theta = trial
    if theta is None:
        raise ValueError("Invalid simplex total")
    projected = [max(v - theta, 0.0) for v in values]
    seats = [int(math.floor(v)) for v in projected]
    remaining = total - sum(seats)
    if not 0 <= remaining <= len(seats):
        raise ValueError("Numerically unstable rounding")
    order = sorted(range(len(seats)), key=lambda i: (-(projected[i] - seats[i]), i))
    for index in order[:remaining]:
        seats[index] += 1
    if sum(seats) != total or any(type(v) is not int or v < 0 for v in seats):
        raise ValueError("Post-rounding allocation must be nonnegative integers summing to total")
    return seats


def build_case(snapshot, cutoff, window=14, minimum_groups=3):
    """Inputs only: publication and source revision cutoffs precede any feature extraction."""
    if cutoff >= snapshot["election_date"]:
        raise ValueError("Cutoff must precede the election")
    ids = [item["id"] for item in snapshot["lists"]]
    if not ids or ids != sorted(set(ids)):
        raise ValueError("Historical IDs must be unique and sorted")
    polls = [p for p in snapshot["polls"] if p.get("kind") == "pre_election_poll"]
    if any(p["election_id"] != snapshot["election_id"] for p in polls):
        raise ValueError("Mixed historical elections")
    selected, rejected = select_polls(polls, cutoff, window)
    if len(selected) < minimum_groups:
        raise ValueError("Insufficient independent polling groups")
    # Reuse selection rules to recover eligible superseded releases for trajectory models.
    ineligible = {p["id"] for p in rejected if p["reason"] != "superseded_within_pollster_group"}
    history = sorted([p for p in polls if p["id"] not in ineligible],
                     key=lambda p: (p["published_on"], p["pollster_group"], p["id"]))
    history_keys = [(p["pollster_group"], p["published_on"]) for p in history]
    if len(history_keys) != len(set(history_keys)):
        raise ValueError("Ambiguous same-day releases in historical trajectory; resolve syndicated copies")
    vectors = [historical_vector(p, ids) for p in selected]
    historic_vectors = [historical_vector(p, ids) for p in history]
    ages = [(date.fromisoformat(cutoff) - date.fromisoformat(p.get("fieldwork_end") or p["published_on"])).days
            for p in selected]
    anchor = [sum(c) / len(c) for c in zip(*vectors)]
    # Average within-group slopes, so a pollster entering later cannot create a trend.
    group_history = defaultdict(list)
    for poll, vector in zip(history, historic_vectors):
        group_history[poll["pollster_group"]].append((poll["published_on"], vector))
    slopes = []
    for entries in group_history.values():
        first, last = entries[0], entries[-1]
        days = (date.fromisoformat(last[0]) - date.fromisoformat(first[0])).days
        if days:
            slopes.append([(b - a) / days for a, b in zip(first[1], last[1])])
    trend = [sum(c) / len(c) for c in zip(*slopes)] if slopes else [0.0] * len(ids)
    features = []
    for i, column in enumerate(zip(*vectors)):
        features.append([anchor[i], math.sqrt(sum((v - anchor[i]) ** 2 for v in column) / len(column)),
                         max(column) - min(column), sum(ages) / len(ages), len(vectors),
                         sum(v == 0 for v in column) / len(column), trend[i], int(not slopes)])
    return {"election_id": snapshot["election_id"], "election_date": snapshot["election_date"],
            "cutoff": cutoff, "ids": ids, "anchor": anchor, "features": features,
            "vectors": vectors, "ages": ages, "selected_polls": selected,
            "history": history, "history_vectors": historic_vectors, "excluded_polls": rejected,
            "snapshot_id": snapshot.get("snapshot_id", snapshot["election_id"]),
            "historical_vintage_limit": snapshot.get("historical_vintage_limit", "synthetic fixture"),
            "audit_tier": "original_source_audited_retrospective_not_archival_vintage"}


def dynamic_prediction(case, ratio, observation_variance):
    """Daily scalar random walks per list, grouped by publication day; no trend extrapolation.

    Multiple same-day polls are averaged with fixed R rather than claiming independent errors.
    No uncertainty interval is exported from this heuristic filter.
    """
    daily = defaultdict(list)
    for poll, vector in zip(case["history"], case["history_vectors"]):
        daily[poll["published_on"]].append(vector)
    state, previous, variance = None, None, observation_variance
    for day, vectors in sorted(daily.items()):
        observation = [sum(c) / len(c) for c in zip(*vectors)]
        if state is None:
            state = observation
        else:
            days = (date.fromisoformat(day) - date.fromisoformat(previous)).days
            variance += days * ratio * observation_variance
            gain = variance / (variance + observation_variance)
            state = [a + gain * (b - a) for a, b in zip(state, observation)]
            variance *= 1 - gain
        previous = day
    return state


def training_arrays(training):
    """Each election gets equal total weight; horizons/party rows are dependent observations."""
    counts = Counter(case["election_id"] for case in training)
    x, y, weights = [], [], []
    for case in training:
        actual = case["actual"]
        if set(actual) != set(case["ids"]):
            raise ValueError("Outcome list coverage differs from the audited historical panel")
        score_seats(dict(zip(case["ids"], reconcile(case["anchor"]))), actual)
        x.extend(case["features"])
        y.extend(actual[key] - value for key, value in zip(case["ids"], case["anchor"]))
        weights.extend([1 / (counts[case["election_id"]] * len(case["ids"]))] * len(case["ids"]))
    # Mean row weight one keeps ridge alpha interpretable across folds of different sizes.
    scale = len(weights) / sum(weights)
    return x, y, [w * scale for w in weights]


def supervised_prediction(spec, training, case, seed):
    import numpy as np
    x, y, weights = training_arrays(training)
    x, y, weights = np.asarray(x), np.asarray(y), np.asarray(weights)
    family = spec["family"]
    if family == "ridge":
        from sklearn.linear_model import Ridge
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler().fit(x, sample_weight=weights)
        model = Ridge(alpha=spec["alpha"], solver="svd")
        model.fit(scaler.transform(x), y, sample_weight=weights)
        correction = model.predict(scaler.transform(case["features"]))
    elif family == "forest":
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=spec["n_estimators"], max_depth=spec["max_depth"],
                                      min_samples_leaf=spec["min_samples_leaf"], random_state=seed, n_jobs=1)
        model.fit(x, y, sample_weight=weights)
        correction = model.predict(case["features"])
    elif family == "xgboost":
        from xgboost import XGBRegressor
        model = XGBRegressor(objective="reg:squarederror", tree_method="hist", device="cpu",
                             n_estimators=spec["n_estimators"], max_depth=spec["max_depth"],
                             learning_rate=spec["learning_rate"], random_state=seed, n_jobs=1,
                             subsample=1.0, colsample_bytree=1.0, reg_lambda=1.0)
        model.fit(x, y, sample_weight=weights)
        correction = model.predict(np.asarray(case["features"]))
    else:
        raise ValueError("Unknown supervised family")
    return [float(a + b) for a, b in zip(case["anchor"], correction)]


def fit_ensemble_weights(records, members, penalty):
    """Linear program: equal-election mean absolute seat loss + L1 weight shrinkage.

    Each record must be an earlier strict OOF prediction, not an in-sample fitted value.
    Operates on continuous unshrunk candidates; integer/shrunk scoring is reported separately.
    """
    import numpy as np
    from scipy.optimize import linprog
    k = len(members)
    counts = Counter(r["election_id"] for r in records)
    rows, targets, loss_weights = [], [], []
    for record in records:
        for i, key in enumerate(record["ids"]):
            rows.append([record["candidates"][m][i] for m in members])
            targets.append(record["actual"][key])
            loss_weights.append(1 / (len(counts) * counts[record["election_id"]]))
    a, target = np.asarray(rows), np.asarray(targets)
    n = len(target)
    # Variables: k simplex weights, n absolute residuals, k absolute weight deviations.
    objective = np.r_[np.zeros(k), loss_weights, np.full(k, penalty)]
    upper = np.vstack([np.c_[a, -np.eye(n), np.zeros((n, k))],
                       np.c_[-a, -np.eye(n), np.zeros((n, k))],
                       np.c_[np.eye(k), np.zeros((k, n)), -np.eye(k)],
                       np.c_[-np.eye(k), np.zeros((k, n)), -np.eye(k)]])
    rhs = np.r_[target, -target, np.full(k, 1 / k), np.full(k, -1 / k)]
    equality = np.zeros((1, 2 * k + n))
    equality[0, :k] = 1
    result = linprog(objective, A_ub=upper, b_ub=rhs, A_eq=equality, b_eq=[1.0],
                     bounds=(0, None), method="highs")
    if not result.success:
        raise ValueError(f"Ensemble optimization failed: {result.message}")
    return result.x[:k].tolist()


def candidate(spec, case, training, config):
    family = spec["family"]
    if family == "recency":
        weights = [2 ** (-age / spec["half_life_days"]) for age in case["ages"]]
        return [sum(v * w for v, w in zip(column, weights)) / sum(weights)
                for column in zip(*case["vectors"])]
    if family == "dynamic":
        return dynamic_prediction(case, spec["variance_ratio"], config["dynamic_observation_variance"])
    if family in SUPERVISED:
        return supervised_prediction(spec, training, case, config["seed"])
    raise ValueError("Ensembles require OOF inputs")


def evaluate_cases(cases, outcomes, config):
    """Walk-forward forecasts. Only finalized earlier elections supply supervised targets."""
    cases = sorted(cases, key=lambda c: (c["election_date"], c["cutoff"]))
    rows, oof = [], []
    for case in cases:
        # A prior election must be completed before this case's forecast cutoff.
        training = [dict(c, actual=outcomes[c["election_id"]]) for c in cases
                    if c["election_date"] < case["cutoff"] and c["election_id"] != case["election_id"]]
        training_ids = sorted({c["election_id"] for c in training})
        strict = len(training_ids) >= config["minimum_training_elections"]
        diagnostic = bool(training_ids) and config["allow_one_election_diagnostic"]
        candidates = {}
        result = {"election_id": case["election_id"], "election_date": case["election_date"],
                  "cutoff": case["cutoff"], "horizon_days": case["horizon_days"], "ids": case["ids"],
                  "anchor": case["anchor"], "audit_tier": case["audit_tier"],
                  "snapshot_id": case["snapshot_id"], "historical_vintage_limit": case["historical_vintage_limit"],
                  "cutoff_timezone": "Asia/Jerusalem", "cutoff_time": "23:59:59",
                  "features_by_list": {key: dict(zip(FEATURES, values)) for key, values in zip(case["ids"], case["features"])},
                  "training_elections": training_ids, "selected_polls": case["selected_polls"],
                  "excluded_polls": case["excluded_polls"],
                  "history_poll_ids": [p["id"] for p in case["history"]],
                  "turnout_prediction_pct": case.get("turnout_prediction_pct"), "methods": {}}
        for name, vector in [(REFERENCES[0], rounded_mean(case["vectors"], 120)),
                             (REFERENCES[1], l1_consensus(case["vectors"], 120))]:
            result["methods"][name] = {"status": "reference", "seats": dict(zip(case["ids"], vector))}
        for spec in config["models"]:
            name, family = spec["id"], spec["family"]
            entry = {"configuration": spec, "training_elections": training_ids if family in SUPERVISED else []}
            if family in SUPERVISED and not (strict or diagnostic):
                entry.update(status="insufficient_data", reason="No earlier election available for fitting")
            elif family == "ensemble":
                members = config["ensemble_members"]
                earlier = [r for r in oof if r["election_date"] < case["cutoff"]]
                enough = len({r["election_id"] for r in earlier}) >= config["minimum_ensemble_oof_elections"]
                if any(m not in candidates for m in members) or (spec["penalty"] is not None and not enough):
                    entry.update(status="insufficient_data", reason="Need all members and two earlier strict OOF elections")
                else:
                    weights = ([1 / len(members)] * len(members) if spec["penalty"] is None else
                               fit_ensemble_weights(earlier, members, spec["penalty"]))
                    raw = [sum(w * candidates[m][i] for w, m in zip(weights, members)) for i in range(len(case["ids"]))]
                    entry.update(status="chronological_screen" if strict else "one_training_election_diagnostic",
                                 ensemble_weights=dict(zip(members, weights)),
                                 ensemble_fit_elections=sorted({r["election_id"] for r in earlier}) if spec["penalty"] is not None else [])
                    candidates[name] = raw
            else:
                candidates[name] = candidate(spec, case, training, config)
                entry["status"] = ("chronological_screen" if strict else "one_training_election_diagnostic") if family in SUPERVISED else "untrained_poll_diagnostic"
            if name in candidates:
                raw = candidates[name]
                shrunk = [a + config["correction_fraction"] * (b - a) for a, b in zip(case["anchor"], raw)]
                entry.update(continuous_unshrunk=raw, continuous_shrunk=shrunk,
                             seats=dict(zip(case["ids"], reconcile(shrunk))),
                             unshrunk_diagnostic_seats=dict(zip(case["ids"], reconcile(raw))))
            result["methods"][name] = entry
        # Save strict OOF rows only; never permit one-election previews to train the ensemble.
        if strict and all(m in candidates for m in config["ensemble_members"]):
            oof.append({"election_id": case["election_id"], "election_date": case["election_date"],
                        "ids": case["ids"], "candidates": candidates, "actual": outcomes[case["election_id"]]})
        # Scoring this case occurs after its predictions. Its target never enters its fitting path.
        actual = outcomes[case["election_id"]]
        anchor_seats = reconcile(case["anchor"])
        for entry in result["methods"].values():
            if "seats" not in entry:
                continue
            entry["score"] = score_seats(entry["seats"], actual)
            changes = [entry["seats"][key] - v for key, v in zip(case["ids"], anchor_seats)]
            entry["movement_from_rounded_anchor"] = sum(abs(v) for v in changes)
            entry["maximum_party_movement"] = max(abs(v) for v in changes)
            entry["representation_changes_from_anchor"] = [key for key, a in zip(case["ids"], anchor_seats)
                                                            if (a > 0) != (entry["seats"][key] > 0)]
            if "unshrunk_diagnostic_seats" in entry:
                entry["unshrunk_diagnostic_error"] = score_seats(entry["unshrunk_diagnostic_seats"], actual)["total_absolute_seat_error"]
        rows.append(result)
    return rows


def synthetic_smoke(config):
    """Exercise every adapter, including optimized ensembles; never report synthetic accuracy."""
    cases, outcomes = [], {}
    for year in range(2010, 2016):
        eid = f"synthetic_{year}"
        ids = [f"synthetic_party_{i}" for i in range(6)]
        polls = []
        for offset in (10, 3):
            for group in range(3):
                vector = reconcile([40 + group, 25 - group, 20 + (year % 3), 15 - year % 3, 12, 8])
                polls.append({"id": f"{eid}_{offset}_{group}", "election_id": eid, "kind": "pre_election_poll",
                              "published_on": f"{year}-10-{20-offset:02d}", "pollster_group": str(group),
                              "seat_projection_complete": True, "reported_seats": dict(zip(ids, vector))})
        snapshot = {"election_id": eid, "election_date": f"{year}-10-20", "lists": [{"id": i} for i in ids], "polls": polls}
        case = build_case(snapshot, f"{year}-10-19")
        case["horizon_days"] = 1
        case["audit_tier"] = "synthetic_software_test_only"
        cases.append(case)
        outcomes[eid] = dict(zip(ids, reconcile([42, 24, 19, 16, 11, 8])))
    results = evaluate_cases(cases, outcomes, config)
    exercised = {name for result in results for name, entry in result["methods"].items() if "seats" in entry}
    expected = {s["id"] for s in config["models"]} | set(REFERENCES)
    if exercised != expected:
        raise AssertionError(f"Unexercised configurations: {expected - exercised}")
    return {"status": "synthetic_software_smoke_only_not_accuracy_evidence", "synthetic_elections": len(cases),
            "exercised_configurations": sorted(exercised),
            "all_integer_nonnegative_sum_120": True,
            "optimized_ensemble_weights": {name: results[-1]["methods"][name]["ensemble_weights"]
                                          for name in ("ensemble_1", "ensemble_5")}}


def build_report(config_path=ROOT / "config/experiments.json"):
    start = time.perf_counter()
    config = load_json(config_path)
    validate_config(config)
    historical_path = ROOT / config["historical_config"]
    historical = load_json(historical_path)
    files = [config_path, historical_path, ROOT / "scripts/experiments.py", ROOT / "scripts/baseline.py",
             ROOT / "scripts/backtest.py", ROOT / "requirements-experiments.txt"]
    files.extend(ROOT / path for path in config.get("additional_provenance_paths", []))
    if len({item["id"] for item in historical["elections"]}) != len(historical["elections"]):
        raise ValueError("Historical elections must be unique")
    horizons = historical["horizons_days"]
    if not horizons or len(set(horizons)) != len(horizons) or any(type(h) is not int or h < 1 for h in horizons):
        raise ValueError("Historical horizons must be unique positive integers")
    cases, exclusions = [], []
    for item in historical["elections"]:
        path = ROOT / item["polls_path"]
        files.append(path)
        snapshot = load_json(path)
        if snapshot["election_id"] != item["id"]:
            raise ValueError("Snapshot/specification ID mismatch")
        for horizon in historical["horizons_days"]:
            cutoff = (date.fromisoformat(snapshot["election_date"]) - timedelta(days=horizon)).isoformat()
            try:
                case = build_case(snapshot, cutoff, historical["poll_window_days"], historical["minimum_groups"])
            except ValueError as exc:
                exclusions.append({"election_id": item["id"], "horizon_days": horizon, "reason": str(exc)})
                continue
            case.update(horizon_days=horizon, turnout_prediction_pct=turnout_prediction(item["turnout_reference"], cutoff))
            cases.append(case)
    if not cases:
        raise ValueError("No eligible historical cases")
    outcome_path = ROOT / historical["outcomes_path"]
    files.append(outcome_path)
    targets = load_json(outcome_path)["elections"]
    outcomes = {}
    for case in cases:
        target = targets[case["election_id"]]
        if target["election_date"] != case["election_date"]:
            raise ValueError("Outcome date mismatch")
        outcomes[case["election_id"]] = target["seat_results"]
    results = evaluate_cases(cases, outcomes, config)
    evaluation_ids = config.get("evaluation_elections", sorted({c["election_id"] for c in results}))
    if not evaluation_ids or set(evaluation_ids) - {c["election_id"] for c in results}:
        raise ValueError("Every requested evaluation election must have eligible cases")
    for row in results:
        row["evaluation_role"] = "comparison" if row["election_id"] in evaluation_ids else "training_and_oof_history"
        if config.get("require_complete_evaluation") and row["evaluation_role"] == "comparison":
            if any("seats" not in entry for entry in row["methods"].values()):
                raise ValueError(f"Incomplete comparison: {row['election_id']}; expand earlier training/OOF history")
        row["actual_turnout_pct"] = targets[row["election_id"]]["turnout_pct"]
        row["turnout_error_pp"] = round(abs(row["turnout_prediction_pct"] - row["actual_turnout_pct"]), 6)
    smoke = synthetic_smoke(config)
    versions = {}
    for package in ("numpy", "scipy", "scikit-learn", "xgboost-cpu", "joblib", "threadpoolctl"):
        versions[package] = importlib.metadata.version(package)
    return {"status": config["status"], "configuration": config, "features": FEATURES,
            "cases": results, "excluded_cases": exclusions, "smoke": smoke,
            "runtime_seconds": round(time.perf_counter() - start, 3), "python": platform.python_version(),
            "packages": versions, "code_commit": os.environ.get("GITHUB_SHA", "local_unrecorded_commit"),
            "input_and_code_sha256": {str(p.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
            "limitations": [f"{len({c['election_id'] for c in results})} audited election panels; convenience poll coverage and retrospective source vintages remain limited.",
                            "2021/2022 outcomes already inspected; this is not a pristine blind holdout or a final model choice.",
                            "Bulk poll indexes, CBS and INES data are not model inputs; historical availability remains unaudited.",
                            "Polls/party rows and repeated horizons are dependent; only elections count as independent outcomes.",
                            "Dynamic filter variances and 25% shrinkage are experimental defaults, not calibrated uncertainty.",
                            "Integer sum-120 arithmetic is enforced; no vote-to-seat allocator or electoral attainability claim.",
                            "Optimized weights require earlier strict OOF elections; unavailable warm-up fits are not comparison failures."]}


def validate_config(config):
    models = config["models"]
    names = [m["id"] for m in models]
    if len(names) != len(set(names)) or set(names) & set(REFERENCES):
        raise ValueError("Model IDs must be unique and distinct from references")
    if not 0 <= config["correction_fraction"] <= 1:
        raise ValueError("Invalid correction fraction")
    if config["minimum_training_elections"] < 2 or config["minimum_ensemble_oof_elections"] < 2:
        raise ValueError("Strict comparisons require at least two earlier elections")
    families = SUPERVISED | {"recency", "dynamic", "ensemble"}
    if any(m["family"] not in families for m in models):
        raise ValueError("Unknown model family")
    if not math.isfinite(config["dynamic_observation_variance"]) or config["dynamic_observation_variance"] <= 0:
        raise ValueError("Dynamic observation variance must be positive")
    for spec in models:
        for key in ("half_life_days", "alpha", "max_depth", "min_samples_leaf", "n_estimators", "learning_rate", "variance_ratio"):
            if key in spec and (not math.isfinite(spec[key]) or spec[key] <= 0):
                raise ValueError(f"Model parameter {key} must be positive")
        if spec.get("penalty") is not None and (not math.isfinite(spec["penalty"]) or spec["penalty"] < 0):
            raise ValueError("Ensemble penalty must be nonnegative")
    members = config["ensemble_members"]
    nonensemble = {m["id"] for m in models if m["family"] != "ensemble"}
    if not members or len(members) != len(set(members)) or not set(members) <= nonensemble:
        raise ValueError("Invalid ensemble members")
    if any(m["family"] != "ensemble" for m in models[next((i for i, m in enumerate(models) if m["family"] == "ensemble"), len(models)):]):
        raise ValueError("Ensembles must follow all base models")


def write_report(report, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    def write_json(name, value):
        (out_dir / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    write_json("experiments.json", report)
    write_json("smoke.json", report["smoke"])
    with (out_dir / "predictions.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["election_id", "horizon_days", "cutoff", "method", "status", "list_id", "seats", "signed_error", "continuous_shrunk", "continuous_unshrunk"])
        for case in report["cases"]:
            for name, entry in case["methods"].items():
                if "seats" not in entry:
                    continue
                for i, key in enumerate(case["ids"]):
                    writer.writerow([case["election_id"], case["horizon_days"], case["cutoff"], name, entry["status"], key,
                                     entry["seats"][key], entry["score"]["signed_error_by_list"][key],
                                     entry.get("continuous_shrunk", [""] * len(case["ids"]))[i],
                                     entry.get("continuous_unshrunk", [""] * len(case["ids"]))[i]])
    comparison = [c for c in report["cases"] if c["evaluation_role"] == "comparison"]
    warmup = [c for c in report["cases"] if c["evaluation_role"] != "comparison"]
    lines = ["# Lightweight model screen — exploratory, no model selected", "",
             "Real historical diagnostics below; synthetic smoke results are separate and contain no accuracy ranking.",
             ("Earlier elections provide training and chronological out-of-fold history; every displayed comparison configuration must run successfully. Both 2021/2022 outcomes were previously inspected."
              if warmup else "Limited historical diagnostic; inspect each method's training status before drawing conclusions."),
             "25% correction around the latest-group mean; T−6 and T−1 remain separate. No current-election forecast is changed.", ""]
    lines += ["## Historical coverage and roles", "",
              "Warm-up elections train models and generate earlier strict out-of-fold (OOF) predictions. Missing early fits are expected and never appear as failed comparison cells.", "",
              "| Election | Horizon | Groups | Earlier training elections | Role |", "| --- | ---: | ---: | ---: | --- |"]
    for case in report["cases"]:
        lines.append(f"| {case['election_id']} | {case['horizon_days']} | {len(case['selected_polls'])} | {len(case['training_elections'])} | {case['evaluation_role']} |")
    lines.append("")
    names = list(REFERENCES) + [m["id"] for m in report["configuration"]["models"]]
    for horizon in sorted({c["horizon_days"] for c in comparison}, reverse=True):
        subset = [c for c in comparison if c["horizon_days"] == horizon]
        lines += [f"## T−{horizon}: real-data diagnostics", "",
                  "Each cell: total absolute seat error / total movement from rounded anchor. Missing fits are explicit.", "",
                  "| Configuration | " + " | ".join(c["election_id"] for c in subset) + " |",
                  "| --- | " + " | ".join("---:" for _ in subset) + " |"]
        for name in names:
            cells = []
            for case in subset:
                entry = case["methods"][name]
                cells.append(f"{entry['score']['total_absolute_seat_error']} / {entry['movement_from_rounded_anchor']}" if "seats" in entry else "insufficient data")
            lines.append("| " + " | ".join([name] + cells) + " |")
    lines += ["", "## Common-case summaries (descriptive, not a model ranking)", "",
              "Compare each candidate with both references on exactly the same elections, separately by horizon.", "",
              "| Method | Horizon | Elections | Mean error | Worst error | Mean reference | L1 reference |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for name in names:
        for horizon in sorted({c["horizon_days"] for c in comparison}, reverse=True):
            subset = [c for c in comparison if c["horizon_days"] == horizon and "seats" in c["methods"][name]]
            if not subset:
                continue
            errors = [c["methods"][name]["score"]["total_absolute_seat_error"] for c in subset]
            refs = [sum(c["methods"][r]["score"]["total_absolute_seat_error"] for c in subset) / len(subset) for r in REFERENCES]
            lines.append(f"| {name} | {horizon} | {len(subset)} | {sum(errors)/len(errors):.2f} | {max(errors)} | {refs[0]:.2f} | {refs[1]:.2f} |")
    lines += ["", "## Turnout reference", ""]
    for case in comparison:
        lines.append(f"- {case['election_id']} T−{case['horizon_days']}: persistence {case['turnout_prediction_pct']:.2f}%; error {case['turnout_error_pp']:.2f} percentage points.")
    lines += ["", "## Synthetic software smoke checks", "",
              f"All {len(report['smoke']['exercised_configurations'])} configurations (including two references) exercised; nonnegative integer totals verified.",
              "Synthetic outcomes are used only to exercise code paths, including optimized ensemble weights. They are never election evidence.",
              "", "## Limits and next steps", ""]
    lines.extend(f"- {item}" for item in report["limitations"])
    lines += ["- Next: inspect stability and source-metadata sensitivities before narrowing the shortlist; six elections remain a small history.",
              "- Full provenance, configurations, statuses, continuous corrections, representation errors and unshrunk diagnostics: `experiments.json`; per-list output: `predictions.csv`.",
              f"- Excluded historical cases: {len(report['excluded_cases'])}.", ""]
    (out_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "config/experiments.json")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "output/experiments")
    args = parser.parse_args()
    report = build_report(args.config)
    write_report(report, args.out_dir)
    print(f"Generated {len(report['cases'])} real-data cases; all configurations smoke-tested in {report['runtime_seconds']}s. No model selected.")


if __name__ == "__main__":
    main()

