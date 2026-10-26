import copy
from datetime import date, timedelta
import importlib.util
import unittest
from scripts import baseline, turnout_context as tc


class TurnoutContextBoundaries(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = baseline.load_json(tc.CONFIG)
        cls.rows, cls.series, cls.events, cls.audit = tc.load_inputs(cls.config)

    def test_source_integrity_and_fixed_grid(self):
        self.assertEqual(len(tc.configurations(self.config)), 48)
        self.assertEqual(len({c['id'] for c in tc.configurations(self.config)}), 48)
        self.assertEqual(len(self.events), 13)
        self.assertIn(1960, self.series['SP.POP.65UP.TO.ZS'])

    def test_demographic_release_gate_and_exact_year(self):
        value, detail = tc.demographics('2022-11-01', self.series, self.config, self.audit, strict=True)
        self.assertIsNone(value)
        self.assertEqual(detail['status'], 'historical_release_unverified')
        value, detail = tc.demographics('1961-08-15', self.series, self.config, self.audit)
        self.assertIsNone(value)  #1959 missing; must not backfill1960.
        self.assertEqual(detail['reference_year'], 1959)
        _, detail = tc.demographics('2026-10-27', self.series, self.config, self.audit)
        self.assertEqual(detail['reference_year'], 2022)

    def test_demographic_denominators_are_not_combined(self):
        series = {'SP.POP.65UP.TO.ZS': {2020: 12}, 'SP.POP.2024.FE.5Y': {2020: 7},
                  'SP.POP.2529.FE.5Y': {2020: 6}, 'SP.POP.TOTL.FE.ZS': {2020: 99}}
        value, _ = tc.demographics('2022-11-01', series, self.config, self.audit)
        self.assertEqual(value, {'resident_65plus_pct': 12, 'female_resident_20_29_pct': 13})
        series['SP.POP.2529.FE.5Y'][2020] = None
        self.assertIsNone(tc.demographics('2022-11-01', series, self.config, self.audit)[0])

    def test_event_cutoff_future_end_invariance_and_unknown_current(self):
        events = [{'id': 'old', 'onset': '2019-01-01', 'end': None},
                  {'id': 'future', 'onset': '2021-05-10', 'end': '2021-05-21'}]
        value, detail = tc.conflict('2021-03-22', events, self.audit)
        self.assertEqual(value['catalogued_onsets_365d'], 0)
        self.assertEqual(detail['last_onset_id'], 'old')
        self.assertIsNone(detail['active_status'])
        events[0]['end'] = '2030-01-01'
        self.assertEqual((value, detail), tc.conflict('2021-03-22', events, self.audit))
        self.assertIsNone(tc.conflict('2026-10-25', events, self.audit)[0])
        self.assertIsNone(tc.conflict('2021-03-22', events, self.audit, strict=True)[0])

    def test_target_and_future_outcomes_cannot_enter_features(self):
        row = self.rows[23]; cutoff = (date.fromisoformat(row['election_date'])-timedelta(days=1)).isoformat()
        value = tc.feature_row(self.rows[:23], row['election_date'], cutoff, self.series, self.events, self.config, self.audit)
        changed = copy.deepcopy(self.rows); changed[23]['turnout_pct'] = 99
        self.assertEqual(value, tc.feature_row(changed[:23], row['election_date'], cutoff, self.series, self.events, self.config, self.audit))
        self.assertEqual(len(value['features']['both']), 6)
        with self.assertRaises(ValueError):
            tc.feature_row(self.rows[:24], row['election_date'], cutoff, self.series, self.events, self.config, self.audit)


@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('scipy'), 'Optional turnout CPU dependencies')
class TurnoutContextEvaluation(unittest.TestCase):
    def test_matched_training_folds_and_past_only_choices(self):
        result = tc.build()
        predictions = result['historical_predictions']
        expected = result['matched_outer_knessets']
        for candidate in result['configurations']:
            rows = [r for r in predictions if r['id'] == candidate['id']]
            self.assertEqual([r['knesset'] for r in rows], expected)
            for row in rows:
                self.assertTrue(all(k < row['knesset'] for k in row['training_knessets']))
        for selection in result['nested_selections']:
            self.assertTrue(all(k < selection['knesset'] for k in selection['validation_knessets']))
        for knesset in expected:
            for window in (None, 8):
                matching = [r for r in predictions if r['knesset'] == knesset and ('__w'+str(window or 'all')+'__') in r['id']]
                self.assertEqual(len({tuple(r['training_knessets']) for r in matching}), 1)
        for c in result['configurations']:
            if c['block'] in ('conflict', 'both'):
                self.assertIsNone(result['current_fits'][c['id']]['prediction_pct'])
        self.assertFalse(result['strict_context_eligible'])

    def test_outer_truth_change_does_not_change_its_prediction_or_choice(self):
        config = baseline.load_json(tc.CONFIG)
        config['blocks'] = ['history']; config['families'] = ['linear_level']
        config['training_windows'] = [8]; config['alphas'] = [.1]
        inputs = tc.load_inputs(config)
        before = tc.build(config, inputs=inputs)
        changed = copy.deepcopy(inputs[0]); changed[-1]['turnout_pct'] = 95
        after = tc.build(config, rows=changed, inputs=inputs)
        a = [r for r in before['historical_predictions'] if r['knesset'] == 25]
        b = [r for r in after['historical_predictions'] if r['knesset'] == 25]
        self.assertEqual([(r['id'],r['prediction_pct']) for r in a], [(r['id'],r['prediction_pct']) for r in b])
        self.assertEqual(before['nested_selections'][-1]['selected'], after['nested_selections'][-1]['selected'])
