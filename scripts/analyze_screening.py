"""Analyze a saved screening report offline, without refitting or selecting models."""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / "reports/screening-six-elections-2026-10-21/experiments.json"


def analyze(report_path):
    report = json.loads(report_path.read_text(encoding="utf-8"))
    families = {m["id"]: m["family"] for m in report["configuration"]["models"]}
    comparison = [c for c in report["cases"] if c["evaluation_role"] == "comparison"]
    analysis = {"status": "descriptive_analysis_no_model_selected",
                "source_report": str(report_path.relative_to(ROOT)).replace("\\", "/") if report_path.is_relative_to(ROOT) else report_path.name,
                "source_report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
                "analysis_code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "comparison_elections": [c["election_id"] for c in comparison],
                "cases": [], "family_summaries": {}, "history_features": []}
    family_errors = defaultdict(lambda: defaultdict(list))
    for case in report["cases"]:
        features = list(case["features_by_list"].values())
        analysis["history_features"].append({
            "election_id": case["election_id"], "role": case["evaluation_role"],
            "party_rows": len(features), "polling_groups": len(case["selected_polls"]),
            "trend_missing_rows": sum(row["trend_missing"] == 1 for row in features),
            "group_count_values": sorted({row["group_count"] for row in features}),
            "mean_poll_age_days": features[0]["mean_poll_age_days"]})
    for case in comparison:
        baseline = case["methods"]["rounded_mean_reference"]
        actual = {key: baseline["seats"][key] - baseline["score"]["signed_error_by_list"][key] for key in case["ids"]}
        if sum(actual.values()) != 120:
            raise ValueError("Reconstructed outcome does not sum to 120")
        details, allocations = {}, set()
        for name, entry in case["methods"].items():
            if "seats" not in entry:
                raise ValueError("Comparison unexpectedly contains an unavailable fit")
            seats = entry["seats"]
            if set(seats) != set(actual) or sum(seats.values()) != 120:
                raise ValueError("Invalid prediction coverage/total")
            error = sum(abs(seats[key] - actual[key]) for key in case["ids"])
            if error != entry["score"]["total_absolute_seat_error"]:
                raise ValueError("Saved score differs from reconstructed per-list error")
            allocations.add(tuple(seats[key] for key in case["ids"]))
            changes = {key: seats[key] - baseline["seats"][key] for key in case["ids"] if seats[key] != baseline["seats"][key]}
            delta_error = {key: abs(seats[key] - actual[key]) - abs(baseline["seats"][key] - actual[key]) for key in changes}
            full = entry.get("continuous_unshrunk")
            shrunk = entry.get("continuous_shrunk")
            details[name] = {
                "family": families.get(name, "reference"), "error": error,
                "error_change_from_mean": error - baseline["score"]["total_absolute_seat_error"],
                "identical_integer_forecast_to_mean": not changes,
                "seat_changes_from_mean": changes, "error_changes_by_changed_list": delta_error,
                "unshrunk_diagnostic_error": entry.get("unshrunk_diagnostic_error"),
                "continuous_unshrunk_distance_from_anchor": sum(abs(a-b) for a,b in zip(full, case["anchor"])) if full is not None else None,
                "continuous_shrunk_distance_from_anchor": sum(abs(a-b) for a,b in zip(shrunk, case["anchor"])) if shrunk is not None else None,
                "false_positive_representation": entry["score"]["representation_false_positives"],
                "false_negative_representation": entry["score"]["representation_false_negatives"],
                "one_or_two_seat_estimates": entry["score"]["one_or_two_seat_point_estimates"],
                "ensemble_weights": entry.get("ensemble_weights"),
                "ensemble_fit_elections": entry.get("ensemble_fit_elections")}
            family_errors[families.get(name, "reference")][case["election_id"]].append(error)
        baseline_errors = [{"list_id": key, "predicted": baseline["seats"][key], "actual": actual[key],
                            "signed_error": baseline["seats"][key] - actual[key]}
                           for key in sorted(case["ids"], key=lambda k: (-abs(baseline["seats"][k] - actual[k]), k))]
        earlier = [c for c in report["cases"] if c["election_id"] in case["training_elections"]]
        analysis["cases"].append({
            "election_id": case["election_id"], "horizon_days": case["horizon_days"],
            "training_election_count": len(case["training_elections"]),
            "training_party_rows": sum(len(c["ids"]) for c in earlier),
            "training_trend_missing_rows": sum(row["trend_missing"] == 1 for c in earlier for row in c["features_by_list"].values()),
            "baseline_errors_by_list": baseline_errors,
            "distinct_integer_allocations": len(allocations),
            "candidate_count": len(families),
            "candidates_identical_to_mean": sum(details[name]["identical_integer_forecast_to_mean"] for name in families),
            "candidates_better_than_mean": sum(details[name]["error_change_from_mean"] < 0 for name in families),
            "candidates_equal_error_to_mean": sum(details[name]["error_change_from_mean"] == 0 for name in families),
            "candidates_worse_than_mean": sum(details[name]["error_change_from_mean"] > 0 for name in families),
            "methods": details})
    for family, elections in family_errors.items():
        analysis["family_summaries"][family] = {
            "per_election_error_range": {eid: {"minimum": min(values), "maximum": max(values)} for eid, values in elections.items()}}
    return analysis


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "output/screening-analysis")
    args = parser.parse_args()
    report_path = args.report.resolve()
    analysis = analyze(report_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")
    print(f"Analyzed {len(analysis['cases'])} evaluation cases; all per-list errors reconcile. No models refitted.")


if __name__ == "__main__":
    main()
