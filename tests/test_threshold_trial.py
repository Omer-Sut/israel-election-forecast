import copy
import importlib.util
import itertools
import unittest
from scripts import baseline, threshold_trial as tt


class ThresholdDecisionBoundaries(unittest.TestCase):
    def test_candidate_population_does_not_depend_on_outcomes(self):
        case={'ids':['a','b','c','d'],'vectors':[[0,0,4,9],[0,4,5,9],[0,0,6,0]],'actual':{'a':4,'b':0,'c':6,'d':9}}
        config=baseline.load_json(tt.CONFIG)
        rows=tt.candidate_rows(case,config)
        self.assertEqual([r['id'] for r in rows if r['candidate']],['b','c'])
        changed=copy.deepcopy(case);changed['actual']={k:99 for k in case['ids']}
        self.assertEqual(rows,tt.candidate_rows(changed,config))
        self.assertIsNone(rows[0]['features'])
        self.assertEqual(rows[1]['features'],[1/3,4])

    def test_expected_loss_dynamic_program_matches_enumeration(self):
        distributions=[[(0,.6),(4,.4)],[(3,1.)],[(0,.2),(4,.8)]]
        anchor=[1.6,3,3.2];total=7;values=[0,3,4,5,6,7]
        def objective(vector):
            loss=sum(sum(w*abs(a-y) for y,w in d) for a,d in zip(vector,distributions))
            return(round(loss,10),round(sum((a-b)**2 for a,b in zip(vector,anchor)),10),vector)
        expected=min((v for v in itertools.product(values,repeat=3) if sum(v)==total),key=objective)
        self.assertEqual(tt.expected_loss_decision(distributions,anchor,total=total),list(expected))
        with self.assertRaises(ValueError):
            tt.expected_loss_decision([[(0,.4)]],[0],total=7)
        fixed=tt.expected_loss_decision(distributions,anchor,total=total,fixed={0:0})
        self.assertEqual(fixed[0],0);self.assertEqual(sum(fixed),7)

    def test_selector_warmup_and_earlier_complete_folds(self):
        past=[{'election_date':day,'learned_available':True,'method':method,'seat_l1':error}
              for day in ('2019-09-17','2020-03-02')
              for method,error in [('square_0or3',8),('absolute_0or3',6),('hurdle_a1',4)]]
        now={key:{} for key in ('square_0or3','absolute_0or3','hurdle_a1')}
        self.assertEqual(tt.select(past,now)['id'],'hurdle_a1')
        self.assertEqual(tt.select(past[:3],now)['status'],'warmup_control')
        for r in past:r['seat_l1']=4
        self.assertIn(tt.select(past,now)['id'],tt.CONTROLS)


@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('scipy'),'Optional threshold CPU dependencies')
class ThresholdLearningBoundaries(unittest.TestCase):
    def test_campaign_balancing_train_only_scaling_and_single_class_fallback(self):
        rows=[{'election':'old1','id':'a','features':[1.,5.],'represented':1,'weight':1.},
              {'election':'old2','id':'b','features':[.5,4.],'represented':0,'weight':.5},
              {'election':'old2','id':'c','features':[1.,6.],'represented':1,'weight':.5}]
        target=[{'id':'x','candidate':True,'features':[.25,4.]}]
        probs,fit=tt.fit_probabilities(rows,target,.1)
        self.assertAlmostEqual(fit['centers'][0],.875)
        self.assertTrue(0<probs['x']<1)
        changed=copy.deepcopy(target);changed[0]['features']=[100.,100.]
        _,other=tt.fit_probabilities(rows,changed,.1)
        self.assertEqual(fit['centers'],other['centers']);self.assertEqual(fit['scales'],other['scales'])
        self.assertEqual(fit['coefficients'],other['coefficients'])
        for row in rows:row['represented']=1
        probs,fit=tt.fit_probabilities(rows,target,.1)
        self.assertEqual(fit['status'],'single_class_smoothed_intercept')
        self.assertAlmostEqual(probs['x'],2.5/3)

    def test_target_truth_and_identity_cannot_affect_prediction(self):
        config=baseline.load_json(tt.CONFIG);cases=tt.historical_cases(config)
        first=tt.predict(cases[-1],cases[:-1],config,.1)
        changed=copy.deepcopy(cases[-1]);changed['actual']={k:0 for k in changed['ids']}
        second=tt.predict(changed,cases[:-1],config,.1)
        self.assertEqual(first,second)
        self.assertEqual(sum(first['seats']),120)
        self.assertFalse(any(v in (1,2) for v in first['seats']))
        self.assertNotIn(cases[-1]['election_id'],first['fit']['training_campaigns'])
        masses={}
        for row in first['fit']['training_rows']:masses[row['election']]=masses.get(row['election'],0)+row['weight']
        self.assertLess(max(masses.values())-min(masses.values()),1e-12)
