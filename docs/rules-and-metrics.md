# Rules, latency functions and terminology

Source: **Automated Bootstrapping Placement**, course snapshot obtained
2026-09-24, Sections 2 and 4.1-4.5, especially pp. 3-4 and 6-10.
[Canvas topic PDF](https://cityu-dg.instructure.com/courses/911/files/180071/download?download_frd=1).
Later Canvas updates have not been verified.

## Required instances and objective

Solve the MLP block first, then Attention. Each block is a separate problem for
all integer input levels `L_init = 0..14`, with `L_max = 14`: 30 instances.
There is no required output level. Minimise total **estimated inference latency**,
not merely bootstrap count. No real FHE library or model training is required.
Joint optimisation of the connected blocks is optional (Section 4.6).

An ordinary operator with cost `d` consumes `d` levels. Its input must be in
the stated valid range and its output must be nonnegative. At a merge, the input
level is the minimum incoming level; switching the higher input down is free.
All levels remain integers in `[0,14]`.

## Insertions, sharing and ciphertexts

On any original edge, including the block input, the allowed chains are:
empty, B1, B2, M, B1-M, B2-M. Modswitch lowers a level strictly and costs zero.
Two chains from the same original node that start with the same operators
share those prefixes: represent each shared operation by one real DAG node.
Pay each distinct inserted node once, even if it has several readers.

- B1 restores level 14, costs 1,040.15 ms per ciphertext and contributes `#ct` to B1 count.
- B2 restores level 13 and costs 1,293.13 ms per pair; it contributes `#ct/2` to B2 count.
  It is allowed only where `#ct` is 8 or 16 in these graphs.
- An inserted node preserves the edge's tensor ciphertext count. B2 pairs its
  work; it does not halve the stored edge count.
- Conjugate, Conjugate back, Sum and Rotate are already part of the given graphs.
  They cannot be freely inserted or removed. Original edges and ciphertext
  counts must survive removal of the inserted chains.

## Operator latency table

`l` is the input level; costs below are milliseconds **per operator**, except
for the explicit B1/B2 multiplicities. Ordinary operator costs are not multiplied
again by the edge ciphertext count.

| Operator | Level cost | Valid input | Latency (ms) |
|---|---:|---|---|
| PCMM1 | 2 | 2..14 | 366.20*l + 1797.71 |
| PCMM2 | 2 | 2..14 | 104.64*l + 2262.12 |
| PCMM3 | 2 | 2..14 | 443.12*l + 1581.48 |
| PCMM4 | 2 | 2..14 | 377.74*l + 2095.11 |
| CCMM1 | 4 | 4..14 | 529.58*l - 159.50 |
| CCMM2 | 2 | 2..14 | 98.67*l + 1566.84 |
| PolyEval1 | 5 | 5..14 | 142.64*l - 455.72 |
| PolyEval2 | 5 | 5..14 | 145.59*l - 409.08 |
| PolyEval3 | 8 | 8..14 | 562.27*l + 819.37 |
| PolyEval4 | 8 | 8..14 | 460.34*l + 1311.36 |
| Mul | 1 | 1..14 | 0.0663*l + 0.4192 |
| Add | 0 | 0..14 | 0.0034*l + 0.0379 |
| Conjugate | 0 | 0..14 | 0.16*l + 1.67 |
| Conjugate back | 0 | 0..14 | 0.60*l + 2.02 |
| Sum | 0 | 0..14 | 4.06 |
| Rotate, Identity | 0 | 0..14 | 0 |
| B1 | refresh to 14 | 0..14 | 1040.15 per ciphertext |
| B2 | refresh to 13 | 0..14 | 1293.13 per pair |
| Modswitch | chosen positive drop | sufficient for drop | 0 |

The handout scorer uses binary floats. The independent S1 audit uses these
decimal coefficients exactly. Preserve the raw score and full decimal result;
round only when displaying a value. Four decimal places suffice for exact
integer-level costs in this table. Any future integer objective should preserve
this precision and check its numerical range.

## Reported metrics

| Term | Definition / unit |
|---|---|
| Placement | Original-edge chains plus actual inserted/shared nodes |
| Estimated latency | Sum of all original and distinct inserted operator costs, ms |
| B1 count | Sum of ciphertext counts into B1 nodes |
| B2 count | Sum of ciphertext pairs into B2 nodes |
| Bootstrap count | B1 count + B2 count; not the number of drawn refresh nodes |
| Depth | Maximum original level cost along a path; inserted B1/B2/M add zero |
| Budget | 14*B1 + 13*B2 + L_init |
| Utilisation | Depth / budget; a reported ratio, not the optimisation objective |
| Evaluation wall time | Measured local time spent scoring a fixed graph, seconds |
| Solver wall time | Future time spent finding a placement; not measured in S1 |

For each input level, report latency, counts, depth, budget, utilisation and
placement. The course asks for diagrams for at least two input levels; the
project plan is at least two per module. S1 retains numeric placed graphs for
all 30 cases. Final optimised placement diagrams remain later work.

Use the scorer on a reconstructed inserted DAG. Its accepting a graph alone is
not proof of all rules: it does not explicitly enforce B2 eligibility, all
operator domains, original-graph preservation or canonical shared chains.
S1 adds independent checks for those conditions on the fixed baselines.

## Version and graph-label caution

The instructor's descriptions contain sample labels such as `X (in, L=9)`.
They are preserved as source text and are not the level of every instance.
Actual per-instance levels are the numeric `l_in`, `l_out` and `edge_levels`
fields in each saved case. Do not infer an input condition from a description.
