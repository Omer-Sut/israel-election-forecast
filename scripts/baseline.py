"""Reproduce preliminary seat-consensus baselines using Python's standard library."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def seat_integer(value):
    return type(value) is int and value >= 0


def validate_forecast(seats, turnout, contract):
    expected = [field["id"] for field in contract["seat_fields"]]
    if set(seats) != set(expected):
        raise ValueError("Forecast must contain exactly the configured seat fields")
    if not all(seat_integer(value) for value in seats.values()):
        raise ValueError("Seats must be nonnegative integers, excluding booleans")
    if sum(seats.values()) != contract["seat_total"]:
        raise ValueError("Seat forecast does not sum to the required total")
    limits = contract["turnout_field"]
    if (type(turnout) not in (int, float) or not math.isfinite(turnout)
            or not limits["minimum"] <= turnout <= limits["maximum"]):
        raise ValueError("Turnout lies outside the configured inclusive bounds")


def select_polls(polls, as_of, window_days):
    """Select latest audited publication per declared group, without future releases."""
    if type(window_days) is not int or window_days < 0:
        raise ValueError("Poll window must be a nonnegative number of days")
    cutoff = date.fromisoformat(as_of)
    start = cutoff - timedelta(days=window_days)
    selected = {}
    rejected = []
    seen_ids = set()
    for poll in polls:
        if poll["id"] in seen_ids:
            raise ValueError("Duplicate poll ID")
        seen_ids.add(poll["id"])
        published = date.fromisoformat(poll["published_on"])
        updated = date.fromisoformat(poll.get("source_updated_on", poll["published_on"]))
        field_end = poll.get("fieldwork_end")
        if field_end and date.fromisoformat(field_end) > published:
            raise ValueError("Fieldwork ends after the stated publication date")
        if published > cutoff or updated > cutoff:
            rejected.append({"id": poll["id"], "reason": "not_available_by_cutoff"})
            continue
        # Unknown fieldwork dates stay unknown. Publication date is an explicit proxy.
        effective_date = date.fromisoformat(field_end) if field_end else published
        if effective_date < start:
            rejected.append({"id": poll["id"], "reason": "outside_poll_window"})
            continue
        group = poll["pollster_group"]
        previous = selected.get(group)
        if previous and previous["published_on"] == poll["published_on"]:
            raise ValueError("Ambiguous same-day releases in one pollster group; resolve explicitly")
        if previous is None or published > date.fromisoformat(previous["published_on"]):
            if previous:
                rejected.append({"id": previous["id"], "reason": "superseded_within_pollster_group"})
            selected[group] = poll
        else:
            rejected.append({"id": poll["id"], "reason": "superseded_within_pollster_group"})
    if not selected:
        raise ValueError("No eligible audited polls")
    return [selected[key] for key in sorted(selected)], sorted(rejected, key=lambda p: p["id"])


def poll_vector(poll, contract, mapping):
    """Map an audited complete published seat allocation, never vote percentages."""
    raw = poll["reported_seats"]
    total = contract["seat_total"]
    if not poll.get("seat_projection_complete") or not raw:
        raise ValueError("Only audited complete seat allocations can supply residual zeros")
    if not all(seat_integer(value) for value in raw.values()) or sum(raw.values()) != total:
        raise ValueError("Reported seat allocation is invalid or incomplete")
    ids = [field["id"] for field in contract["seat_fields"]]
    result = dict.fromkeys(ids, 0)
    mapped = set()
    for source_id, seats in raw.items():
        alias = mapping["aliases"].get(source_id)
        target = alias["target"] if alias else source_id
        if alias and target not in result:
            raise ValueError("Alias refers to an unknown form target")
        if target not in result:
            # These are already allocated individual-list seats, not pooled votes.
            target = "other_qualifying_lists"
        if target in mapped and target != "other_qualifying_lists":
            raise ValueError("Two source labels map to the same named list")
        mapped.add(target)
        result[target] += seats
    return [result[key] for key in ids]


def validate_vectors(vectors, total):
    if not vectors or not vectors[0] or not seat_integer(total):
        raise ValueError("Need nonempty scenarios and a nonnegative integer seat total")
    width = len(vectors[0])
    for vector in vectors:
        if (len(vector) != width or not all(seat_integer(x) for x in vector)
                or sum(vector) != total):
            raise ValueError("Scenarios must be nonnegative integer allocations of the total")


def rounded_mean(vectors, total):
    """Equal-group mean, largest-remainder rounding; ties use form field order."""
    validate_vectors(vectors, total)
    count = len(vectors)
    sums = [sum(column) for column in zip(*vectors)]
    result = [value // count for value in sums]
    remaining = total - sum(result)
    order = sorted(range(len(sums)), key=lambda i: (-(sums[i] % count), i))
    for index in order[:remaining]:
        result[index] += 1
    return result


def l1_consensus(vectors, total):
    """Minimize equal-poll absolute seat disagreement subject to integer total.

    This is consensus with observed polls, NOT calibrated expected election loss.
    Ties minimize squared distance to the mean, then lexicographic field order.
    Constraints are form arithmetic only, not a claim of electoral feasibility.
    """
    validate_vectors(vectors, total)
    count = len(vectors)
    states = {0: (0, 0, ())}
    for column in zip(*vectors):
        column_sum = sum(column)
        costs = [(sum(abs(value - observed) for observed in column),
                  (count * value - column_sum) ** 2) for value in range(total + 1)]
        next_states = {}
        for allocated, (loss, tie_cost, allocation) in states.items():
            for value in range(total - allocated + 1):
                candidate = (loss + costs[value][0], tie_cost + costs[value][1],
                             allocation + (value,))
                new_total = allocated + value
                if new_total not in next_states or candidate < next_states[new_total]:
                    next_states[new_total] = candidate
        states = next_states
    return list(states[total][2])


def disagreement(vector, scenarios):
    return sum(sum(abs(a - b) for a, b in zip(vector, scenario))
               for scenario in scenarios) / len(scenarios)


def build_report(config_path=ROOT / "config/baseline.json"):
    config = load_json(config_path)
    if config["selection"] != "latest_audited_publication_per_pollster_group":
        raise ValueError("Unknown poll-selection method")
    if config["weights"] != "equal_per_selected_group":
        raise ValueError("Only explicit equal-group weights are implemented")
    contract_path = ROOT / "config/submission-fields.json"
    mapping_path = ROOT / "config/poll-mappings.json"
    snapshot_path = ROOT / config["poll_snapshot"]
    reference_path = ROOT / config["turnout_reference"]
    contract, mapping = load_json(contract_path), load_json(mapping_path)
    snapshot, reference = load_json(snapshot_path), load_json(reference_path)
    if config["turnout_method"] != "last_official_election_persistence":
        raise ValueError("Unknown turnout method")
    if date.fromisoformat(reference["election_date"]) > date.fromisoformat(config["as_of_date"]):
        raise ValueError("Future turnout reference")
    selected, rejected = select_polls(snapshot["polls"], config["as_of_date"], config["poll_window_days"])
    vectors = [poll_vector(poll, contract, mapping) for poll in selected]
    ids = [field["id"] for field in contract["seat_fields"]]
    total = contract["seat_total"]
    mean, consensus = rounded_mean(vectors, total), l1_consensus(vectors, total)
    turnout = reference["turnout_pct"]
    for vector in [mean, consensus]:
        validate_forecast(dict(zip(ids, vector)), turnout, contract)
    sensitivity = []
    if len(vectors) > 1:
        for index, poll in enumerate(selected):
            remaining = vectors[:index] + vectors[index + 1:]
            alternative = l1_consensus(remaining, total)
            sensitivity.append({"omitted_group": poll["pollster_group"],
                                "seats": dict(zip(ids, alternative)),
                                "seat_distance_from_full_consensus": sum(abs(a-b) for a,b in zip(alternative,consensus))})
    files = [config_path, contract_path, mapping_path, snapshot_path, reference_path, Path(__file__)]
    return {
        "status": config["status"],
        "as_of_date": config["as_of_date"],
        "snapshot_id": snapshot["snapshot_id"],
        "input_and_code_sha256": {str(path.relative_to(ROOT)).replace("\\", "/"): hashlib.sha256(path.read_bytes()).hexdigest() for path in files},
        "poll_count": len(selected),
        "weighting": "Equal weight per latest audited pollster group; independence is not assumed",
        "selected_polls": [{"id": p["id"], "pollster_group": p["pollster_group"], "publisher": p["publisher"],
                            "published_on": p["published_on"], "fieldwork_end": p.get("fieldwork_end"),
                            "source_url": p["source_url"], "weight": 1/len(selected)} for p in selected],
        "excluded_or_archived": rejected,
        "methods": {
            "rounded_mean_reference": {"seats": dict(zip(ids, mean)), "mean_absolute_disagreement_with_polls": disagreement(mean, vectors)},
            "empirical_l1_consensus": {"seats": dict(zip(ids, consensus)), "mean_absolute_disagreement_with_polls": disagreement(consensus, vectors)}
        },
        "turnout": {"prediction_pct": turnout, "formatted": f"{turnout:.2f}", "method": config["turnout_method"],
                    "reference_election": reference["election_id"], "source_url": reference["source_url"],
                    "minimum": contract["turnout_field"]["minimum"], "maximum": contract["turnout_field"]["maximum"]},
        "turnout_intention_diagnostics": [{"poll_id": p["id"], "reported_intention_pct": p["turnout_intention_pct"],
                                          "used_in_prediction": False} for p in selected if "turnout_intention_pct" in p],
        "poll_seat_ranges_not_confidence_intervals": {key: {"min": min(column), "max": max(column)} for key, column in zip(ids, zip(*vectors))},
        "leave_one_group_out_sensitivity_not_probability": sensitivity,
        "limitations": [
            "Audited convenience sample, not all latest polls; additional October 20 releases remain unaudited.",
            "No historical poll-to-election backtest or probability calibration has run.",
            "Poll disagreement is not forecast accuracy or an election-outcome probability.",
            "Only form arithmetic is enforced; a vote-to-seat allocator and full electoral feasibility are not implemented.",
            "Current alliance-to-form mappings are explicit assumptions and do not merge historical electorates.",
            "Unreported seat zeros follow a verified complete 120-seat table, not missing percentage imputation.",
            "Turnout is a historical persistence baseline; current self-reported intention is diagnostic only.",
            "No adjustment for support redistribution after Blue and White's reported withdrawal."
        ]
    }


def write_report(report, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "baseline.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    contract = load_json(ROOT / "config/submission-fields.json")
    fields = contract["seat_fields"]
    with (output_dir / "seats.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["field_id", "form_label_he", "rounded_mean_reference", "empirical_l1_consensus"])
        for field in fields:
            writer.writerow([field["id"], field["label_he"], *[method["seats"][field["id"]] for method in report["methods"].values()]])
    lines = ["# Preliminary baseline - not submission ready", "", f"As-of date: {report['as_of_date']}. Latest audited release per group; {report['poll_count']} selected groups.", "",
             "| Form field | Rounded-mean reference | Empirical L1 consensus |", "| --- | ---: | ---: |"]
    for field in fields:
        values = [method["seats"][field["id"]] for method in report["methods"].values()]
        lines.append(f"| {field['label_en']} | {values[0]} | {values[1]} |")
    lines.extend(["| **Total** | **120** | **120** |", "", f"Turnout persistence baseline: **{report['turnout']['formatted']}%**, within the configured form bounds.", "",
                  "Empirical L1 minimizes disagreement with these polls, not validated error against the future election. Neither column is a final submission recommendation.", "", "## Sources", ""])
    lines.extend(f"- {p['published_on']} [{p['publisher']}]({p['source_url']}) ({p['pollster_group']})" for p in report["selected_polls"])
    lines.extend(["", "## Limitations", ""] + [f"- {item}" for item in report["limitations"]])
    lines.extend(["", "Detailed input/code hashes, method diagnostics, and leave-one-group-out results are in `baseline.json`.", ""])
    (output_dir / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "output/baseline")
    args = parser.parse_args()
    report = build_report()
    write_report(report, args.out_dir)
    print(f"Generated {report['poll_count']}-group preliminary baselines in {args.out_dir}")


if __name__ == "__main__":
    main()
