import copy
import importlib.util
import unittest
from scripts import baseline, threshold_share_trial as trial


class ShareDataBoundaries(unittest.TestCase):
    def test_release_selection_obeys_publication_revision_and_fieldwork(self):
        polls = [dict(id='old', pollster_group='a', published_on='2021-03-01', fieldwork_end='2021-03-01'),
                 dict(id='new', pollster_group='a', published_on='2021-03-10', source_updated_on=None),
                 dict(id='future', pollster_group='b', published_on='2021-03-16'),
                 dict(id='revised', pollster_group='c', published_on='2021-03-09', source_updated_on='2021-03-17'),
                 dict(id='stale', pollster_group='d', published_on='2021-03-12', fieldwork_end='2021-02-20')]
        selected, history = trial.select_history(polls, '2021-03-15', 14)
        self.assertEqual([p['id'] for p in selected], ['new'])
        self.assertEqual([p['id'] for p in history], ['old', 'new'])
        self.assertEqual(trial.select_history(polls, '2021-02-01', 14), ([], []))
        self.assertIn('source_updated_on', polls[1])

    def test_missing_zero_and_repeated_firm_are_distinct(self):
        config = baseline.load_json(trial.CONFIG)
        case = {'ids': ['a', 'b'], 'vectors': [[0, 0], [0, 4]], 'percentage_polls': [
            {'id': 'x', 'pollster_group': 'x', 'published_on': '2021-03-01', 'reported_below_threshold_pct': {'a': 0., 'b': 2.}},
            {'id': 'y', 'pollster_group': 'x', 'published_on': '2021-03-02', 'reported_below_threshold_pct': {'b': 3.}},
            {'id': 'z', 'pollster_group': 'y', 'published_on': '2021-03-03', 'reported_below_threshold_pct': {}}]}
        a, b = trial.rows(case, config)
        self.assertTrue(a['candidate']); self.assertTrue(a['all_zero_with_percentage'])
        self.assertEqual(a['share'], 0.); self.assertEqual(a['coverage'], .25)
        self.assertEqual(b['share'], 2.5); self.assertEqual(b['coverage'], .5)
        changed = copy.deepcopy(case); changed['actual'] = {'a': 120, 'b': 0}
        self.assertEqual(trial.rows(changed, config), [a, b])
        changed['percentage_polls'] = [case['percentage_polls'][-1]]
        self.assertIsNone(trial.rows(changed, config)[0]['share'])
        self.assertFalse(trial.rows(changed, config)[0]['candidate'])

    def test_panels_match_sources_and_do_not_backfill_latest_percentages(self):
        from scripts import prepare_threshold_data
        config = baseline.load_json(trial.CONFIG); overlay = prepare_threshold_data.build()
        latest, _ = trial.cases_from_overlay(overlay, 1, 'latest', config)
        history, _ = trial.cases_from_overlay(overlay, 1, 'eligible_history', config)
        self.assertEqual(len(latest), 6)
        for a, b in zip(latest, history):
            self.assertEqual(a['vectors'], b['vectors']); self.assertEqual(a['selected_polls'], b['selected_polls'])
            self.assertEqual(a['percentage_polls'], a['selected_polls'])
            for p in b['percentage_polls']:
                self.assertLessEqual(p['published_on'], b['cutoff'])
                self.assertLessEqual(p.get('source_updated_on', p['published_on']), b['cutoff'])


@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('scipy'), 'Optional share-trial dependencies')
class ShareLearningBoundaries(unittest.TestCase):
    def test_imputation_scaling_weights_are_training_only(self):
        train = [dict(election='a', id='a', seat=[0., 0.], coverage=.5, share=2., represented=0, weight=1.),
                 dict(election='b', id='b', seat=[1., 4.], coverage=0., share=None, represented=1, weight=.5),
                 dict(election='b', id='c', seat=[.5, 4.], coverage=1., share=3., represented=0, weight=.5)]
        target = [dict(id='x', candidate=True, seat=[0., 0.], coverage=0., share=None)]
        p, fit = trial.fit(train, target, 'share', .1)
        self.assertAlmostEqual(fit['impute'][-1], 7/3)
        changed = copy.deepcopy(target); changed[0]['share'] = 1000.
        _, other = trial.fit(train, changed, 'share', .1)
        self.assertEqual(fit, other); self.assertTrue(0 < p['x'] < 1)
        for row in train: row['represented'] = 1
        p, fit = trial.fit(train, target, 'share', .1)
        self.assertEqual(fit['status'], 'single_class_fallback')
        self.assertAlmostEqual(p['x'], 2.5/3)

    def test_target_outcomes_do_not_enter_fit_or_decision(self):
        from scripts import prepare_threshold_data
        config = baseline.load_json(trial.CONFIG)
        cases, _ = trial.cases_from_overlay(prepare_threshold_data.build(), 1, 'latest', config)
        first = trial.predict(cases[-1], cases[:-1], config, 'share', .1)
        changed = copy.deepcopy(cases[-1]); changed['actual'] = {k: 0 for k in changed['ids']}
        self.assertEqual(first, trial.predict(changed, cases[:-1], config, 'share', .1))
        self.assertEqual(sum(first['seats']), 120); self.assertFalse(any(v in (1, 2) for v in first['seats']))
        self.assertNotIn(cases[-1]['election_id'], first['fit']['training_campaigns'])
        mass = {}
        for row in first['fit']['training_rows']: mass[row['election']] = mass.get(row['election'], 0.)+row['weight']
        self.assertTrue(all(abs(v-1) < 1e-12 for v in mass.values()))
        with self.assertRaises(ValueError): trial.predict(cases[-1], cases, config, 'share', .1)

    def test_no_share_training_data_cannot_create_share_coefficient(self):
        train = [dict(election=str(i), id=str(i), seat=[float(i%2), 4.], coverage=0., share=None,
                      represented=i%2, weight=1.) for i in range(4)]
        target = [dict(id='x', candidate=True, seat=[0., 4.], coverage=0., share=3.)]
        _, fit = trial.fit(train, target, 'share', .1)
        self.assertEqual(fit['impute'][-1], 0.)
        self.assertEqual(fit['coefficients'][-1], 0.)
