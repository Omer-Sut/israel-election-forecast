"""Evaluate unchanged seat-consensus references on audited historical poll panels."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from datetime import date, timedelta
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.baseline import ROOT, l1_consensus, load_json, rounded_mean, seat_integer, select_polls

METHODS = {"rounded_mean_reference": rounded_mean, "empirical_l1_consensus": l1_consensus}


def historical_vector(poll, ids):
    """Reject unmapped lists; never use the current form's catch-all mapping."""
    raw = poll["reported_seats"]
    if (not poll.get("seat_projection_complete") or not raw or set(raw) - set(ids)
            or not all(seat_integer(v) for v in raw.values()) or sum(raw.values()) != 120):
        raise ValueError("Historical poll must be an audited complete allocation with known list IDs")
    return [raw.get(key, 0) for key in ids]


def forecast_case(snapshot, cutoff, window_days, method_names, minimum_groups=3):
    """Generate forecasts from poll inputs only; election outcomes are not an argument."""
    if date.fromisoformat(cutoff) >= date.fromisoformat(snapshot["election_date"]):
        raise ValueError("Historical forecast cutoff must precede election day")
    ids = [row["id"] for row in snapshot["lists"]]
    if not ids or ids != sorted(set(ids)):
        raise ValueError("List order must be unique alphabetical election-specific IDs")
    polls = snapshot["polls"]
    if any(p["election_id"] != snapshot["election_id"] for p in polls):
        raise ValueError("Historical polls cannot be mixed across elections")
    pre_election = [p for p in polls if p.get("kind") == "pre_election_poll"]
    selected, rejected = select_polls(pre_election, cutoff, window_days)
    if len(selected) < minimum_groups:
        raise ValueError("Insufficient audited polling groups for this configured case")
    vectors = [historical_vector(p, ids) for p in selected]
    # Keep generation independent of outcomes and score only after every forecast exists.
    forecasts = {name: dict(zip(ids, METHODS[name](vectors, 120))) for name in method_names}
    return {
        "election_id": snapshot["election_id"], "election_date": snapshot["election_date"],
        "cutoff": cutoff, "list_order": ids, "poll_count": len(selected),
        "list_labels": {row["id"]: row["label_en"] for row in snapshot["lists"]},
        "selected_polls": [{"id": p["id"], "pollster_group": p["pollster_group"],
                            "publisher": p["publisher"], "published_on": p["published_on"],
                            "source_updated_on": p.get("source_updated_on"),
                            "fieldwork_end": p.get("fieldwork_end"), "source_url": p["source_url"],
                            "weight": 1 / len(selected)} for p in selected],
        "excluded_polls": rejected + [{"id": p["id"], "reason": "not_pre_election_poll"}
                                      for p in polls if p.get("kind") != "pre_election_poll"],
        "forecasts": forecasts,
        "single_poll_allocations": {p["id"]: dict(zip(ids, vector)) for p, vector in zip(selected, vectors)},
    }


def score_seats(predicted, actual):
    if set(predicted) != set(actual):
        raise ValueError("Prediction and outcome must have identical historical list coverage")
    for allocation in (predicted, actual):
        if not all(seat_integer(v) for v in allocation.values()) or sum(allocation.values()) != 120:
            raise ValueError("Prediction and outcome must each be integer allocations of 120")
    signed = {key: predicted[key] - actual[key] for key in predicted}
    return {
        "total_absolute_seat_error": sum(abs(v) for v in signed.values()),
        "signed_error_by_list": signed,
        "representation_false_positives": [k for k in predicted if predicted[k] > 0 and actual[k] == 0],
        "representation_false_negatives": [k for k in predicted if predicted[k] == 0 and actual[k] > 0],
        "one_or_two_seat_point_estimates": [k for k, v in predicted.items() if v in (1, 2)],
    }


def turnout_prediction(reference, cutoff):
    if date.fromisoformat(reference["election_date"]) >= date.fromisoformat(cutoff):
        raise ValueError("Turnout reference must be a past election, not the target or future")
    value = reference["turnout_pct"]
    if type(value) not in (int, float) or not math.isfinite(value) or not 40 <= value <= 100:
        raise ValueError("Turnout prediction must satisfy the current competition output bounds")
    return value


