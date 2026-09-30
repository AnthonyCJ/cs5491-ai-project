# Milestone M-W01-v1

Evidence date: 2026-09-29. Read the [four-page PDF](milestone.pdf) or the
[resolved English source](resolved-source.md). The editable
[template](milestone.md) resolves numerical fields from preserved S3 evidence.
This is a content-review draft, not a new experiment or a submission-ready copy.

## Changes and evidence boundaries

Compared with the preserved [M-S3-v1](../../README.md), this version adds:

- A problem-based explanation of why the integer, shared-refresh model is
  appropriate, and how the S1-S3 progression supports retaining CP-SAT.
- The distinction between the project's model/reconstruction/checking work and
  the general search engine supplied by OR-Tools.
- Conceptual alternatives and their verification costs, without claiming a
  full-instance alternative-method benchmark or an empirical ranking.
- Explicit limits of independent enumeration: its search is separate, while
  the rule table and some original-graph checks are shared.
- The local-search research direction and its unresolved design, implementation,
  protocol and inclusion. No candidate result, feasibility or speed claim is made.
- A saved-cost explanation for attention input 0, distinguished from a causal
  ablation and from a proof about all minimum-bootstrap-count solutions.

The four score ranges, 30-case curve and measured S3 resource observations are
unchanged. They remain preliminary stage evidence under the encoded handout
model. Thirty input conditions on two topologies are not thirty different
networks, and estimated inference latency is not real FHE timing. S4 frozen
experiments and S6 independent reproduction remain separate future work.

[sources.json](sources.json) maps claims and pins public evidence bytes.
[build-info.json](build-info.json) separates the historical numerical execution
commit from this report's source, generator and output hashes.
[format-check.json](format-check.json) records this version's new PDF checks.
The earlier source/PDF/generator/resolved source/build/format records retain
their original bytes and do not act as validation receipts for the new draft.

## Regeneration and checks

Use an existing environment with `reportlab==4.4.9`, as recorded in the unchanged
[report dependency file](../../requirements.txt). Automated PDF checking uses
[verification-requirements.txt](../../../verification-requirements.txt).
From the repository root:

```powershell
python -B reports/milestone/versions/M-W01-v1/build_milestone.py
python -B reports/check_w01_report.py reports/milestone/versions/M-W01-v1
```

Expected output is four pages, a resolved source, a build record and a passed
automated document check. Each generation/check step takes a few seconds or less
in the observed local tool session; this is approximate tool time, not a search
benchmark. The builder checks saved hashes and fields without importing the
optimiser, rescoring graphs or rerunning project tests. It is intentionally tied
to S3-OPT-001 and its score ranges; it is not a generic candidate/S4 renderer.
Changed data require a new narrative and source review rather than bypassed checks.

The new builder retains the earlier chart and table logic and uses the preserved
Proposal font helper, with both source dependencies identified. It changes the
version, evidence checks and output/provenance while keeping the original scripts.
Use `--output <separate-directory>/milestone.pdf` for a separate reproduction,
then pass that directory to the checker. PDF timestamps can vary.

All text, table cells and chart labels use actual embedded Times New Roman 12 pt.
The page is A4, margins are 2.5 cm and body leading is 12 pt. The body reserves
space for a page number inside the lower margin boundary. Fonts default to
`C:/Windows/Fonts`; `--font-dir` accepts a directory with legally available
`times.ttf`, `timesbd.ttf`, `timesi.ttf` and `timesbi.ttf`. Fonts are not distributed.

Render all four pages with Poppler, for example
`pdftoppm -r 150 -png <PDF> <preview-prefix>`, and inspect prose, table, chart,
captions and page numbers after any relevant change. Extraction alone does not
verify appearance. A changed PDF invalidates its old visual-review flag.

## Readiness, review and remaining requirements

| State | This version |
|---|---|
| Content-review draft | Prepared with new source, numerical, format and page checks |
| Human content review | Pending; M-S3-v1 acceptance remains historical |
| Final submission-ready version | No |
| Submission authorization | None for this version |
| Actual submission | No recorded submission |

Review Sections 2 and 4 for choice reasoning and the meaning of the comparisons;
Sections 3, 5 and 6 for validation limits and interpretation; Sections 7 and 8
for candidate status and remaining work. Comments or acceptance concern this
content scope, not publication or submission.

| Pending item | Owner and next trigger | Effect |
|---|---|---|
| Content comments and acceptance | Report maintenance when human feedback arrives | New content is not yet accepted |
| Official names, IDs and group email | Team supplies them before restricted-copy preparation | Required before formal submission; then recheck layout |
| Instructor permission or approved code acquisition | Team supplies the reply; check before relevant publication/submission preparation | Unresolved; not a content-review blocker |
| Actual online repository and grading revision | Submission preparation, with corresponding authorization | Local files do not meet the online requirement |
| Candidate design, evidence and inclusion decision | Subsequent design/validation tasks; review material report impact when evidence arrives | No candidate claim can be added now |
| S4 and S6 | Respective formal-experiment/reproduction tasks | Stage evidence is not their completion; S6 remains necessary for final project readiness |

The supplied course snapshot sets the Milestone deadline at 2026-11-19 23:59
Beijing time. Later online changes have not been independently checked.
Identity, permission and online preparation do not prevent this content review.
Publication and course submission remain separately authorized actions.
