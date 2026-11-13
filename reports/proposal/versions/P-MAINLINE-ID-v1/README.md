# P-MAINLINE-ID-v1: CP-SAT proposal

Prepared 4 October 2026. [English source](proposal.md) and [one-page PDF](proposal.pdf)
describe the CP-SAT method and the instructor's fixed-placement baseline.
This is a new content-review draft. Human review is pending; acceptance of
[P-W01-ID-v1](../P-W01-ID-v1/README.md) does not transfer to this revision.

The instructor supplies the graphs, latency model and scoring interface.
OR-Tools supplies the general solver. The team's contribution is the
formulation, reconstruction and validation workflow. The evaluation keeps
all 30 required conditions, full-cost comparisons, required metrics and at
least two placement diagrams per block. S3 results remain preliminary stage
evidence: S4 frozen experiments and S6 independent reproduction are future work.

## Version, evidence and review

| State | This version |
|---|---|
| Produced and saved | Source, PDF and generation/check companions |
| Document checks | See [format-check.json](format-check.json); full-page inspection recorded separately from automated checks |
| Human content/layout review | Pending |
| Identities | Complete; unchanged approved names, student IDs and contact email |
| Final submission-ready | Not designated |
| Remote publication / course submission | Separate authorization required; none performed |

[Sources](sources.json) maps claims to the pinned S1/S3 evidence and preserves
the predecessor's fingerprints. [Build record](build-info.json) identifies the
actual new source, generator, PDF and numerical evidence version.
The numerical execution commit is 415f2a91462fb361782b84756a552ad85f44a7b5;
the current document is not a new algorithm run. Hash checks and saved audit
flags preserve the applicability of historical evidence; they do not establish
current CP-SAT runtime readiness or repeat the algorithm validation.
[Document regeneration](regeneration-check.json) records the separate local
document-chain check. It is not S6 reproduction.

Estimated-latency reductions remain 7.32-22.11% for MLP and 14.68-22.44% for
attention, rounded from saved S3 values. Optimality is limited to the encoded
course model; these are not real encrypted-inference measurements, guarantees
for other devices or evidence of superiority over other search methods.

## Generate and check

Use the existing document environment with ReportLab 4.4.9 and the pinned
[verification packages](../../../verification-requirements.txt).
Provide licensed Times New Roman files (times.ttf, timesbd.ttf, timesi.ttf,
timesbi.ttf); the default location is C:/Windows/Fonts, or pass --font-dir.
Fonts are not redistributed. No optimisation environment is needed.

From the repository root, select an unused results/local-* directory:

```powershell
python -B reports/proposal/versions/P-MAINLINE-ID-v1/build_proposal.py --output results/local-proposal-mainline-regeneration/proposal.pdf
python -B reports/proposal/versions/P-MAINLINE-ID-v1/check_proposal.py --directory results/local-proposal-mainline-regeneration
pdftoppm -r 150 -png results/local-proposal-mainline-regeneration/proposal.pdf results/local-proposal-mainline-regeneration/page
```

The builder refuses to overwrite an existing PDF or build record. The checker
can also check this saved version by omitting --directory. Inspect the full
rendered page after any change; visual approval never carries across changed
PDF bytes. PDF creation timestamps may differ while content and rendering match.
Report companions read saved evidence and document helpers only; they do not
execute the optimiser, scorer or project tests.

The required format is one A4 page, Times New Roman 12 pt, 2.5 cm margins and
single spacing, with no abstract or reference list. Proposal is due
15 October 2026 at 23:59 Beijing time under the supplied course snapshot.
Later online changes have not been independently checked.

All prior Proposal/Milestone files and reviews remain intact. The minimum
identity input is [identity.json](identity.json); no private identity master,
control records or tool configuration is required. Before formal submission,
check the intended copy and current course requirements and applicable
permission/acquisition arrangements. Human acceptance, final readiness,
authorization and actual submission remain separate.
