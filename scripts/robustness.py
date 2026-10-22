"""E004: bounded correction/forest-seed sensitivities; no model selection."""
from __future__ import annotations

import copy
import csv
import gzip
import hashlib
import html
import json
import math
import os
from pathlib import Path
import statistics
import sys
import time

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.baseline import ROOT, load_json
from scripts.campaign_history import prepare_variants, write_json
from scripts.experiments import FEATURES, build_report, reconcile, supervised_prediction
from scripts.backtest import score_seats

FRACTIONS = (0.0, 0.1, 0.25, 0.5, 1.0)
VARIANTS = ("reference", "expanded_history")
SEEDS = tuple(20261021 + i for i in range(20))
COLORS = ("#2463a6", "#b65f00", "#008060", "#ac328a", "#6a51a3", "#666666")


def project(values):
    """Continuous Euclidean projection onto the nonnegative sum-120 simplex."""
    if not values or not all(math.isfinite(x) for x in values):
        raise ValueError("Finite nonempty values required")
    running, theta = 0.0, None
    for n, x in enumerate(sorted(values, reverse=True), 1):
        running += x
        trial = (running - 120) / n
        if x > trial:
            theta = trial
    if theta is None:
        raise ValueError("Invalid projection")
    result = [max(x - theta, 0.0) for x in values]
    if abs(sum(result) - 120) > 1e-8:
        raise ValueError("Projection total failure")
    return result


def evaluate_fraction(anchor, raw, actual, fraction):
    if len(anchor) != len(raw) or len(raw) != len(actual):
        raise ValueError("Vector size mismatch")
    if not 0 <= fraction <= 1:
        raise ValueError("Invalid correction fraction")
    mixed = [a + fraction * (r - a) for a, r in zip(anchor, raw)]
    continuous, integer = project(mixed), reconcile(mixed)
    return continuous, integer, sum(abs(a - b) for a, b in zip(continuous, actual)), sum(abs(a - b) for a, b in zip(integer, actual))


def collect(report, variant, seed, targets):
    scores, predictions, missing = [], [], []
    for case in report["cases"]:
        ids = case["ids"]
        actual = [targets[case["election_id"]]["seat_results"][key] for key in ids]
        base = case["methods"]["rounded_mean_reference"]
        base_cont = sum(abs(a - b) for a, b in zip(project(case["anchor"]), actual))
        for name, entry in case["methods"].items():
            if "seats" not in entry:
                missing.append(dict(variant=variant, seed=seed, election=case["election_id"], method=name, status=entry["status"]))
                continue
            if "continuous_unshrunk" not in entry:
                continue  # Both reference vectors/scores are preserved in every raw report.
            for fraction in FRACTIONS:
                continuous, integer, ce, ie = evaluate_fraction(case["anchor"], entry["continuous_unshrunk"], actual, fraction)
                if fraction == 0.25 and integer != [entry["seats"][key] for key in ids]:
                    raise ValueError("25% reconstruction disagrees with fitted pipeline")
                if fraction == 0 and integer != reconcile(case["anchor"]):
                    raise ValueError("0% does not reproduce pipeline anchor")
                row = dict(variant=variant, seed=seed, election=case["election_id"], cutoff=case["cutoff"],
                           role=case["evaluation_role"], method=name, fraction=fraction, continuous_error=ce,
                           integer_error=ie, reference_continuous_error=base_cont,
                           reference_integer_error=base["score"]["total_absolute_seat_error"],
                           l1_reference_integer_error=case["methods"]["empirical_l1_consensus"]["score"]["total_absolute_seat_error"],
                           same_vector_as_reference=integer == [base["seats"][key] for key in ids],
                           zero_fraction_exact_reference_tie_difference=reconcile(case["anchor"]) != [base["seats"][key] for key in ids],
                           movement_from_reference=sum(abs(x - base["seats"][key]) for key, x in zip(ids, integer)))
                scores.append(row)
                for key, cp, ip, truth in zip(ids, continuous, integer, actual):
                    predictions.append(dict(variant=variant, seed=seed, election=case["election_id"], method=name,
                                            fraction=fraction, list_id=key, continuous=cp, seats=ip, actual=truth))
    return scores, predictions, missing


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"Empty output: {path}")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def forest_report(base, config, targets, seed):
    """Reuse audited features, but refit forests with unchanged chronological weights."""
    start = time.perf_counter()
    report = copy.deepcopy(base)
    report["configuration"] = copy.deepcopy(config)
    report["configuration"]["seed"] = seed
    specs = [m for m in config["models"] if m["family"] == "forest"]
    report["configuration"]["models"] = specs
    report["configuration"]["ensemble_members"] = []
    # Not a build_report configuration: this saved report is explicitly forest-only.
    report["smoke"] = {"status": "Base full-grid smoke already passed; only forest seeds refitted here"}
    cases = [dict(c, features=[[c["features_by_list"][key][f] for f in FEATURES] for key in c["ids"]]) for c in base["cases"]]
    for row, case in zip(report["cases"], cases):
        training = [dict(c, actual=targets[c["election_id"]]["seat_results"]) for c in cases
                    if c["election_date"] < case["cutoff"] and c["election_id"] != case["election_id"]]
        train_ids = sorted({c["election_id"] for c in training})
        if train_ids != row["training_elections"]:
            raise ValueError("Forest refit changed chronological training set")
        row["methods"] = {name: entry for name, entry in row["methods"].items()
                          if name in ("rounded_mean_reference", "empirical_l1_consensus")}
        for spec in specs:
            if len(train_ids) < config["minimum_training_elections"]:
                row["methods"][spec["id"]] = dict(status="insufficient_data")
                continue
            raw = supervised_prediction(spec, training, case, seed)
            mixed = [a + .25*(b-a) for a,b in zip(case["anchor"],raw)]
            seats = dict(zip(case["ids"], reconcile(mixed)))
            row["methods"][spec["id"]] = dict(configuration=spec, status="chronological_screen",
                    training_elections=train_ids, continuous_unshrunk=raw, continuous_shrunk=mixed,
                    seats=seats, score=score_seats(seats, targets[case["election_id"]]["seat_results"]))
    report["runtime_seconds"] = round(time.perf_counter()-start, 3)
    return report


