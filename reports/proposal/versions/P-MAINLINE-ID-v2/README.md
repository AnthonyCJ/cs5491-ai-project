# P-MAINLINE-ID-v2: proposal revision

Prepared 4 October 2026. [English source](proposal.md) and [one-page PDF](proposal.pdf)
explain the placement problem, the CP-SAT method, the evaluation plan and
preliminary progress. The source contains no internal stage or run labels.
Those labels appear below only to locate evidence.

[P-MAINLINE-ID-v1](../P-MAINLINE-ID-v1/README.md) received human feedback
requesting revision and was not accepted. Its files and checks remain intact;
their review statements record the state at the time of creation.
This v2 requires its own human content and layout review.

## What changed

The problem statement explains why shared refreshes and level-dependent operator
costs make placement decisions interact. The method follows from that difficulty:
joint constrained optimisation, its fit to finite discrete choices, the team's
implementation and the roles of the instructor and OR-Tools. The instructor
baseline is disclosed as both the comparison and a source of search guidance
and a feasible cost upper bound. No claim of superiority over untested solvers
is made.

The evaluation retains both blocks, all 30 input conditions, full costs,
the required metrics and at least two placement diagrams per block.
Progress distinguishes the completed preliminary comparison from the remaining
fixed final protocol, formal resource and placement reporting, and independent
reproduction. Administrative status and internal identifiers were removed
from the report body; required identity fields and substantive limits remain.

## Evidence and details outside the one-page body

| Report statement | Evidence and meaning |
|---|---|
| Coupled levels, shared refreshes and full cost objective | [Rules and metrics](../../../../docs/rules-and-metrics.md); [formulation](../../../../docs/s2-method.md) |
| Formulation, reconstruction, validation and solver roles | The formulation document and the source files pinned in [sources.json](sources.json); current model/runner hashes match the saved numerical run |
| Baseline guides search and excludes higher-cost solutions | [Model](../../../../src/bootplacement/s2_model.py) adds a baseline cost upper bound and hints; [runner](../../../../src/bootplacement/s2_runner.py) supplies the validated placement |
| All 30 baselines calibrated | [S1-BL-001](../../../../results/S1-BL-001/run.json), the preserved baseline calibration, and its [table](../../../../results/S1-BL-001/summary.csv) |
| All 30 preliminary improvements and matching optimal bounds | [S3-OPT-001](../../../../results/S3-OPT-001/run.json), the preserved full preliminary comparison, its [table](../../../../results/S3-OPT-001/summary.csv) and saved case files |
| Tiny exhaustive correctness checks | [Saved examples](../../../../results/S3-OPT-001/tiny-examples.json) and [validation record](../../../../docs/s3-checks.json) |
| Remaining formal experiments and independent reproduction | Planned work, not new results; the former is internally S4 and the latter S6 |

The numerical execution commit is 415f2a91462fb361782b84756a552ad85f44a7b5.
Reduction ranges remain 7.32-22.11% for MLP and 14.68-22.44% for attention,
rounded to two decimals from the saved values. These are two fixed graphs
at 15 input levels each, not 30 different graph architectures.
Optimality is limited to the encoded course model and its supplied cost
functions. It is not a measured FHE speedup, a cross-device guarantee or
evidence that CP-SAT outperforms other search methods.

The full technical definitions remain in the linked method and metrics files:
Bootstrap1 restores level 14 and is charged per ciphertext; Bootstrap2 restores
level 13, is eligible only for 8 or 16 ciphertexts and is charged per pair.
Shared insertions are charged once. Integer objective coefficients are scaled
by 10,000 to preserve the supplied precision. Depth is maximum path level
consumption; the handout's budget is 14*B1 + 13*B2 + input level, and utilisation
is depth/budget. These details were relocated for readability, not relaxed.

The method document's old progress section predates the full preliminary
comparison; use it for the formulation and use the saved comparison for
current numerical coverage. Source and evidence hashes are pinned in
[sources.json](sources.json). This revision reads saved evidence only and
does not establish present solver readiness or add new experiments.

## Checks and state

| Item | State |
|---|---|
| Produced and saved | Source, PDF and generation/check companions |
| Document checks | [Format and full-text checks](format-check.json), including the actual full-page visual review |
| Local document regeneration | [Regeneration check](regeneration-check.json); same document environment only |
| Human content/layout acceptance | Pending for v2; not inferred from execution approval |
| Identity fields | Same approved names, student IDs and contact email |
| Final submission-ready | Not designated |
| Remote publication / course submission | Neither performed; separate authorization required |

[Build information](build-info.json) binds the source, generator, PDF and
historical numerical evidence. Automated document checks and assistant
editorial review do not constitute human acceptance or algorithm validation.
No independent-machine or relocated-repository reproduction is claimed.

## Generate and check

Use ReportLab 4.4.9 and the pinned
[verification packages](../../../verification-requirements.txt).
Provide licensed Times New Roman fonts (times.ttf, timesbd.ttf, timesi.ttf,
timesbi.ttf). The default is C:/Windows/Fonts; --font-dir accepts another
location. Fonts are not redistributed.

From the repository root, select an unused results/local-* directory.
The following example directory is deliberately different from the recorded
verification output, so it is available for a later user regeneration:

```powershell
python -B reports/proposal/versions/P-MAINLINE-ID-v2/build_proposal.py --output results/local-proposal-v2-user-check/proposal.pdf
python -B reports/proposal/versions/P-MAINLINE-ID-v2/check_proposal.py --directory results/local-proposal-v2-user-check
pdftoppm -r 150 -png results/local-proposal-v2-user-check/proposal.pdf results/local-proposal-v2-user-check/page
```

The builder refuses to overwrite PDFs and build records. The checker without
--directory checks this saved version. Inspect the complete rendered page after
a change; visual approval never transfers to changed PDF bytes. Creation
timestamps may differ while text and rendered pages remain identical.
Helpers read saved data; they do not run the optimiser, scorer or project tests.

The course snapshot requires one A4 page, Times New Roman 12 pt, 2.5 cm margins,
single spacing, no abstract and no reference list. The proposal deadline is
15 October 2026 at 23:59 Beijing time; later online updates were not checked.
The minimum public input is [identity.json](identity.json). No private
identity master, control file or tool configuration is needed.

Before formal submission, check the intended copy, current course requirements
and applicable permission/acquisition arrangements. Previous reports, their
review histories and experiment records are preserved.
