# S2-OPT-001: S2 optimisation evidence

Method: `shared-refresh-cp-sat-v1`. Scope: MLP coverage and representative Attention feasibility.

These are actual CPU optimisation runs scored with fitted inference costs. No encrypted inference was executed.
This S2 run does not replace S4 formal experiments or S6 independent reproduction.

Source fingerprint: `44f430c354686ba5fdd48d40ec350ac1d1ef6f5cbf4e27d465162421511bbcc3`.

| Case | Status | Estimated latency (ms) | Baseline (ms) | Reduction (%) | B1 / B2 | Depth | Budget | Utilisation | Solve (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mlp-L00 | OPTIMAL | 26069.9524 | 28129.6897 | 7.3223 | 4 / 4 | 26 | 108 | 0.240741 | 0.013067 |
| mlp-L01 | OPTIMAL | 26069.9524 | 28129.8497 | 7.3228 | 4 / 4 | 26 | 109 | 0.238532 | 0.007948 |
| mlp-L02 | OPTIMAL | 26069.9524 | 28130.0097 | 7.3233 | 4 / 4 | 26 | 110 | 0.236364 | 0.007534 |
| mlp-L03 | OPTIMAL | 26069.9524 | 28130.1697 | 7.3239 | 4 / 4 | 26 | 111 | 0.234234 | 0.007926 |
| mlp-L04 | OPTIMAL | 26069.9524 | 28130.3297 | 7.3244 | 4 / 4 | 26 | 112 | 0.232143 | 0.009494 |
| mlp-L05 | OPTIMAL | 26069.9524 | 28130.4897 | 7.3249 | 4 / 4 | 26 | 113 | 0.230088 | 0.010016 |
| mlp-L06 | OPTIMAL | 26069.9524 | 28130.6497 | 7.3255 | 4 / 4 | 26 | 114 | 0.228070 | 0.009692 |
| mlp-L07 | OPTIMAL | 26069.9524 | 28130.8097 | 7.3260 | 4 / 4 | 26 | 115 | 0.226087 | 0.010116 |
| mlp-L08 | OPTIMAL | 26069.9524 | 28130.9697 | 7.3265 | 4 / 4 | 26 | 116 | 0.224138 | 0.010215 |
| mlp-L09 | OPTIMAL | 26069.9524 | 28131.1297 | 7.3270 | 4 / 4 | 26 | 117 | 0.222222 | 0.011331 |
| mlp-L10 | OPTIMAL | 26069.9524 | 28131.2897 | 7.3276 | 4 / 4 | 26 | 118 | 0.220339 | 0.010414 |
| mlp-L11 | OPTIMAL | 26069.9524 | 28131.4497 | 7.3281 | 4 / 4 | 26 | 119 | 0.218487 | 0.009133 |
| mlp-L12 | OPTIMAL | 26069.9524 | 28131.6097 | 7.3286 | 4 / 4 | 26 | 120 | 0.216667 | 0.009721 |
| mlp-L13 | OPTIMAL | 26069.9524 | 28131.7697 | 7.3291 | 4 / 4 | 26 | 121 | 0.214876 | 0.009370 |
| mlp-L14 | OPTIMAL | 21911.5924 | 28131.9297 | 22.1113 | 0 / 4 | 26 | 66 | 0.393939 | 0.009526 |
| attention-L00 | OPTIMAL | 45698.2664 | 53558.1718 | 14.6755 | 10 / 8 | 62 | 244 | 0.254098 | 0.610839 |
| attention-L09 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 197 | 0.314721 | 0.635640 |
| attention-L14 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 202 | 0.306931 | 0.613328 |

B1 counts ciphertexts; B2 counts ciphertext pairs. Shared nodes are charged once.
`OPTIMAL` refers to the encoded handout model with exact integer costs and zero configured gap tolerances; it is not a claim about real FHE runtime.
`FEASIBLE` is a valid incumbent without an optimality proof. Other statuses do not contain an accepted placement. No baseline fallback is presented as an improvement.

The JSON case records include decisions, the reconstructed DAG, every level and node cost, independent checks, the raw reference score, solver bounds and resources.
Timing and RSS are local observations. Resource scope is described in each case; process RSS includes imported libraries.
Figures are generated separately from these immutable case files. See the repository README for exact commands.
