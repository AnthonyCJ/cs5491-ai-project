# Evidence index and version binding

Analysis package: `T3-ANALYSIS-20261005-001`, derived on 2026-10-05 from `T2-FORMAL-20261004-004`. The analysis introduces no new optimization runs. The [provenance record](provenance.json) binds every condition to its saved case, run, check and configuration, with SHA-256 hashes and the original source fingerprint.

| Claim or reading task | Figure / derived record | Authoritative formal evidence |
|---|---|---|
| All 30 conditions improve and have optimal matching bounds | [Full comparison](comparison.md), [summary](analysis-summary.json) | [Summary JSON](../T2-FORMAL-20261004-004/summary.json), all 30 case/check entries in [provenance](provenance.json) |
| MLP cost transition between input 13 and 14 | [Figure 1](figures/comparison-mlp.svg), [plot data](figures/comparison-mlp.data.json), [case explanations](case-explanations.json) | MLP saved cases listed below; `validated.audit.node_latency_decimal_ms` and saved `solution.shared_refreshes` |
| Attention cost transition between input 5 and 6 | [Figure 2](figures/comparison-attention.svg), [plot data](figures/comparison-attention.data.json), [case explanations](case-explanations.json) | Attention saved cases listed below; costs, shared refreshes and reconstructed edges |
| Refresh count can increase while total modeled cost decreases | [Figure 3](figures/cost-components.svg), [case table](cases.md) | [Attention level-5 check](../T2-FORMAL-20261004-004/checks/attention-L05-V221.json): `baseline_costs`, `current_costs`, `baseline_audit`; saved case audit |
| Complete selected placements and shared-node identities | Figures 4–7 in the table below; accompanying `.data.json` files | Each case's `validated.nodes`, `validated.edges`, `validated.audit.l_in`, `l_out`, `edge_levels` and `placement_chains` |
| Configurations and numerical precision | [Data dictionary](data-dictionary.md), [provenance](provenance.json) | [Protocol](../T2-FORMAL-20261004-004/protocol.json), [frozen input hashes](../T2-FORMAL-20261004-004/inputs.sha256.json), per-condition configurations below |
| Recorded compute and memory scope | [Resource table](resource-observations.md), [complete record](resource-observations.json) | [Formal summary](../T2-FORMAL-20261004-004/summary.json): `resources` and `numerical_results`; source run/check files |
| Derived files match saved evidence and diagrams show complete labels | [Generation and checks](generation.md), [check result](checks/data-check.json) | [Checker](../../analysis/check_t3.py), generated-file hashes and saved sources above |

## Selected-case anchors

| Condition | Saved case | Saved check | Configuration | Figure |
|---|---|---|---|---|
| MLP level 13 | [case](../T2-FORMAL-20261004-004/runs/mlp-L13-R214/cases/mlp-L13.json) | [check](../T2-FORMAL-20261004-004/checks/mlp-L13-V214.json) | [config](../../configs/t2-formal-20261004-r4/mlp-L13.json) | [4](figures/placement-mlp-L13.svg) |
| MLP level 14 | [case](../T2-FORMAL-20261004-004/runs/mlp-L14-R215/cases/mlp-L14.json) | [check](../T2-FORMAL-20261004-004/checks/mlp-L14-V215.json) | [config](../../configs/t2-formal-20261004-r4/mlp-L14.json) | [5](figures/placement-mlp-L14.svg) |
| Attention level 5 | [case](../T2-FORMAL-20261004-004/runs/attention-L05-R221/cases/attention-L05.json) | [check](../T2-FORMAL-20261004-004/checks/attention-L05-V221.json) | [config](../../configs/t2-formal-20261004-r4/attention-L05.json) | [6](figures/placement-attention-L05.svg) |
| Attention level 6 | [case](../T2-FORMAL-20261004-004/runs/attention-L06-R222/cases/attention-L06.json) | [check](../T2-FORMAL-20261004-004/checks/attention-L06-V222.json) | [config](../../configs/t2-formal-20261004-r4/attention-L06.json) | [7](figures/placement-attention-L06.svg) |

The same per-condition structure in `provenance.json` covers the other 26 cases, including each `run.json` and configuration hash. The generator checks the source package's 160 manifest entries and all 57 frozen public inputs before deriving anything.

## Version interpretation

The formal experiment records Git HEAD `aa89f7bb870b1f11d305946f007b1cbb76073b2f` with a dirty worktree. That commit alone does not identify all executed bytes: use the formal input hashes and case fingerprints. The formal package manifest SHA-256 is `0c465b0e11b76c417aa731da2863ad5739a24629e7246d9663559c154472e1f1`.

This package's final generator SHA-256 is `2e4222b0b32faf6a1c0e4fc1f6fd86596931b895fbb3b35e0a38485df1b1bd1a`; checker SHA-256 is `8b41c26ee21da0691e4fcb45674b3da23f7293cf2eaf4cae076572d34d32e353`. The [generated manifest](generated.sha256.json) covers 31 generated data/table/figure files. The [delivery manifest](artifacts.sha256.json) additionally covers authored explanations and delivered checks, excluding itself to avoid self-reference.

The existing method document's **What S2 found** section is an earlier, partially covered experimental snapshot. Its statement that the full optimizer experiment had not been completed is historical; the formal package indexed here covers all 30 conditions. Earlier figures and report versions have not been synchronized to this analysis and must not be represented as its current derived outputs. Their original evidence is preserved. Method definitions may be read at the linked sections above; current numerical conclusions should use this version's formal anchors.
