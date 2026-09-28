# S2 correctness evidence and limits

Evidence version: S2-OPT-001, executed 2026-09-28. This is S2 feasibility and
MLP coverage evidence, not the later formal 30-case experiment or an independent
clean-machine reproduction.

## Independent checks

The preserved S1 audit validates the original graph after virtual removal of
inserted chains; integer level domains and operator validity; B2 eligibility;
strict Modswitch drops; canonical shared prefixes; ciphertext counts; per-node
decimal costs; bootstrap counts; depth, budget and utilisation. It is independent
of the CP-SAT constraints and teacher scorer. The model uses the checked decimal
table; the teacher implementation supplies a separately implemented score.

S2 additionally compares the extracted assignment with the reconstructed DAG,
checks the objective against exact decimal cost, compares every node and edge
level with the teacher scorer, and checks the objective bound and status claim.
The float/decimal score tolerance is 1e-7 ms. Summary rows and saved metrics
are checked against the detailed cases. A successful numerical scorer call
alone is insufficient for acceptance.

All 28 unit checks passed: the original 12 S1 cases were rerun in the S2
environment, and 16 S2 checks exercise enumeration agreement, shared nodes,
both refresh types at one producer, invalid assignments, tampered costs,
levels and bounds, and misleading status/gap claims. This is a new S2 test
observation; it does not rewrite the original S1 test record.
The timestamped test output and exact test-file hashes are preserved in
[s2-checks.json](s2-checks.json).

## Complete tiny examples

The separate enumerator explores all feasible edge refresh and delivery-level
choices in each tiny graph, with only necessary operator-domain pruning. It
does not call CP-SAT or the reconstruction code. See
[tiny-examples.json](../results/S2-OPT-001/tiny-examples.json).

| Example | Complete placements scored | Exact optimum (ms) |
|---|---:|---:|
| One-cipher refresh | 14 | 1040.6355 |
| Paired refresh | 27 | 5173.0055 |
| Shared refresh and Modswitch | 729 | 5173.4910 |
| Minimum-level merge | 33280 | 0.5234 |
| Shared refresh, different drops | 182 | 6628.8055 |
| Refresh after a ciphertext-count change | 616 | 4162.7555 |

Each minimum agrees with the hand calculation, CP-SAT optimum, reconstructed
graph, independent audit and teacher score. Exhaustive search is intentionally
limited to at most four nodes and three edges; it is never used on MLP or Attention.

For the shared example, one B2 on eight ciphertexts costs four pairs times
1293.13 = 5172.52 ms. A shared Modswitch supplies level 1 to two Muls, each
costing 0.4855 ms. The total is 5173.4910 ms. The figure draws one B2 and one M,
not duplicate copies for the two readers.

## Scope and resource observations

MLP inputs 0..14 and Attention inputs 0/9/14 all returned `OPTIMAL`, with no
failed, timed-out, baseline-equivalent or fallback cases. MLP scores are
26069.9524 ms for inputs 0..13 and 21911.5924 ms for input 14. The three
Attention scores are 45698.2664, 41537.6664 and 41537.6664 ms respectively.

The configured ceiling was 60 seconds per instance, with one worker and seed
5491. Actual search calls summed to 2.0053 seconds. MLP solves ranged from
0.0075 to 0.0131 seconds and Attention solves from 0.6108 to 0.6357 seconds.
The largest sampled process RSS was 115.98 MiB, including imported packages.
Each case records process CPU time, a separate pipeline interval, a 20 ms RSS
sampling interval, and Windows' process-lifetime peak working set when available.
Sampling is not an exact per-case peak measurement; the Windows peak includes
earlier activity in the same process. These local observations do not establish
teammate-device compatibility or runtime guarantees.

The real measured quantity is search/pipeline time. The much larger millisecond
inference scores are calculated from fitted functions; no FHE execution occurred.

## Remaining work

The 12 untested Attention inputs remain for S3. Their results cannot be inferred
from the three representatives. Formal frozen experiments and both modules'
required placement figures remain S4 responsibilities. The initial MLP diagrams
are reusable evidence but do not mark S4 complete. Independent environment
reproduction and delivery checks remain S6 work. This run provides encouraging
feasibility evidence, not proof that every later requirement has been met.

The [Proposal](../reports/proposal/README.md) has its technical content and
one-page formatting prepared. Formal identities still need completion in a
restricted copy. Teacher-code redistribution permission must be resolved before
public release. No public release or course submission has occurred.