def build_report(config_path=ROOT / "config/historical-backtest.json"):
    config = load_json(config_path)
    if (set(config["methods"]) != set(METHODS) or len(config["methods"]) != len(METHODS)
            or not config["horizons_days"] or len(set(config["horizons_days"])) != len(config["horizons_days"])
            or any(type(h) is not int or h < 1 for h in config["horizons_days"])):
        raise ValueError("Use the two fixed methods and unique positive forecast horizons")
    cases, files, snapshots = [], [config_path, Path(__file__), ROOT / "scripts/baseline.py"], {}
    seen_elections = set()
    for specification in config["elections"]:
        path = ROOT / specification["polls_path"]
        snapshot = load_json(path)
        if specification["id"] != snapshot["election_id"] or specification["id"] in seen_elections:
            raise ValueError("Election IDs must match inputs and occur only once")
        seen_elections.add(specification["id"])
        snapshots[specification["id"]] = snapshot
        files.append(path)
        for horizon in config["horizons_days"]:
            cutoff = (date.fromisoformat(snapshot["election_date"]) - timedelta(days=horizon)).isoformat()
            case = forecast_case(snapshot, cutoff, config["poll_window_days"], config["methods"],
                                 config["minimum_groups"])
            case.update(horizon_days=horizon, period=specification["period"],
                        cutoff_timezone=config["cutoff_timezone"], cutoff_time="23:59:59",
                        turnout_prediction_pct=turnout_prediction(specification["turnout_reference"], cutoff),
                        turnout_reference=specification["turnout_reference"])
            cases.append(case)

    # Outcomes are loaded only after all point predictions have been generated.
    outcome_path = ROOT / config["outcomes_path"]
    outcomes = load_json(outcome_path)
    files.append(outcome_path)
    for case in cases:
        actual = outcomes["elections"][case["election_id"]]
        if actual["election_date"] != case["election_date"]:
            raise ValueError("Outcome election date mismatch")
        actual_turnout = actual["turnout_pct"]
        if type(actual_turnout) not in (int, float) or not math.isfinite(actual_turnout) or not 0 <= actual_turnout <= 100:
            raise ValueError("Invalid observed turnout")
        case["actual_seats"] = actual["seat_results"]
        case["actual_turnout_pct"] = actual_turnout
        case["turnout_absolute_error_pp"] = round(abs(case["turnout_prediction_pct"] - actual_turnout), 6)
        case["official_source_url"] = actual["source_url"]
        case["scores"] = {name: score_seats(prediction, actual["seat_results"])
                          for name, prediction in case["forecasts"].items()}
        case["single_poll_total_absolute_seat_errors"] = {
            key: score_seats(vector, actual["seat_results"])["total_absolute_seat_error"]
            for key, vector in case.pop("single_poll_allocations").items()}

    aggregates = []
    for horizon in config["horizons_days"]:
        subset = [case for case in cases if case["horizon_days"] == horizon]
        aggregates.append({
            "horizon_days": horizon, "independent_elections_not_poll_count": len(subset),
            "equal_election_mean_total_absolute_seat_error": {
                name: sum(c["scores"][name]["total_absolute_seat_error"] for c in subset) / len(subset)
                for name in config["methods"]},
            "equal_election_mean_turnout_absolute_error_pp": sum(c["turnout_absolute_error_pp"] for c in subset) / len(subset),
        })
    return {
        "status": config["status"], "poll_window_days": config["poll_window_days"],
        "methods": config["methods"], "cases": cases, "aggregates_by_horizon": aggregates,
        "input_and_code_sha256": {str(path.relative_to(ROOT)).replace("\\", "/"):
                                 hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
        "source_snapshots": [{"election_id": key, "snapshot_id": value["snapshot_id"],
                              "coverage": value["coverage"], "historical_vintage_limit": value["historical_vintage_limit"]}
                             for key, value in snapshots.items()],
        "limitations": [
            "Two elections only; repeated horizons do not create additional independent outcomes.",
            "Three-group original-source convenience panel per election, not all polls; groups differ across elections.",
            "No model weights, window, or hyperparameters fitted or selected from these outcomes.",
            "Dated publisher pages and known updates checked; authenticated historical archive versions unavailable.",
            "Historical list identities are separate; no 2026 form mapping or pooled other bucket is used.",
            "All official seat-winning lists included; omitted unmodeled lists have zero official and predicted seats.",
            "Point estimates enforce integer total only; no independent electoral allocator or probability calibration.",
            "Representation mismatches are seat-positive versus zero diagnostics, not threshold probabilities.",
            "2019-2021 repeated-election-period sensitivity needs more elections; this pilot has only 2021 from that period.",
            "Turnout repeats the preceding election, not a current survey or war-adjusted model."
        ],
    }


def write_report(report, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "backtest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    with (output_dir / "seat-errors.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["election_id", "horizon_days", "cutoff", "list_id", "method", "predicted", "actual", "signed_error", "absolute_error"])
        for case in report["cases"]:
            for method in report["methods"]:
                for key in case["list_order"]:
                    error = case["scores"][method]["signed_error_by_list"][key]
                    writer.writerow([case["election_id"], case["horizon_days"], case["cutoff"], key, method,
                                     case["forecasts"][method][key], case["actual_seats"][key], error, abs(error)])
    lines = ["# Historical backtest pilot - 2021 and 2022", "",
             "Unchanged rounded mean and empirical L1 consensus; 14-day effective poll-age window, equal latest audited group weights.",
             "Both horizons use end-of-day cutoffs in Asia/Jerusalem. Lower total absolute seat error is better.", "",
             "| Election | Days before voting | Cutoff | Groups | Rounded mean error | L1 error | Turnout prediction / actual | Turnout error (pp) |",
             "| --- | ---: | --- | ---: | ---: | ---: | --- | ---: |"]
    for case in report["cases"]:
        mean = case["scores"]["rounded_mean_reference"]["total_absolute_seat_error"]
        l1 = case["scores"]["empirical_l1_consensus"]["total_absolute_seat_error"]
        lines.append(f"| {case['election_id']} | {case['horizon_days']} | {case['cutoff']} | {case['poll_count']} | {mean} | {l1} | {case['turnout_prediction_pct']:.2f}% / {case['actual_turnout_pct']:.2f}% | {case['turnout_absolute_error_pp']:.2f} |")
    lines.extend(["", "## Equal-election averages (keep horizons separate)", ""])
    for aggregate in report["aggregates_by_horizon"]:
        errors = aggregate["equal_election_mean_total_absolute_seat_error"]
        horizon = aggregate["horizon_days"]
        unit = "day" if horizon == 1 else "days"
        lines.append(f"- {horizon} {unit} before voting, {aggregate['independent_elections_not_poll_count']} elections: rounded mean **{errors['rounded_mean_reference']:.1f}**, L1 **{errors['empirical_l1_consensus']:.1f}** total absolute seat error.")
    lines.extend(["", "These are retrospective errors against official results, not in-sample poll disagreement. Two elections cannot establish a reliable model ranking; neither method is selected as final.",
                  "Each reassigned seat contributes two to the total absolute error. Turnout error is in percentage points; the same persistence forecast is evaluated at both horizons.",
                  "", "## Largest per-list errors", ""])
    for case in report["cases"]:
        for method, score in case["scores"].items():
            worst = sorted(score["signed_error_by_list"],
                           key=lambda k: (-abs(score["signed_error_by_list"][k]), k))[:3]
            lines.append(f"- {case['election_id']}, T-{case['horizon_days']}, {method}: " + "; ".join(
                f"{case['list_labels'][k]} {case['forecasts'][method][k]} predicted / {case['actual_seats'][k]} actual"
                for k in worst) + ".")
    lines.extend(["", "## Representation diagnostics", ""])
    for case in report["cases"]:
        for method, score in case["scores"].items():
            lines.append(f"- {case['election_id']}, T-{case['horizon_days']}, {method}: false positive lists={score['representation_false_positives']}; false negative lists={score['representation_false_negatives']}; one/two-seat point estimates={score['one_or_two_seat_point_estimates']}.")
    lines.extend(["", "## Audited source selection", ""])
    for case in report["cases"]:
        lines.append(f"- {case['election_id']}, T-{case['horizon_days']}: " + "; ".join(
            f"[{p['publisher']}, {p['published_on']}]({p['source_url']})" for p in case["selected_polls"]) + ".")
    lines.extend(["", "## Limitations", ""] + [f"- {item}" for item in report["limitations"]])
    lines.extend(["", "Per-list predictions/errors are in `seat-errors.csv`; input/code hashes, exclusions, group selections and individual-poll errors are in `backtest.json`.", ""])
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "output/backtest")
    args = parser.parse_args()
    report = build_report()
    write_report(report, args.out_dir)
    print(f"Generated {len(report['cases'])} historical cases (two elections, two horizons) in {args.out_dir}")


if __name__ == "__main__":
    main()
