import tempfile
import unittest
from pathlib import Path

from scripts.baseline import ROOT, load_json
from scripts.experiments import build_case
from scripts.campaign_history import prepare_variants, VARIANTS


class CampaignHistoryTests(unittest.TestCase):
    def test_variants_change_only_declared_data_and_preserve_anchors(self):
        original = load_json(ROOT / "config/experiments.json")
        with tempfile.TemporaryDirectory(dir=ROOT) as folder:
            paths = prepare_variants(Path(folder))
            self.assertEqual(tuple(paths), VARIANTS)
            cases = {}
            for variant, config_path in paths.items():
                config = load_json(config_path)
                for field in ("models", "seed", "correction_fraction", "minimum_training_elections", "ensemble_members", "evaluation_elections"):
                    self.assertEqual(config[field], original[field])
                historical = load_json(ROOT / config["historical_config"])
                self.assertEqual(historical["horizons_days"], [1])
                cases[variant] = []
                for item in historical["elections"]:
                    snapshot = load_json(ROOT / item["polls_path"])
                    from datetime import date, timedelta
                    cutoff = (date.fromisoformat(snapshot["election_date"]) - timedelta(days=1)).isoformat()
                    cases[variant].append(build_case(snapshot, cutoff))
            for variant in VARIANTS:
                for ref, other in zip(cases["reference"], cases[variant]):
                    self.assertEqual(ref["anchor"], other["anchor"])
                    self.assertEqual([p["id"] for p in ref["selected_polls"]], [p["id"] for p in other["selected_polls"]])
            self.assertEqual([len(c["history"]) for c in cases["reference"]], [3, 3, 3, 3, 6, 6])
            self.assertEqual([len(c["history"]) for c in cases["expanded_history"]], [3, 4, 4, 4, 6, 6])
            self.assertEqual([c["features"][0][-1] for c in cases["expanded_history"]], [1, 0, 0, 0, 0, 0])
            ref_walla = next(p for p in cases["reference"][3]["history"] if p["id"] == "2020_walla_midgam_0226")
            alt_walla = next(p for p in cases["publication_age"][3]["history"] if p["id"] == ref_walla["id"])
            self.assertEqual(ref_walla["fieldwork_end"], "2020-02-17")
            self.assertNotIn("fieldwork_end", alt_walla)
            self.assertEqual(alt_walla["original_printed_fieldwork"]["fieldwork_end"], "2020-02-17")


if __name__ == "__main__":
    unittest.main()
