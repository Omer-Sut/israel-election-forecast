import copy
import unittest
from scripts import baseline, turnout_history as th


class TurnoutHistoryTests(unittest.TestCase):
    def test_forecast_does_not_use_target_or_future_outcomes(self):
        rows=baseline.load_json(th.INPUT)['elections']
        original=th.rolling_checks(rows)
        changed=copy.deepcopy(rows);changed[-1]['turnout_pct']=99
        revised=th.rolling_checks(changed)
        self.assertEqual([r['predictions'] for r in original],[r['predictions'] for r in revised])
        last=original[-1]
        self.assertNotIn(25,last['training_knessets'])
        self.assertAlmostEqual(last['predictions']['last_three_mean'],(69.83+71.52+67.44)/3)

    def test_context_respects_event_time_and_deduplicates_elections(self):
        data=baseline.load_json(th.INPUT);rows=data['elections'];events=data['conflict_events']
        context=th.first_election_context(rows,events,{'war','operation'})
        mapping={r['knesset']:r for r in context}
        self.assertEqual(set(mapping[18]['events']),{'lebanon_2','cast_lead'})
        self.assertEqual(len([r for r in context if r['knesset']==18]),1)
        self.assertIn('guardian',mapping[25]['events'])
        self.assertNotIn(24,mapping)
        self.assertIsNone(mapping[1]['turnout_change_pp'])
        same_day=[{'kind':'war','id':'same_day','onset':rows[-1]['election_date']}]
        self.assertEqual(th.first_election_context(rows,same_day,{'war'}),[])

    def test_counts_conflicts_and_independent_poll_coverage(self):
        report=th.build()
        self.assertEqual(len(report['history']),25)
        self.assertFalse(any(r['election_date'].startswith('2001') for r in report['history']))
        r=report['history'][10]
        self.assertEqual(r['cbs_reported_turnout_pct'],79.8)
        self.assertEqual(r['turnout_pct'],78.8)
        self.assertLess(abs(100*r['ballots']/r['electorate']-r['turnout_pct']),.05)
        self.assertEqual(report['poll_coverage'],{'release_rows':24,'known_numeric_rows':2,'independent_elections':1})
        self.assertEqual(report['current_forecast']['turnout_pct'],'70.63')
        self.assertAlmostEqual(report['metrics']['previous_election']['recent_six_mae'],18.7/6)

    def test_form_bounds_are_inclusive_and_unconstrained_diagnostics_preserved(self):
        contract=baseline.load_json(th.ROOT/'config/submission-fields.json')
        for value,eligible in [(40,True),(100,True),(39.99,False),(100.01,False)]:
            result=th.form_candidate(value,contract)
            self.assertEqual(result['within_form_bounds'],eligible)
            self.assertEqual(result['unconstrained_pct'],value)


if __name__=='__main__':unittest.main()
