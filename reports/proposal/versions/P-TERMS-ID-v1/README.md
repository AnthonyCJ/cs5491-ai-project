# P-TERMS-ID-v1: Proposal terminology revision

Prepared 15 October 2026 from the accepted P-D1-ID-v1. The [English source](proposal.md)
and [one-page PDF](proposal.pdf) clarify terminology and the evaluation plan.
The empirical results, method, approved identities and remaining work retain
their previous evidence basis. This revision requires its own human review;
it is not designated final submission-ready and has not been submitted.

## Changes for readers

- Expand CP-SAT as Constraint Programming - Satisfiability at first use, identify
  Google's OR-Tools toolkit, and explain integer and true/false decisions, the
  project's joint level/insertion choices and the solver's role.
- Introduce ciphertexts as encrypted data and explain the level model and
  coupled placement decisions before discussing the optimisation method.
- Distinguish Bootstrap1, Bootstrap2 and Modswitch, including restoration levels,
  Bootstrap2 eligibility and one charge for each shared insertion.
- Explain how the validated instructor placement guides and bounds the search,
  and why reaching a lower cost bound establishes optimality only within the model.
- Specify that 30 conditions are input levels on two fixed graphs. Define latency
  units, the matching baseline for percentage reduction, ciphertext/pair counts,
  depth, the course-defined budget and utilisation. Time spent searching is
  recorded separately from estimated inference latency.

The text retains all 30 calibrated baselines, one formal optimisation run per
condition, the unchanged reduction ranges, the small exhaustive checks, the
four prepared diagrams, and the independent-environment reproduction requirement.
It makes no new experimental or performance claim.

## Sources and document checks

[sources.json](sources.json) pins the predecessor, method definitions, formal
comparison, diagram evidence and unchanged document dependencies.
[build-info.json](build-info.json) associates this PDF with the exact revised source.
[format-check.json](format-check.json) records automated checks and the separate
full-page visual inspection. [artifacts.sha256.json](artifacts.sha256.json) identifies
this version's files; it excludes itself.

The official naming explanation identifies CP as constraint programming and SAT
as satisfiability. The expanded name in this report expresses those components,
rather than naming a new algorithm. See Google's
[constraint programming overview](https://developers.google.com/optimization/cp/),
[CP-SAT guide](https://developers.google.com/optimization/cp/cp_solver) and
[solver source overview](https://github.com/google/or-tools/blob/stable/ortools/sat/README.md).
These were consulted on 15 October 2026; no reference list is added to the Proposal.
Project-specific meanings come from the preserved [rules and metrics](../../../../docs/rules-and-metrics.md)
and [formulation](../../../../docs/s2-method.md). Those documents' historical
progress paragraphs do not replace the current formal evidence cited in sources.json.

The actual PDF is one A4 page, with embedded Times New Roman at 12 pt, 2.5 cm
margins and 12 pt body leading. All source paragraphs and approved identity
pairings are present. There is no abstract, reference list, embedded attachment,
private path in metadata, clipped text or overlapping text.

## Rebuild

Use the existing pinned document environment: ReportLab 4.4.9, pdfplumber 0.11.9
and pypdf 6.10.0. The build was performed with Python 3.12.14. Licensed Times New
Roman files are required and are not redistributed; `--font-dir` overrides the
Windows font-directory default. From the repository root, use a fresh output:

```powershell
python -B reports/proposal/versions/P-TERMS-ID-v1/build_proposal.py --output results/local-proposal-terms-check/proposal.pdf
python -B reports/proposal/versions/P-TERMS-ID-v1/check_proposal.py --directory results/local-proposal-terms-check
pdftoppm -r 150 -png results/local-proposal-terms-check/proposal.pdf results/local-proposal-terms-check/page
```

The builder preserves existing outputs and checks pinned saved evidence; it does
not rerun optimisation, scoring or historical tests. Expected output is a
one-page document with the same text and identities. Inspect any newly generated
PDF separately; timestamps can change, and a successful check is not human approval.

## Review and frozen versions

Human content/layout acceptance of this revision is pending. The
[P-D1-ID-v1 acceptance](../../../reviews/P-D1-ID-v1-review-20261005.md)
continues to apply only to its unchanged original. The fixed reader R2 package
still contains P-D1-ID-v1; this revision does not update or validate that package.

Latest Canvas requirements remain unverified. Final submission selection,
release and actual upload are separate decisions; this document revision performs
none of them. Historical reports, experiments and acceptance records are preserved.
