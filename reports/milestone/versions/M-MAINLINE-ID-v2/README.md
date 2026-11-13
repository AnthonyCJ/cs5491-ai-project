# M-MAINLINE-ID-v2 Milestone explanatory revision

Prepared 4 October 2026. [English source](milestone.md), [resolved source](resolved-source.md)
and [four-page PDF](milestone.pdf) describe the implemented CP-SAT formulation,
reconstruction and checks, full preliminary comparison, interpretation and remaining work.
The report body uses explanatory terms rather than internal stage/run/version labels.

## Scope and review state

The method scope is CP-SAT and the instructor's fixed-placement baseline.
This version develops the problem and overall method before the detailed rules,
introduces the comparison and figures, explains saved cost differences before
quantifying them, and identifies the team's work directly. It clarifies the
course refresh-count units and preserves model, measurement and validation limits.
[M-MAINLINE-ID-v1](../M-MAINLINE-ID-v1/README.md) received revision feedback;
its original files and checks remain intact. This v2 draft awaits its own
content and layout review. Earlier versions retain their own review history.

| Item | State |
|---|---|
| Produced and saved | Source, PDF and generation/check companions |
| Document checks | [Format, source and evidence checks](format-check.json); full-page visual review is recorded separately within that receipt |
| Local document regeneration | [Regeneration receipt](regeneration-check.json); same machine and document runtime |
| Human content/layout acceptance | Pending for M-MAINLINE-ID-v2 |
| Identity fields | Same approved three names, student IDs and contact email |
| Final submission-ready | Not designated |
| Online repository / grading revision | Not supplied; course delivery requirement remains open |
| Remote publication / course submission | Neither performed by this revision; separate authorization required |

The minimal [identity input](identity.json) carries only the approved report fields.
The source, PDF and metadata retain those fields. No private identity master,
control record or tool configuration is required by the public document chain.

## Evidence and interpretation

The numerical evidence is [S3-OPT-001](../../../../results/S3-OPT-001/README.md),
executed on 28 September 2026, with
[source revision 415f2a91462fb361782b84756a552ad85f44a7b5](../../../../results/S3-OPT-001/run.json)
and fingerprint 7a71e0079618ffd5acc911d5eb1b1629340f76f2494a0e3ffcc94efb3eefe146.
The editorial date is not a new experiment date. [sources.json](sources.json)
binds the source, predecessor, helper files and evidence; [build-info.json](build-info.json)
binds the generated document to them.

| Report content | Evidence |
|---|---|
| Rules, sharing, full costs and formulation | [Metrics](../../../../docs/rules-and-metrics.md), [method](../../../../docs/s2-method.md), model/runner files pinned in sources.json |
| Graph checks, 44 historical tests and six tiny examples | [Validation](../../../../docs/s3-validation.md), [test receipt](../../../../docs/s3-checks.json), [saved examples](../../../../results/S3-OPT-001/tiny-examples.json) |
| Calibrated instructor baseline | [Baseline record](../../../../results/S1-BL-001/run.json), [calibration](../../../../results/S1-BL-001/calibration.json), [table](../../../../results/S1-BL-001/summary.csv) |
| All 30 results, bounds and resources | [Run](../../../../results/S3-OPT-001/run.json), [summary](../../../../results/S3-OPT-001/summary.csv), every saved case and [manifest](../../../../results/S3-OPT-001/artifacts.sha256.json) |
| Equal prototype-overlap scores | [Saved comparison](../../../../results/S3-OPT-001/s2-comparison.json) |
| Placement and cost interpretation | The five case records pinned in sources.json and [figure provenance](../../../../figures/S3-OPT-001/provenance.json) |
| Existing complete placement diagrams | [MLP input-14 and attention input-0 diagrams](../../../../figures/S3-OPT-001/README.md) |

The four displayed cost groups, all 30 curve points and resource fields are read
from the preserved cases. MLP reductions remain 7.3223-22.1113%; attention
reductions remain 14.6755-22.4438%. Bootstrap1 counts ciphertexts and Bootstrap2
counts pairs; shared insertions are charged once. Depth/budget/utilisation are
course metrics, not alternative objectives.

The 44 tests and tiny enumerations are historical validation, not tests rerun
for this report. Some technical documents retain older progress or preparation
statements. Use them for the linked technical definition, the saved run for
numerical coverage, and the current report entries for review/preparation state.

