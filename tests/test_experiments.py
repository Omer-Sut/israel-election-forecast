"""Boundary tests for the separate optional experiment environment."""

import copy
import importlib.util
import os
import unittest

from scripts.baseline import ROOT, load_json
from scripts.experiments import (build_case, candidate, evaluate_cases, fit_ensemble_weights,
                                 reconcile, synthetic_smoke, training_arrays, validate_config)
from scripts.prepare_screening_panel import prepare


CONFIG = ROOT / "config/experiments.json"
SNAPSHOT = ROOT / "data/snapshots/historical-2026-10-21/polls-2021.json"


class ExperimentBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.config = load_json(CONFIG)
        self.snapshot = load_json(SNAPSHOT)

    def test_simplex_extremes_and_deterministic_ties(self):
        self.assertEqual(reconcile([-100, 200, 20]), [0, 120, 0])
        self.assertEqual(reconcile([40.5, 40.5, 39]), [41, 40, 39])
        for vector in ([0, 0, 0], [500, -10, 20, 3], [-1000] * 7):
            result = reconcile(vector)
            self.assertEqual(sum(result), 120)
            self.assertTrue(all(type(x) is int and x >= 0 for x in result))
        for vector in ([], [float("nan")], [float("inf")]):
            with self.assertRaises(ValueError):
                reconcile(vector)

    def test_future_polls_and_revisions_cannot_change_features(self):
        original = build_case(self.snapshot, "2021-03-17")
        changed = copy.deepcopy(self.snapshot)
        for poll in changed["polls"]:
            if poll["published_on"] > "2021-03-17":
                poll["reported_seats"] = {"unmapped_future_label": 120}
        later_revision = copy.deepcopy(self.snapshot["polls"][0])
        later_revision.update(id="future_revision", source_updated_on="2021-03-18",
                              reported_seats={"bad_future_label": 120})
        changed["polls"].append(later_revision)
        other = build_case(changed, "2021-03-17")
        for key in ("features", "anchor", "vectors", "history_vectors"):
            self.assertEqual(original[key], other[key])

    def test_syndicated_release_cannot_increase_group_weight(self):
        changed = copy.deepcopy(self.snapshot)
        duplicate = copy.deepcopy(changed["polls"][0])
        duplicate["id"] = "syndicated_copy"
        changed["polls"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "Ambiguous same-day"):
            build_case(changed, "2021-03-22")

    def test_bad_lineup_and_low_coverage_rejected(self):
        changed = copy.deepcopy(self.snapshot)
        for poll in changed["polls"]:
            poll["reported_seats"] = {"unmapped_party": 120}
        with self.assertRaisesRegex(ValueError, "known list IDs"):
            build_case(changed, "2021-03-22")
        with self.assertRaisesRegex(ValueError, "Insufficient"):
            build_case(self.snapshot, "2021-03-22", minimum_groups=20)

    def test_no_earlier_election_means_no_supervised_fit(self):
        case = build_case(self.snapshot, "2021-03-22")
        case["horizon_days"] = 1
        actual = dict(zip(case["ids"], reconcile(case["anchor"])))
        rows = evaluate_cases([case], {case["election_id"]: actual}, self.config)
        self.assertEqual(rows[0]["methods"]["ridge_1"]["status"], "insufficient_data")
        self.assertEqual(rows[0]["methods"]["ensemble_1"]["status"], "insufficient_data")

    def test_held_out_target_changes_scores_not_forecasts(self):
        case = build_case(self.snapshot, "2021-03-22")
        case["horizon_days"] = 1
        actual = dict(zip(case["ids"], reconcile(case["anchor"])))
        changed = dict(actual)
        keys = [k for k in case["ids"] if changed[k] > 1]
        changed[keys[0]] -= 1
        changed[keys[1]] += 1
        first = evaluate_cases([case], {case["election_id"]: actual}, self.config)[0]
        second = evaluate_cases([case], {case["election_id"]: changed}, self.config)[0]
        for name, entry in first["methods"].items():
            if "seats" in entry:
                self.assertEqual(entry["seats"], second["methods"][name]["seats"])
        self.assertNotEqual(first["methods"]["rounded_mean_reference"]["score"],
                            second["methods"]["rounded_mean_reference"]["score"])

    def test_training_weights_equalize_elections_and_missing_targets_fail(self):
        case = build_case(self.snapshot, "2021-03-22")
        case["actual"] = dict(zip(case["ids"], reconcile(case["anchor"])))
        later = copy.deepcopy(case)
        later["election_id"] = "another_election"
        _, _, weights = training_arrays([case, case, later])
        width = len(case["ids"])
        self.assertAlmostEqual(sum(weights[:2 * width]), sum(weights[2 * width:]))
        del later["actual"][later["ids"][0]]
        with self.assertRaisesRegex(ValueError, "coverage"):
            training_arrays([later])

    def test_all_untrained_configurations_obey_arithmetic(self):
        case = build_case(self.snapshot, "2021-03-22")
        for spec in self.config["models"]:
            if spec["family"] in ("recency", "dynamic"):
                raw = candidate(spec, case, [], self.config)
                self.assertEqual(sum(reconcile(raw)), 120)

    def test_configuration_rejects_duplicate_models_and_invalid_shrinkage(self):
        validate_config(self.config)
        self.config["models"].append(self.config["models"][0])
        with self.assertRaises(ValueError):
            validate_config(self.config)
        self.config = load_json(CONFIG)
        self.config["correction_fraction"] = 1.1
        with self.assertRaises(ValueError):
            validate_config(self.config)
        self.config = load_json(CONFIG)
        self.config["models"][0]["half_life_days"] = 0
        with self.assertRaisesRegex(ValueError, "positive"):
            validate_config(self.config)

    def test_six_election_panel_has_eligible_groups_and_preserved_source_dates(self):
        files = prepare()
        config = files["historical.json"]
        self.assertEqual(len(config["elections"]), 6)
        self.assertEqual(config["horizons_days"], [1])
        for name, snapshot in files.items():
            if not name.startswith("polls-"):
                continue
            from datetime import date, timedelta
            cutoff = (date.fromisoformat(snapshot["election_date"]) - timedelta(days=1)).isoformat()
            case = build_case(snapshot, cutoff)
            self.assertEqual(len(case["selected_polls"]), 3)
            self.assertEqual(sum(files["outcomes.json"]["elections"][snapshot["election_id"]]["seat_results"].values()), 120)
        april = files["polls-21.json"]["polls"]
        self.assertTrue(all(p["published_on"] == "2019-04-05" for p in april))
        self.assertEqual(next(p for p in files["polls-23.json"]["polls"] if "103fm" in p["id"])["published_on"], "2020-02-26")
        # Distinct Arab alliances in April 2019 are not pooled into a Joint List alias.
        names = {r["id"] for r in files["polls-21.json"]["lists"]}
        self.assertIn("hadash_taal_2019apr", names)
        self.assertIn("raam_balad_2019apr", names)


