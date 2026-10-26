import copy
from fractions import Fraction
import importlib.util
import itertools
import unittest
from scripts import baseline, numerical_search as ns, forecast_review


class NumericalInputBoundaries(unittest.TestCase):
    def test_constraints_and_budget(self):
        ns.validate([60,60,0],[60,60,0],0,{2:0})
        for vector in ([59,60,0],[59,60,1],[58,60,2],[-3,123,0]):
            with self.assertRaises(ValueError): ns.validate(vector,[60,60,0],None,{2:0})
        with self.assertRaises(ValueError): ns.validate([57,63,0],[60,60,0],4,{2:0})
        with self.assertRaises(ValueError): ns.validate([57,60,3],[60,60,0],None,{2:0})

    def test_scenarios_do_not_read_outcomes_and_keep_rational_weights(self):
        case={'ids':['a','b','c'],'vectors':[[60,56,4],[64,56,0]],'anchor':[62,56,2], 'actual':{'a':1,'b':2,'c':3}}
        config=baseline.load_json(ns.CONFIG); first=ns.scenario_models(case,config)
        changed=copy.deepcopy(case); changed['actual']={'a':120,'b':0,'c':0}
        self.assertEqual(first,ns.scenario_models(changed,config))
        for model in first['models']:
            self.assertEqual(sum(model['weights'].values()),1)
            self.assertTrue(all((w*first['scale']).denominator==1 for w in model['weights'].values()))
        for vector in first['scenarios'][2:]: ns.validate(vector,first['reference'],None,{})


@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('scipy'),'Optional numerical CPU dependencies')
class HighsNumericalBoundaries(unittest.TestCase):
    def fixture(self,budget=None):
        family={'reference':[3,4],'fixed':{},'scale':2,'scenarios':[[0,7],[4,3]],'models':[
            {'name':'equal','weights':{0:Fraction(1,2),1:Fraction(1,2)}},
            {'name':'first','weights':{0:Fraction(1)}},{'name':'second','weights':{1:Fraction(1)}}]}
        return ns.problem({'ids':['a','b']},family,budget,total=7)

    def candidates(self,p):
        return [list(v) for v in itertools.product((0,3,4,5,6,7),repeat=2) if sum(v)==7 and
                (p['budget'] is None or sum(abs(a-b) for a,b in zip(v,p['family']['reference']))<=p['budget'])]

    def exact(self,p,vector,m):
        return sum(int(w*p['family']['scale'])*sum(abs(a-b) for a,b in zip(vector,p['family']['scenarios'][s])) for s,w in p['family']['models'][m]['weights'].items())

    def test_oracles_and_robust_regret_match_exhaustive_search(self):
        for budget in (None,6):
            p=self.fixture(budget); candidates=self.candidates(p)
            expected=[min(self.exact(p,v,m) for v in candidates) for m in range(3)]
            actual=[ns.highs(p,objective=cost,seconds=10) for cost in p['costs']]
            self.assertTrue(all(r['optimal'] for r in actual))
            self.assertEqual([r['value_scaled'] for r in actual],expected)
            robust=ns.highs(p,oracles=expected,seconds=10)
            best=min(max(self.exact(p,v,m)-expected[m] for m in range(3)) for v in candidates)
            self.assertTrue(robust['optimal']); self.assertEqual(robust['value_scaled'],best)

    def test_zero_budget_returns_reference(self):
        p=self.fixture(0); oracle=[ns.highs(p,objective=c,seconds=10)['value_scaled'] for c in p['costs']]
        result=ns.highs(p,oracles=oracle,seconds=10)
        self.assertEqual(result['seats'],p['family']['reference']); self.assertEqual(result['value_scaled'],0)

    def test_highs_reproduces_exact_mean_objective(self):
        import numpy as np
        vectors=[[60,56,4],[64,56,0]]; case={'ids':['a','b','c'],'vectors':vectors,'anchor':[62,56,2]}
        config=baseline.load_json(ns.CONFIG); family=ns.scenario_models(case,config); p=ns.problem(case,family,None)
        costs=np.array([(len(vectors)*v-sum(a[i] for a in vectors))**2 for i,v in p['slots']],dtype=np.int64)
        result=ns.highs(p,objective=costs,seconds=10)
        dp=forecast_review.constrained_decision(vectors)
        expected=sum((len(vectors)*v-sum(a[i] for a in vectors))**2 for i,v in enumerate(dp))
        self.assertTrue(result['optimal']); self.assertEqual(result['value_scaled'],expected)


@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('scipy') and importlib.util.find_spec('ortools'),'Optional CP-SAT dependencies')
class IndependentSolverBoundaries(unittest.TestCase):
    def fixture(self): return HighsNumericalBoundaries().fixture(None)

    def test_independent_solver_certifies_same_regret(self):
        p=self.fixture(); config=baseline.load_json(ns.CONFIG)
        oracle=[ns.highs(p,objective=c,seconds=10)['value_scaled'] for c in p['costs']]
        a=ns.highs(p,oracles=oracle,seconds=10); b=ns.cp_solve(p,oracle,config)
        self.assertTrue(a['optimal']); self.assertTrue(b['optimal']); self.assertEqual(a['value_scaled'],b['value_scaled'])

    def test_forbidden_conditional_seat_is_infeasible(self):
        p=self.fixture(); config=baseline.load_json(ns.CONFIG)
        oracle=[ns.highs(p,objective=c,seconds=10)['value_scaled'] for c in p['costs']]
        result=ns.cp_solve(p,oracle,config,{0:1})
        self.assertEqual(result['status'],'INFEASIBLE'); self.assertNotIn('seats',result)

    def test_enumerated_vectors_are_unique_and_inside_regret_bound(self):
        p=self.fixture(); config=baseline.load_json(ns.CONFIG); config['maximum_near_optimal_vectors']=20
        oracle=[ns.highs(p,objective=c,seconds=10)['value_scaled'] for c in p['costs']]
        optimum=ns.highs(p,oracles=oracle,seconds=10)['value_scaled']
        result=ns.enumerate_near(p,oracle,optimum,config); vectors=result['vectors']
        self.assertTrue(vectors); self.assertEqual(len(vectors),len({tuple(v) for v in vectors}))
        fixture=HighsNumericalBoundaries()
        for vector in vectors:
            value=max(fixture.exact(p,vector,m)-oracle[m] for m in range(3))
            self.assertLessEqual(value,result['cap_scaled'])
