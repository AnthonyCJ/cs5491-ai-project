# attention-L12-R228: S2 optimisation evidence

Method: `shared-refresh-cp-sat-v1`. Scope: T2 formal 30-condition experiment; raw S2 compatibility; T2-FORMAL-20261004-004/protocol.json.

These are actual CPU optimisation runs scored with fitted inference costs. No encrypted inference was executed.
This S2 run does not replace S4 formal experiments or S6 independent reproduction.

Source fingerprint: `93f69945bc8e7049ceaa22e2c83350d438cfc7e582877db0365f59d11e4ebe00`.

| Case | Status | Estimated latency (ms) | Baseline (ms) | Reduction (%) | B1 / B2 | Depth | Budget | Utilisation | Solve (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| attention-L12 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 200 | 0.310000 | 0.610834 |

B1 counts ciphertexts; B2 counts ciphertext pairs. Shared nodes are charged once.
`OPTIMAL` refers to the encoded handout model with exact integer costs and zero configured gap tolerances; it is not a claim about real FHE runtime.
`FEASIBLE` is a valid incumbent without an optimality proof. Other statuses do not contain an accepted placement. No baseline fallback is presented as an improvement.

The JSON case records include decisions, the reconstructed DAG, every level and node cost, independent checks, the raw reference score, solver bounds and resources.
Timing and RSS are local observations. Resource scope is described in each case; process RSS includes imported libraries.
Figures are generated separately from these immutable case files. See the repository README for exact commands.
