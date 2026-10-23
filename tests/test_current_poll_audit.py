import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import baseline
import current_poll_audit as audit


class CurrentAuditTests(unittest.TestCase):
    def test_archives_preserved_and_selected_main_lineups_valid(self):
        new = baseline.load_json(baseline.ROOT / "data/snapshots/polls-2026-10-23.json")
        old = baseline.load_json(baseline.ROOT / "data/snapshots/polls-2026-10-21.json")
        self.assertEqual(new["polls"][:len(old["polls"])], old["polls"])
        selected, _ = baseline.select_polls(new["polls"], "2026-10-23", 14)
        self.assertEqual(len(selected), 5)
        self.assertEqual(sorted(p["sample_size"] for p in selected), [500, 505, 601, 1084, 7937])
        for poll in selected:
            self.assertEqual(sum(poll["reported_seats"].values()), 120)
        n12 = next(p for p in selected if p["publisher"] == "N12")
        self.assertEqual(n12["reported_seats"].get("amcha_yisrael"), 4)
        self.assertNotIn("reservists_economic", n12["reported_seats"])

    def test_current_article_versions_do_not_claim_earlier_availability(self):
        snapshot = baseline.load_json(baseline.ROOT / "data/snapshots/polls-2026-10-23.json")
        selected, rejected = baseline.select_polls(snapshot["polls"], "2026-10-22", 14)
        self.assertTrue(all(p["reviewed_on"] == "2026-10-23" for p in snapshot["polls"][6:]))
        self.assertFalse(set(p["id"] for p in selected) & set(p["id"] for p in snapshot["polls"][6:]))
        self.assertEqual(sum(r["reason"] == "not_available_by_cutoff" for r in rejected), 4)

    def test_missing_percent_zero_seats_and_positive_percent_distinct(self):
        report = audit.build_audit()
        rows = {(r["poll_id"], r["party"]): r for r in report["threshold_measurements"]}
        bw = rows[("n12-midgam-2026-10-21", "blue_and_white")]
        self.assertIsNone(bw["reported_vote_pct"])
        self.assertEqual(bw["published_seats"], 0)
        reservists = rows[("c13-consortium-2026-10-21", "reservists_economic")]
        self.assertEqual(reservists["reported_vote_pct"], 3.6)
        self.assertEqual(reservists["distance_from_threshold_pp"], .35)
        self.assertTrue(all(r["crossing_probability"] is None for r in rows.values()))
        for method in report["methods"].values():
            baseline.validate_forecast(method["seats"], report["turnout"]["prediction_pct"],
                                       baseline.load_json(baseline.ROOT / "config/submission-fields.json"))

    def test_conflicting_threshold_transcription_rejected(self):
        poll = copy.deepcopy(baseline.load_json(baseline.ROOT / "data/snapshots/polls-2026-10-23.json")["polls"][-1])
        poll["reported_below_threshold_pct"]["amcha_yisrael"] = 3.3
        with self.assertRaisesRegex(ValueError, "conflicts"):
            audit.threshold_rows([poll], 3.25)


if __name__ == "__main__":
    unittest.main()
