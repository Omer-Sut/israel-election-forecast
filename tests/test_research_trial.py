import unittest
from scripts.research_trial import index_vector, select_past, describe
from scripts.experiments import reconcile


class ResearchTrialTests(unittest.TestCase):
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

