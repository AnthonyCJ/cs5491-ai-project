# Validation coverage and acceptance criteria

The criteria cover directed acyclic graphs (DAGs), Portable Network Graphics (PNG)
images, Scalable Vector Graphics (SVG) sources and Portable Document Format (PDF) reports.

This page distinguishes existing evidence from the checks a new reader must
perform. Engineering candidate preparation is not a fresh installation or another
complete business run. Its public entry is [README](../README.md), with exact
[reproduction commands](reproduction.md) and [numerical criteria](grading.md).

## Existing evidence

| Object | Evidence and limit |
|---|---|
| Frozen formal comparison | T2-FORMAL-20261004-004: all 30 conditions, independently checked saved graphs, same-input baselines and recorded resources |
| Formal analysis | T3-ANALYSIS-20261005-001: saved-data derivation, seven figure groups and four complete placements; whole-package human acceptance is not supplied by later report/T4 acceptance |
| Existing-machine reader R6 | One complete final pass after a retained failed first pass and one technical repair; two numerical protocols, saved scoring, figures, historical reports and actual viewing |
| Reader R7 | Documentation correction; unchanged R6 code/results inherited by exact identity, with new documentation/package/viewing checks; no new complete business pass |
| T4 owner acceptance | Owner accepted R7 and the explicitly inherited R6 evidence on 12 November 2026; the report-output documentation issue was closed |
| This engineering candidate | Byte-preserving public packaging, instructions and source/metadata checks; current-candidate full execution and fresh installation remain untested |

The [historical validation summary](validation-history.json) identifies the R6/R7
evidence sets by hash and states their scope. Original process records, failures,
machine details and acceptance records remain in the producer's private archive;
the public package does not require them to run. This dated summary records later
acceptance without changing the original records or claiming new execution.

## What a new reproduction must establish

| Requirement | Completion evidence |
|---|---|
| Input identity | Actual commit/tag, complete candidate payload check, exact instructor input and source/configuration hashes |
| Environment | Actual interpreter builds, installed package versions, fonts/tools used, and whether the environment was new or reused |
| Execution entry | Successful preflight plus complete creation, identity, exit and cleanup receipts for controlled tasks |
| Formal numerical protocol | All 30 new conditions and 30 saved-result checks; exact costs compared with frozen references |
| S3 numerical protocol | All 30 new conditions, six required exhaustive examples and saved-result verification |
| Legality and score | Full graph/level/refresh/shared-cost checks; strict improvement against the matching baseline; exact objective equals bound, zero gap, instructor-score error <=1e-7 ms |
| Figure derivation | Seven formal groups and separate three-group saved/fresh S3 sets, with original checkers and correct source identity |
| Figure viewing | All 13 PNG and 13 SVG sources actually inspected, including complete long diagrams |
| Historical reports | New P-D1-ID-v1 one-page and M-MAINLINE-ID-v2 four-page PDFs from their unchanged builders/checkers |
| Report viewing | All five new historical report pages at 150 dpi actually inspected; timestamps and equal-cost tied layouts may differ |
| Current Proposal, if rebuilt | P-TERMS-ID-v1 gets separate compatibility, content/format and one-page inspection evidence; it does not inherit the historical report rebuild |
| Instructions and facts | Current Markdown actually readable, links usable and claims tied to correct evidence; no omitted private setup step |
| Preservation | New outputs, commands, failures and observations saved under unique names with hashes; original evidence remains intact |

Each required row must be marked passed, failed, blocked or not run with evidence.
Successful process exit alone is insufficient. Refusal checks, such as deliberately
missing input or controlled timeout, are diagnostic successes only when their own
contracts hold; they are never scientific successes. Use such checks only when an
affected change requires them, not as automatic extra experiments.

## Unverified boundaries

Fresh installation, candidate-wide execution, cross-machine portability and a
complete final course-delivery audit remain outstanding. The current terminology
Proposal was accepted as a document but not rebuilt under the R6 document lock.
The optional fresh Node/browser installation route also remains untested. Public
access requires actual publication and anonymous acquisition of the fixed revision.
None of these states is implied by the historical same-machine pass.

New results may vary in solver timing, memory and tied graph layout. Missing
conditions, illegal graphs, incorrect costs or changed scientific inputs cannot
be excused as those ordinary variations. Preserve failures and assess their impact
before another attempt. A later version needs an explicit difference/coverage
record; it must not silently inherit every old pass.
