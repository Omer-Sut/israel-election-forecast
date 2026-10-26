# E016: turnout context ablations

Retrospective revised-vintage sensitivity. No strict real-time demographic/conflict backtest is certified.

48 configurations; common outer Knessets: [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]. Two history, two demographic, two conflict features at most; identical training/evaluation rows across blocks.

| Past-only selected block | Recent six MAE pp | Equal-three-block MAE pp | All-fold MAE pp |
|---|---:|---:|---:|
| history | 2.684 | 3.068 | 4.212 |
| demographics | 2.663 | 2.740 | 3.999 |
| conflict | 2.634 | 3.058 | 3.770 |
| both | 2.500 | 2.487 | 3.703 |
| last-three mean reference | 2.059 | 3.032 | 3.607 |

Positive paired error deltas mean context made predictions worse. Fixed-grid rankings are hindsight diagnostics, not model selections.

Demographics: exact year minus2, capped at2022.65+ denominator is total resident population;20-29 denominator is female resident population. Neither is the electorate. Current reference year2022 is deliberately stale; no projection used. Historical publication/revision vintages unverified.

Conflict: count of curated onsets365days and time since latest onset capped10years. Zero means no entry in this catalogue, not peace. End/active status/severity unknown and unused. Catalogue incomplete after2022: current conflict/both model estimates are unavailable rather than set to zero.

Three past OOF folds required for selection; last6 past errors only, references included and form bounds enforced before selection. First three outer folds use persistence. Scalers fit on training rows only. One election has one weight; no ballot-count GLM weighting.

Four2019-2021 elections remain dependent; equal2015/2019-21/2022 block scores reported. Outcomes were previously inspected; no untouched holdout or causal interpretation. No forecast changed.

See results.json for feature coverage, all paired contrasts, selections, coefficients/scalers and current missing-context diagnostics. Historical rows stored once in predictions.csv.
