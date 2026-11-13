# Automated Bootstrapping Placement for Encrypted Inference

CS5491 Artificial Intelligence Project Proposal - P-MAINLINE-ID-v1

Member 1: Xing Chunjie | Student ID: 72655910
Member 2: Yang Mianji | Student ID: 72655251
Member 3: Zhang Qi | Student ID: 72655380
Contact email: 72655910@cityu-dg.edu.cn

## Problem and motivation

We optimise bootstrapping placement for the supplied MLP and attention blocks used in encrypted inference. Multiplicative operations consume ciphertext levels, while expensive bootstrapping restores them. Fan-out and residual connections couple decisions: refreshing a producer once can benefit several consumers. Our objective is the handout's total estimated inference latency, including ordinary operators and shared insertions, subject to every original operator and level constraint.

## Method and rationale

The instructor supplies the graphs, latency model and scoring interface. Our Python model assigns integer operator levels, edge refresh choices and delivered levels. Shared activation variables charge each refresh once; reconstruction produces the inserted DAG. Bootstrap2 is restricted to tensors of 8 or 16 ciphertexts and charged per pair. Costs are scaled by 10,000 to preserve the supplied precision. OR-Tools CP-SAT provides the general search engine; our contribution is the formulation, reconstruction and validation workflow. This approach fits the finite levels, discrete choices and shared costs, and yields objective bounds. An independent structural and level audit, the instructor's scorer and tiny exhaustive examples check the implementation. These checks support this model, without establishing superiority over other search methods.

## Evaluation plan

We evaluate CP-SAT against the instructor's fixed placement on 30 input conditions: each of the two blocks at L_init = 0 through 14, with L_max = 14. Comparisons use legal solutions at the same input level and the full latency model. We report estimated latency, percentage reduction, bootstrap counts (B1 ciphertexts and B2 pairs), depth, budget and utilisation, with saved DAGs and placement diagrams. Solver time, sampled process memory, status and bounds are separate from estimated inference latency. Formal experiments (S4) will freeze the protocol and produce placements for at least two input levels per block.

## Progress and delivery

S1 calibrated all 30 baselines. S3-OPT-001 covers all 30 inputs with validated improvements and matching optimal bounds for the encoded course model. Preliminary estimated-latency reductions are 7.32-22.11% for MLP and 14.68-22.44% for attention. These stage results precede S4 frozen experiments and S6 independent reproduction; they are not real FHE timings or cross-device guarantees. The proposal, milestone and final report are due 15 October, 19 November and 3 December 2026. The method requires no training, GPU or LLM API. This version is a content-review draft with complete team identities; human review and submission preparation remain pending.
