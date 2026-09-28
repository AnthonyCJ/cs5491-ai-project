# Automated Bootstrapping Placement

CS5491 Artificial Intelligence course project: minimise the estimated latency of
an encrypted MLP block and an attention block by choosing legal bootstrapping
placements. Each block has 15 input levels (`0..14`) with `L_max = 14`.

The target is a complete course-project delivery: an original optimisation
method, reproduced instructor baselines, real experiments across all 30 cases,
reproducible code, and the required Proposal, Milestone and Final reports.
Final acceptance requires correct placements and scoring, complete evidence,
independent reproduction, and consistent results and documentation. Staged
prototypes support that target; they do not reduce the final requirements.
Production deployment and publication-level research are outside this scope.

**Current implementation: S2, an original shared-refresh optimisation model.**
All 15 MLP inputs and Attention inputs 0, 9 and 14 have valid lower-cost
placements. The remaining 12 Attention inputs, the formal experiment stage
and independent clean-environment reproduction remain future work.
The [one-page Proposal and editable source](reports/proposal/README.md) are
prepared with public identity placeholders; the formal identity requirement
must be completed in a separate submission copy.

## S2 results

[S2-OPT-001](results/S2-OPT-001/README.md) contains 18 actual CPU searches,
reconstructed DAGs, independent checks and reference scores. Every case has
CP-SAT status `OPTIMAL` with a matching objective bound for the encoded model.

| Cases | Estimated latency (ms) | Reduction against same-input baseline |
|---|---:|---:|
| MLP, inputs 0..13 | 26,069.9524 | 7.3223% to 7.3291% |
| MLP, input 14 | 21,911.5924 | 22.1113% |
| Attention, input 0 | 45,698.2664 | 14.6755% |
| Attention, inputs 9 and 14 | 41,537.6664 | 22.4438% |

See the [method and equivalence argument](docs/s2-method.md),
[validation and limitations](docs/s2-validation.md),
[all 18 rows](results/S2-OPT-001/summary.csv) and
[preliminary figures](figures/S2-OPT-001/README.md).
The optimiser uses Python and OR-Tools CP-SAT 9.15.6755 with one search worker.
All 28 unit checks passed, including six exhaustive tiny examples.

From this repository directory, in PowerShell:

```powershell
py -3.13 -m venv .venv-s2
.\.venv-s2\Scripts\python.exe -m pip install -r requirements-s2.txt
.\.venv-s2\Scripts\python.exe -m pip check
.\.venv-s2\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv-s2\Scripts\python.exe -B run_optimizer.py verify --output results/S2-OPT-001
.\.venv-s2\Scripts\python.exe -B run_optimizer.py run --config configs/s2-mlp-attention.json --output results/local-s2-reproduction
.\.venv-s2\Scripts\python.exe -B run_optimizer.py plot --output results/local-s2-reproduction --figures results/local-s2-figures
```

The expected run message is `PASSED: 18/18 instances improved`. The verification
command rechecks saved placements and scores without searching. The plot
command produces a comparison, MLP input-0/input-14 DAGs, and a shared-prefix
example, each as SVG and PNG. Existing run/figure directories are not overwritten;
choose another `results/local-*` name for a repeat. Plotting reads the saved run.

The recorded search calls summed to **2.0053 s**. Individual MLP solves took
0.0075-0.0131 s; the three Attention solves took 0.6108-0.6357 s. The largest
sampled process RSS was **115.98 MiB**, including resident imported libraries.
The configured ceiling was 60 s per case. These are single-run local Windows
AMD64 / CPython 3.13.9 observations, not guarantees for other machines. Import,
validation and writing are outside the search-call timing; each JSON explains
the separate pipeline and memory measurements. None is actual FHE execution time.

The executed source is identified by commit
`19b72147c5a8474e1df52f26a09a62ef20256160` and SHA-256 fingerprint
`44f430c354686ba5fdd48d40ec350ac1d1ef6f5cbf4e27d465162421511bbcc3`.
Numerical scores should reproduce. Timing, memory and timestamps vary; equal-cost
placements can differ in zero-cost switches. Saved records identify the exact
placement used for each figure. Report-generation instructions are separate in
the Proposal directory.

## S1 calibrated baselines

The saved [S1-BL-001 report](results/S1-BL-001/README.md) and
[30-row table](results/S1-BL-001/summary.csv) reproduce the course handout:

| Block | Estimated latency (ms) | B1 / B2 | Depth | Budget |
|---|---:|---:|---:|---:|
| MLP | 28,129.6897 + 0.16 * input level | 5 / 4 | 26 | 122 + input level |
| Attention | 53,558.1718 | 9 / 8 | 62 | 230 + input level |

These are scores computed with the handout's fitted latency functions, not
measurements of actual encrypted inference. B1 counts ciphertexts; B2 counts
ciphertext pairs. See [rules and metrics](docs/rules-and-metrics.md).

## Preserve and reproduce S1

Tested with **CPython 3.13.9, Windows AMD64, CPU only**. All 12 resolved package
versions are pinned in `requirements.txt`. No GPU, account, API or paid service
is needed to execute the bundled local calibration. Internet access is needed
for initial package installation. Other Python versions and operating systems
have not yet been tested.

From this repository directory, in PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p test_baseline_audit.py -v
.\.venv\Scripts\python.exe -B run_baselines.py verify --output results/S1-BL-001
.\.venv\Scripts\python.exe -B run_baselines.py run --output results/local-reproduction
```

The verification command checks saved evidence without running the scorer.
The final command actually evaluates all 30 fixed placements and checks their
structure, levels, counts, budget and cost. Expected final message:

```text
PASS: 30/30 teacher baselines calibrated. Results: results/local-reproduction
```

Choose a new output directory for a later run; existing runs are never
overwritten. Both `run` and `verify` take `--output results/<run-name>`.
Directories named `results/local-*` are excluded from Git by default.

The recorded run took **2.80 seconds** for reference import and the 30-case
pipeline; the reference scoring calls totalled **0.00471 seconds**. Windows
reported a process peak working set of **67.61 MiB**. These are single-run local
observations, not runtime guarantees or future optimiser resource estimates.
Timing excludes interpreter startup and final report/manifest writing.

## Repository map

- `src/bootplacement/`: loading, independent rule checks, calibration and reporting.
- `src/bootplacement/s2_*.py`: original model, reconstruction, validation, experiments and figures.
- `configs/s1-baselines.json`: fixed 30-case configuration.
- `configs/s2-mlp-attention.json`: the 18 instances permitted by the S2 scope.
- `vendor/dag_builder.py`: byte-preserved instructor reference implementation.
- `tests/`: 12 original S1 checks plus 16 S2 checks.
- `results/S1-BL-001/`: raw DAGs, all levels, per-node costs, metrics and checksums.
- [Calibration evidence and limits](docs/s1-calibration.md).
- [Rules, latency table and terminology](docs/rules-and-metrics.md).
- [Source attribution and redistribution status](vendor/README.md).

S1 uses a source SHA-256 fingerprint to identify the exact executable version.
The saved run preceded the first Git commit, so its `git_head_at_run` is null;
its full source manifest is retained and checked against the current files.
Numeric results are deterministic; execution time, memory and timestamps vary.

The instructor's file was supplied without an explicit redistribution licence;
that point needs resolution before publishing the local repository. No licence
is asserted for third-party material. Public release and course submission have
not occurred. This repository contains no personal workspace or identity files.

Later stages will complete Attention coverage, freeze the formal experiment
configuration, prepare the remaining reports and independently reproduce the project.
The optional connected Attention + MLP problem is outside the agreed course-project scope.
