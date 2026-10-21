"""Check decision arithmetic, source selection, and real submission boundaries."""

import itertools
import unittest

from scripts.baseline import (ROOT, build_report, l1_consensus, load_json,
                              poll_vector, rounded_mean, select_polls, validate_forecast)


class DecisionTests(unittest.TestCase):
    def test_l1_matches_brute_force_when_marginal_medians_do_not_sum_to_total(self):
        scenarios = [[4, 0, 0], [0, 4, 0], [0, 0, 4]]
        answer = l1_consensus(scenarios, 4)
        def loss(x):
            return sum(abs(a-b) for row in scenarios for a,b in zip(x,row))
        possible = [v for v in itertools.product(range(5), repeat=3) if sum(v) == 4]
        self.assertEqual(loss(answer), min(map(loss, possible)))
        self.assertEqual(sum(answer), 4)

    def test_l1_is_deterministic_on_ties_and_not_worse_than_mean_for_its_objective(self):
        rows = [[4, 0, 0], [0, 2, 2]]
        answer = l1_consensus(rows, 4)
        self.assertEqual(answer, l1_consensus(list(reversed(rows)), 4))
        def loss(x):
            return sum(abs(a-b) for row in rows for a,b in zip(x,row))
        self.assertLessEqual(loss(answer), loss(rounded_mean(rows, 4)))

    def test_invalid_scenarios_are_not_silently_normalized(self):
        for rows in ([[1, 1]], [[True, 3]], [[1.5, 2.5]], [[-1, 5]], []):
            with self.subTest(rows=rows), self.assertRaises(ValueError):
                l1_consensus(rows, 4)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = load_json(ROOT / "config/submission-fields.json")
        self.seats = dict.fromkeys([f["id"] for f in self.contract["seat_fields"]], 0)
        self.seats["likud"] = 120

    def test_inclusive_turnout_bounds_and_nonfinite_rejection(self):
        for value in (40, 40.0, 70.63, 100.0):
            validate_forecast(self.seats, value, self.contract)
        for value in (39.99, 100.01, float("nan"), float("inf"), True, "70.63"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_forecast(self.seats, value, self.contract)

    def test_incomplete_or_invalid_seats_rejected(self):
        for change in ({"likud":119}, {"likud":120.0}, {"likud":True}, {"blue_and_white":-1}):
            bad = self.seats | change
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_forecast(bad, 70, self.contract)
        del self.seats["blue_and_white"]
        with self.assertRaises(ValueError):
            validate_forecast(self.seats, 70, self.contract)

    def test_mapping_aggregates_allocated_other_seats_and_rejects_incomplete_poll(self):
        mapping = load_json(ROOT / "config/poll-mappings.json")
        poll = {"seat_projection_complete":True, "reported_seats":{"joint_list":10,"likud":100,"other_a":5,"other_b":5}}
        vector = poll_vector(poll, self.contract, mapping)
        ids = [f["id"] for f in self.contract["seat_fields"]]
        self.assertEqual(vector[ids.index("hadash_taal")], 10)
        self.assertEqual(vector[ids.index("other_qualifying_lists")], 10)
        poll["reported_seats"]["likud"] = 99
        with self.assertRaises(ValueError):
            poll_vector(poll, self.contract, mapping)


class SelectionTests(unittest.TestCase):
    def test_latest_group_dedup_and_future_revision_exclusion(self):
        def poll(identifier, group, published, **extra):
            return {"id":identifier,"pollster_group":group,"published_on":published,**extra}
        rows = [poll("old","same","2026-10-14"), poll("new","same","2026-10-20"),
                poll("future","second","2026-10-22"),
                poll("revised","third","2026-10-19",source_updated_on="2026-10-22")]
        selected, rejected = select_polls(rows, "2026-10-21", 14)
        self.assertEqual([p["id"] for p in selected], ["new"])
        self.assertEqual(len(rejected), 3)

    def test_same_group_same_day_needs_explicit_resolution(self):
        row = {"id":"one","pollster_group":"g","published_on":"2026-10-20"}
        with self.assertRaises(ValueError):
            select_polls([row, row | {"id":"two"}], "2026-10-21", 14)

    def test_checked_in_data_runs_with_unique_groups_and_form_valid_outputs(self):
        report = build_report()
        groups = [p["pollster_group"] for p in report["selected_polls"]]
        self.assertEqual(len(groups), len(set(groups)))
        self.assertIn("superseded_within_pollster_group", [p["reason"] for p in report["excluded_or_archived"]])
        contract = load_json(ROOT / "config/submission-fields.json")
        for method in report["methods"].values():
            validate_forecast(method["seats"], report["turnout"]["prediction_pct"], contract)


if __name__ == "__main__":
    unittest.main()
