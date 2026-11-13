# Automated Bootstrapping Placement

This project places refresh operations in two encrypted-computation graphs: a
multilayer perceptron (MLP) and Attention. Refreshing restores usable computation
levels but adds cost. Our formulation jointly chooses levels, insertions and
shared refreshes using Constraint Programming - Satisfiability (CP-SAT), the
integer constraint solver in Google's OR-Tools toolkit. It reconstructs the
complete directed acyclic graph (DAG) and independently checks legality and cost.

The objective is total **estimated inference latency** in the supplied course
model, including ordinary operations and shared inserted operations. It is not
measured encrypted execution time. The instructor supplies the graphs, cost
functions, reference placements and scorer; the project supplies the formulation,
reconstruction, audits and analysis. See the [method](docs/s2-method.md) and
[rules and metrics](docs/rules-and-metrics.md).

## Read, install and reproduce

This is engineering candidate **ENGINEERING-CANDIDATE-20261113-02**, prepared for
public review. The intended repository is
[AnthonyCJ/cs5491-ai-project](https://github.com/AnthonyCJ/cs5491-ai-project).
Its candidate tag is `engineering-candidate-20261113-02`; before the tag is
published, remote acquisition is unavailable. The tag is a reproduction candidate,
not a designated course grading or final-submission version.

1. Read [source access and licences](docs/public-scope.md).
2. Follow [acquisition and installation](docs/installation-unverified.md).
   The corrected commands passed a local fresh installation. The revised public
   acquisition chain and owner acceptance remain pending; see the
   [installation revision record](docs/installation-revision-20261113.json).
3. Run the [reproduction commands](docs/reproduction.md), which specify inputs,
   outputs, checks and time limits without a private machine-locator file.
4. Compare results using [scoring criteria](docs/grading.md), then inspect
   [figures and reports](docs/reader-visual.md).

The documented target is Windows x64, PowerShell 7.6.9, numerical CPython 3.13.9
and document CPython 3.12.14, with separate locked Python dependencies. Report
builds require legally available Times New Roman; no font files are distributed.
Other platforms and a fresh installation of the optional viewing tools remain
untested. The local reproduction used existing viewers, Windows and system fonts.

## Results and reports

The formal comparison has **30 conditions on two fixed graphs**: input levels
0-14 for each graph, maximum level 14. Each saved solution strictly improves its
same-input instructor baseline and passes graph/score checks. Objective and bound
agree for the encoded model. The [full table](results/T2-FORMAL-20261004-004/summary.csv)
retains costs, counts, levels, timing and provenance.

| Graph and input levels | Optimized estimated latency (milliseconds, ms) |
|---|---:|
| MLP, 0-13 | 26069.9524 |
| MLP, 14 | 21911.5924 |
| Attention, 0-5 | 45698.2664 |
| Attention, 6-14 | 41537.6664 |

| Material | Version and evidence |
|---|---|
| [Current Proposal](reports/proposal/versions/P-TERMS-ID-v1/proposal.pdf) | Accepted terminology revision; formal comparison and analysis; not included in the historical reader report-rebuild pass |
| [Milestone](reports/milestone/versions/M-MAINLINE-ID-v2/milestone.pdf) | Accepted four-page stage report based on earlier S3 results; not the later formal-results update |
| [Formal analysis](results/T3-ANALYSIS-20261005-001/README.md) | Seven figure groups from frozen formal results, including four complete placements |
| [Historical reader Proposal](reports/proposal/versions/P-D1-ID-v1/proposal.pdf) | Earlier accepted one-page report; the Proposal actually rebuilt in the R6 reader run |

The [report index](reports/README.md) and [version map](docs/version-map.md)
separate report acceptance, numerical sources and reproduction coverage. The Final
report and a final grading version are not included. Timing and memory values are
observations from their named runs, not measurements of this candidate on a new host.

## Validation and provenance

The owner accepted fixed reader R7 and its explicitly inherited R6 business evidence
on 12 November 2026. R6 ran the two numerical protocols, figures and historical
reports on an existing Windows environment. R7 corrected documentation; it did
not repeat a complete business pass. This candidate preserves their executable
and scientific inputs by byte identity and supplies public acquisition instructions.
See [validation coverage](docs/reader-acceptance.md), [claims and evidence](docs/claim-evidence.json)
and the [candidate inventory](candidate-manifest.json).

The original candidate 01 failed installation. The corrected commands and unchanged
business inputs passed local same-machine checks, including an independent rebuild
of the current Proposal. Revised-public-chain verification, owner acceptance and
cross-machine operation remain unverified. Public availability is established only after publication and
anonymous acquisition of the named tag. Earlier creation-time `pending` statements
remain in frozen evidence; later dated records supply the decisions without
rewriting those originals. Private machine records are not required project inputs.
