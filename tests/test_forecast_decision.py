import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from scripts import forecast_decision as fd


class ForecastDecisionTests(unittest.TestCase):
    def test_approved_turnout_changes_no_seats_or_historical_reference(self):
        old = fd.ROOT/'reports/review-package-2026-10-24/forecast.json'
        before = hashlib.sha256(old.read_bytes()).hexdigest()
        package = fd.build()
        self.assertEqual(package['forecast']['seats'], package['previous_forecast']['seats'])
        self.assertEqual(package['forecast']['national_turnout_pct'], '69.86')
        self.assertAlmostEqual(package['turnout']['unrounded_pct'], (71.52+67.44+70.63)/3)
        self.assertEqual([r['knesset'] for r in package['turnout']['input_elections']], [23,24,25])
        self.assertEqual(hashlib.sha256(old.read_bytes()).hexdigest(), before)
        self.assertFalse(package['submitted'])
        self.assertFalse(package['source_freeze_complete'])

    def test_export_consistent_method_and_all_alternatives(self):
        package = fd.build()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp); fd.write(package, out)
            forecast = json.loads((out/'forecast.json').read_text(encoding='utf-8'))
            self.assertEqual(forecast['national_turnout_pct'], '69.86')
            method = (out/'method-description.txt').read_text(encoding='utf-8')
            self.assertIn('arithmetic mean', method)
            self.assertNotIn('as a persistence estimate', method)
            self.assertLessEqual(len(method.split()), 500)
            for scenario in package['reservists_scenarios'].values():
                self.assertEqual(sum(scenario['seats'].values()), 120)
                self.assertFalse(any(v in (1,2) for v in scenario['seats'].values()))
            self.assertIn('69.86%', (out/'review.md').read_text(encoding='utf-8'))
            self.assertEqual((out/'scenario-comparison.csv').read_bytes(),
                (fd.ROOT/'reports/review-package-2026-10-24/scenario-comparison.csv').read_bytes())
