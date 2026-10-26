import copy
from fractions import Fraction
import importlib.util
import itertools
import unittest
from scripts import diversity_bands as db


class BandDiagnosticBoundaries(unittest.TestCase):
    def test_width_only_and_interval_score_disagree_on_false_precision(self):
        narrow=db.score_band([3],[3],[0],'9/10')
        wide=db.score_band([0],[4],[0],'9/10')
        self.assertEqual(narrow['total_width'],0)
        self.assertEqual(narrow['sum_marginal_interval_score'],60)
        self.assertEqual(wide['sum_marginal_interval_score'],4)

    def test_whole_campaign_rank_does_not_invent_finite90percent(self):
        earlier=[2,1,4,3,5,6]
        q=db.earlier_inflation(earlier,'9/10')
        self.assertEqual(q['status'],'unavailable_insufficient_campaigns')
        self.assertEqual(q['rank'],7);self.assertIsNone(q['inflation'])
        q=db.earlier_inflation(earlier,'4/5')
        self.assertEqual(q['inflation'],6);self.assertEqual(q['earlier_campaigns'],6)
        self.assertEqual(earlier,[2,1,4,3,5,6])

    def test_region_count_matches_complete_legal_enumeration(self):
        lower=[0,0];upper=[7,7]
        expected=sum(sum(v)==7 for v in itertools.product((0,3,4,5,6,7),repeat=2))
        self.assertEqual(db.region_count(lower,upper,total=7),expected)
        lo,hi=db.inflate([3,4,0],[3,4,0],1,{2:0},total=7)
        self.assertEqual((lo,hi),([3,3,0],[4,5,0]))


@unittest.skipUnless(importlib.util.find_spec('ortools') and importlib.util.find_spec('numpy') and importlib.util.find_spec('scipy'),'Optional diversity/band CPU dependencies')
class BandSolverBoundaries(unittest.TestCase):
    config={'solver_seconds':5,'seed':20261026,'maximum_diverse_vectors':4}

    def case(self):
        return {'party_ids':['a','b'],'family':{'reference':[3,4],'fixed':{},'scale':3,
            'scenarios':[[3,4],[4,3],[0,7]],'models':[{'name':'equal','weights':{'0':'1/3','1':'1/3','2':'1/3'}}]},'actual':{'a':0,'b':7}}

    def test_minimum_width_equals_exhaustive_coverage_constrained_solution(self):
        case=self.case();result=db.minimum_width(case,'2/3',self.config,total=7)
        allowed=[0,3,4,5,6,7];candidates=[]
        for lo in itertools.product(allowed,repeat=2):
            for hi in itertools.product(allowed,repeat=2):
                if not all(a<=r<=b for a,r,b in zip(lo,[3,4],hi)):continue
                if min(db.covered_mass(case,lo,hi,total=7))>=2:candidates.append(sum(b-a for a,b in zip(lo,hi)))
        self.assertTrue(result['primary_optimal']);self.assertEqual(result['total_width'],min(candidates))
        changed=copy.deepcopy(case);changed['actual']={'a':7,'b':0}
        other=db.minimum_width(changed,'2/3',self.config,total=7)
        self.assertEqual(result,other)

    def test_invalid_scenario_mass_is_not_silently_normalized(self):
        case=self.case();case['family']['scenarios']=[[1,6]]
        case['family']['models']=[{'name':'invalid','weights':{'0':'1'}}];case['family']['scale']=1
        result=db.minimum_width(case,'9/10',self.config,total=7)
        self.assertEqual(result['status'],'INFEASIBLE');self.assertNotIn('lower',result)

    def test_greedy_diversity_matches_finite_region_and_step_optima(self):
        case={'party_ids':['a','b'],'family':{'reference':[61,59],'fixed':{},'scale':2,
            'scenarios':[[60,60],[62,58]],'models':[{'name':'equal','weights':{'0':'1/2','1':'1/2'}}]},
            'cells':[{'budget':12,'oracles':[{'optimal':True,'value_scaled':4}],
                      'highs':{'optimal':True,'value_scaled':0}}]}
        result=db.diverse_vectors(case,12,0,self.config)
        expected={(60,60),(61,59),(62,58)}
        self.assertEqual({tuple(v) for v in result['vectors']},expected)
        self.assertEqual(result['status'],'exhausted');self.assertTrue(result['all_steps_optimal'])
        for i,step in enumerate(result['steps']):
            kept=result['vectors'][:min(i+1,len(result['vectors']))]
            best=max(min(sum(abs(a-b) for a,b in zip(v,w)) for w in kept) for v in expected)
            self.assertEqual(step['actual_minimum_l1'],best)
