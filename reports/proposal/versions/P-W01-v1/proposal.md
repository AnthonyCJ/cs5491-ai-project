# Automated Bootstrapping Placement for Encrypted Inference

CS5491 Artificial Intelligence Project Proposal - P-W01-v1

Member 1: [Confirmed English name] | Student ID: [ID]
Member 2: [Confirmed English name] | Student ID: [ID]
Member 3: [Confirmed English name] | Student ID: [ID]
Contact email: [Email]

## Problem and motivation

We optimise bootstrapping placement for the supplied MLP and attention blocks used in encrypted inference. Multiplicative operations consume ciphertext levels, while expensive bootstrapping restores them. Fan-out and residual connections couple decisions: refreshing a producer once can benefit several consumers. Our objective is the handout's total estimated inference latency, including ordinary operators and shared insertions, subject to every original operator and level constraint.

## Method and rationale

Our Python model assigns integer operator levels, edge refresh choices and delivered levels. Shared activation variables charge each refresh once; reconstruction produces the inserted DAG. Bootstrap2 is restricted to tensors of 8 or 16 ciphertexts and charged per pair. Costs are scaled by 10,000 to preserve the supplied precision. OR-Tools CP-SAT provides the general search engine; our contribution is the formulation, reconstruction and validation workflow. This approach fits the finite levels, discrete choices and shared costs, and yields objective bounds. An independent structural and level audit, the instructor's scorer and tiny exhaustive examples check the implementation. These checks support this model, without establishing superiority over other search methods.

## Evaluation plan

The benchmark has 30 input conditions on two fixed graphs: each block at L_init = 0 through 14, with L_max = 14. We compare legal solutions against the instructor's fixed placement at the same input level. We report estimated latency, percentage reduction, ciphertext-based bootstrap counts, depth, budget and utilisation, with saved DAGs and placement diagrams. Solver time, sampled CPU memory, status and bounds are separate from estimated inference latency. S4 will freeze the formal protocol and produce placements for at least two input levels per block.

We plan to assess one local-search candidate starting from the instructor's legal placement. Its design, implementation and inclusion in formal comparison remain pending. Evaluation will consider legal full-cost quality against the baseline and known model optima, resource use and validation effort, with disclosed initial information and timing boundaries. No candidate performance claim is available; CP-SAT remains the main method.

## Progress and delivery

S1 calibrated all 30 baselines. S3-OPT-001 now covers all 30 inputs with validated improvements and matching optimal bounds for the encoded course model. Preliminary estimated-latency reductions are 7.32-22.11% for MLP and 14.68-22.44% for attention. These stage results precede S4 frozen experiments and S6 independent reproduction; they are not real FHE timings or cross-device guarantees. The milestone is due 19 November and the final report on 3 December. The method requires no training, GPU or LLM API. This is a content-review draft; formal identities and submission preparation remain pending.
