import assert from 'node:assert/strict';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { project, integerSeats, absoluteError, diagnose } from '../scripts/screening_diagnostics.mjs';

export function runChecks() {
  assert.deepEqual(project([-100, 200, 20]), [0, 120, 0]);
  assert.deepEqual(integerSeats([40.5, 40.5, 39]), [41, 40, 39]);
  assert.deepEqual(integerSeats([-1000, -1000, -1000]), [40, 40, 40]);
  assert.throws(() => project([NaN]));
  assert.equal(absoluteError([60, 60], [59, 61]), 2);
  const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
  const read = p => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
  const report = read('reports/screening-six-elections-2026-10-21/experiments.json');
  const outcomes = read('data/snapshots/screening-six-elections-2026-10-21/prepared/outcomes.json');
  const result = diagnose(report, outcomes);
  assert.equal(result.cases.length, 6);
  assert.equal(result.cases[0].methods.ridge_10.stages, null);
  assert.equal(result.cases[2].methods.ridge_10.status, 'chronological_screen');
  assert.equal(result.cases[2].methods.ensemble_1.stages, null);
  assert.equal(Object.values(result.cases[5].methods).filter(m => m.family !== 'reference' && m.identical_integer_to_mean).length, 16);
  assert(result.cases[5].methods.dynamic_01.stages.projected.delta_from_mean < 0);
  assert.equal(result.cases[5].methods.dynamic_01.stages.integer.delta_from_mean, 0);
  const badScore = structuredClone(report);
  badScore.cases[5].methods.ridge_10.score.total_absolute_seat_error += 2;
  assert.throws(() => diagnose(badScore, outcomes), /score mismatch/);
  const badTarget = structuredClone(outcomes);
  const target = badTarget.elections.knesset_25_2022.seat_results;
  const keys = Object.keys(target).filter(k => target[k] > 0);
  target[keys[0]]--; target[keys[1]]++;
  assert.throws(() => diagnose(report, badTarget), /score mismatch/);
  const badRounding = structuredClone(report);
  badRounding.cases[5].methods.ridge_10.continuous_shrunk[0] += 1;
  assert.throws(() => diagnose(badRounding, outcomes), /shrinkage mismatch/);
  return 'Passed projection, tie rounding, direct-outcome scoring, stage identity, missing-fold and corruption checks.';
}
if (typeof process !== 'undefined') console.log(runChecks());
