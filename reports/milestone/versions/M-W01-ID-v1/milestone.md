# Automated Bootstrapping Placement for Encrypted Inference

CS5491 Artificial Intelligence - Milestone content-review draft M-W01-ID-v1

Member 1: Xing Chunjie | Student ID: 72655910
Member 2: Yang Mianji | Student ID: 72655251
Member 3: Zhang Qi | Student ID: 72655380
Contact email: 72655910@cityu-dg.edu.cn

Evidence date: 29 September 2026. Identities updated 30 September 2026; online submission materials remain pending. No course submission has occurred.

## 1. Problem and objective

We optimise bootstrapping placement for the supplied MLP and attention blocks, including their LayerNorm and Softmax computations. Operators consume integer ciphertext levels; expensive bootstrapping restores them and free Modswitch lowers them. Fan-out permits several consumers to share one refreshed tensor. The objective includes all ordinary-operator and distinct inserted-operation costs under the course handout's fitted latency model.

There are 30 input conditions on two fixed graphs, not 30 independent networks: each block at L_init = 0 through 14, with L_max = 14 and no required output level. Original operators, edges and ciphertext counts are preserved. A merge uses the minimum incoming level. Bootstrap1 (B1) restores level 14 at 1040.15 ms per ciphertext. Bootstrap2 (B2) restores level 13 at 1293.13 ms per pair and is allowed only for tensors of 8 or 16 ciphertexts. Modswitch must strictly lower the level.

## 2. Method and choice rationale

Our contribution is the shared-refresh formulation, DAG reconstruction and validation workflow; OR-Tools CP-SAT supplies the general search engine. For each operator v we choose integer input/output levels a_v and b_v, enforce its input domain and b_v = a_v - d_v. Each edge (u,v) has a refresh mode r_uv in {0,1,2} and delivered level t_uv. Its available level is b_u, 14 or 13 respectively; t_uv cannot exceed it. Sources are fixed to L_init; other inputs are the minimum delivered predecessor level. B2 is disabled on ineligible tensors.

An activation per producer and refresh type is the OR of its outgoing choices. The objective charges active shared refreshes once, together with every original operator's level-dependent cost. Multiplying coefficients by 10000 preserves four-decimal costs; the checked conservative magnitude bound is below 2^53, with zero solver gap tolerances. The verified instructor placement supplies both a cost upper bound and search hints.

Finite integer levels, discrete refresh choices and coupled shared costs make this formulation appropriate. Our selection process moved from constraint modelling to baseline calibration, prototype checks and full-instance stage validation. Those observations support retaining CP-SAT at the course scale. They do not establish a speed, simplicity or scalability ranking against other methods, and the solver does not replace checking that the encoding matches the rules.

<!-- pagebreak -->

## 3. Reconstruction and validation boundaries

The model represents the permitted empty, B1, B2, M, B1-M and B2-M chains. Reconstruction inserts M only for a strict drop, keys refreshes by producer/type, and keys switches by producer/mode/target. Equal prefixes become shared nodes; different consumers can use both refresh types after one producer. Conversely, a permitted chain determines the model's refresh mode and delivered level. This correspondence and matching objective/bound support optimality for the encoded course problem.

Each saved solution underwent an audit of graph preservation, ciphertext counts, chains, shared prefixes, integer levels, operator domains, merges and B2 eligibility. Exact-decimal costs and the unchanged instructor scorer were compared, including node/edge levels and required metrics; the float/decimal tolerance was 1e-7 ms. The S3 suite passed 44 tests, including failures and falsified summaries. Six tiny graphs were exhaustively enumerated and agreed with hand arithmetic, CP-SAT, reconstruction, audit and scoring. They are small correctness checks, not a second full-scale optimisation benchmark.

Independence has limits: enumeration does not call CP-SAT or reconstruction, but modelling, audit and enumeration share the RULES table, and enumeration/model building share original-graph checks. They do not independently interpret the requirements. These are historical S3 checks; this report refresh reads preserved evidence and performs document checks without new searches, scoring or project tests.

## 4. Experiment and comparison scope

Run {{RUN_ID}} used shared-refresh-cp-sat-v1, CPython 3.13.9, OR-Tools 9.15.6755, one CPU search worker, seed 5491 and a 60-second limit per case. The 19 dependencies are pinned. Its clean execution commit was {{SOURCE_COMMIT}}; run.json retains the source fingerprint, configuration and timestamps. The later report version is not substituted for that execution commit.

All 30 S1-BL-001 baselines were calibrated. Costs are 28129.6897 + 0.16*L_init ms for MLP and 53558.1718 ms for attention. Each saved DAG is compared at the same block and input. Our empirical quality comparison is with the instructor's fixed placement, which performs no placement search; its scoring time is not a competing optimiser's search time.

