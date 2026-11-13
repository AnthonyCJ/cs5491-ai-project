# P-D1-ID-v1: Proposal submission candidate

Prepared 5 October 2026. The [English source](proposal.md) and [one-page PDF](proposal.pdf)
update the previously accepted Proposal to reflect the saved formal comparison,
resource records and four complete placement diagrams. This new candidate awaits
its own human content/layout review and verification of the latest Canvas
requirements. It is not designated final submission-ready and has not been submitted.

## What changed and what the results support

The problem and method sections retain the accepted explanation of coupled
placement decisions, the use of CP-SAT and the respective contributions of the
instructor, OR-Tools and the team. The approved names, student IDs and contact
email are unchanged. Evaluation now describes the implemented fixed protocol.
Progress reports one formal optimization run per condition and the prepared
resource records and four complete diagrams. Independent-environment reproduction
and final report preparation remain outstanding.

Reduction ranges remain 7.32-22.11% for MLP and 14.68-22.44% for attention,
rounded to two decimals. The current numerical basis is the formal comparison,
whose exact objectives agree with the earlier preliminary comparison. These are
30 input conditions on two fixed graphs, not 30 architectures. Optimal bounds
apply to the encoded course cost and level model. The report establishes neither
measured encrypted-inference performance nor performance on other devices.
One run per condition does not establish repeated-run variability.

The placement package is technically delivered, including its corrected Figure 3
caption; its whole-package human acceptance remains pending. The Proposal states
that the saved diagrams exist and does not record acceptance of that package.
The prior [P-MAINLINE-ID-v2 acceptance](../../../reviews/P-MAINLINE-ID-v2-review-20261004.md)
remains valid for its original bytes; it does not transfer to this new candidate.

## Evidence outside the one-page report

| Statement | Saved source |
|---|---|
| Coupled levels, shared insertions, full costs and method roles | [Rules](../../../../docs/rules-and-metrics.md), [formulation](../../../../docs/s2-method.md), model/runner hashes in [sources.json](sources.json) |
| All 30 baselines calibrated | [Original baseline record](../../../../results/S1-BL-001/run.json) |
| Fixed protocol and one run per condition | [Formal protocol](../../../../results/T2-FORMAL-20261004-004/protocol.json) |
| All 30 saved legal improvements and matching optimal bounds | [Formal results](../../../../results/T2-FORMAL-20261004-004/summary.json), [condition associations](../../../../results/T2-FORMAL-20261004-004/condition-status.json) |
| Solver time and scoped process-memory observations | [Formal resource records](../../../../results/T2-FORMAL-20261004-004/attempt-resources.json); measurement limits are explained in the [formal package](../../../../results/T2-FORMAL-20261004-004/README.md) |
| Complete diagrams for two levels per block | [Analysis and diagrams](../../../../results/T3-ANALYSIS-20261005-001/README.md): MLP 13/14 and Attention 5/6 |
| Additional small exhaustive correctness checks | Preserved [small examples](../../../../results/S3-OPT-001/tiny-examples.json) and [historical validation](../../../../docs/s3-checks.json) |

[sources.json](sources.json) pins the source, minimal identity input, predecessor,
evidence and document helpers. [build-info.json](build-info.json) binds the PDF
to those bytes. The generator checks saved package hashes and recorded result
flags; it does not rerun optimization, scoring, legality validation or tests.
The original run's recorded source fingerprints remain in its own evidence.

The method document's historical progress section predates the formal comparison;
use it for definitions and use the formal package for numerical progress.
Resource time and memory describe the recorded local run and its stated process
and sampling scope, not total project effort or an exact whole-machine peak.
No historical process-evidence gap is resolved by preparing this document.

## Document checks and remaining decisions

| Item | State for this candidate |
|---|---|
| Source and actual PDF | Produced and saved; source paragraphs and identity pairings match |
| Format | One A4 page, actual embedded Times New Roman 12 pt, 2.5 cm margins, 12 pt body leading; no abstract or reference list |
| Actual page inspection | Passed for the PDF identified in [format-check.json](format-check.json) |
| Identity | Same approved three name/ID pairs and contact email; no placeholders |
| Human content/layout acceptance | Pending for this version |
| Latest Canvas requirements | Not verified; the supplied course snapshot is the current preparation basis |
| Final submission readiness | Not designated |
| Public release or course submission | Neither performed; separate authorization required |

The saved course snapshot specifies one PDF submission per group and a deadline
of 15 October 2026, 23:59 Beijing time. Verify the actual Proposal assignment,
deadline, accepted files and any updated instructions before final designation
and upload. This report does not require publishing a repository as part of the
saved Proposal requirement. Applicable instructor-code distribution permission
must still be checked before publishing code; the Proposal PDF contains no code.

## Generate and inspect

Use the existing document environment with ReportLab 4.4.9 and the pinned
[verification packages](../../../verification-requirements.txt). Supply licensed
Times New Roman files `times.ttf`, `timesbd.ttf`, `timesi.ttf` and `timesbi.ttf`;
fonts are not redistributed. The default directory is `C:/Windows/Fonts`, and
`--font-dir` accepts a different licensed font directory. The build used Python
3.12.14 for documents; that is separate from the formal experiment's runtime.

From the repository root, choose an unused `results/local-*` directory:

```powershell
python -B reports/proposal/versions/P-D1-ID-v1/build_proposal.py --output results/local-proposal-d1-user-check/proposal.pdf
python -B reports/proposal/versions/P-D1-ID-v1/check_proposal.py --directory results/local-proposal-d1-user-check
pdftoppm -r 150 -png results/local-proposal-d1-user-check/proposal.pdf results/local-proposal-d1-user-check/page
```

The builder refuses an existing PDF or generation record. Review the whole
rendered page after changes; a new PDF cannot inherit an older visual approval.
Expected output is one A4 page with identical source text and approved identities;
creation timestamps may vary. The recorded build, check and render each took
under three seconds on the document machine; this is an observation, not a
runtime guarantee. No separate regenerated copy or independent-machine check is
claimed for this delivery.

Keep this candidate, its predecessor and their reviews distinct. The historical
PDF directly under `reports/proposal/` contains placeholders and is not this
candidate. Use the versioned PDF above when reviewing the proposed submission.
