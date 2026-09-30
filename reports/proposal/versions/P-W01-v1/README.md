# Proposal P-W01-v1

Evidence date: 2026-09-29. This is a new English content-review draft using
the preserved S3 results and method-choice reasoning. It does not report a
new experiment. Start with [proposal.pdf](proposal.pdf) or the editable
[proposal.md](proposal.md).

The preserved [P-S2-v1](../../README.md) remains the historical S2 version,
including its source, PDF, generator and original checks. Its incomplete
Attention coverage describes that earlier stage; use this version for the
current plan. No historical file or submission record is rewritten.

## What changed

- Progress now covers all 30 S3 input conditions rather than the 18-case S2
  prototype. Percentage ranges retain their original, model-based meaning.
- The evaluation plan separates saved stage evidence, future S4 frozen
  experiments and S6 independent reproduction.
- The rationale connects integer levels, shared costs and objective bounds
  with the chosen model. The project implements the formulation, reconstruction
  and validation; OR-Tools provides the general search engine.
- One local-search direction is planned for assessment from a legal instructor
  placement. Design, implementation, protocol and inclusion remain pending.
  There are no candidate performance claims or cross-method speed rankings.

## Evidence and regeneration

[sources.json](sources.json) pins the public evidence bytes and maps claims to
their sources. [build-info.json](build-info.json) identifies this report's
source, generator, preserved font helper, numerical run and output separately.
[format-check.json](format-check.json) records the new PDF's checks.

Use an existing Python environment with `reportlab==4.4.9`; the unchanged
[report dependency file](../../requirements.txt) records that version.
For automated PDF checks, use the packages listed in
[verification-requirements.txt](../../../verification-requirements.txt).
From the repository root:

```powershell
python -B reports/proposal/versions/P-W01-v1/build_proposal.py
python -B reports/check_w01_report.py reports/proposal/versions/P-W01-v1
```

Expected output is a one-page PDF and a passed automated check. Building and
checking each take a few seconds or less in the observed local tool session;
this is approximate tool time, not an optimisation benchmark. The builder reads
saved evidence and never searches or scores a placement. A changed pinned source
requires a narrative/source review before the index is updated.

The PDF uses A4, actual embedded Times New Roman 12 pt, 2.5 cm margins and
12 pt single-line leading, with no abstract or reference list. Fonts default
to `C:/Windows/Fonts`; elsewhere pass `--font-dir` with legally available
`times.ttf`, `timesbd.ttf`, `timesi.ttf` and `timesbi.ttf`. Fonts are not bundled.
The original font helper is preserved and checked by hash.

An optional `--output` can put a reproduction PDF and its build record in a
separate directory. Pass that directory to the checker. Render every page
with Poppler, for example `pdftoppm -r 150 -png <PDF> <preview-prefix>`, and
inspect it after any content, identity, chart or layout change. Automated
extraction alone cannot establish visual quality; a changed PDF invalidates
the previous visual-review flag. PDF timestamps may vary between builds.

## Readiness and review

| State | This version |
|---|---|
| Content-review draft | Prepared; new content/format checks accompany the draft |
| Human content review | Pending; earlier P-S2-v1 acceptance does not cover these changes |
| Final submission-ready version | No |
| Submission authorization | None for this version |
| Actual submission | No recorded submission |

Review the current progress statement, the CP-SAT rationale, and the evaluation
plan including the candidate's pending status. This review does not authorize
publication or course submission.

Before submission, supply three confirmed English names, student IDs and one
contact email in the restricted copy, close relevant content comments, and
regenerate/recheck that copy. Check applicable instructor permission and
submission information at preparation time; do not infer redistribution
permission from a pending inquiry. Publishing code or submitting the report
requires its corresponding authorization. These pending items do not prevent
review of the present technical content.

The supplied course snapshot sets the Proposal deadline at 2026-10-15 23:59
Beijing time. Later online updates have not been independently checked.
Candidate design/validation or other material evidence changes trigger a new
content-impact check; no automatic background monitor is implied.
