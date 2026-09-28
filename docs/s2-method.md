# Shared refresh formulation

Method version: `shared-refresh-cp-sat-v1`. The project implements the model,
reconstruction and validation; Google's [OR-Tools CP-SAT](https://developers.google.com/optimization/cp/cp_solver)
provides the general search engine. The exact dependency used is
[OR-Tools 9.15.6755](https://pypi.org/project/ortools/9.15.6755/).
The required graph and cost definitions remain those of the calibrated
course handout, summarized in [rules and metrics](rules-and-metrics.md).

## Variables and constraints

The graph is fixed. No original operator, edge or ciphertext count is removed.
For each original node v, use integer input level a_v and output level b_v in
0..14. A source has a_v = L_init; an ordinary operator consumes its given depth,
so b_v = a_v - d_v. Enforce the operator's minimum valid input level as well as
the nonnegative output bound. There is no required block output level.

For each original edge (u,v), choose refresh mode r_uv from {0,1,2} and an
integer delivery level t_uv. Mode 0 uses u's original output, mode 1 refreshes
to 14, and mode 2 refreshes to 13. Mode 2 is available only for 8 or 16
ciphertexts. The delivery constraints are:

```text
r_uv = 0: 0 <= t_uv <= b_u
r_uv = 1: 0 <= t_uv <= 14
r_uv = 2: 0 <= t_uv <= 13
a_v = min(t_uv for all predecessors u of v)
```

If delivery is below the selected available level, insert a strict Modswitch.
Otherwise omit it. The minimum at a merge follows the reference scorer's free
alignment rule. Decisions after the block's input Identity cover input-edge
refreshes and switches.

For each producer u and eligible refresh type k, a Boolean y_uk is the logical
OR of all outgoing edges that choose k. Its cost is paid once. Both types can
exist after the same producer; the model does not introduce an unjustified
mutual-exclusion restriction. Edges may read the raw output, a shared refresh,
or distinct lower levels after that refresh.

## Objective and numerical precision

Minimise the sum of all original-node latency functions and the active refresh
costs. A B1 activation costs `ct_u * 1040.15` ms; a B2 activation costs
`(ct_u / 2) * 1293.13` ms. All Modswitch costs are zero. Ordinary operator
costs are per operator and are not multiplied by ciphertext count.

All coefficients are multiplied by 10,000 before building the integer
objective. This exactly preserves the handout's four-decimal coefficients.
A conservative absolute-expression bound is checked below 2^53, which also
keeps the reported objective exactly representable in a double. Both CP-SAT
gap tolerances are zero. No objective rounding is used to claim improvement.

A validated saved teacher baseline supplies a feasible upper bound and search
hints. It cannot remove a better solution. A returned baseline-equivalent
incumbent would be recorded as no improvement; there is no silent fallback
labelled as an optimisation success.

## Equivalence to the six allowed chains

Every edge assignment maps to one allowed chain: mode 0 yields empty or M;
mode 1 yields B1 or B1-M; mode 2 yields B2 or B2-M. A strict drop is the only
reason to create M. Its output level equals the chosen delivery level.

Conversely, every handout chain fixes a refresh mode and delivery level in
these domains. Chains from one producer with the same refresh type activate
the same y variable. Thus the shared refresh cost equals the cost of its one
distinct inserted node. Zero-cost Modswitches need no objective activation
variable, but they still become actual nodes in the reconstructed graph.

The reconstructor uses keys `(producer, refresh type)` for refreshes and
`(producer, refresh type, target level)` for switches. It thereby shares every
identical prefix and preserves the original graph when inserted chains are
removed. The assignment and reconstructed DAG have identical levels and cost.
This establishes the model's correspondence with the specified chain problem;
it is also checked on small exhaustive cases and each saved course solution.

An `OPTIMAL` status with a matching bound establishes optimality for this
encoded handout problem. It does not establish measured FHE performance or a
claim beyond the supplied graphs and fitted latency functions. A `FEASIBLE`
status would provide only a validated incumbent and an explicit bound gap.

## Algorithm and implementation

1. Validate the original DAG and load the verified fixed baseline.
2. Build the finite-domain model, exact objective, baseline bound and hints.
3. Run one CPU search worker with seed 5491 and a 60-second per-case ceiling.
4. Extract levels and decisions only for a feasible solver status.
5. Reconstruct canonical shared nodes, run the independent audit and teacher scorer,
   and compare their levels, counts, budget, depth and costs with the assignment.
6. Save the accepted graph, decisions, metrics, bound, actual time, memory and source version.

The key modules are `s2_model.py`, `s2_placement.py`, `s2_validation.py` and
`s2_runner.py` under `src/bootplacement`. The original S1 audit is reused
unchanged for structural and decimal checks. `s2_oracle.py` independently
enumerates tiny edge choices without using CP-SAT or the reconstructor.

The model size grows linearly in the supplied nodes and edges, but this is
not a polynomial-time guarantee for search. Limits and failures must still be
recorded on larger graphs. No claim is made for the optional combined block.

## What S2 found

[S2-OPT-001](../results/S2-OPT-001/README.md) covers all 15 MLP inputs and only
Attention inputs 0, 9 and 14. All 18 are validated improvements with matching
optimal bounds. The full 30-case optimiser experiment has not been completed.

At MLP input 14, the saved optimum removes the early B1 on four ciphertexts,
saving 4160.60 ms, while Conjugate X costs 2.24 ms more than in the input-0
solution. All other nonzero node costs match. This explains the 4158.36 ms
difference between their optimal totals. See the two saved placement diagrams.

At Attention input 0, the new bootstrap count is 18 (B1=10, B2=8), versus 17
for the teacher baseline (B1=9, B2=8), yet estimated latency decreases by
14.6755%. Level-dependent operator costs make bootstrap count alone an
inadequate objective.

Zero-cost switches can create multiple equally optimal placements. Numerical
score reproducibility and exact saved-placement identity are different checks.
The saved DAG, rather than a newly selected tie, is the source for each figure.
