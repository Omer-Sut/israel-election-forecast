import unittest
from scripts.party_area_trial import area_context, validate_lineage, choose_earlier


class PartyAreaTrialTests(unittest.TestCase):
    def setUp(self):
        self.lineage={'initial_election':{'reason':'no preceding data'},'elections':{'22':{
            'source_knesset':21,'unmapped_reason':'split or new list','mappings':[
                {'target_id':'stable','status':'continuity','source_ballot_codes':['a'],'rationale':'proxy'},
                {'target_id':'merged','status':'pooled_proxy','source_ballot_codes':['b','c'],'rationale':'pool'}]}}}
        self.official={(21,'a'):{'votes':100},(21,'b'):{'votes':200},(21,'c'):{'votes':100}}
        self.totals={('cities',21,'a'):(20,50),('cities',21,'b'):(100,100),('cities',21,'c'):(-25,50),
                     ('edition2015',21,'a'):(80,100)}
        self.available={'cities':'2018-11-28','edition2015':'2019-08-31'}

    def ctx(self,target='stable',cutoff='2019-09-16',ablation='cities_continuity'):
        return area_context(22,target,cutoff,ablation,self.lineage,self.totals,self.official,self.available)

    def test_previous_election_only_and_no_target_vote_denominator(self):
        first=self.ctx()
        self.totals['cities',22,'a']=(999999,999999)
        self.totals['cities',25,'a']=(999999,999999)
        self.assertEqual(first,self.ctx())
        self.assertEqual(first['feature_values'],[.4,.5,0,0])
        self.assertEqual(first['source_knesset'],21)

    def test_pools_votes_before_average_and_keeps_strict_mode_separate(self):
        self.assertEqual(self.ctx('merged')['feature_values'],[0,0,1,0])
        p=self.ctx('merged',ablation='cities_pooled')
        self.assertEqual(p['feature_values'],[.5,.5,0,1])
        self.assertEqual(p['prior_national_votes'],300)

    def test_availability_fallback_and_split_missing(self):
        self.assertEqual(self.ctx(cutoff='2018-11-28')['feature_values'][2],1)
        self.assertEqual(self.ctx(cutoff='2019-08-31',ablation='edition2015_continuity')['scope'],'cities')
        self.assertEqual(self.ctx(ablation='edition2015_continuity')['feature_values'],[.8,1,0,0])
        self.assertEqual(self.ctx('unmapped')['lineage_status'],'unmapped')

    def test_no_same_election_or_reused_predecessor_in_config(self):
        validate_lineage(self.lineage,self.official)
        self.lineage['elections']['22']['source_knesset']=22
        with self.assertRaises(ValueError): validate_lineage(self.lineage,self.official)
        self.lineage['elections']['22']['source_knesset']=21
        self.lineage['elections']['22']['mappings'][1]['source_ballot_codes']=['a']
        with self.assertRaises(ValueError): validate_lineage(self.lineage,self.official)

    def test_inner_selection_never_uses_current_or_future_scores(self):
        rows=[dict(election=str(y),election_date=f'{y}-01-01',fraction=f,continuous_error=loss,integer_error=loss)
              for y in (2018,2019,2021) for f,loss in ((0,10),(.25,12 if y<2021 else 0))]
        self.assertEqual(choose_earlier(rows,'2020-01-01','continuous_error')[0],0)
        self.assertIsNone(choose_earlier(rows,'2019-01-01','integer_error'))
