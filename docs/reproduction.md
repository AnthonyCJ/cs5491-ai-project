# Reproduce the candidate's results and reports

The outputs include directed acyclic graphs (DAGs), Portable Network Graphics (PNG)
images, Scalable Vector Graphics (SVG) sources and Portable Document Format (PDF) reports.

Start with a fresh copy acquired from the fixed candidate tag and the
[installation guide](installation-unverified.md). These commands define a future
reader run; candidate preparation did not execute a new full numerical, figure or
report pass. [Validation coverage](reader-acceptance.md) states what was tested
historically and what remains untested.

## 1. Select explicit inputs

From the repository root in the same PowerShell terminal used for setup:

```powershell
$ErrorActionPreference = 'Stop'
$readerRoot = (Get-Location).Path
$ReaderPwsh = Join-Path $readerRoot '.tools/powershell/pwsh.exe'
$NumericalPython = Join-Path $readerRoot '.venv-s2/Scripts/python.exe'
$DocumentPython = Join-Path $readerRoot '.venv-docs/Scripts/python.exe'
$ReaderFontDir = Join-Path $env:WINDIR 'Fonts'
$readerRunPrefix = 'candidate-01'
if ((Get-FileHash -LiteralPath 'vendor/dag_builder.py').Hash.ToLowerInvariant() -ne '47a63fd1698da64731f8b9e77067f3ef7e0889534c4e7659bb7fc113ce97acee') { throw 'Instructor input differs' }
$readerEvidenceDir = Join-Path $readerRoot ('results/local-' + $readerRunPrefix + '-record')
if (Test-Path -LiteralPath $readerEvidenceDir) { throw 'Choose a new prefix' }
New-Item -ItemType Directory -Path $readerEvidenceDir | Out-Null
Start-Transcript -Path (Join-Path $readerEvidenceDir 'commands.txt')
```

Use explicitly checked existing tool paths instead if reusing an environment;
record that choice and do not call it a fresh installation. A machine-locator file
is unnecessary. Keep execution logs local because they contain machine paths.
Each task refuses an existing output directory. After a failure preserve that
attempt and use a new prefix only for a justified new attempt.

The controlled launcher requires an ordinary non-administrator, non-AppContainer
Windows context. It selects process-local temporary/cache directories, checks
creation/identity/exit evidence and refuses unobserved Python child creation.
A refusal or incomplete receipt is a failed or blocked step; do not remove checks
or elevate privileges to obtain a successful label.

## 2. Check entry and reproduce both numerical protocols

```powershell
& $ReaderPwsh -NoProfile -File scripts/reader-run.ps1 -Python $NumericalPython -Task preflight -Output "results/local-$readerRunPrefix-preflight" -LimitSeconds 60
if ($LASTEXITCODE -ne 0) { throw 'Preflight failed' }
& $ReaderPwsh -NoProfile -File scripts/reader-run.ps1 -Python $NumericalPython -Task formal -Output "results/local-$readerRunPrefix-formal" -LimitSeconds 1200
if ($LASTEXITCODE -ne 0) { throw 'Formal reproduction incomplete' }
& $ReaderPwsh -NoProfile -File scripts/reader-run.ps1 -Python $NumericalPython -Task s3 -Output "results/local-$readerRunPrefix-s3" -LimitSeconds 1200
if ($LASTEXITCODE -ne 0) { throw 'S3 reproduction incomplete' }
```

| Task | Expected outputs and checks |
|---|---|
| Preflight | Task `receipt.json` and worker results confirm imports, actual entry conditions and temporary/cache cleanup |
| Formal comparison | `results/local-<prefix>-formal/local-formal/reproduction.json`, 30 condition directories and 30 adjacent `*-check.json` files; all conditions and saved-result checks pass |
| Earlier S3 protocol | `results/local-<prefix>-s3/local-s3/run.json`, `cases/`, `summary.csv`, `tiny-examples.json`, `s2-comparison.json`, `artifacts.sha256.json`; 30 conditions, six small exhaustive examples and saved-DAG verification |

The formal protocol fixes one search worker, seed 5491, a 60-second solver ceiling
per condition and zero objective gap. Its existing run/check watchdogs remain
90/30 seconds. These are two report protocols on the same 30 course conditions,
not 60 different benchmark problems. The [scoring criteria](grading.md) require
legality, complete costs, strict same-input improvement, exact objective/bound
agreement and instructor-score error at most 1e-7 milliseconds.

Read task receipts as well as exit codes. Require confirmed worker/job exits,
complete process records and cleanup. Compare all 30 exact formal objectives with
the frozen table; timing, memory and equally optimal graph arrangements may differ.
Historical S1/S2 checks remain preserved evidence, not additional mandatory reruns.
The older driver's `independent_environment_reproduction=false` field is a
creation-time statement; a new reproduction needs its own result record.

## 3. Generate figures from the correct sources

