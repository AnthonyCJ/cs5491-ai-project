# Generate the derived tables and figures

Use the existing repository environment identified by [requirements-s2.txt](../../requirements-s2.txt): CPython 3.13.9, matplotlib 3.11.2 and Pillow 12.3.0. The scripts read saved JSON/CSV and draw with matplotlib; they do not import the optimizer or scoring modules. The renderer adapts the existing layered graph layout, using complete saved graphs.

From the `cs5491-ai-project` repository root, the executed generation command was equivalent to:

```powershell
& '.venv-s2/Scripts/python.exe' -B 'analysis/generate_t3.py' --output 'results/T3-ANALYSIS-20261005-001'
```

That delivery directory now exists, and the generator deliberately refuses to overwrite it. For a separately authorized local regeneration, use a fresh destination:

```powershell
& '.venv-s2/Scripts/python.exe' -B 'analysis/generate_t3.py' --output 'results/T3-ANALYSIS-REGEN-001'
& '.venv-s2/Scripts/python.exe' -B 'analysis/check_t3.py' --package 'results/T3-ANALYSIS-REGEN-001'
```

The checker can also inspect the delivered package without regenerating it:

```powershell
& '.venv-s2/Scripts/python.exe' -B 'analysis/check_t3.py' --package 'results/T3-ANALYSIS-20261005-001'
```

The output comprises 7 SVGs, 7 PNGs, 7 adjacent drawing-data JSONs, exact comparison CSV/JSON, readable full comparison and case tables, resource CSV/JSON/Markdown, case explanations, an analysis summary, provenance and a generated-file manifest. The generator produces 32 files including that manifest, whose 31 entries exclude itself. Narrative analysis, the evidence index, dictionary, these instructions and delivery checks are authored separately and bound by the delivery manifest. A fresh generated directory therefore does not include the authored narrative or its links until supplied from this version.

Each run verifies the formal manifest, all 160 source-package entries and 57 frozen public inputs, then reconciles saved CSV, exact costs, bounds and checks. The separate checker compares all 30 derived rows with source JSON, verifies components/counts/level metrics, matches plotted data, checks all selected saved nodes and edges, and reads actual SVG text/IDs to check the visible labels. PNG decoding checks file validity; separate visual inspection checks readability and layout.

The final local generation completed in 6.022203 seconds, and its immediate file check in 0.172940 seconds. These are bounded single-process derivation observations; they are separate from the original experiment's resource measurements. [Delivered checks](checks/README.md) distinguish arithmetic/structure checks and visual review. Re-execution may differ in rendering metadata or font behavior in another environment; a saved-figure derivation is not an independent numerical optimizer reproduction.

The final generation used a temporary, per-process matplotlib cache and the already installed environment. No persistent package, permission, Git configuration or system-environment change was needed.
