import copy
import importlib.util
import unittest
from scripts import baseline, turnout_models as tm
from scripts.compare_turnout_models import compare


class TurnoutTimeSeriesBoundaries(unittest.TestCase):
    def test_features_exclude_target_and_future(self):
        rows=baseline.load_json(baseline.ROOT/'data/snapshots/turnout-history-2026-10-24/inputs.json')['elections']
        target=rows[20]['election_date'];a=tm.features(rows[:20],target)
        changed=copy.deepcopy(rows);changed[20]['turnout_pct']=99
        self.assertEqual(a,tm.features(changed[:20],target))
        with self.assertRaises(ValueError):tm.features(rows[:21],target)
        self.assertEqual(a['ar3'],{'lag1':72.3,'lag2':67.77,'lag3':64.7})

    def test_selector_uses_only_supplied_past_errors_and_rejects_invalid_current(self):
        past=[{'id':name,'knesset':k,'eligible':True,'absolute_error_pp':error}
              for k in (20,21,22) for name,error in [('previous_election',3),('model',1)]]
        current={'previous_election':{'family':'reference','eligible':True},'model':{'family':'linear_level','eligible':True}}
        self.assertEqual(tm.choose(past,current)['selected'],'model')
        current['model']['eligible']=False
        self.assertEqual(tm.choose(past,current)['selected'],'previous_election')
        self.assertEqual(tm.choose(past[:2],current)['status'],'warmup_reference')

    def test_grid_size_bounds_and_numeric_reproduction(self):
        configs=tm.configurations(baseline.load_json(tm.CONFIG))
        self.assertEqual(len(configs),264)
        self.assertEqual(len({c['id'] for c in configs}),264)
        contract=baseline.load_json(baseline.ROOT/'config/submission-fields.json')
        self.assertTrue(tm.allowed(40,contract));self.assertTrue(tm.allowed(100,contract))
        self.assertFalse(tm.allowed(39.99,contract));self.assertFalse(tm.allowed(100.01,contract))
        compare({'x':1.},{'x':1.+1e-8})
        with self.assertRaises(AssertionError):compare({'selected':'a'},{'selected':'b'})
        with self.assertRaises(AssertionError):compare({'x':1.},{'x':1.+1e-5})


@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('scipy'),'Optional turnout CPU dependencies')
class TurnoutRegressionFits(unittest.TestCase):
    def test_linear_fit_recovers_relationship_and_scaler_is_training_only(self):
        examples=[{'knesset':i,'turnout_pct':60+2*i,'previous_turnout':60,
                   'features':{'x':float(i)}} for i in range(1,9)]
        c={'family':'linear_level','alpha':0}
        value,fit=tm.fit_predict(examples,{'x':9.},60,c)
        self.assertAlmostEqual(value,78,places=8)
        self.assertAlmostEqual(fit['training_centers'][0],4.5)
        _,extreme=tm.fit_predict(examples,{'x':9000.},60,c)
        self.assertEqual(fit['training_centers'],extreme['training_centers'])

    def test_fractional_logit_reproduces_constant_rate_without_population_weighting(self):
        examples=[{'knesset':i,'turnout_pct':70.,'previous_turnout':70.,'features':{'x':float(i)}} for i in range(1,9)]
        value,fit=tm.fit_predict(examples,{'x':9.},70,{'family':'fractional_logit','alpha':.01})
        self.assertAlmostEqual(value,70,places=6)
        self.assertEqual(fit['status'],'converged')


if __name__=='__main__':unittest.main()
