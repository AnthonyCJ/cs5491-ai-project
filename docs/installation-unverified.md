# Acquire and install the engineering candidate

**Validation status:** the original candidate 01 failed environment creation because
`UV_PYTHON_PREFERENCE=only-managed` conflicts with the redundant `--managed-python`
option in uv 0.12.23. This revision removes that option from the two `uv venv`
commands while retaining managed-only selection and exact Python versions.
The corrected route passed a local same-machine fresh installation and the
required numerical, figure and three-report checks on 13 November 2026.
Viewing tools, Windows and licensed fonts were shared. The revised public
acquisition chain and owner acceptance remain pending; see the
[revision record](installation-revision-20261113.json).

## 1. Obtain the fixed revision

Use Windows x64 and Git from its [official Windows distribution](https://git-scm.com/download/win).
After the candidate tag has been published, run from a parent directory in which
`cs5491-reader` does not already exist:

```powershell
git -c core.autocrlf=false clone --single-branch --branch engineering-candidate-20261113-02 https://github.com/AnthonyCJ/cs5491-ai-project.git cs5491-reader
if ($LASTEXITCODE -ne 0) { throw 'Candidate acquisition failed' }
Set-Location -LiteralPath cs5491-reader
git rev-parse HEAD
```

Record that actual commit and compare it with the published candidate reference.
The repository's attributes preserve exact bytes, including frozen line endings.
Do not run a formatter over evidence or historical generators. Verify the payload:

```powershell
$ErrorActionPreference = 'Stop'
$readerRoot = (Get-Location).Path
$expected = (Get-Content -LiteralPath candidate-manifest.sha256 -Raw).Trim().Split(' ')[0]
if ((Get-FileHash -LiteralPath candidate-manifest.json).Hash.ToLowerInvariant() -ne $expected) { throw 'Candidate manifest differs' }
$manifest = Get-Content -LiteralPath candidate-manifest.json -Raw | ConvertFrom-Json
if ($manifest.file_count -ne @($manifest.files).Count) { throw 'File count differs' }
foreach ($item in $manifest.files) {
    $path = [IO.Path]::GetFullPath((Join-Path $readerRoot $item.path))
    if (-not $path.StartsWith($readerRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) { throw 'Path escaped candidate' }
    if ((Get-Item -LiteralPath $path).Length -ne $item.bytes -or (Get-FileHash -LiteralPath $path).Hash.ToLowerInvariant() -ne $item.sha256) { throw ('Changed input: ' + $item.path) }
}
```

The sidecar checks integrity within the acquired revision; the trusted repository
and exact tag/commit provide the acquisition reference. There is no training-data
download. The exact instructor input and small benchmark graphs are included.

## 2. Obtain an explicit PowerShell and Python tool

An existing PowerShell 7.2+ can run the launcher. For the specified 7.6.9 target,
use its official portable archive. These bootstrap commands can run in ordinary
Windows PowerShell; they install no system-wide executable or shell profile.
Use a fresh `.tools` directory and a legally licensed Windows environment.

```powershell
$readerTools = Join-Path $readerRoot '.tools'
if (Test-Path -LiteralPath $readerTools) { throw 'Use a fresh reader directory' }
New-Item -ItemType Directory -Path $readerTools | Out-Null
Invoke-WebRequest 'https://github.com/PowerShell/PowerShell/releases/download/v7.6.9/PowerShell-7.6.9-win-x64.zip' -OutFile (Join-Path $readerTools 'powershell.zip')
if ((Get-FileHash -LiteralPath (Join-Path $readerTools 'powershell.zip')).Hash.ToLowerInvariant() -ne 'ce7484804c0f0ad4dda10c958e71acdaf7eebfb22505c1b480f89e0e9f1da94d') { throw 'PowerShell archive differs' }
Expand-Archive -LiteralPath (Join-Path $readerTools 'powershell.zip') -DestinationPath (Join-Path $readerTools 'powershell')
$ReaderPwsh = Join-Path $readerTools 'powershell/pwsh.exe'
& $ReaderPwsh --version
if ($LASTEXITCODE -ne 0) { throw 'PowerShell failed' }
Invoke-WebRequest 'https://github.com/astral-sh/uv/releases/download/0.12.23/uv-x86_64-pc-windows-msvc.zip' -OutFile (Join-Path $readerTools 'uv.zip')
if ((Get-FileHash -LiteralPath (Join-Path $readerTools 'uv.zip')).Hash.ToLowerInvariant() -ne '75d05de6762778c31ee183398de7dd15093fad0ed90b1f236d8205ea5ec00c90') { throw 'uv archive differs' }
Expand-Archive -LiteralPath (Join-Path $readerTools 'uv.zip') -DestinationPath (Join-Path $readerTools 'uv')
$uvPaths = @(Get-ChildItem -LiteralPath (Join-Path $readerTools 'uv') -Recurse -File -Filter uv.exe)
if ($uvPaths.Count -ne 1) { throw 'Expected exactly one uv executable' }
$ReaderUv = $uvPaths[0].FullName
& $ReaderUv --version
if ($LASTEXITCODE -ne 0) { throw 'uv failed' }
```

The [uv command reference](https://docs.astral.sh/uv/reference/cli/#uv-python-install)
documents the local installation controls. The exact release assets, hashes and interpreter catalogue entries are in
[dependency-sources.json](dependency-sources.json). CPython 3.13.9 also has an
[official Windows installer](https://www.python.org/downloads/release/python-3139/),
but [CPython 3.12.14 is source-only at python.org](https://www.python.org/downloads/release/python-31214/).
This route uses uv 0.12.23's fixed catalogue of
[python-build-standalone](https://github.com/astral-sh/python-build-standalone)
Windows builds for both versions. They need not be byte-identical to the prior
local interpreters. Their compatibility is a new verification responsibility.

## 3. Create separate new dependency environments

Keep the same terminal and repository root. The following variables affect that
terminal and child processes only. No existing virtual environment is copied.
The cache is local to this new reader directory; do not prefill it from old runs.

```powershell
$env:UV_PYTHON_INSTALL_DIR = Join-Path $readerTools 'python'
$env:UV_CACHE_DIR = Join-Path $readerTools 'uv-cache'
$env:UV_NO_CONFIG = '1'
$env:UV_PYTHON_PREFERENCE = 'only-managed'
$env:UV_PYTHON_INSTALL_BIN = '0'
$env:UV_PYTHON_INSTALL_REGISTRY = '0'
& $ReaderUv python install --no-bin --no-registry 3.13.9 3.12.14
if ($LASTEXITCODE -ne 0) { throw 'Exact interpreter acquisition failed' }
& $ReaderUv venv --python 3.13.9 .venv-s2
if ($LASTEXITCODE -ne 0) { throw 'Numerical environment creation failed' }
& $ReaderUv venv --python 3.12.14 .venv-docs
if ($LASTEXITCODE -ne 0) { throw 'Document environment creation failed' }
$NumericalPython = Join-Path $readerRoot '.venv-s2/Scripts/python.exe'
$DocumentPython = Join-Path $readerRoot '.venv-docs/Scripts/python.exe'
& $ReaderUv pip install --python $NumericalPython --index-url https://pypi.org/simple --only-binary :all: --no-deps -r requirements-s2.txt
if ($LASTEXITCODE -ne 0) { throw 'Numerical package installation failed' }
& $ReaderUv pip install --python $DocumentPython --index-url https://pypi.org/simple --only-binary :all: --no-deps -r requirements-docs-lock.txt
if ($LASTEXITCODE -ne 0) { throw 'Document package installation failed' }
& $ReaderUv pip check --python $NumericalPython
if ($LASTEXITCODE -ne 0) { throw 'Numerical dependency check failed' }
& $ReaderUv pip check --python $DocumentPython
if ($LASTEXITCODE -ne 0) { throw 'Document dependency check failed' }
& $NumericalPython --version
& $DocumentPython --version
$ReaderFontDir = Join-Path $env:WINDIR 'Fonts'
foreach ($name in @('times.ttf','timesbd.ttf','timesi.ttf','timesbi.ttf')) {
    if (-not (Test-Path -LiteralPath (Join-Path $ReaderFontDir $name) -PathType Leaf)) { throw ('Missing licensed font: ' + $name) }
}
```

The locks contain 19 numerical and 10 document pins. Their 29 active non-extra
supplier dependency constraints are satisfied by those pins for the declared
Windows/Python versions; compatible wheel files are listed. This is a metadata
check, not a resolver/install/import test. `--no-deps` deliberately prevents an
unrecorded package from silently supplementing the complete declared closure.
A failure must be investigated, not bypassed by upgrading packages.

If legally held fonts are elsewhere, set `$ReaderFontDir` to that directory.
Record their hashes and inspect rebuilt layouts. See [font terms](public-scope.md).
Numerical work needs neither these fonts nor document packages.

## 4. Viewing and optional rendering tools

The numeric/figure/report commands use Python and PowerShell. Their outputs can
be inspected in suitable local image, Scalable Vector Graphics (SVG), Portable Document Format (PDF) and Markdown viewers. The optional
controlled rendering utilities preserve the earlier reader inspection route; they
use Node.js 24.22.1, sharp 0.35.5, marked 17.0.5 and Playwright 1.62.1.

Official source records are in [dependency-sources.json](dependency-sources.json),
including the Node Windows ZIP checksum and a Chrome for Testing 158.0.8127.18
Windows download. These components are not redistributed. A legally installed
Chrome was used historically; Chrome for Testing is a public acquisition option,
not a tested substitute. The optional Node packages' transitive closure has not
been installed or frozen for this candidate. Record the actual package lock and
browser identity when provisioning them in the separate environment-validation task.
Do not represent the optional rendering route as freshly installed or validated.

For existing explicit tool paths, the complete rendering and inspection commands
are in [reader-visual.md](reader-visual.md). Otherwise use appropriate viewers and
record which sources were actually viewed; an unavailable display is a coverage gap.

## 5. Continue and record limitations

Proceed to [reproduction](reproduction.md) only after prerequisites succeed.
Retain installation logs, versions, source hashes, commands, elapsed time and
failures locally. Do not publish logs containing usernames or machine paths.
Fresh-installation duration is unmeasured; package download time depends on network
access. Existing-machine historical timings in the reproduction guide are not an
installation estimate. This guide does not certify a new machine or the entire
course-delivery workflow.
