# Check and score the submitted method

The grading object is the shared-refresh Constraint Programming - Satisfiability (CP-SAT) method on a multilayer perceptron (MLP) and Attention,
each at input levels 0–14 and maximum level 14. Compare every result with the
instructor's fixed placement for the **same graph and input level**.
The objective includes ordinary operations, Bootstrap1, Bootstrap2 and Modswitch;
shared inserted operations are charged once. Minimizing refresh count alone is
not the objective. These are model scores, not measured encrypted inference.

## Inspect the implementation

| Responsibility | Source |
|---|---|
| Supplied graphs, costs and scorer | [dag_builder.py](../vendor/dag_builder.py) |
| Integer model, baseline hints and bounds | [s2_model.py](../src/bootplacement/s2_model.py) |
| Complete directed acyclic graph (DAG) reconstruction and sharing | [s2_placement.py](../src/bootplacement/s2_placement.py) |
| Independent structure, level and cost audits | [s2_validation.py](../src/bootplacement/s2_validation.py), [audit.py](../src/bootplacement/audit.py) |
| Numerical execution and evidence | [s2_runner.py](../src/bootplacement/s2_runner.py) |
| Formal saved-DAG and baseline rescore | [t2_formal_check.py](../experiments/t2_formal_check.py) |
| Milestone protocol and saved-DAG verification | [s3_runner.py](../src/bootplacement/s3_runner.py) |
| Saved-data figures / figure-file checks | [generate_t3.py](../analysis/generate_t3.py), [check_t3.py](../analysis/check_t3.py) |

OR-Tools supplies CP-SAT; the team's contribution is the placement formulation,
reconstruction, validation and analysis. [Rules and metrics](rules-and-metrics.md)
define the supplied cost/level conventions.

## Execute the scoring path

Follow [reproduction sections 1–3](reproduction.md). The formal command generates
and then rescans all 30 saved solutions with the original checker. It also
reconstructs/checks the same-input baseline and calls the instructor scorer.
The S3 command runs its original saved-result verifier after generation.

To score one saved formal condition without searching, after the environment
guide has defined the interpreter variables (diagnostic only, not a default extra run):

```powershell
& $ReaderPwsh -NoProfile -File scripts/reader-run.ps1 -Python $NumericalPython -Task saved-score -InputRun results/T2-FORMAL-20261004-004/runs/mlp-L00-R201 -Output results/local-one-score -LimitSeconds 60
if ($LASTEXITCODE -ne 0) { throw 'Saved-result scoring failed' }
```

For a new formal run, replace `-InputRun` with that condition's directory, for
example `results/local-candidate-01-formal/local-formal/mlp-L00`. The output `saved-check.json`
contains full baseline/current costs, teacher-score errors, audits and input hashes.
This extra single-condition command is for diagnosis; it is not an additional
mandatory rescore after the full formal command already produced all 30 checks.

## Required numerical judgments

| Check | Pass criterion |
|---|---|
| Coverage | Exactly MLP/Attention × levels 0–14; complete fresh saved DAGs |
| Legality | Original computation preserved; levels, ciphertext counts, refresh eligibility and shared charging valid |
| Score | Exact independent cost agrees with the objective; instructor floating score differs by at most 1e-7 milliseconds (ms) |
| Optimization | Every condition strictly improves its own baseline; `OPTIMAL`, matching objective/bound and zero gap |
| Complete accounting | Ordinary/B1/B2/switch costs add to total; report refresh counts, depth, budget, utilisation and placements |
| Evidence | Original check files, source/configuration hashes, normal completion and no substituted baseline/result |

The exact formal objective groups are 26069.9524 / 21911.5924 ms (MLP) and
45698.2664 / 41537.6664 ms (Attention). Check all rows against
[summary.json](../results/T2-FORMAL-20261004-004/summary.json), not only these four
numbers. Counts and level metrics must be recomputed from each run's own DAG;
permitted equally optimal zero-cost-switch arrangements can differ. A numeric
score alone does not prove legality. Failure, timeout, infeasibility, missing
evidence or baseline fallback is not an optimized success.

## Relate scores to the reports

The current Proposal P-TERMS-ID-v1 and historical reader Proposal P-D1-ID-v1 use the formal comparison and prepared analysis. Milestone
M-MAINLINE-ID-v2 uses S3; its resource observations and figures retain those sources.
Complete both declared protocols and the figure/report checks in
[reader acceptance](reader-acceptance.md). Historical correctness tests are
evidence with their original scope; the reader run does not claim to rerun all of them.

For course evaluation, inspect the problem/motivation, method and team contribution,
numerical evidence, result interpretation, limitations and reproducibility route.
Use the current instructor rubric for any marks; this project does not invent
weights or award itself a final grade. The eventual Final deliverable also needs
the public repository URL and exact grading commit/tag. This engineering candidate does not designate a
grading revision or a Final report. See [version map](version-map.md).
