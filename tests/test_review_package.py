import json
from pathlib import Path
import tempfile
import unittest
from scripts import review_package


class ReviewPackageTests(unittest.TestCase):
    def test_reservists_scenarios_isolate_assumption_and_conserve_seats(self):
        package=review_package.build()
        self.assertEqual(package['reservists_scenarios']['3']['seats'],package['reference']['seats'])
        expected={'0':{'reservists_economic':-3,'likud':1,'united_torah_judaism':1,'raam':1},
                  '4':{'reservists_economic':1,'religious_zionism':-1}}
        for n,changes in expected.items():
            row=package['reservists_scenarios'][n]
            self.assertEqual({k:v for k,v in row['delta_from_reference'].items() if v},changes)
            self.assertEqual(sum(row['seats'].values()),120)
            self.assertFalse(any(v in (1,2) for v in row['seats'].values()))
            self.assertEqual(row['seats']['amcha_yisrael'],0)
        self.assertFalse(package['source_freeze_complete'])
        self.assertFalse(package['exact_current_bader_ofer'])

    def test_export_preserves_selected_forecast_and_method_word_limit(self):
        package=review_package.build()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp);review_package.write(package,out)
            original=(review_package.ROOT/package['reference_source']).read_bytes()
            self.assertEqual((out/'forecast.json').read_bytes(),original)
            self.assertLessEqual(len((out/'method-description.txt').read_text(encoding='utf-8').split()),500)
            validation=json.loads((out/'validation.json').read_text(encoding='utf-8'))
            self.assertEqual(validation['forecast_copy_sha256'],validation['reference_sha256'])


if __name__ == '__main__':unittest.main()
