"""Reproduce a separate current-source/threshold audit; no fitted model selection."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from html import escape
from pathlib import Path

import baseline

ROOT = baseline.ROOT
CONFIG = ROOT / "config/current-poll-audit.json"


def threshold_rows(polls, threshold):
    """Keep published partial percentages, complete-table seat zeros and missing distinct."""
    parties = sorted({"amcha_yisrael", "reservists_economic", "blue_and_white"} |
                     {key for poll in polls for key in poll.get("reported_below_threshold_pct", {})} |
                     {key for poll in polls for key in poll.get("reported_above_threshold_pct", {})})
    rows = []
    for poll in polls:
        if not poll.get("seat_projection_complete") or sum(poll["reported_seats"].values()) != 120:
            raise ValueError("Threshold seat diagnostics require a complete allocation")
        below = poll.get("reported_below_threshold_pct", {})
        above = poll.get("reported_above_threshold_pct", {})
        if set(below) & set(above):
            raise ValueError("Percentage appears in both below/above categories")
        for party in parties:
            pct = below.get(party, above.get(party))
            seats = poll["reported_seats"].get(party, 0)
            if pct is not None:
                if type(pct) not in (int, float) or not math.isfinite(pct) or not 0 <= pct <= 100:
                    raise ValueError("Invalid published percent")
                if (party in below and (pct >= threshold or seats > 0) or
                        party in above and (pct < threshold or seats == 0)):
                    raise ValueError("Published threshold category conflicts with seats/percentage")
            rows.append({"poll_id": poll["id"], "publisher": poll["publisher"],
                         "party": party, "reported_vote_pct": pct,
                         "distance_from_threshold_pp": None if pct is None else round(pct - threshold, 6),
                         "published_seats": seats,
                         "seat_status": "positive_allocation" if seats else "zero_in_complete_allocation",
                         "crossing_probability": None})
    return rows


def build_audit():
    config = baseline.load_json(CONFIG)
    snapshot_path = ROOT / config["poll_snapshot"]
    snapshot = baseline.load_json(snapshot_path)
    report = baseline.build_report(CONFIG)
    selected, _ = baseline.select_polls(snapshot["polls"], config["as_of_date"], config["poll_window_days"])
    contract = baseline.load_json(ROOT / "config/submission-fields.json")
    mapping = baseline.load_json(ROOT / "config/poll-mappings.json")
    fields = [field["id"] for field in contract["seat_fields"]]
    vectors = [baseline.poll_vector(poll, contract, mapping) for poll in selected]
    previous = baseline.load_json(ROOT / "reports/baseline-2026-10-21/baseline.json")
    report["continuous_mean_seats"] = dict(zip(fields, [sum(col) / len(vectors) for col in zip(*vectors)]))
    report["change_from_october21"] = {
        name: {key: method["seats"][key] - previous["methods"][name]["seats"][key] for key in fields}
        for name, method in report["methods"].items()}
    report["rule_and_eligibility_audit"] = snapshot["rule_and_eligibility_audit"]
    report["threshold_measurements"] = threshold_rows(selected, snapshot["rule_and_eligibility_audit"]["threshold_pct"])
    report["not_ingested"] = snapshot["not_ingested"]
    report["selected_metadata"] = [{key: poll.get(key) for key in
                                  ("id", "sample_size", "fieldwork_start", "fieldwork_end", "source_updated_on", "audit")}
                                 for poll in selected]
    report["limitations"] = [
        "Bounded original-source update, not all final Friday polls. New Maariv release remains unaudited; Lazar anchor is October 20 Walla.",
        "Four newer releases are current article versions reviewed October 23; conservative update dates prevent claiming earlier historical availability.",
        "Equal-group weights retained; sample sizes do not establish independence or remove systematic bias.",
        "Previously inspected historical backtests are limited retrospective evidence; current consensus disagreement is not future accuracy.",
        "Published partial vote percentages cannot supply a full vote-share allocation or calibrated threshold-crossing probability.",
        "Arithmetic averages/consensus can give small positive seats to borderline lists; no official electoral feasibility allocator implemented.",
        "Official current eligibility, withdrawal notice and operative publication restriction remain unverified; indexed official threshold text supports 3.25%.",
        "Joint List/form mapping is the existing user-accepted slot assumption, not organizer verification or historical identity equivalence.",
        "No learned correction, poll-quality weighting, withdrawal redistribution or turnout-intention adjustment adopted. Turnout remains 70.63% persistence.",
    ]
    for path in (Path(__file__), ROOT / "reports/baseline-2026-10-21/baseline.json"):
        report["input_and_code_sha256"][path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return report


def threshold_svg(report):
    rows = [r for r in report["threshold_measurements"] if r["party"] in ("amcha_yisrael", "reservists_economic")]
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="980" height="590" viewBox="0 0 980 590">',
           '<rect width="980" height="590" fill="white"/>',
           '<g font-family="Arial,sans-serif" fill="#172b4d">',
           '<text x="28" y="30" font-size="21">Published borderline-list support: five audited groups</text>',
           '<text x="28" y="55" font-size="14">Points = reported vote percent; missing stays unknown. Right column = published seats.</text>']
    x = lambda pct: 320 + pct * 125
    for tick in range(5):
        svg.extend([f'<line x1="{x(tick)}" x2="{x(tick)}" y1="85" y2="530" stroke="#e2e8f0"/>',
                    f'<text x="{x(tick)}" y="555" font-size="13">{tick}%</text>'])
    cutoff = report["rule_and_eligibility_audit"]["threshold_pct"]
    svg.extend([f'<line x1="{x(cutoff)}" x2="{x(cutoff)}" y1="80" y2="530" stroke="#a33" stroke-dasharray="6 4"/>',
                f'<text x="{x(cutoff)-15}" y="75" font-size="13">{cutoff}%</text>',
                '<text x="870" y="75" font-size="14">Seats</text>'])
    for i, row in enumerate(rows):
        y = 105 + i * 44
        party = "Amcha" if row["party"] == "amcha_yisrael" else "Reservists"
        label = escape(row["publisher"] + " / " + party)
        svg.append(f'<text x="28" y="{y+5}" font-size="14">{label}</text>')
        pct = row["reported_vote_pct"]
        if pct is None:
            svg.append(f'<text x="330" y="{y+5}" fill="#64748b" font-size="14">percent unreported</text>')
        else:
            color = "#2878a0" if row["published_seats"] else "#a33"
            svg.extend([f'<circle cx="{x(pct)}" cy="{y}" r="6" fill="{color}"/>',
                        f'<text x="{x(pct)+10}" y="{y+5}" font-size="14">{pct:g}%</text>'])
        svg.append(f'<text x="890" y="{y+5}" font-size="14">{row["published_seats"]}</text>')
    svg.extend(['<text x="28" y="580" font-size="13">Source differences are descriptive; these are not confidence intervals or crossing probabilities.</text>', '</g></svg>'])
    return "\n".join(svg) + "\n"


def write_audit(report, out_dir):
    # Reuse the frozen serializer but replace its snapshot-specific limitations above.
    baseline.write_report(report, out_dir)
    (out_dir / "threshold-support.svg").write_text(threshold_svg(report), encoding="utf-8", newline="\n")
    lines = ["# Current poll audit - October 23", "", "Research update; neither column is a selected final forecast.", "",
             "![Published borderline support](threshold-support.svg)", "",
             "Four new original releases replace older anchors; October 20 Walla remains the fifth group. A newer Maariv release is a known collection gap.", "",
             "The two references still sum to 120 after rounding and pass every configured turnout/field check. Exact vectors, continuous means, changes from October 21, omission sensitivity and hashes are in baseline.json; source links and both seat tables are in summary.md.", "",
             "| Party | Continuous mean | Rounded mean | L1 consensus | Mean change since Oct 21 |", "| --- | ---: | ---: | ---: | ---: |"]
    contract = baseline.load_json(ROOT / "config/submission-fields.json")
    for field in contract["seat_fields"]:
        key = field["id"]
        lines.append(f"| {field['label_en']} | {report['continuous_mean_seats'][key]:.2f} | {report['methods']['rounded_mean_reference']['seats'][key]} | {report['methods']['empirical_l1_consensus']['seats'][key]} | {report['change_from_october21']['rounded_mean_reference'][key]:+d} |")
    lines.extend(["", "Amcha has seats in one selected release; Reservists in three. This frequency is not a calibrated election probability. Missing percentages stay null even when a complete table implies zero seats. Main-lineup observations are kept separate from N12's hypothetical withdrawal scenarios.", "",
                  "Averaging a zero-seat and a four-seat poll can produce one, two or three seats. That is an arithmetic point estimate, not proof of an attainable allocation. L0 feature regularization does not resolve this discontinuity. With partial percentages and no calibrated joint vote-share error model, forcing threshold outcomes now would add an unvalidated assumption.", "",
                  "Keep both references and the published measurements. Complete the final-source/official-lineup audit before choosing a submission vector; then assess any explicit threshold scenario adjustment against historical absolute seat error. No wider model sweep is justified by this update.", "",
                  "Official pages returned 403/geographic restriction; indexed CEC/Knesset text supports 3.25%, but current list eligibility, withdrawal notice, full allocator/agreements and operative blackout rules remain unverified. The competition PDF's Friday cutoff is retained as a document statement.", ""])
    (out_dir / "analysis.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=ROOT / "output/current-poll-audit")
    args = parser.parse_args()
    report = build_audit()
    write_audit(report, args.out_dir)
    # Small public report is recoverable from hosted logs as well as the artifact.
    print("E007_REPORT_JSON=" + json.dumps(report, ensure_ascii=False, separators=(",", ":")))
    print((args.out_dir / "analysis.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
