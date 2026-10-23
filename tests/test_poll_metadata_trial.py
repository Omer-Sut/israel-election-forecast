import copy
import importlib.util
import unittest
from scripts.poll_metadata_trial import (poll_metadata, vocabulary, encode_metadata,
    base_weights, normalize_campaign_weights, reliability, poll_prediction, choose_fraction)


class MetadataContractTests(unittest.TestCase):
    def row(self, election='2015', creator='midgam', poll='one'):
        return dict(poll_id=poll,election=election,election_date=election+'-03-17',creator=creator,
                    publisher='publisher',mode='unknown',sample_size=None,fieldwork_duration_days=None,
                    publication_lag_days=None,publication_lead_days=4,vector=[60,60],actual=[58,62],
                    error=4,reliability={'multiplier':1})

    def test_repeat_releases_do_not_increase_firm_or_campaign_mass(self):
        rows=[self.row(creator='a'),self.row(creator='a',poll='two'),self.row(creator='b'),self.row('2019','c')]
        self.assertEqual(base_weights(rows),[.25,.25,.5,1])
        weights=normalize_campaign_weights(rows,[.75,1.5,1,1])
        self.assertAlmostEqual(sum(weights[:3]),1)
        self.assertEqual(weights[3],1)

    def test_unseen_creator_does_not_expand_training_vocabulary(self):
        row=self.row(); vocab=vocabulary([row]); new=self.row(creator='unseen')
        self.assertEqual(vocab['creator'],['midgam'])
        self.assertEqual(len(encode_metadata(new,vocab)),len(encode_metadata(row,vocab)))
        self.assertNotEqual(encode_metadata(new,vocab),encode_metadata(row,vocab))

    def test_metadata_missingness_and_firm_alias_are_explicit(self):
        p=dict(id='p',pollster_group='midgam_rc',publisher='N12',source_url='https://example.org',published_on='2021-03-19')
        row=poll_metadata(p,'2021-03-23')
        self.assertEqual(row['creator'],'midgam')
        self.assertIsNone(row['sample_size'])
        self.assertEqual(row['mode'],'unknown')
        self.assertIsNone(row['fieldwork_duration_days'])

    def test_future_campaign_rejected_before_fit(self):
        with self.assertRaisesRegex(ValueError,'precede'):
            reliability([self.row('2022')],[self.row('2021')])
        with self.assertRaisesRegex(ValueError,'precede'):
            poll_prediction({},[self.row('2022')],[self.row('2021')],True,True)

    def test_fraction_selection_cannot_see_own_or_later_error(self):
        rows=[dict(election=str(year),election_date=f'{year}-01-01',ablation='a',method='m',fraction=f,
                   integer_error=(10 if f==0 else 20)) for year in (2019,2020) for f in (0,.05,.25,1)]
        choice=choose_fraction(rows,'2021-01-01','a','m')
        rows.append(dict(election='2021',election_date='2021-01-01',ablation='a',method='m',fraction=1,integer_error=-999))
        self.assertEqual(choose_fraction(rows,'2021-01-01','a','m'),choice)
        self.assertEqual(choice,(0,['2019','2020']))

    @unittest.skipUnless(importlib.util.find_spec('sklearn'), 'optional scientific dependency')
    def test_current_targets_cannot_change_features_quality_or_predictions(self):
        past=[self.row('2015','a'),self.row('2019','b')]
        target=[self.row('2021','new')]
        changed=copy.deepcopy(target); changed[0]['actual']=[0,120]; changed[0]['error']=999
        self.assertEqual(reliability(past,target),reliability(past,changed))
        spec={'family':'ridge','alpha':10}
        self.assertEqual(poll_prediction(spec,past,target,True,True),poll_prediction(spec,past,changed,True,True))
        for r in reliability(past,target):
            self.assertTrue(.75<=r['multiplier']<=1.5)


if __name__=='__main__': unittest.main()
