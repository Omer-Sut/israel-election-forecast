"""Predeclared data-only sensitivities with the unchanged E002 model grid, on hosted CPU."""
from __future__ import annotations

import argparse
import copy
from datetime import date, timedelta
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.baseline import ROOT, load_json
from scripts.backtest import historical_vector
from scripts.experiments import build_case, build_report, write_report

AUDIT = ROOT / "data/snapshots/campaign-history-2026-10-22/audit.json"
VARIANTS = ("reference", "publication_age", "expanded_history", "expanded_publication_age")


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8", newline="\n")


def prepare_variants(out_dir):
    """No outcomes used in source selection, mapping or variant construction."""
    out_dir = out_dir.resolve()
    config = load_json(ROOT / "config/experiments.json")
    historical = load_json(ROOT / config["historical_config"])
    audit = load_json(AUDIT)
    configurations = {}
    for variant in VARIANTS:
        folder = out_dir / variant
        history = copy.deepcopy(historical)
        for spec in history["elections"]:
            snapshot = copy.deepcopy(load_json(ROOT / spec["polls_path"]))
            cutoff = (date.fromisoformat(snapshot["election_date"]) - timedelta(days=1)).isoformat()
            original = build_case(snapshot, cutoff, historical["poll_window_days"], historical["minimum_groups"])
            if "expanded" in variant:
                names = {r["label_en"]: r["id"] for r in snapshot["lists"]}
                for raw in audit["polls"]:
                    if raw["election_id"] != snapshot["election_id"]:
                        continue
                    if set(raw["raw_seats_by_label"]) != set(names):
                        raise ValueError("New source labels must map exactly to historical lists")
                    if raw["pollster_group"] not in {p["pollster_group"] for p in snapshot["polls"]}:
                        raise ValueError("Trajectory-only extension cannot add polling groups")
                    poll = {k: copy.deepcopy(v) for k, v in raw.items() if k != "raw_seats_by_label"}
                    poll.update(kind="pre_election_poll", seat_projection_complete=True,
                                reported_seats={names[k]: v for k, v in raw["raw_seats_by_label"].items()},
                                retrieved_on=audit["retrieved_on"], audit_status=audit["audit_tier"])
                    historical_vector(poll, original["ids"])
                    snapshot["polls"].append(poll)
            if "publication_age" in variant:
                for poll in snapshot["polls"]:
                    if poll["id"] == "2020_walla_midgam_0226":
                        poll["original_printed_fieldwork"] = {k: poll.pop(k) for k in ("fieldwork_start", "fieldwork_end") if k in poll}
                        poll["age_sensitivity_assumption"] = "Publication age fallback only; original printed metadata retained separately, not certified corrected."
            changed = build_case(snapshot, cutoff, historical["poll_window_days"], historical["minimum_groups"])
            if [p["id"] for p in changed["selected_polls"]] != [p["id"] for p in original["selected_polls"]] or changed["anchor"] != original["anchor"]:
                raise ValueError("Data sensitivity unexpectedly changed the latest-group anchor")
            snapshot.update(snapshot_id=f"{snapshot['snapshot_id']}-{variant}-2026-10-22",
                            extension_audit=str(AUDIT.relative_to(ROOT)).replace("\\", "/"))
            destination = folder / f"polls-{snapshot['election_id']}.json"
            write_json(destination, snapshot)
            spec["polls_path"] = str(destination.relative_to(ROOT)).replace("\\", "/")
        history_path = folder / "historical.json"
        write_json(history_path, history)
        experiment = copy.deepcopy(config)
        experiment["historical_config"] = str(history_path.relative_to(ROOT)).replace("\\", "/")
        experiment["status"] = f"E003_{variant}_data_sensitivity_not_model_selection"
        experiment["additional_provenance_paths"] += [str(AUDIT.relative_to(ROOT)).replace("\\", "/"), "scripts/campaign_history.py"]
        config_path = folder / "config.json"
        write_json(config_path, experiment)
        configurations[variant] = config_path
    return configurations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "output/campaign-history")
    parser.add_argument("--prepare-only", action="store_true")
    args = parser.parse_args()
    paths = prepare_variants(args.out_dir)
    if not args.prepare_only:
        for name, config_path in paths.items():
            report = build_report(config_path)
            write_report(report, config_path.parent / "results")
            print(f"{name}: {len(report['cases'])} chronological cases; runtime {report['runtime_seconds']}s")
    print("Prepared four data-only variants. Grid, shrinkage, cutoffs, latest-group anchors and official outcomes unchanged.")


if __name__ == "__main__":
    main()
