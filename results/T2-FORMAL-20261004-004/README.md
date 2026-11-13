# Formal comparison of bootstrapping placement

The placement optimizer passed a fresh comparison against the fixed teacher baseline for all 30 required conditions: MLP and Attention, each with input levels 0–14 and maximum level 14. Every saved solution is legal, strictly improves the baseline's total estimated latency, and has an optimal objective matching the solver's lower bound. These are results under the encoded course cost and level model, not measurements of encrypted inference.

The method, `shared-refresh-cp-sat-v1`, and numerical implementation are unchanged. Shared inserted operations are charged once, and the comparison includes ordinary operations, Bootstrap1, Bootstrap2 and Modswitch costs. Each new result was reconstructed into a DAG and checked again from its saved representation without another search. The fixed baseline was independently audited and teacher-scored during each saved-result check. All exact objectives agree with the earlier full-instance results; the earlier results were used as a consistency reference, not substituted for this run.

## Results and evidence

| Module | Input levels | Conditions | Optimized estimated latency (ms) | Reduction from the same-level baseline |
|---|---|---:|---:|---:|
| MLP | 0–13 | 14 | 26069.9524 | 7.3223%–7.3291% |
| MLP | 14 | 1 | 21911.5924 | 22.1113% |
| Attention | 0–5 | 6 | 45698.2664 | 14.6755% |
| Attention | 6–14 | 9 | 41537.6664 | 22.4438% |

[summary.csv](summary.csv) and [summary.json](summary.json) contain all 30 rows, exact costs, cost components, refresh counts, depth, budget, utilisation, solver bounds, timings and source hashes. Each row points to its saved run and its independent check. The run's case JSON contains the solution and reconstructed nodes and edges. [condition-status.json](condition-status.json) records the per-condition run/check association.

The frozen [protocol](protocol.json) uses one search thread, seed 5491, a 60-second solver limit, zero absolute and relative gap, a cost scale of 10000 per millisecond, and the original validated baseline hint and upper bound. Teacher-score agreement is checked within 0.0000001 ms. Each condition was run once; no repair or retry was used after dynamic execution began. The raw interface retains its historical `S2` field, while this package identifies the formal comparison as T2 within S4.

## Process evidence and local resource observations

Before the comparison, six bounded executions tested fast-process handover, an explicitly marked optional-image-query failure, two sequential real Git processes with a controlled discovery interleaving, normal preflight, early business failure, and controlled timeout. A separate data-only check rejected historical incomplete evidence. All required gates passed before any formal condition was dispatched; see [validation-summary.json](validation-summary.json).

The new association check reads each child's intent, creation and identity records directly by sequence. It verifies the attempt identity, parent relation, PID, creation time and expected command instead of treating an old discovery cache as evidence that a creation record is absent. The controlled interleaving recorded the second real creation after an earlier discovery snapshot. It tests that ordering on the new controller; it does not reconstruct the exact schedule of a historical failure.

The worker closes and seals its creation registry before declaring that no further child can be created. In the timeout test it did so before entering the wait. The observer verifies that seal against the original records and collects exit codes and final CPU only after exit signals. An unsealed registry remains incomplete even when every known process has a final record.

| Recorded quantity | Value | Scope |
|---|---:|---|
| Dynamic attempts | 66 | 6 validation executions, 30 runs, 30 saved-result checks |
| Controlled processes with final records | 265 / 265 | Observer, launcher, worker and explicitly created children; every new creation registry reconciled |
| Sum of recorded attempt windows | 201.9114114 s | Controlled launches through collection; preparation and delivery time are separate |
| Sum of process CPU | 220.515625 s | Includes 156.671875 s of observer CPU; do not add that again |
| Sum of solver wall time | 10.6562887000473 s | Nested within run attempts, not added to their wall time |
| Largest core sampled RSS | 123621376 bytes | Worker core interval; approximately 117.895 MiB |
| Largest observed held-process RSS sum | 128081920 bytes | Concurrent held launcher/worker/child samples; approximately 122.148 MiB |

[attempt-resources.json](attempt-resources.json) preserves every attempt and per-process final CPU/exit value in a form without private machine paths. The 20 ms sampling interval is a target: the largest observed interval was 0.1952339 s. Sampling and per-process lifetime peaks do not establish an exact simultaneous process-tree or whole-machine peak. The observer, tool host and app are outside the held-process RSS sum; tool-host/app lifecycle CPU was not measured. There were 66 missing optional image queries, including one explicitly injected diagnostic. Required identity, creation, exit and CPU evidence remained complete in every new attempt.

Three earlier control attempts remain preserved as historical failures. Earlier P001/Q001 lifecycle gaps are still unknown. Q101 has final exit and CPU records for five known processes, but its creation registry is unsealed, so its complete creation universe is not certified. A narrowly authorized continuation exception allowed this isolated run without changing those historical facts. No such exception was applied to a new attempt, and no precise all-history resource total is claimed.

## Version and numerical reproduction

The comparison ran locally on Windows with CPython 3.13.9 and the existing pinned environment, including OR-Tools 9.15.6755. The recorded repository HEAD was `aa89f7bb870b1f11d305946f007b1cbb76073b2f`, with local changes; it is not a substitute for the executed-byte fingerprints. [inputs.sha256.json](inputs.sha256.json) identifies the public frozen inputs, each run records its source fingerprint, and [artifacts.sha256.json](artifacts.sha256.json) binds the saved delivery. The frozen private controller manifest hash is `91afa68823015b5baa173eba8f173512aa40bb0b84369d222f52ae1e893079f5`.

From the repository root, with the documented pinned environment already available, the following command reproduces the numerical conditions and saved-result checks into a new directory:

```powershell
& ./results/T2-FORMAL-20261004-004/reproduce-numerics.ps1 -OutputDirectory results/T2-numerical-reproduction
```

The [script](reproduce-numerics.ps1) refuses an existing destination and calls the unchanged optimizer and checker for each frozen configuration. It was supplied as a reproduction entry, not executed again for this delivery. It does not claim to reproduce this run's Windows process instrumentation or complete an independent-environment reproduction. The measured supervised attempt total above describes this run and is not a runtime guarantee for that script or another device.

The 30-condition numerical and process-evidence checks passed. Human review is pending. Analysis and placement figures remain a separate task, and independent reproduction, final report readiness, publication and course submission remain outstanding. This package does not change the previously reviewed Proposal or Milestone.
