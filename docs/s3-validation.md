# S3 full-instance validation

Evidence: [S3-OPT-001](../results/S3-OPT-001/README.md), executed 2026-09-28.
Method remains `shared-refresh-cp-sat-v1`; the S2 formulation, reconstruction,
independent audit, reference file and historical records are unchanged.
The new S3 runner adds an exact 30-case configuration, persistent case states,
uniform output and verification of all summaries and historical comparisons.

## Results and interpretation

All 30 actual searches returned OPTIMAL with matching bounds, valid reconstructed
DAGs and lower exact costs than their same-module, same-input S1 baselines.
There were no failed, unsolved, timed-out, non-improving or fallback course cases.
All 18 overlapping scores match S2 exactly; tied zero-cost switches need not match.

| Module and input levels | Estimated latency (ms) | Reduction (%) | B1 / B2 | Budget |
|---|---:|---:|---:|---|
| MLP 0..13 | 26069.9524 | 7.3223..7.3291 | 4 / 4 | 108 + L_init |
| MLP 14 | 21911.5924 | 22.1113 | 0 / 4 | 66 |
| Attention 0..5 | 45698.2664 | 14.6755 | 10 / 8 | 244 + L_init |
| Attention 6..14 | 41537.6664 | 22.4438 | 6 / 8 | 188 + L_init |

Depth is 26 for MLP and 62 for Attention. Utilisation is depth/budget.
B1 counts individual ciphertexts, B2 counts pairs, and their sum is the reported
bootstrap count. Shared operations are charged once. Every input's complete
metrics and graph are saved, even where a range has the same score.

Attention's threshold is input 6. Comparing its saved input-0 and input-6
solutions, the only change in nonzero node costs is the removed B1 after the
input, worth 4 * 1040.15 = 4160.60 ms. At input 6, Q and K PCMM1 receive level
6 and output level 4 to CCMM1. This explains the saved solution's change; the
individual optimal solver results establish all 15 values. At input 0 the new
bootstrap count is 18 versus 17 for the baseline, yet cost decreases. Minimising
bootstrap count alone would miss the level-dependent ordinary-operator costs.

For MLP, the input-14 solution removes a B1 on four ciphertexts compared with
input 0, saving 4160.60 ms; Conjugate X costs 2.24 ms more. All other nonzero
costs agree. The total difference is 4158.36 ms.

## Checks and version linkage

- Execution commit: `415f2a91462fb361782b84756a552ad85f44a7b5`, clean at run time.
- Source fingerprint: `7a71e0079618ffd5acc911d5eb1b1629340f76f2494a0e3ffcc94efb3eefe146`.
- The [test receipt](s3-checks.json) records 44 passed checks: the existing 28
  and 16 new coverage, evidence and failure-path checks.
- Six tiny examples were independently enumerated again for this run. Their
  costs agree with hand arithmetic, CP-SAT, reconstruction, independent audit
  and teacher scoring. See [saved examples](../results/S3-OPT-001/tiny-examples.json).
- Every course solution is independently audited, reconstructed and scored.
  Float/decimal tolerance remains 1e-7 ms; exact decimal values determine improvement.
- Verification checks source and result hashes, all 30 case identities, the
  persistent ledger, exact configuration, solver settings, every saved DAG,
  all CSV/JSON/report totals, and the immutable S1/S2 links.
- The unit suite deliberately injects solver errors and a falsified success
  summary. Those temporary records are test fixtures, not course experiments.

The S3 source manifest covers the numeric runner, shared source, configuration
and tests. Plot generation has separate provenance, including every source-case
hash and its generator hash. The Milestone has its own source/build/PDF hashes.
The material commit containing figures and reports is later than the execution
commit; neither is retroactively substituted into the run record.

## Actual local resources and limitations

One CPU worker, seed 5491, 60 seconds per instance, CPython 3.13.9 and OR-Tools
9.15.6755. All 19 pinned dependencies match and `pip check` passes.
The 30 solve calls total 10.6445215 seconds. MLP ranges from 0.0075298 to
0.0132371 seconds; Attention ranges from 0.5166124 to 0.9655904 seconds.
Maximum sampled process RSS is 124104704 bytes (118.3555 MiB).

RSS includes imported libraries and uses 20 ms samples, not an exact per-case
peak. The separately saved Windows working-set peak spans the process lifetime.
Pipeline intervals cover model construction, solving, reconstruction and
validation; baseline preparation, reference import and result writing are
outside them. Estimated inference latency is a fitted cost, not any of these
measured durations and not a real FHE benchmark.

S3 does not replace S4's frozen experiment and at least two placement levels per
module, or S6's independent clean-environment reproduction. Teammate devices
have not been tested. The [Milestone draft](../reports/milestone/README.md) still
needs formal identities, resolved instructor-code redistribution permission and
an online public repository before its complete submission requirements are met.
No publication or course submission has occurred.
