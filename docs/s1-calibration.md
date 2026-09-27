# S1 calibration evidence

Run [S1-BL-001](../results/S1-BL-001/README.md) was executed on 2026-09-27
at 04:47:35 UTC. Its exact configuration and source fingerprint are in
[run.json](../results/S1-BL-001/run.json). All 30 cases passed.

## Three checks of each baseline

1. Load the byte-verified instructor file and obtain the given fixed placement.
   Call `evaluate_dag`, `depth_of` and `budget_of` without changing those functions.
2. Independently check original-graph preservation, ciphertext counts, allowed
   insertion chains, shared prefixes, integer/range constraints, merge levels,
   B2 eligibility, counts, depth and budget. Recalculate each node's latency
   using decimal coefficients transcribed from the PDF.
3. Compare full reference scores within **1e-7 ms**, require the same displayed
   two-decimal result, and compare counts/depth/budget with the PDF. Match the
   MLP endpoint range and level-6 anchor, and all 15 Attention scores. The
   intermediate MLP values are independently computed, not claimed to have
   individual printed rows in the PDF.

| Checkpoint | Executed exact-decimal score (ms) | PDF display (ms) |
|---|---:|---:|
| MLP, input 0 | 28129.6897 | 28129.69 |
| MLP, input 6 | 28130.6497 | 28130.65 |
| MLP, input 14 | 28131.9297 | 28131.93 |
| Attention, every input | 53558.1718 | 53558.17 |

MLP increases by exactly 0.16 ms per input level because Conjugate X precedes
the first refresh. Attention's first refresh removes its input-level dependence.
These explanations are consistent with the stored node-level cost breakdowns.
No discrepancy remains at the handout's display precision.

## Checks and reproduction boundary

Twelve unit checks passed in the same environment before the run. They cover
shared B2 charging, minimum-level merges, invalid B2 ciphertext counts,
duplicated shared prefixes, removed branches, Modswitch depth, level underflow,
noninteger/out-of-range inputs, zero-drop Modswitch, cycles and changed reference
bytes. They use small counterexamples rather than just replaying result tables.
`pip check` reported no broken requirements.

The run directory has 30 detailed case records, a summary CSV, a calibration
record, execution metadata, a report and an artifact hash manifest. The
`verify` command checks saved files, the source version and instance coverage
without another scorer run. This is local S1 evidence, not an S6 independent
clean-machine reproduction or a proof that future optimisation models are valid.

The local run occurred before the first successful Git commit. A source
fingerprint plus the per-file hashes identifies its executable version; the
subsequent local commit includes these same source bytes and the saved evidence.
Do not invent a pre-run commit hash or replace that null metadata field.

## Resource observations

| Quantity | Observed value | Scope |
|---|---:|---|
| Import and 30-case pipeline wall time | 2.8012145 s | Includes import, audits, scores and case/summary writes |
| Sum of reference evaluation wall times | 0.0047106 s | `evaluate_dag`, `depth_of`, `budget_of` for 30 fixed placements |
| Process CPU time | 0.703125 s | Measured pipeline interval |
| Sampled maximum RSS | 69,115,904 bytes | Samples after import and each case |
| Windows peak working set | 70,893,568 bytes | Current process lifetime high water mark |

Measurements exclude interpreter startup and final report/manifest writes.
No GPU, placement search or real encrypted inference was used. A single local
observation is not a speed benchmark or a guarantee for a teammate's laptop.
Resource data uses the current process's [psutil memory information](https://psutil.io/).
Package versions and platform family are recorded without user names or paths.

## Next technical work

S2 must build an original model and optimiser, first cover MLP's 15 inputs,
validate reconstruction and check representative Attention cases. A feasible
placement is not an improvement unless its latency is smaller than the
same-input teacher baseline, and it is not proven optimal without appropriate
solver evidence. No optimisation success is claimed by S1.
