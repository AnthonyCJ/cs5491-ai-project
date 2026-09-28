# S3 stage figures

Source: [S3-OPT-001](../../results/S3-OPT-001/README.md).
All 30 points and both complete diagrams come from verified saved cases.
The [provenance record](provenance.json) identifies the run, source-case hashes
and plotting source. The artifact manifest covers generated images and data;
this explanatory README is maintained separately.

- [Full latency comparison](latency-comparison.svg), with [PNG preview](latency-comparison.png)
  and [30 exact data points](latency-comparison.data.json).
- [MLP input 14](placement-mlp-L14.svg), with [drawn data](placement-mlp-L14.data.json):
  the optimum omits the early B1 and has B1/B2 counts 0/4.
- [Attention input 0](placement-attention-L00.svg), with [drawn data](placement-attention-L00.data.json):
  latency improves even though the total bootstrap count increases to 18.

Open the SVG diagrams with zoom to inspect the large graphs. Every node,
inserted operation, edge, level and ciphertext count is included. Node labels
show input/output levels; edge labels show the actual producer output. At a
merge, the receiving operator uses the minimum incoming level. Counts use
ciphertexts for B1 and pairs for B2, rather than the number of drawn boxes.
The captions report estimated latency, counts, depth, budget and utilisation.

From the repository root:

```powershell
.\.venv-s2\Scripts\python.exe -B run_s3.py plot --output results/S3-OPT-001 --figures results/local-s3-figures
```

Use a new figure directory; existing directories are not overwritten. Plotting
verifies saved evidence without a placement search. These S3 representatives
do not complete S4's requirement for at least two levels per module.
