import itertools
import unittest
from scripts import baseline
from scripts.forecast_review import constrained_decision, ROOT


class ForecastReviewTests(unittest.TestCase):
    def test_decision_matches_exhaustive_small_problem(self):
        vectors=[[1,5],[4,2]]
        for objective in ('square','absolute'):
            def cost(v):
                absolute=sum(abs(x-p) for row in vectors for x,p in zip(v,row))
                square=sum((2*v[i]-sum(row[i] for row in vectors))**2 for i in range(2))
                return (square,absolute,v) if objective=='square' else (absolute,square,v)
            candidates=[v for v in itertools.product([0,3,4,5,6],repeat=2) if sum(v)==6]
            self.assertEqual(tuple(constrained_decision(vectors,6,3,objective)),min(candidates,key=cost))

    def test_threshold_scenarios_enforce_assumptions_and_total(self):
        answer=constrained_decision([[1,4,115],[0,0,120]],minimum=4,fixed={0:4,1:0})
        self.assertEqual(answer,[4,0,116])
        with self.assertRaises(ValueError):
            constrained_decision([[60,60]],fixed={0:120,1:120})

    def test_aggregate_other_field_is_not_an_individual_threshold(self):
        answer=constrained_decision([[119,1]],minimum=4,exempt=[1])
        self.assertEqual(answer,[119,1])
        self.assertEqual(constrained_decision([[119,1]],minimum=4),[120,0])

    def test_original_records_preserved_and_each_new_transcription_complete(self):
        old=baseline.load_json(ROOT/'data/snapshots/polls-2026-10-23.json')
        new=baseline.load_json(ROOT/'data/snapshots/polls-2026-10-24.json')
        self.assertEqual(new['polls'][:len(old['polls'])],old['polls'])
        for poll in new['polls'][len(old['polls']):]:
            self.assertEqual(sum(poll['reported_seats'].values()),120)
            self.assertEqual(sum(r['seats'] for r in poll['raw_seat_transcription']),120)
        selected,_=baseline.select_polls(new['polls'],'2026-10-24',14)
        self.assertEqual(len(selected),7)
        self.assertEqual(sum(p['pollster_group']=='kantar' for p in selected),1)
        self.assertNotIn('maagar_mohot',{p['pollster_group'] for p in selected})

    def test_new_source_versions_cannot_enter_old_cutoff(self):
        new=baseline.load_json(ROOT/'data/snapshots/polls-2026-10-24.json')
        selected,_=baseline.select_polls(new['polls'],'2026-10-23',14)
        self.assertTrue(all(p['id'] not in {x['id'] for x in new['polls'][10:]} for p in selected))