HAS_DEPS = all(importlib.util.find_spec(p) for p in ("numpy", "scipy", "sklearn", "xgboost"))
if os.environ.get("REQUIRE_EXPERIMENT_DEPS") == "1" and not HAS_DEPS:
    raise RuntimeError("Cloud experiment tests require all locked scientific dependencies")


@unittest.skipUnless(HAS_DEPS, "Optional scientific environment: use the cloud screening workflow")
class ScientificExperimentTests(unittest.TestCase):
    def test_all_configs_and_learned_weights_are_exercised(self):
        result = synthetic_smoke(load_json(CONFIG))
        self.assertEqual(len(result["exercised_configurations"]), 20)
        for weights in result["optimized_ensemble_weights"].values():
            self.assertAlmostEqual(sum(weights.values()), 1)
            self.assertTrue(all(w >= -1e-9 for w in weights.values()))

    def test_ensemble_linear_program_responds_to_signal_and_penalty(self):
        records = [{"election_id": str(i), "ids": ["a", "b"], "actual": {"a": 60, "b": 60},
                    "candidates": {"good": [60, 60], "bad": [0, 120]}} for i in range(2)]
        fitted = fit_ensemble_weights(records, ["good", "bad"], 1)
        self.assertAlmostEqual(fitted[0], 1)
        shrunk = fit_ensemble_weights(records, ["good", "bad"], 1000)
        self.assertAlmostEqual(shrunk[0], 0.5)

    def test_supervised_target_and_future_features_do_not_leak(self):
        config = load_json(CONFIG)
        config["allow_one_election_diagnostic"] = True
        config["models"] = [m for m in config["models"] if m["family"] in ("ridge", "forest", "xgboost")]
        # No ensemble models here, but keep valid named members for the runner's OOF gate.
        config["ensemble_members"] = [m["id"] for m in config["models"][:1]]
        first = build_case(load_json(SNAPSHOT), "2021-03-22")
        second = build_case(load_json(ROOT / "data/snapshots/historical-2026-10-21/polls-2022.json"), "2022-10-31")
        for case in (first, second):
            case["horizon_days"] = 1
        actual = {c["election_id"]: dict(zip(c["ids"], reconcile(c["anchor"]))) for c in (first, second)}
        changed = copy.deepcopy(actual)
        changed[second["election_id"]] = dict(zip(second["ids"], [120] + [0] * (len(second["ids"]) - 1)))
        original = evaluate_cases([first, second], actual, config)
        alternate = evaluate_cases([first, second], changed, config)
        for name, entry in original[1]["methods"].items():
            self.assertEqual(entry["seats"], alternate[1]["methods"][name]["seats"])
        # Test inputs must not affect fitted scaler/model state or earlier predictions.
        altered_case = copy.deepcopy(second)
        altered_case["features"] = [[1000.0] * 8 for _ in second["ids"]]
        alternate = evaluate_cases([first, altered_case], actual, config)
        self.assertEqual(original[0], alternate[0])

    def test_real_comparison_has_all_models_and_only_earlier_ensemble_targets(self):
        from scripts.experiments import build_report
        report = build_report()
        comparison = [c for c in report["cases"] if c["evaluation_role"] == "comparison"]
        self.assertEqual(len(comparison), 2)
        self.assertEqual([len(c["training_elections"]) for c in comparison], [4, 5])
        for case in comparison:
            self.assertEqual(len(case["methods"]), 20)
            self.assertTrue(all("seats" in m for m in case["methods"].values()))
            for name in ("ensemble_1", "ensemble_5"):
                entry = case["methods"][name]
                self.assertEqual(entry["status"], "chronological_screen")
                self.assertNotIn(case["election_id"], entry["ensemble_fit_elections"])
                self.assertGreaterEqual(len(entry["ensemble_fit_elections"]), 2)
                self.assertAlmostEqual(sum(entry["ensemble_weights"].values()), 1)


if __name__ == "__main__":
    unittest.main()