```powershell
& $ReaderPwsh -NoProfile -File scripts/reader-run.ps1 -Python $NumericalPython -Task formal-figures -Output "results/local-$readerRunPrefix-formal-figures" -LimitSeconds 300
if ($LASTEXITCODE -ne 0) { throw 'Formal figures failed' }
& $ReaderPwsh -NoProfile -File scripts/reader-run.ps1 -Python $NumericalPython -Task s3-saved-figures -Output "results/local-$readerRunPrefix-s3-saved-figures" -LimitSeconds 300
if ($LASTEXITCODE -ne 0) { throw 'Saved S3 figures failed' }
& $ReaderPwsh -NoProfile -File scripts/reader-run.ps1 -Python $NumericalPython -Task s3-fresh-figures -InputRun "results/local-$readerRunPrefix-s3/local-s3" -Output "results/local-$readerRunPrefix-s3-fresh-figures" -LimitSeconds 300
if ($LASTEXITCODE -ne 0) { throw 'Fresh S3 figures failed' }
```

The formal output has `local-figures/` with 32 files, including seven PNG images,
seven Scalable Vector Graphics (SVG) files and seven drawing-data files. It derives
from **frozen T2**, not the new numerical output; its original checker covers all
30 table rows and four complete placements. Compare the new costs with the frozen
costs before treating these report curves as reproduced.

Each S3 output has three PNG/SVG/data groups and separate provenance. One set
reconstructs saved report figures; the other depicts newly generated S3 graphs.
Inspect all 13 PNG and 13 SVG sources, including full long-graph extents, according
to [the viewing guide](reader-visual.md). Generation and image decoding alone do
not establish visual correctness.

## 4. Rebuild the two historical reader reports

```powershell
& $ReaderPwsh -NoProfile -File scripts/reader-run.ps1 -Python $DocumentPython -Task proposal -Output "results/local-$readerRunPrefix-proposal" -FontDir $ReaderFontDir -LimitSeconds 120
if ($LASTEXITCODE -ne 0) { throw 'Historical Proposal build failed' }
& $ReaderPwsh -NoProfile -File scripts/reader-run.ps1 -Python $DocumentPython -Task milestone -Output "results/local-$readerRunPrefix-milestone" -FontDir $ReaderFontDir -LimitSeconds 120
if ($LASTEXITCODE -ne 0) { throw 'Milestone build failed' }
```

These unchanged tasks build **P-D1-ID-v1** and **M-MAINLINE-ID-v2**. Each PDF is
written **directly into its selected task output directory**, alongside
`receipt.json`, `build-info.json`, `format-check.json`, `render.json` and rendered
page images. There is no extra `document/` directory:

- `results/local-<prefix>-proposal/proposal.pdf`: one page;
- `results/local-<prefix>-milestone/milestone.pdf`: four pages.

The existing document stack renders the five pages at 150 dots per inch (dpi).
Inspect all pages for complete content/identities, clipping, overlap, A4 page size,
Times New Roman 12-point text and 2.5 cm margins. A successful automated checker
or a historically accepted original does not accept a newly generated PDF.

## 5. Current Proposal terminology revision

The latest accepted Proposal is **P-TERMS-ID-v1**. Its unchanged original PDF and
build inputs are included, but it was not part of R6/R7's report rebuild. Its
historical build used Python 3.12.14, ReportLab 4.4.9, pdfplumber 0.11.9 and
pypdf 6.10.0. The candidate document lock instead includes the R6-tested pypdf
6.21.4 and other recorded newer document packages. A rebuild of this latest report
in that environment is **not yet validated**.

The original standalone entry is supplied for that separately recorded check:

```powershell
$termsDir = "results/local-$readerRunPrefix-proposal-terms"
& $DocumentPython -B -s reports/proposal/versions/P-TERMS-ID-v1/build_proposal.py --output "$termsDir/proposal.pdf" --font-dir $ReaderFontDir
if ($LASTEXITCODE -ne 0) { throw 'Current Proposal build failed' }
& $DocumentPython -B -s reports/proposal/versions/P-TERMS-ID-v1/check_proposal.py --directory $termsDir
if ($LASTEXITCODE -ne 0) { throw 'Current Proposal check failed' }
```

Expected output is a one-page PDF and its source/evidence/format records. Inspect
that new page independently using a suitable PDF viewer or the optional PDF
renderer. Do not substitute it for the historical reader Proposal or infer its
compatibility from the older report's pass. No report substance is changed here.

## 6. Timings and completion record

Historical observations provide scale only: an earlier local formal reproduction
driver took 39.9841531 seconds; the earlier S3 solver calls totalled
10.64452149963472 seconds. These are different scopes and must not be added.
The frozen formal experiment's 201.9114114-second supervised total includes
validation launches as well as runs/checks; it is not a setup or reproduction
estimate. Sources are in [claim-evidence.json](claim-evidence.json).

The command limits above are ceilings, not measured durations or permission for
unbounded retries. Installation and new-host runtimes are unmeasured. Record each
actual start/end, output, version and failure. Finish with `Stop-Transcript` after
all work or a safely stopped attempt. Recheck the candidate payload against the
manifest, and preserve/hash new outputs separately. Record each numerical,
figure, report and visual requirement as passed, failed, blocked or not run.
Do not replace missing evidence with saved outputs from an older run.
