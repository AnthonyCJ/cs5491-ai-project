# S3-OPT-001: full-instance S3 evidence

Method: `shared-refresh-cp-sat-v1`. Full 30-instance stage validation; not the frozen S4 experiment.
Actual CPU searches; fitted inference scores are not real FHE timings.
Execution commit: `415f2a91462fb361782b84756a552ad85f44a7b5`.
Source SHA-256: `7a71e0079618ffd5acc911d5eb1b1629340f76f2494a0e3ffcc94efb3eefe146`.

| Case | Status | Estimated latency (ms) | Baseline (ms) | Reduction (%) | B1 / B2 | Depth | Budget | Utilisation | Solve (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| mlp-L00 | OPTIMAL | 26069.9524 | 28129.6897 | 7.3223 | 4 / 4 | 26 | 108 | 0.240741 | 0.013237 |
| mlp-L01 | OPTIMAL | 26069.9524 | 28129.8497 | 7.3228 | 4 / 4 | 26 | 109 | 0.238532 | 0.007781 |
| mlp-L02 | OPTIMAL | 26069.9524 | 28130.0097 | 7.3233 | 4 / 4 | 26 | 110 | 0.236364 | 0.007553 |
| mlp-L03 | OPTIMAL | 26069.9524 | 28130.1697 | 7.3239 | 4 / 4 | 26 | 111 | 0.234234 | 0.007530 |
| mlp-L04 | OPTIMAL | 26069.9524 | 28130.3297 | 7.3244 | 4 / 4 | 26 | 112 | 0.232143 | 0.009211 |
| mlp-L05 | OPTIMAL | 26069.9524 | 28130.4897 | 7.3249 | 4 / 4 | 26 | 113 | 0.230088 | 0.009493 |
| mlp-L06 | OPTIMAL | 26069.9524 | 28130.6497 | 7.3255 | 4 / 4 | 26 | 114 | 0.228070 | 0.009727 |
| mlp-L07 | OPTIMAL | 26069.9524 | 28130.8097 | 7.3260 | 4 / 4 | 26 | 115 | 0.226087 | 0.009503 |
| mlp-L08 | OPTIMAL | 26069.9524 | 28130.9697 | 7.3265 | 4 / 4 | 26 | 116 | 0.224138 | 0.009244 |
| mlp-L09 | OPTIMAL | 26069.9524 | 28131.1297 | 7.3270 | 4 / 4 | 26 | 117 | 0.222222 | 0.010609 |
| mlp-L10 | OPTIMAL | 26069.9524 | 28131.2897 | 7.3276 | 4 / 4 | 26 | 118 | 0.220339 | 0.010136 |
| mlp-L11 | OPTIMAL | 26069.9524 | 28131.4497 | 7.3281 | 4 / 4 | 26 | 119 | 0.218487 | 0.009537 |
| mlp-L12 | OPTIMAL | 26069.9524 | 28131.6097 | 7.3286 | 4 / 4 | 26 | 120 | 0.216667 | 0.009018 |
| mlp-L13 | OPTIMAL | 26069.9524 | 28131.7697 | 7.3291 | 4 / 4 | 26 | 121 | 0.214876 | 0.008981 |
| mlp-L14 | OPTIMAL | 21911.5924 | 28131.9297 | 22.1113 | 0 / 4 | 26 | 66 | 0.393939 | 0.009760 |
| attention-L00 | OPTIMAL | 45698.2664 | 53558.1718 | 14.6755 | 10 / 8 | 62 | 244 | 0.254098 | 0.579027 |
| attention-L01 | OPTIMAL | 45698.2664 | 53558.1718 | 14.6755 | 10 / 8 | 62 | 245 | 0.253061 | 0.577750 |
| attention-L02 | OPTIMAL | 45698.2664 | 53558.1718 | 14.6755 | 10 / 8 | 62 | 246 | 0.252033 | 0.898975 |
| attention-L03 | OPTIMAL | 45698.2664 | 53558.1718 | 14.6755 | 10 / 8 | 62 | 247 | 0.251012 | 0.918392 |
| attention-L04 | OPTIMAL | 45698.2664 | 53558.1718 | 14.6755 | 10 / 8 | 62 | 248 | 0.250000 | 0.845131 |
| attention-L05 | OPTIMAL | 45698.2664 | 53558.1718 | 14.6755 | 10 / 8 | 62 | 249 | 0.248996 | 0.965590 |
| attention-L06 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 194 | 0.319588 | 0.516612 |
| attention-L07 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 195 | 0.317949 | 0.596819 |
| attention-L08 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 196 | 0.316327 | 0.687947 |
| attention-L09 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 197 | 0.314721 | 0.618816 |
| attention-L10 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 198 | 0.313131 | 0.567639 |
| attention-L11 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 199 | 0.311558 | 0.857376 |
| attention-L12 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 200 | 0.310000 | 0.625927 |
| attention-L13 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 201 | 0.308458 | 0.654651 |
| attention-L14 | OPTIMAL | 41537.6664 | 53558.1718 | 22.4438 | 6 / 8 | 62 | 202 | 0.306931 | 0.592549 |

B1 counts individual ciphertexts; B2 counts pairs. Shared operations are counted once.
OPTIMAL and its matching bound apply to the encoded handout model. FEASIBLE alone is not an optimality proof.
Cases, summary.json, tiny-examples.json and the hash manifest preserve decisions, full DAGs, scores, bounds and resource observations.
s2-comparison.json compares the 18 earlier exact scores without rewriting S2. Timing and tied placements may change.
The independent audit and teacher scorer are applied to every accepted placement. Failures are retained, never silently replaced by a baseline.
S4 frozen experiments, S6 independent reproduction, public hosting and formal submission remain separate work.
