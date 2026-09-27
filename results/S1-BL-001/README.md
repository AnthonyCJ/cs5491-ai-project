# S1 teacher-baseline calibration

Run: `S1-BL-001`. Experiment: `S1-BL-001`.

Source fingerprint: `928e03216e89e54ef03d6e8d34b4f4f89244b0c4169a1fb2492f97175b3c14f8`.

These are executed scores of the fixed teacher placements, not optimisation results.
Latency is the fitted estimate of encrypted inference; it is not measured inference time.
All 30 cases passed independent structure/level/cost checks and reference calibration.

| Module | Input level | Estimated latency (ms) | B1 | B2 | Depth | Budget | Utilisation |
|---|---:|---:|---:|---:|---:|---:|---:|
| mlp | 0 | 28129.69 | 5 | 4 | 26 | 122 | 0.213115 |
| mlp | 1 | 28129.85 | 5 | 4 | 26 | 123 | 0.211382 |
| mlp | 2 | 28130.01 | 5 | 4 | 26 | 124 | 0.209677 |
| mlp | 3 | 28130.17 | 5 | 4 | 26 | 125 | 0.208000 |
| mlp | 4 | 28130.33 | 5 | 4 | 26 | 126 | 0.206349 |
| mlp | 5 | 28130.49 | 5 | 4 | 26 | 127 | 0.204724 |
| mlp | 6 | 28130.65 | 5 | 4 | 26 | 128 | 0.203125 |
| mlp | 7 | 28130.81 | 5 | 4 | 26 | 129 | 0.201550 |
| mlp | 8 | 28130.97 | 5 | 4 | 26 | 130 | 0.200000 |
| mlp | 9 | 28131.13 | 5 | 4 | 26 | 131 | 0.198473 |
| mlp | 10 | 28131.29 | 5 | 4 | 26 | 132 | 0.196970 |
| mlp | 11 | 28131.45 | 5 | 4 | 26 | 133 | 0.195489 |
| mlp | 12 | 28131.61 | 5 | 4 | 26 | 134 | 0.194030 |
| mlp | 13 | 28131.77 | 5 | 4 | 26 | 135 | 0.192593 |
| mlp | 14 | 28131.93 | 5 | 4 | 26 | 136 | 0.191176 |
| attention | 0 | 53558.17 | 9 | 8 | 62 | 230 | 0.269565 |
| attention | 1 | 53558.17 | 9 | 8 | 62 | 231 | 0.268398 |
| attention | 2 | 53558.17 | 9 | 8 | 62 | 232 | 0.267241 |
| attention | 3 | 53558.17 | 9 | 8 | 62 | 233 | 0.266094 |
| attention | 4 | 53558.17 | 9 | 8 | 62 | 234 | 0.264957 |
| attention | 5 | 53558.17 | 9 | 8 | 62 | 235 | 0.263830 |
| attention | 6 | 53558.17 | 9 | 8 | 62 | 236 | 0.262712 |
| attention | 7 | 53558.17 | 9 | 8 | 62 | 237 | 0.261603 |
| attention | 8 | 53558.17 | 9 | 8 | 62 | 238 | 0.260504 |
| attention | 9 | 53558.17 | 9 | 8 | 62 | 239 | 0.259414 |
| attention | 10 | 53558.17 | 9 | 8 | 62 | 240 | 0.258333 |
| attention | 11 | 53558.17 | 9 | 8 | 62 | 241 | 0.257261 |
| attention | 12 | 53558.17 | 9 | 8 | 62 | 242 | 0.256198 |
| attention | 13 | 53558.17 | 9 | 8 | 62 | 243 | 0.255144 |
| attention | 14 | 53558.17 | 9 | 8 | 62 | 244 | 0.254098 |

B1 counts ciphertexts; B2 counts ciphertext pairs. A shared inserted node is charged once.
The budget is 14 * B1 + 13 * B2 + input level. Inserted operations contribute zero to depth.

## Evidence

- `summary.csv`: all scalar scores and reference-evaluation wall times.
- `cases/`: every placed DAG, inserted chain, node/edge level and exact-decimal node cost.
- `calibration.json`: all comparisons against the independent check and published PDF anchors.
- `run.json`: configuration, source hashes, package versions and resource measurement scope.
- `artifacts.sha256.json`: hashes of all result files except the manifest itself.

## Limits

One local CPU run; no optimisation search, GPU work or real FHE evaluation occurred.
The MLP PDF gives a range and the level-6 anchor, not 15 individually printed scores.
Cross-device reproduction and a separate clean environment are not validated by this run.
Resource measurements describe baseline evaluation, not the future optimiser.
