import unittest

from scripts.robustness import FRACTIONS, SEEDS, evaluate_fraction, project
from scripts.experiments import reconcile


class RobustnessTests(unittest.TestCase):
    def test_projection(self):
        self.assertEqual(project([60, 60]), [60, 60])
        self.assertEqual(project([-10, 140]), [0, 120])
        for values in ([.1, 70, 60], [-5, 3, 4, 200]):
            result = project(values)
            self.assertAlmostEqual(sum(result), 120)
            self.assertTrue(all(x >= 0 for x in result))
        with self.assertRaises(ValueError):
            project([float('nan')])

    def test_fraction_endpoints_and_rounding(self):
        anchor, raw, actual = [60.2, 59.8], [70, 50], [65, 55]
        for fraction in FRACTIONS:
            cp, ip, ce, ie = evaluate_fraction(anchor, raw, actual, fraction)
            mixed = [a + fraction*(r-a) for a, r in zip(anchor, raw)]
            self.assertEqual(ip, reconcile(mixed))
            self.assertAlmostEqual(sum(cp), 120)
            self.assertEqual(ie, sum(abs(a-b) for a,b in zip(ip,actual)))
            self.assertAlmostEqual(ce, sum(abs(a-b) for a,b in zip(cp,actual)))
        self.assertEqual(evaluate_fraction(anchor, raw, actual, 0)[1], reconcile(anchor))
        self.assertEqual(evaluate_fraction(anchor, raw, actual, 1)[1], reconcile(raw))
        self.assertEqual(len(set(SEEDS)), 20)

    def test_bad_fraction_and_shape(self):
        with self.assertRaises(ValueError):
            evaluate_fraction([120], [120], [120], 2)
        with self.assertRaises(ValueError):
            evaluate_fraction([120], [60,60], [120], .25)


if __name__ == '__main__':
    unittest.main()