Other routes have been considered conceptually. A second exact model/backend would add equivalence and numerical checks; state-space search needs a sufficient state and safe pruning bounds; ordinary chain dynamic programming does not directly handle shared DAGs. None has a full-instance comparison here. One local-search direction is prioritised for future assessment because it can examine how far legal local improvements approach the known model optima. No concrete candidate or performance result is available; a second exact solver and multiple ablations are deferred.

<!-- pagebreak -->

## 5. Preliminary full-instance results

All 30 saved cases are independently valid, strictly improve their same-input baselines and return OPTIMAL with matching bounds. No course case failed, timed out or used a baseline fallback. All 18 overlapping scores agree exactly with S2-OPT-001; the additional 12 attention inputs complete coverage. These are S3 stage results, before S4 frozen experiments.

{{RESULTS_TABLE}}

Table 1. Equal-cost ranges summarise all 30 records. B1 counts ciphertexts and B2 counts pairs; shared operations are charged once. Depth is 26 for MLP and 62 for attention. Budget = 14*B1 + 13*B2 + L_init; utilisation = depth/budget. Per-input metrics and placements remain in case JSON and summary.csv.

{{LATENCY_FIGURE}}

Figure 1. Estimated latency across all 30 input conditions, from {{RUN_ID}}. Lines connect integer inputs for readability. These fitted inference costs are not actual encrypted-inference measurements or solver times.

Measured solve calls sum to {{SOLVE_SUM}} seconds: MLP {{MLP_MIN}}-{{MLP_MAX}} and attention {{ATTN_MIN}}-{{ATTN_MAX}} seconds per call. Maximum sampled process RSS is {{RSS_MIB}} MiB. RSS includes imported libraries and uses 20 ms samples, so it is not an exact per-case peak. These are one local Windows AMD64 run's observations, not end-to-end time or stable speed rankings. Separate records distinguish model/search/validation intervals and the process-lifetime Windows memory peak.

<!-- pagebreak -->

## 6. Interpreting the saved placements

Attention's lower-cost range begins at input 6. Its saved input-0 and input-6 solutions differ in nonzero costs only by an early B1 on four ciphertexts, worth 4160.60 ms. At input 6, Q and K PCMM1 output level 4 to CCMM1. MLP input 14 similarly removes an early B1 relative to input 0, while Conjugate X costs 2.24 ms more: the net reduction between these optima is 4158.36 ms. Individual solver bounds establish the values; these comparisons explain the saved cost changes.

At attention input 0, bootstrap count rises from the baseline's 17 to 18, yet total latency falls 14.6755%. Ordinary-operator costs decrease by 8900.0554 ms while refresh costs increase by 1040.1500 ms. This explains why complete cost, rather than bootstrap count alone, is the objective. It is arithmetic on saved placements, not a causal ablation or proof that every minimum-count solution is worse. The repository preserves complete MLP input-14 and attention input-0 diagrams tied to those saved DAGs; equally optimal switch arrangements can differ.

## 7. Candidate status and limitations

The planned local-search candidate would start from the instructor's legal placement. Its representation, moves, acceptance/stopping rules, budget and formal inclusion are undecided; design and implementation have not begun. Assessment would retain the same rules and full-cost scoring, report quality relative to the baseline and known model optima, and consider resource and validation costs. A gap to a known optimum is an external reference, not a bound proved by the candidate. Starting information, use of known optima, timing boundaries and failures must be disclosed. Ties or limited improvement can still be informative. CP-SAT remains the main method; no candidate feasibility or speed advantage is claimed.

Optimality is conditional on the encoding of the supplied graphs, insertion rules and fitted costs. It implies neither real FHE speed nor generalisation to larger or unseen networks. Local observations do not guarantee other devices' runtime. No training, real encryption library, GPU or optional connected attention-plus-MLP problem was used. Independent clean-environment reproduction remains outstanding.

## 8. Remaining work and delivery

Candidate design and prototype validation will precede an evidence-based inclusion decision. S4 will freeze the method scope and comparison protocol, retain all 30 conditions and CPU resource records, and provide placements at two or more input levels per block. S5 will consolidate reports and content; S6 will independently reproduce and resolve necessary discrepancies before the Final report is submission-ready. Historical S1-S3, P-S2-v1 and M-S3-v1 remain preserved.

Before formal submission, verify this restricted copy, clarify instructor-code redistribution or an approved acquisition method, and supply the actual online repository URL and grading revision. These requirements and submission authorization remain pending. Sources: supplied CS5491 project/topic instructions, unchanged dag_builder.py and OR-Tools 9.15.6755; public evidence and restricted-copy regeneration instructions accompany this draft.
