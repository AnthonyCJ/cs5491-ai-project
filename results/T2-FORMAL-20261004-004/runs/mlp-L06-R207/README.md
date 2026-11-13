# mlp-L06-R207: S2 optimisation evidence

Method: `shared-refresh-cp-sat-v1`. Scope: T2 formal 30-condition experiment; raw S2 compatibility; T2-FORMAL-20261004-004/protocol.json.

These are actual CPU optimisation runs scored with fitted inference costs. No encrypted inference was executed.
This S2 run does not replace S4 formal experiments or S6 independent reproduction.

Source fingerprint: `0cb8c14c564a208a5da62a93b6daaeaa44f4f85cc5f3a1164ca7e8c28f87077f`.

| Case | Status | Estimated latency (ms) | Baseline (ms) | Reduction (%) | B1 / B2 | Depth | Budget | Utilisation | Solve (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mlp-L06 | OPTIMAL | 26069.9524 | 28130.6497 | 7.3255 | 4 / 4 | 26 | 114 | 0.228070 | 0.012476 |

B1 counts ciphertexts; B2 counts ciphertext pairs. Shared nodes are charged once.
`OPTIMAL` refers to the encoded handout model with exact integer costs and zero configured gap tolerances; it is not a claim about real FHE runtime.
`FEASIBLE` is a valid incumbent without an optimality proof. Other statuses do not contain an accepted placement. No baseline fallback is presented as an improvement.

The JSON case records include decisions, the reconstructed DAG, every level and node cost, independent checks, the raw reference score, solver bounds and resources.
Timing and RSS are local observations. Resource scope is described in each case; process RSS includes imported libraries.
Figures are generated separately from these immutable case files. See the repository README for exact commands.
