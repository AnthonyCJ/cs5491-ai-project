# Automated Bootstrapping Placement

CS5491 Artificial Intelligence course project: minimise the estimated latency of
an encrypted MLP block and an attention block by choosing legal bootstrapping
placements. Each block has 15 input levels (`0..14`) with `L_max = 14`.

**Current implementation: S1, teacher-baseline calibration.** All 30 fixed
teacher baselines have been executed and checked. An original optimisation
method and claims of improvement are not part of this version.

## Results

The saved [S1-BL-001 report](results/S1-BL-001/README.md) and
[30-row table](results/S1-BL-001/summary.csv) reproduce the course handout:

| Block | Estimated latency (ms) | B1 / B2 | Depth | Budget |
|---|---:|---:|---:|---:|
| MLP | 28,129.6897 + 0.16 * input level | 5 / 4 | 26 | 122 + input level |
| Attention | 53,558.1718 | 9 / 8 | 62 | 230 + input level |

These are scores computed with the handout's fitted latency functions, not
measurements of actual encrypted inference. B1 counts ciphertexts; B2 counts
ciphertext pairs. See [rules and metrics](docs/rules-and-metrics.md).

## Reproduce

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
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
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
- `configs/s1-baselines.json`: fixed 30-case configuration.
- `vendor/dag_builder.py`: byte-preserved instructor reference implementation.
- `tests/`: 12 small rule and tamper-detection checks.
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

Later work will build and evaluate an original optimiser, starting with MLP.
The optional connected Attention + MLP problem is outside the initial scope.
