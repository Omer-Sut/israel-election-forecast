import unittest
from scripts.research_trial import index_vector, select_past, describe, prior_area_profiles, creator_key
from scripts.experiments import reconcile


class ResearchTrialTests(unittest.TestCase):
    def test_audited_creator_aliases_preserve_organization_identity(self):
        self.assertEqual(creator_key('midgam_geva'),creator_key('midgam_rc'))
        self.assertEqual(creator_key('channel13_fuchs'),creator_key('camil_fuchs'))
        self.assertEqual(creator_key('unknown_publisher'),'unknown_publisher')

    def test_index_unknown_positive_cannot_be_hidden(self):
        def c(label,value):
            return dict(list_label=label,column_role='list_or_unresolved',unit='seats',value=value)
        with self.assertRaises(ValueError):
            index_vector([c('Known',119),c('Hypothetical',1)],{'known':'a'},['a'])
        with self.assertRaises(ValueError):
            index_vector([c('Known',119)],{'known':'a'},['a'])
        vector,_=index_vector([c('Known',120),c('Gov.',60)],{'known':'a'},['a','b'])
        self.assertEqual(vector,[120,0])

    def test_temporal_selection_excludes_test_and_future(self):
        rows=[dict(election=str(y),election_date=f'{y}-01-01',method='ridge',fraction=f,integer_error=loss)
              for y in (2018,2019,2021) for f,loss in ((0,10),(.25,12 if y<2021 else 0))]
        self.assertEqual(select_past(rows,'2020-01-01')[:2],('ridge',0))
        self.assertIsNone(select_past(rows,'2019-01-01'))

    def test_sample_variance_and_final_integer_total(self):
        self.assertEqual(describe([10,20,30])['variance'],100)
        for values in ([39.5,39.5,41],[-5,60.4,80.2],[0]*12):
            seats=reconcile(values)
            self.assertEqual(sum(seats),120)
            self.assertTrue(all(type(x) is int and x>=0 for x in seats))

    def test_city_source_transcription_is_explicit_and_predates_tests(self):
        from scripts.baseline import ROOT, load_json
        source=load_json(ROOT/'data/snapshots/party-area-vintage-2018-2026-10-22.json')
        self.assertEqual(source['publication_date'],'2018-11-28')
        self.assertEqual(len({r['code'] for r in source['cities']}),15)
        self.assertEqual(next(r['index'] for r in source['cities'] if r['code']=='3000'),-.919)

