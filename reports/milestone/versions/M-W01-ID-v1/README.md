# M-W01-ID-v1: reviewed milestone with team identities

This 4-page English report has passed human review for its current content,
layout and identity fields. Technical evidence is the preserved S3 run and
method-choice reasoning as of 29 September 2026; identities were updated on
30 September. Milestone remains open to updates supported by new reliable evidence; acceptance is not a final content freeze.

[Approved PDF](milestone.pdf) and [English source](milestone.md) are byte-for-byte
copies of the reviewed originals. [Resolved English source](resolved-source.md) is also preserved unchanged.

The report version is unchanged. PUBLIC-PACKAGING-v1 is the new repository
packaging and regeneration companion, not a new technical report. The project
owner authorized these names, student IDs and contact email in this repository
for team sharing and submission preparation. See the
[review and inclusion record](../../../reviews/W01-review-20260930.md).

| State | This version |
|---|---|
| Produced and saved | Yes |
| Source, identity, provenance and format checks | Passed; all 4 pages inspected |
| Human content/layout/identity review | Passed for this version and evidence scope |
| Identity information | Complete, using approved pinyin names |
| Final submission-ready | Not designated; applicable preparation remains |
| Remote upload/public release authorization | Separate; not granted here |
| Course submission authorization / actual submission | None / no record |

The [import record](import-info.json) fixes the approved bytes and identifies
original generation fingerprints. It does not claim that the public companion
generated the imported PDF. [Sources](sources.json) retain evidence hashes,
claim mappings, the preserved anonymous M-W01-v1 hashes and the exact declared
identity/version/preparation edits. [Identity input](identity.json) contains
only the fields needed by the report. Original private generation records are
not copied into or required by this repository.

The approved text and PDF metadata retain their original references to a
"restricted copy" and its workflow. These are historical creation wording;
current permission and repository-local instructions are here. Editing that
wording later requires a new report version and review. Do not overwrite this
approved source or PDF just to change its status.

## Regenerate and check

Use Python with ReportLab 4.4.9 and the pinned
[document verification packages](../../../verification-requirements.txt).
Provide legally available Times New Roman fonts; they are not redistributed.
The existing font loader defaults to C:/Windows/Fonts; --font-dir accepts
another directory with times.ttf, timesbd.ttf, timesi.ttf and timesbi.ttf.
This update installed no dependencies and changed no environment.

From the repository root, check the imported copy and regenerate into a fresh
results/local-* directory:

```powershell
python -B reports/check_identity_report.py reports/milestone/versions/M-W01-ID-v1
python -B reports/milestone/versions/M-W01-ID-v1/build_milestone.py --output results/local-milestone-regeneration/milestone.pdf
python -B reports/check_identity_report.py reports/milestone/versions/M-W01-ID-v1 --regenerated results/local-milestone-regeneration
pdftoppm -r 120 -png results/local-milestone-regeneration/milestone.pdf results/local-milestone-regeneration/page
```

Expected: 4 pages and passing source, identity pairing, fonts, geometry and
provenance checks. Inspect every rendered page. A changed PDF invalidates its
previous visual flag. The builder refuses an existing output directory and
never overwrites these approved files. Regenerated PDF timestamps/document IDs
can differ; this does not change the source content. New build-info.json and
format-check.json belong to the separate output directory.

Milestone also writes resolved-source.md, which must match this approved resolved
source. The chart reads all 30 preserved cases; no optimisation or scoring runs.

[Format checks](format-check.json) describe the imported PDF.
[Regeneration checks](regeneration-check.json) document a relocated copy
containing only public dependencies: the generated PDF passed checks and every
120-dpi rendered page matched the imported report. This is local document-chain
verification, not S6 independent reproduction or a new experiment.

Substantive future changes use a new report version and human review.
Preserve this version, the anonymous predecessor and all older reports/checks.
Before submission, recheck the intended copy and current course requirements,
applicable permission/acquisition arrangements and required online/grading
information. Final readiness, action authorization and actual submission remain
separate. CP-SAT and the S3 evidence scope are unchanged; candidate performance
and formal inclusion remain unestablished.