Matching objectives and bounds establish optimality for the encoded course
model, not measured FHE speed or superiority over other solvers. Rule-table
sharing limits validation independence. Solve times and sampled process RSS
describe one local run, not end-to-end or cross-device performance.
The final frozen experiment (internally S4), formal resource and placement
reporting, and independent reproduction (S6) remain separate work.

## Numerical and implementation details

The saved execution used CPython 3.13.9 and OR-Tools 9.15.6755, with all 19
numeric dependencies pinned in requirements-s2.txt. Its source revision is the
execution revision given above, not the later repository or report revision.
The report's one worker, seed 5491, 60-second per-condition limit and 20 ms
memory sampling describe that saved preliminary run.

The model scales objective coefficients by 10000 to preserve four-decimal
costs. A conservative expression-magnitude bound is checked below 2^53;
absolute and relative solver gap tolerances are zero. The independent
exact-decimal cost sum is compared with the instructor scorer at a tolerance
of 1e-7 ms, together with levels, refresh counts and the required metrics.
These saved implementation checks are not new tests performed for this revision.

The allowed edge chains are empty, M, B1, B2, B1-M and B2-M, where M is a strict
Modswitch. Refresh mode and delivered level determine a permitted chain, and
each permitted chain determines those choices. Refresh sharing is keyed by
producer and type; switch sharing by producer, refresh mode and target level.
Both refresh types may be used after one producer, subject to B2 eligibility.
The graph audit recovers original operators, edges and ciphertext counts after
removing inserted chains. The report retains these correctness conditions while
this companion carries the detailed numerical implementation parameters.

All 18 prototype-overlap conditions have the same saved scores; the other 12
attention conditions complete the 30-condition preliminary coverage. This is
a historical consistency observation, with its source in the evidence table.

## Code and evaluation access

The [numerical entry point](../../../../run_s3.py) and
[pinned numeric dependencies](../../../../requirements-s2.txt) support
the saved experiment. The [repository instructions](../../../../README.md)
describe the original environment and expected outputs; their unrelated historical
sections are not additional methods evaluated in this report.
The following existing numerical workflow is documented for later reproduction.
It was not executed or checked for present runtime readiness during this revision:

```powershell
python -B run_s3.py verify --output results/S3-OPT-001
python -B run_s3.py run --config configs/s3-all-instances.json --output results/local-s3-milestone-user
python -B run_s3.py plot --output results/local-s3-milestone-user --figures results/local-s3-milestone-user-figures
```

Use the pinned numerical environment and fresh output paths. The expected run
reports 30/30 improved placements; saved verification reports 30/30 valid and
improved. Verification includes scoring even though it does not search.
The historical solve calls total 10.6445 seconds and maximum sampled RSS is
118.36 MiB; these are not predicted reproduction costs. Timing, memory and
equally optimal switch arrangements can vary. Current solver readiness and
independent-machine reproduction are not established here.

This local code/evidence access does not fulfill the course's public online
repository URL and grading commit/tag requirements. Before submission,
check the intended report, current course requirements and applicable
instructor-code permission or acquisition arrangements. Final readiness,
publication authorization and actual submission remain distinct.

## Generate and check this document

Use ReportLab 4.4.9 and the pinned
[verification packages](../../../verification-requirements.txt).
The recorded document runtime is CPython 3.12.14. Provide licensed Times New Roman
fonts (times.ttf, timesbd.ttf, timesi.ttf, timesbi.ttf); the default directory
is C:/Windows/Fonts and --font-dir can select another. Fonts are not redistributed.

From the repository root, choose a fresh results/local-* directory:

```powershell
python -B reports/milestone/versions/M-MAINLINE-ID-v2/build_milestone.py --output results/local-milestone-revision-user/milestone.pdf
python -B reports/milestone/versions/M-MAINLINE-ID-v2/check_milestone.py --directory results/local-milestone-revision-user
pdftoppm -r 150 -png results/local-milestone-revision-user/milestone.pdf results/local-milestone-revision-user/page
```

The builder preserves existing PDFs/build records and reads only saved evidence.
The checker without --directory checks this saved version. It checks full source
text, resolved fields and table cells, identities, version/evidence provenance,
four A4 pages, embedded Times New Roman 12 pt and 2.5 cm margins; body leading
is 12 pt. Inspect all four pages after any change. Visual approval is tied to
the actual PDF bytes, and automatic checks do not establish human acceptance.

The saved chart/table presentation and font loader are reused from preserved
public report helpers, all hash-bound in sources.json. This version's generator and checker retain the previous mainline
document checks and use this version's source and metadata. Same-machine regeneration is a document
check, not algorithm validation or independent clean-environment reproduction.
