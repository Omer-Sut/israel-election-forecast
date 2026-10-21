"""Guard historical information boundaries, list identity, and genuine result scoring."""

import copy
import unittest
from unittest.mock import patch

from scripts.backtest import (METHODS, ROOT, build_report, forecast_case, historical_vector,
                              load_json, score_seats, turnout_prediction)


class HistoricalBacktestTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = load_json(ROOT / "data/snapshots/historical-2026-10-21/polls-2021.json")

    def test_later_releases_and_exit_polls_cannot_change_earlier_forecast(self):
        original = forecast_case(self.snapshot, "2021-03-17", 14, list(METHODS))
        changed = copy.deepcopy(self.snapshot)
        for poll in changed["polls"]:
            if poll["published_on"] > "2021-03-17":
                poll["reported_seats"] = {"likud_2021": 120}
        exit_poll = copy.deepcopy(changed["polls"][0])
        exit_poll.update(id="exit-poll-mislabeled-date", kind="exit_poll", published_on="2021-03-16")
        changed["polls"].append(exit_poll)
        answer = forecast_case(changed, "2021-03-17", 14, list(METHODS))
        self.assertEqual(answer["forecasts"], original["forecasts"])
        self.assertTrue(any(p["reason"] == "not_pre_election_poll" for p in answer["excluded_polls"]))
        self.assertEqual({p["published_on"] for p in answer["selected_polls"]},
                         {"2021-03-11", "2021-03-14", "2021-03-16"})

    def test_known_post_cutoff_revision_is_not_used(self):
        changed = copy.deepcopy(self.snapshot)
        changed["polls"][0]["source_updated_on"] = "2021-03-18"
        with self.assertRaisesRegex(ValueError, "Insufficient"):
            forecast_case(changed, "2021-03-17", 14, list(METHODS))

    def test_historical_aliases_are_not_silently_pooled_into_current_form(self):
        poll = {"seat_projection_complete": True, "reported_seats": {"joint_list_2021": 120}}
        with self.assertRaises(ValueError):
            historical_vector(poll, ["hadash_taal_2022"])
        self.assertEqual(historical_vector(poll, ["joint_list_2021"]), [120])
        mixed = copy.deepcopy(self.snapshot)
        mixed["polls"][0]["election_id"] = "knesset_25_2022"
        with self.assertRaisesRegex(ValueError, "mixed"):
            forecast_case(mixed, "2021-03-17", 14, list(METHODS))

    def test_scoring_matches_hand_calculated_reassignment_and_coverage(self):
        score = score_seats({"a": 120, "b": 0}, {"a": 118, "b": 2})
        self.assertEqual(score["total_absolute_seat_error"], 4)
        self.assertEqual(score["signed_error_by_list"], {"a": 2, "b": -2})
        self.assertEqual(score["representation_false_negatives"], ["b"])
        with self.assertRaises(ValueError):
            score_seats({"a": 120}, {"b": 120})

    def test_turnout_cannot_use_target_or_future_election(self):
        with self.assertRaises(ValueError):
            turnout_prediction({"election_date": "2022-11-01", "turnout_pct": 70.63}, "2021-03-17")
        with self.assertRaises(ValueError):
            turnout_prediction({"election_date": "2021-03-17", "turnout_pct": 70}, "2021-03-17")
        self.assertEqual(turnout_prediction({"election_date": "2020-03-02", "turnout_pct": 71.52},
                                            "2021-03-17"), 71.52)

    def test_outcomes_affect_scores_but_not_generated_forecasts(self):
        original = build_report()
        outcome_path = ROOT / "data/snapshots/historical-2026-10-21/outcomes.json"
        changed = copy.deepcopy(load_json(outcome_path))
        for election in changed["elections"].values():
            election["seat_results"] = dict.fromkeys(election["seat_results"], 0)
            election["seat_results"][next(iter(election["seat_results"]))] = 120
            election["turnout_pct"] = 50
        with patch("scripts.backtest.load_json", side_effect=lambda path: changed if path == outcome_path else load_json(path)):
            answer = build_report()
        for before, after in zip(original["cases"], answer["cases"]):
            self.assertEqual(before["forecasts"], after["forecasts"])
            self.assertEqual(before["turnout_prediction_pct"], after["turnout_prediction_pct"])
            self.assertNotEqual(before["scores"], after["scores"])
            self.assertNotEqual(before["turnout_absolute_error_pp"], after["turnout_absolute_error_pp"])

    def test_pilot_integrates_four_cases_but_only_two_election_outcomes(self):
        report = build_report()
        self.assertEqual(len(report["cases"]), 4)
        self.assertEqual(len({case["election_id"] for case in report["cases"]}), 2)
        for case in report["cases"]:
            self.assertEqual(case["poll_count"], 3)
            self.assertEqual(len({p["pollster_group"] for p in case["selected_polls"]}), 3)
            self.assertTrue(all(p["published_on"] <= case["cutoff"] for p in case["selected_polls"]))
            for method in case["forecasts"].values():
                self.assertEqual(sum(method.values()), 120)
        self.assertEqual([a["independent_elections_not_poll_count"] for a in report["aggregates_by_horizon"]], [2, 2])
        self.assertEqual([c["turnout_absolute_error_pp"] for c in report["cases"]], [4.08, 4.08, 3.19, 3.19])


if __name__ == "__main__":
    unittest.main()
