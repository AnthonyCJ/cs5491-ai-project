# S2 preliminary figures

All figures derive from [S2-OPT-001](../../results/S2-OPT-001/README.md).
The [provenance](provenance.json) identifies the source data and generator.
SVG is the scalable version; PNG is a preview.

- [Latency comparison](latency-comparison.svg): all 15 MLP inputs and only the three tested Attention inputs. The Attention points are not connected as a claimed full curve.
- [MLP input 0 placement](placement-mlp-L00.svg) and [input 14 placement](placement-mlp-L14.svg): every saved original/inserted node and edge, with levels and ciphertext counts.
- [Shared-prefix example](method-shared-prefix.svg): the independently enumerated two-reader example, with one shared B2 and one shared Modswitch.

Each placement has an adjacent `.data.json` file retaining exactly the drawn
nodes, edges and levels. The figure numbers are fitted latency scores, not real
FHE timings. B1 counts individual ciphertexts and B2 counts pairs. Modswitch
labels encode the producer, refresh mode and target level; numeric input/output
levels are printed separately on every node.

To regenerate in a new directory, from the repository root:

```powershell
.\.venv-s2\Scripts\python.exe -B run_optimizer.py plot --output results/S2-OPT-001 --figures results/local-s2-figures
```

The generated artifact manifest covers images, diagram data and provenance.
This explanatory README is maintained separately. Visual inspection and exact
graph/level correspondence were checked for this version. These are S2 figures;
S4 still must generate and check at least two input-level placements per module
for its final experiment configuration.
