# Inspect figures, PDFs and instructions

Inspect the actual sources produced by the run being assessed. Portable Network
Graphics (PNG) images, Scalable Vector Graphics (SVG) sources and Portable Document
Format (PDF) pages carry different evidence. Viewing a paired PNG does not show
that its SVG renders correctly, and text extraction does not establish PDF layout.

## Required content coverage

For the complete historical reader workflow in [reproduction](reproduction.md),
inspect 13 PNGs and 13 SVGs: seven formal-analysis groups, three saved-S3 groups and
three fresh-S3 groups. View the complete long diagrams with zoom or scrolling;
check labels, units, legends, arrows, clipping and all nodes/edges. Formal-analysis
figures are regenerated from frozen formal data, not from the new formal run.

Inspect the two historical report PDFs and all five pages: one Proposal page and
four Milestone pages. Their page images are listed in each task's `render.json`,
directly beside `proposal.pdf` or `milestone.pdf`, `receipt.json` and format records.
If the current terminology Proposal is separately rebuilt, inspect its additional
one-page PDF separately; its new-environment compatibility is not inherited.

Read the actual Markdown instructions and tables, and verify local links. Record
files/hashes and what was actually viewed. A successful render or a queued preview
is not a visual judgment. Original source files are available for ordinary local
viewers; display availability must be recorded for the chosen route.

## Optional controlled source rendering

The browser displays Hypertext Markup Language (HTML) generated from Markdown.
The retained utilities support traceable rendering into complete images and
1600 by 1200 pixel tiles with overlap. They use the original ordinary-user
process-control checks. They were exercised during historical R6/R7 inspection;
a newly provisioned toolchain needs its own check. No browser protections should
be disabled to obtain a successful result.

Use explicit existing or separately acquired paths:

```powershell
$VisualNode = Read-Host 'Absolute path to Node.js 24.22.1 node.exe'
$VisualModules = Read-Host 'Absolute node_modules directory containing sharp 0.35.5, marked 17.0.5 and Playwright 1.62.1'
$VisualBrowser = Read-Host 'Absolute path to the browser executable being assessed'
```

The [source index](dependency-sources.json) identifies public acquisition options.
The previous browser was installed Chrome 158.0.8127.18. Chrome for Testing of that
version is available as a public option, but its substitution and the newly
installed Node dependency closure have not been tested. These tools are optional
for numerical execution; do not assert source-rendered viewing if they are absent.

Create a new request JSON under a fresh local output directory, listing all actual
package-relative paths for one format. Obtain the figure paths from the newly
generated manifests, not from a historical capability example. For Markdown:

```powershell
$viewRequest = "results/local-$readerRunPrefix-record/markdown-inputs.json"
@{files=@('README.md','docs/installation-unverified.md','docs/reproduction.md','docs/grading.md','docs/reader-visual.md','docs/reader-acceptance.md','docs/public-scope.md','docs/version-map.md','reports/README.md')} | ConvertTo-Json | Set-Content -LiteralPath $viewRequest -Encoding utf8
& $ReaderPwsh -NoProfile -File scripts/reader-visual.ps1 -Runtime $VisualNode -Task markdown -Request $viewRequest -Output "results/local-$readerRunPrefix-markdown-view" -Modules $VisualModules -Browser $VisualBrowser -LimitSeconds 120
if ($LASTEXITCODE -ne 0) { throw 'Markdown rendering failed' }
```

For PNG/SVG, make separate requests containing the actual new images and use:

```powershell
& $ReaderPwsh -NoProfile -File scripts/reader-visual.ps1 -Runtime $VisualNode -Task png -Request "results/local-$readerRunPrefix-record/png-inputs.json" -Output "results/local-$readerRunPrefix-png-view" -Modules $VisualModules -LimitSeconds 120
if ($LASTEXITCODE -ne 0) { throw 'PNG rendering failed' }
& $ReaderPwsh -NoProfile -File scripts/reader-visual.ps1 -Runtime $VisualNode -Task svg -Request "results/local-$readerRunPrefix-record/svg-inputs.json" -Output "results/local-$readerRunPrefix-svg-view" -Modules $VisualModules -LimitSeconds 120
if ($LASTEXITCODE -ne 0) { throw 'SVG rendering failed' }
```

SVG is rendered from its own bytes at 120 dots per inch. Report commands already
render their PDF pages at 150 dots per inch. For a separate PDF request, the
retained renderer is available without an additional Poppler installation:

```powershell
& $ReaderPwsh -NoProfile -File scripts/reader-visual.ps1 -Runtime $DocumentPython -Task pdf -Request "results/local-$readerRunPrefix-record/pdf-inputs.json" -Output "results/local-$readerRunPrefix-pdf-view" -LimitSeconds 120
if ($LASTEXITCODE -ne 0) { throw 'PDF rendering failed' }
```

Inspect every required output image/tile and keep source-to-render hashes plus
actual observations. The launchers' receipts must confirm full creation/exit
coverage and cleanup. Failed rendering, absent viewing or incomplete process
records remain failed/blocked, even when another format looks correct. Raw viewer
and process logs contain local data and must not enter a public commit.
