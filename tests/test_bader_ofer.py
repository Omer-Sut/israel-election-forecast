import unittest
from scripts import baseline
from scripts.bader_ofer import allocate, _complete, UnresolvedLottery, validate_active_forecast
from scripts.electoral_review import AGREEMENTS_2022, official_2022, build


class ElectoralAllocationTests(unittest.TestCase):
    def test_complete_2022_official_result(self):
        votes, truth = official_2022()
        self.assertEqual(len(votes), 40)
        answer = allocate(votes,total_valid_votes=4764742,agreements=AGREEMENTS_2022)
        self.assertEqual(answer['seats'], truth)
        self.assertNotEqual(allocate(votes,total_valid_votes=4764742)['seats'], truth)
        self.assertNotIn(['אמת','מרצ'],answer['active_agreements'])

    def test_threshold_inclusive_and_failed_partner_not_rescued(self):
        answer = allocate({'a':32500,'b':935001,'c':32499},total_valid_votes=1000000,
                          agreements=[('a','c')])
        self.assertIn('a',answer['initial_seats'])
        self.assertNotIn('c',answer['initial_seats'])
        self.assertEqual(answer['seats']['c'],0)
        self.assertEqual(answer['active_agreements'],[])
        self.assertEqual(answer,allocate({'a':32500,'b':935001,'c':32499},total_valid_votes=1000000))

    def test_invalid_counts_and_agreements(self):
        for votes,total,pairs in [({'a':999999},1000000,[]),({'a':1.0},1,[]),
                ({'a':True},1,[]),({'a':-1,'b':1000001},1000000,[]),
                ({'a':1000000},1000000,[('a','a')]),
                ({'a':500000,'b':300000,'c':200000},1000000,[('a','b'),('a','c')])]:
            with self.subTest(votes=votes,pairs=pairs), self.assertRaises(ValueError):
                allocate(votes,total_valid_votes=total,agreements=pairs)

    def test_exact_quotient_tie_requires_lottery(self):
        with self.assertRaises(UnresolvedLottery):
            _complete({('a',):500000,('b',):500000},{('a',):59,('b',):59},120,[])

    def test_half_vote_list_cannot_take_61st_seat(self):
        seats={('a',):60,('b',):30,('c',):29}
        _complete({('a',):500000,('b',):250001,('c',):249999},seats,120,[])
        self.assertEqual(seats,{('a',):60,('b',):30,('c',):30})

    def test_active_export_rejects_old_draft_and_undisaggregated_other(self):
        from scripts.forecast_review import build_review
        old=build_review()
        contract=baseline.load_json(baseline.ROOT/'config/submission-fields.json')
        with self.assertRaises(ValueError):
            validate_active_forecast(old['recommendation']['seats'],70.63,contract,other_lists={})
        new=build()['active_draft']
        validate_active_forecast(new['seats'],70.63,contract,other_lists={})
        bad=dict(new['seats']);bad['likud']-=3;bad['other_qualifying_lists']=3
        with self.assertRaises(ValueError):
            validate_active_forecast(bad,70.63,contract,other_lists={})
        with self.assertRaises(ValueError):
            validate_active_forecast(bad,70.63,contract,other_lists={'x':1,'y':2})
        validate_active_forecast(bad,70.63,contract,other_lists={'x':3})
        for turnout in (39.99,100.01):
            with self.assertRaises(ValueError):
                validate_active_forecast(new['seats'],turnout,contract,other_lists={})

    def test_active_decision_has_no_one_or_two_and_exact_total(self):
        report=build();draft=report['active_draft']
        self.assertEqual(sum(draft['seats'].values()),120)
        self.assertFalse(any(v in (1,2) for v in draft['seats'].values()))
        self.assertEqual(report['changed_fields'],{
            'amcha_yisrael':{'before':1,'after':0},'reservists_economic':{'before':2,'after':3}})
        self.assertFalse(draft['exact_current_bader_ofer'])


if __name__ == '__main__': unittest.main()
