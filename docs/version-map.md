# Reports, experiments and candidate versions

Report originals are Portable Document Format (PDF) files; hashes identify exact bytes.

| Object | Fixed identity | What it supports |
|---|---|---|
| Current Proposal | [P-TERMS-ID-v1](../reports/proposal/versions/P-TERMS-ID-v1/README.md) | Accepted terminology/content/layout revision; formal evidence unchanged; no inherited R6 rebuild |
| Historical reader Proposal | [P-D1-ID-v1](../reports/proposal/versions/P-D1-ID-v1/README.md) | Earlier accepted report and the one-page Proposal rebuilt by the R6 reader |
| Milestone | [M-MAINLINE-ID-v2](../reports/milestone/versions/M-MAINLINE-ID-v2/README.md) | Accepted four-page stage report based on S3; not a formal-results update |
| Formal experiment | [T2-FORMAL-20261004-004](../results/T2-FORMAL-20261004-004/README.md) | Thirty frozen conditions, saved checks, exact scores and original resource measurements |
| Formal analysis | [T3-ANALYSIS-20261005-001](../results/T3-ANALYSIS-20261005-001/README.md) | Derivation from saved T2, seven figure groups and four complete placements; not a new numerical run |
| Earlier comparison | [S3-OPT-001](../results/S3-OPT-001/README.md) | The Milestone's earlier thirty-condition evidence plus six small examples |
| Reader R6 | [Historical validation summary](validation-history.json) | Existing-machine complete final pass after a retained failed pass and a single repair |
| Reader R7 | [Historical validation summary](validation-history.json) | Documentation correction and exact-file inheritance of R6 business evidence; no complete rerun |
| Original engineering candidate | Tag `engineering-candidate-20261113-01`, commit `4c338cee72d1accb19231aae4e17d0aa3561dba1` | Public input retained; environment creation failed before the local correction |
| Revised engineering candidate | [Candidate inventory](../candidate-manifest.json), intended tag `engineering-candidate-20261113-02` | Local correction checked; revised public acquisition and owner acceptance pending; [revision record](installation-revision-20261113.json) |
| Final | Not designated | No Final report or final grading version here |

The owner accepted R7 and its explicitly inherited R6 evidence on 12 November
2026. Historical creation-time `pending` fields remain unchanged. The later
[coverage statement](reader-acceptance.md) supplies that decision; it does not
rewrite the old artifacts or convert inherited evidence into new measurements.
T3 whole-package acceptance is not inferred from T4 or report acceptance.

The current Proposal PDF SHA-256 is
`1c6d1af4a40b8f9585ef02a95e5764fff490730e5ef1115590a11f3ec9d93f2f`;
the historical reader Proposal is
`d5931a879e8f5b0e0aa07ae034a90e73c676fb58c8aecc253e2d459c0c9735d0`;
the Milestone is
`655f255521ae87a0340bf1b6c1fb67d3cfb0c85628cf9d273daf7cf49a1bb34c`.
Their original sources, identities, generators/checkers and acceptance records are
preserved. New builds require their own inspection and do not inherit acceptance.

The original formal run recorded HEAD
`aa89f7bb870b1f11d305946f007b1cbb76073b2f` with local changes. That commit alone
does not reconstruct the run: source/configuration fingerprints identify its
executed inputs. The candidate retains all nine earlier commits and appends the
public preparation. It does not retag or rewrite history. Use the candidate's
actual resolved commit and inventory for acquisition, and each experiment's own
manifest for scientific claims. The [change map](candidate-changes.json) records
packaging differences from the fixed R7 source.

Frozen numerical/report dependencies stay byte-preserved, including line endings.
Older README instructions describe their original time and environment. Follow
the current [reproduction guide](reproduction.md); old internal paths or progress
statements are not current instructions. Private controls, machine locators,
prompts and alternative-search archives are not public reader prerequisites.
