import test from 'node:test';
import assert from 'node:assert/strict';
import {latest,roundedMean,evaluate,validate} from '../scripts/final_poll_coverage.mjs';
const poll=(id,group,date,seats=[60,60])=>({id,pollster_group:group,published_on:date,reported_seats:{a:seats[0],b:seats[1]}});
test('rounding preserves120 and resolves equal rational remainders in field order',()=>{
  assert.deepEqual(roundedMean([[60,60],[61,59]]),[61,59]);
});
test('future revisions and fieldwork cannot enter an earlier cutoff',()=>{
  const old=poll('old','a','2021-03-18');
  const revised={...poll('rev','b','2021-03-19'),source_updated_on:'2021-03-23'};
  const future={...poll('future','c','2021-03-19'),fieldwork_end:'2021-03-23'};
  assert.deepEqual(latest([old,revised,future],'2021-03-22').map(p=>p.id),['old']);
});
test('aliases and repeated releases give one firm one vote',()=>{
  const a=poll('early','midgam_rc','2021-03-18'),b=poll('late','midgam','2021-03-19');
  assert.deepEqual(latest([a,b],'2021-03-22').map(p=>p.id),['late']);
  assert.throws(()=>evaluate([a,b],['a','b'],[60,60]),/Duplicate firm/);
  assert.throws(()=>latest([b,{...b,id:'different'}],'2021-03-22'),/Ambiguous/);
});
test('invalid totals and historical identities fail rather than being silently repaired',()=>{
  assert.throws(()=>validate(poll('p','a','2021-03-19',[60,59]),['a','b']),/allocation/);
  assert.throws(()=>validate(poll('p','a','2021-03-19'),['a','current_alias']),/historical/);
});
test('poll error and average-vector error are distinct, with signed party contributions',()=>{
  const r=evaluate([poll('p','a','2021-03-19',[62,58]),poll('q','b','2021-03-19',[58,62])],['a','b'],[60,60]);
  assert.equal(r.continuous_error,0);assert.equal(r.mean_poll_error,4);assert.equal(r.cancellation,4);
  assert.equal(r.population_variance_poll_error,0);assert.equal(r.parties[0].above,1);assert.equal(r.parties[0].below,1);
});
