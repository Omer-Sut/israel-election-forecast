# Active forecast decision — October25,2026

The user accepted the recommendation to use the last-three-election turnout average and close turnout experimentation for now. The active decision is configured in `config/forecast-decision.json`; its exported forecast is `reports/forecast-decision-2026-10-25/forecast.json`. Earlier frozen forecasts remain unchanged historical references.

Turnout is(71.52 +67.44 +70.63)/3 =69.863333…%, displayed **69.86%**. Both the unrounded and exported values must pass the configured inclusive40–100 bounds. There is no demographic, war or poll-intention adjustment. Recent mean absolute error favors the three-election mean over persistence,2.059vs3.117pp; all22 older common folds favor persistence,2.385vs2.530pp. This is a user-authorized simple-rule choice, not proof of universal superiority or calibrated uncertainty.

Retain the reviewed120-seat vector, including Reservists3, Amcha0 and no1/2-seat outputs. Reservists0/4 alternatives remain conditional seat-space illustrations without probabilities; all use the adopted turnout. Full current Bader–Ofer inputs are still incomplete. No original poll or historical identity is changed.

The bounded October25 source recheck is recorded in `data/snapshots/forecast-decision-2026-10-25/audit.json`. Official candidate/agreements routes remain inaccessible; the CEC poll repository exposes a template. Kan’s121-seat secondary table remains inconsistent; its old Zman corroboration URL now renders an unrelated feed. Channel16 remains secondary-only. A fresh news read again reports complete BlueandWhite withdrawal, but no direct official notice was authenticated. Neither a missing original poll nor unknown voter support becomes zero. No source is silently promoted and no old snapshot repaired.

Run `python scripts/forecast_decision.py` with standard-library Python3.12. It verifies the inherited package against a fresh build, applies only the approved turnout decision, validates every scenario, updates the actual method description below500words and hashes all consumed inputs. The dedicated hosted workflow tests the exported decision and historical preservation, repeats byte-for-byte and compares the dated report when present.

This package is ready for forecast review, with source gaps explicit. Exact form decimal increments and personal/team choices remain unverified. No competition entry is submitted or PR merged. Read the topic PR for final checks and authoritative remote SHA; local Git metadata is stale.


## Executed verification

Implementation32f2693 / PR29 ran on40187726289: two new tests and byte-identical repeat passed. Actual method333words; active forecast SHA2563a02e8c53ef2b85af839b6d048650c4a581ad64e6a24cae0bd9c316ab449ca97. All alternatives satisfy arithmetic/turnout bounds and unchanged seat assumptions. Final report-commit checks are recorded on PR29.