def svg_panels(path, panels, title, subtitle):
    """Small multiples with shared error scale; solid=continuous, dashed=integer."""
    width, panel_w, panel_h = 1200, 400, 245
    height = 110 + math.ceil(len(panels) / 3) * panel_h
    ymax = max(5, math.ceil(max((y for _, series in panels for _, points, _, _ in series for _, y in points), default=5) / 5) * 5)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
           f'<title>{html.escape(title)}</title><rect width="100%" height="100%" fill="white"/>',
           '<g font-family="sans-serif" font-size="12" fill="#222">',
           f'<text x="20" y="25" font-size="21">{html.escape(title)}</text>',
           f'<text x="20" y="48">{html.escape(subtitle)}</text>']
    for i, (label, series) in enumerate(panels):
        ox, oy = (i % 3) * panel_w + 48, (i // 3) * panel_h + 120
        out.append(f'<text x="{ox}" y="{oy-20}" font-size="15">{html.escape(label)}</text>')
        for tick in range(0, ymax + 1, max(1, ymax // 4)):
            y = oy + 145 * (1 - tick / ymax)
            out += [f'<path d="M {ox} {y} h 320" stroke="#ddd"/>', f'<text x="{ox-30}" y="{y+4}">{tick}</text>']
        for fraction in FRACTIONS:
            x = ox + fraction * 320
            out.append(f'<text x="{x-8}" y="{oy+165}">{fraction:g}</text>')
        for text_label, points, color, dashed in series:
            coords = " ".join(f"{ox+x*320:.2f},{oy+145*(1-y/ymax):.2f}" for x, y in points)
            dash = ' stroke-dasharray="5 4"' if dashed else ""
            out.append(f'<polyline points="{coords}" fill="none" stroke="{color}" stroke-width="1.8"{dash}/>')
            for x, y in points:
                out.append(f'<circle cx="{ox+x*320:.2f}" cy="{oy+145*(1-y/ymax):.2f}" r="2" fill="{color}"><title>{html.escape(text_label)}: {y:.3f}</title></circle>')
        out.append(f'<text x="{ox+95}" y="{oy+188}">Correction fraction (0 = mean)</text>')
    out.append('</g></svg>')
    path.write_text("\n".join(out), encoding="utf-8")


def render(out, scores):
    images = []
    for variant in VARIANTS:
        rows = [r for r in scores if r["variant"] == variant and r["seed"] == SEEDS[0]]
        elections = sorted({r["election"] for r in rows})
        panels = []
        for method in dict.fromkeys(r["method"] for r in rows):
            series = []
            for index, election in enumerate(elections):
                subset = sorted([r for r in rows if r["method"] == method and r["election"] == election], key=lambda r: r["fraction"])
                if not subset:
                    continue
                for metric, dashed in (("continuous_error", False), ("integer_error", True)):
                    series.append((election, [(r["fraction"], r[metric]) for r in subset], COLORS[index], dashed))
            panels.append((method, series))
        name = f"{variant}-correction.svg"
        legend = "; ".join(f"{e}: {COLORS[i]}" for i, e in enumerate(elections))
        svg_panels(out / name, panels, f"E004 {variant}: absolute seat error", "Solid = projected continuous; dashed = rounded. Lower is better. Shared vertical scale.")
        images.append((name, legend))
        panels = []
        for method in sorted({r["method"] for r in rows if r["method"].startswith("forest_")}):
            for fraction in (0.25, 1.0):
                series = []
                for index, election in enumerate(elections):
                    subset = sorted([r for r in scores if r["variant"] == variant and r["method"] == method and r["election"] == election and r["fraction"] == fraction], key=lambda r: r["seed"])
                    if not subset:
                        continue
                    for metric, dashed in (("continuous_error", False), ("integer_error", True)):
                        series.append((election, [((r["seed"]-SEEDS[0])/19, r[metric]) for r in subset], COLORS[index], dashed))
                panels.append((f"{method}, correction {fraction:g}", series))
        name = f"{variant}-forest-seeds.svg"
        svg_panels(out / name, panels, f"E004 {variant}: forest seed stability", "Solid = projected continuous; dashed = rounded. X: seed index scaled 0-1 (20 seeds), not correction.")
        # Correct the generic x-axis label for this seed plot.
        p = out / name
        p.write_text(p.read_text(encoding="utf-8").replace("Correction fraction (0 = mean)", "Seed index (0 = first, 1 = last)"), encoding="utf-8")
        images.append((name, legend))
    page = ['<!doctype html><meta charset="utf-8"><title>E004 robustness</title>',
            '<style>body{font:16px sans-serif;max-width:1400px;margin:30px auto;padding:15px}img{width:100%}p{line-height:1.5}</style>',
            '<h1>E004: correction and forest-seed sensitivity</h1>',
            '<p>Previously inspected outcomes, not a blind holdout. Missing early fits stay missing. Colors identify elections; party rows, seeds and correction settings are not independent elections. No model is selected. Lower error is better. At zero correction, floating-point pipeline rounding can break ties differently from the exact-integer mean reference; CSV flags preserve that difference. No frozen rounding code is changed.</p>',
            '<p><a href="summary.md">Summary</a> | <a href="scores.csv">All scores</a> | <a href="seed-summary.csv">Seed ranges</a> | <a href="predictions.csv">Per-list predictions</a> | <a href="manifest.json">Configuration/provenance</a></p>']
    for name, legend in images:
        page += [f'<h2>{html.escape(name)}</h2><p>{html.escape(legend)}</p><img src="{name}" alt="{html.escape(name)}">']
    (out / "index.html").write_text("\n".join(page), encoding="utf-8")


def main():
    start = time.perf_counter()
    out = ROOT / "output/robustness"
    out.mkdir(parents=True, exist_ok=True)
    configs = prepare_variants(out / "inputs")
    scores, predictions, missing, provenance = [], [], [], []
    for variant in VARIANTS:
        config_path = configs[variant]
        config = load_json(config_path)
        history = load_json(ROOT / config["historical_config"])
        targets = load_json(ROOT / history["outcomes_path"])["elections"]
        # Base fit retains full grid and learned ensembles. Additional fits only vary forests.
        base = build_report(config_path)
        repeat = build_report(config_path)
        if base["cases"] != repeat["cases"]:
            raise ValueError("Base predictions not deterministic")
        check = forest_report(base, config, targets, SEEDS[0])
        for original, refit in zip(base["cases"], check["cases"]):
            for spec in config["models"]:
                if spec["family"] == "forest" and "seats" in original["methods"][spec["id"]]:
                    if original["methods"][spec["id"]]["continuous_unshrunk"] != refit["methods"][spec["id"]]["continuous_unshrunk"]:
                        raise ValueError("Forest-only refit differs from full-grid adapter")
        for seed in SEEDS:
            if seed == SEEDS[0]:
                report = base
            else:
                report = forest_report(base, config, targets, seed)
            a, b, c = collect(report, variant, seed, targets)
            scores.extend(a)
            predictions.extend(b)
            missing.extend(c)
            provenance.append(dict(variant=variant, seed=seed, runtime_seconds=report["runtime_seconds"],
                                   input_and_code_sha256=report["input_and_code_sha256"]))
            folder = out / "raw"
            folder.mkdir(exist_ok=True)
            with gzip.open(folder / f"{variant}-{seed}.json.gz", "wt", encoding="utf-8") as stream:
                json.dump(report, stream, ensure_ascii=False, allow_nan=False)
            print(f"{variant} seed {seed}: {len(a)} score rows", flush=True)
    write_csv(out / "scores.csv", scores)
    write_csv(out / "predictions.csv", predictions)
    write_json(out / "unavailable.json", missing)
    groups = {}
    for row in scores:
        if row["method"].startswith("forest_"):
            key = (row["variant"], row["election"], row["method"], row["fraction"])
            groups.setdefault(key, []).append(row)
    ranges = []
    for (variant, election, method, fraction), rows in groups.items():
        if len(rows) != 20:
            raise ValueError("Incomplete forest seed group")
        row = dict(variant=variant, election=election, method=method, fraction=fraction, seeds=len(rows))
        for metric in ("continuous_error", "integer_error"):
            vals = [r[metric] for r in rows]
            row.update({f"{metric}_min": min(vals), f"{metric}_median": statistics.median(vals), f"{metric}_max": max(vals)})
        row["same_vector_as_reference_fraction"] = sum(r["same_vector_as_reference"] for r in rows) / len(rows)
        ranges.append(row)
    write_csv(out / "seed-summary.csv", ranges)
    render(out, scores)
    manifest = dict(experiment="E004", fractions=FRACTIONS, variants=VARIANTS, seeds=SEEDS,
                    code_commit=os.environ.get("GITHUB_SHA", "local_unrecorded"),
                    task="Descriptive robustness only; no model or correction selection, no current forecast changes",
                    seed_policy="20 forest seeds; full fixed grid/ensembles at original seed only; no ensemble seed sensitivity claimed",
                    source_policy="Original and expanded history with original printed Walla age; metadata sensitivity remains E003",
                    provenance=provenance, runtime_seconds=round(time.perf_counter()-start, 3),
                    script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    write_json(out / "manifest.json", manifest)
    lines = ["# E004 robustness batch", "", "Completed all two data variants, five correction strengths and 20 forest seeds. Base-grid prediction repeats matched exactly.",
             "", "Open index.html for correction and seed plots; scores.csv contains every eligible fold/configuration. seed-summary.csv gives forest min/median/max; unavailable.json preserves early missing fits. raw/ contains all fitted reports and provenance.",
             "", "0% reproduces pipeline reconciliation of the anchor; 25% reproduces the fitted pipeline. The exact-integer mean reference can break fractional ties differently from floating-point pipeline rounding even at 0%. This is flagged, not silently corrected; both controls/scores remain available. Continuous predictions are projected to nonnegative sum 120 before scoring. Integer seats use unchanged reconciliation.",
             "", "## Reference ties at the original seed and 25% correction", ""]
    for variant in VARIANTS:
        for election in sorted({r["election"] for r in scores}):
            rows = [r for r in scores if r["variant"] == variant and r["election"] == election and r["seed"] == SEEDS[0] and r["fraction"] == .25]
            if rows:
                same = sum(r["same_vector_as_reference"] for r in rows)
                better = sum(r["integer_error"] < r["reference_integer_error"] for r in rows)
                cont = sum(r["continuous_error"] < r["reference_continuous_error"] - 1e-9 for r in rows)
                lines.append(f"- {variant}, {election}: {same}/{len(rows)} identical to mean vector; {better} improve integer error; {cont} improve continuous error.")
                if rows[0]["zero_fraction_exact_reference_tie_difference"]:
                    zero = next(r for r in scores if r["variant"] == variant and r["election"] == election and r["fraction"] == 0)
                    lines.append(f"  - Rounding tie caveat: zero-correction pipeline error={zero['integer_error']}, exact mean reference error={zero['reference_integer_error']}; vectors differ before any model correction.")
    lines += ["", "These are previously inspected election outcomes, not independent new tests. Earlier OOF outcomes also train later ensembles. Seeds measure algorithmic sensitivity, not predictive uncertainty. No selection by the best seed/fraction, no L0/threshold mechanism, no turnout changes and no current forecast change.",
              "", f"Compute runtime: {manifest['runtime_seconds']} seconds. Commit: {manifest['code_commit']}."]
    (out / "summary.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("\n".join(lines), flush=True)


if __name__ == "__main__":
    main()

