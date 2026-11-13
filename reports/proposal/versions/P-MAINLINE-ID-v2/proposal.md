# Automated Bootstrapping Placement for Encrypted Inference

CS5491 Artificial Intelligence Project Proposal

Member 1: Xing Chunjie | Student ID: 72655910
Member 2: Yang Mianji | Student ID: 72655251
Member 3: Zhang Qi | Student ID: 72655380
Contact email: 72655910@cityu-dg.edu.cn

## Problem and motivation

We study where to insert bootstrapping in the supplied multilayer perceptron (MLP) and attention blocks for encrypted inference. In the course model, ciphertext levels represent the remaining capacity for multiplication; bootstrapping restores levels but adds substantial latency. Placement decisions interact across branches: one refresh can serve several consumers, while the chosen levels also change ordinary operator costs. Minimising refresh count alone can therefore miss a faster placement. Our goal is to minimise total estimated inference latency while preserving the supplied computation and satisfying every operator's level requirements.

## Method and rationale

These coupled choices call for a joint optimisation model that decides levels and insertions together. We use OR-Tools CP-SAT, a solver for integer and logical constraints, because the available levels and insertion choices are finite and discrete. Our model enforces operator requirements and refresh eligibility, counts shared costs once and minimises the full latency objective. We implemented this formulation, graph reconstruction and independent legality checks; the instructor provides the graphs, latency functions and scorer, and OR-Tools provides the general search engine. The validated teacher placement guides the search and rules out higher-cost solutions. CP-SAT also reports a lower bound on achievable cost, allowing us to assess whether a returned solution is optimal within this model.

## Evaluation plan

We compare our method with the instructor's fixed placement on both blocks, each at input levels 0 through 14 with maximum level 14 (30 conditions). Comparisons use valid placements at the same input level and include all ordinary operator and shared refresh costs. We will report estimated latency and its percentage reduction, refresh counts (Bootstrap1 ciphertexts and Bootstrap2 pairs), maximum path level consumption (depth), level budget and their ratio (utilisation). Saved graphs and placement diagrams for at least two input levels per block will show where operations are inserted. A fixed experimental protocol will record solver time, sampled process memory, status and bounds separately from estimated inference latency.

## Progress and remaining work

We have calibrated all 30 baselines and completed preliminary comparisons across all conditions. All reconstructed placements passed independent structural and level checks and were scored with the instructor's function. Estimated-latency reductions are 7.32-22.11% for MLP and 14.68-22.44% for attention. Matching solver objectives and lower bounds establish optimality within the encoded course model; tiny exhaustive examples provide an additional correctness check. These model estimates do not establish real encrypted-inference or cross-device performance. Remaining work is to freeze the final experimental protocol, complete formal resource and placement reporting, and reproduce the results independently.
