import copy
import unittest
from scripts.compare_poll_metadata import compare


class ReportComparisonTests(unittest.TestCase):
    def test_roundoff_only_for_ordinary_floats(self):
        compare({'value': 1.0}, {'value': 1.0 + 1e-12})
        with self.assertRaises(AssertionError):
            compare({'value': 1.0}, {'value': 1.001})

    def test_forest_tolerance_does_not_hide_decisions_or_other_models(self):
        a = dict(ablation='poll_metadata_weighted', method='forest_3_5',
                 continuous_prediction=[3.0], integer_prediction=[3], fraction=.25)
        b = copy.deepcopy(a); b['continuous_prediction'] = [3.017]
        compare(a, b)
        b['integer_prediction'] = [4]
        with self.assertRaises(AssertionError): compare(a, b)
        b = copy.deepcopy(a); b['fraction'] = .26
        with self.assertRaises(AssertionError): compare(a, b)
        b = copy.deepcopy(a); b['continuous_prediction'] = [3.021]
        with self.assertRaises(AssertionError): compare(a, b)
        a['method'] = b['method'] = 'ridge_10'
        with self.assertRaises(AssertionError): compare(a, b)

    def test_structure_and_nonfinite_values_fail(self):
        for a, b in [([1], [1, 2]), ({'a': 1}, {'b': 1}), (1, 1.0),
                     (1.0, float('nan'))]:
            with self.assertRaises(AssertionError): compare(a, b)
