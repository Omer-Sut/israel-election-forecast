import copy
import hashlib
import unittest
from scripts import baseline, prepare_threshold_data as td


class ThresholdDataAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=td.build()

    def test_extension_counts_and_positive_outcome_coverage(self):
        s=self.report['summary']
        self.assertEqual((s['original_releases'],s['extended_releases']),(24,32))
        self.assertEqual((s['original_exact_percentages'],s['extended_exact_percentages']),(20,37))
        self.assertEqual(s['eventual_pass_observations'],7)
        self.assertEqual(s['unique_eventual_pass_list_outcomes'],3)
        self.assertEqual(s['unmapped_percentage_observations'],1)
        self.assertEqual(s['strict_valid_vote_comparable_observations'],0)
        self.assertFalse(s['model_fitted'])
        self.assertTrue(all(sum(p['reported_seats'].values())==120 for p in self.report['releases']))

    def test_horizons_use_publication_separately_from_fieldwork(self):
        rows=self.report['observations']
        row=next(r for r in rows if r['poll_id']=='midgam_rc-2021-03-07')
        self.assertEqual(row['publication_lead_days'],16)
        self.assertEqual(row['fieldwork_lead_days'],19)
        self.assertEqual(row['publication_horizon_band'],'15_28')
        self.assertFalse(row['date_eligible_at_t1_under_original_age_gate'])
        early=next(r for r in rows if r['poll_id']=='midgam_rc-2021-02-23')
        self.assertEqual(early['publication_lead_days'],28)
        close=next(r for r in rows if r['poll_id']=='midgam_rc-2021-03-10' and r['party_id']=='raam_2021')
        self.assertEqual(close['reported_vote_pct'],3.1)
        self.assertTrue(close['actually_represented'])
        self.assertTrue(close['date_eligible_at_t1_under_original_age_gate'])

    def test_unknowns_and_repeated_wave_warning_are_not_repaired(self):
        row=next(r for r in self.report['observations'] if r['party_id']=='yachad_2015')
        self.assertIsNone(row['reported_vote_pct'])
        self.assertEqual(row['percentage_status'],'not_reported_or_not_retrieved')
        for poll in ('2020_walla_midgam_0217','2020_walla_midgam_0226'):
            rows=[r for r in self.report['observations'] if r['poll_id']==poll]
            self.assertTrue(all(r['wave_linkage_uncertain'] for r in rows))
            self.assertTrue(all(r['fieldwork_lead_days']==14 for r in rows))
        self.assertFalse(any(r['strict_valid_vote_denominator_verified'] for r in self.report['observations']))

    def test_predictor_export_excludes_labels_and_preserves_original_files(self):
        row=copy.deepcopy(self.report['observations'][0]);before=td.pre_election_features(row)
        row['actual_seats']=999;row['actually_represented']=not row['actually_represented']
        self.assertEqual(before,td.pre_election_features(row))
        self.assertNotIn('actual_seats',before);self.assertNotIn('actually_represented',before)
        paths=self.report['input_paths']
        hashes={p:hashlib.sha256((td.ROOT/p).read_bytes()).hexdigest() for p in paths}
        td.build()
        self.assertEqual(hashes,{p:hashlib.sha256((td.ROOT/p).read_bytes()).hexdigest() for p in paths})

    def test_invalid_date_and_current_alias_are_rejected(self):
        poll=copy.deepcopy(self.report['releases'][-1])
        registry={'date':'2021-03-23','lists':{k:{} for k in poll['reported_seats']}}
        poll['source_updated_on']='2021-03-24'
        with self.assertRaises(ValueError):td.temporal_features(poll,registry['date'])
        poll['source_updated_on']='2021-03-10'
        value=poll['reported_seats'].pop('joint_list_2021');poll['reported_seats']['hadash_taal']=value
        with self.assertRaises(ValueError):td.validate_release(poll,registry,28)
        self.assertEqual(td.canonical_url('https://example.com/poll/?utm_source=x'),td.canonical_url('https://example.com/poll'))
