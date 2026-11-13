# Third-party sources and notices

The project distinguishes its placement formulation, reconstruction, checking and
analysis from supplied graphs/scoring and general-purpose dependencies. No blanket
licence is assigned to every file in this repository. Preserve the notices of any
software you obtain; the entries below identify dependencies, not a replacement
for their complete licence terms.

| Material | Role and source | Distribution boundary |
|---|---|---|
| Instructor `dag_builder.py` | Supplied graphs, cost functions, reference placements and scorer; [course attribution](vendor/README.md) | Exact course file included on the owner's report of instructor permission; no invented open-source licence |
| OR-Tools | General Constraint Programming - Satisfiability (CP-SAT) solver used by the project's integer model; [project](https://github.com/google/or-tools) | Apache-2.0; installed separately through the numerical lock |
| Python packages | Numerical arrays/tables/plotting, process observations and document build/check/render support | Pinned supplier versions, dependency constraints, metadata/licence links and wheel hashes are in [dependency sources](docs/dependency-sources.json); package binaries are not vendored |
| CPython | Numerical and document interpreter | [Python licence](https://docs.python.org/3/license.html); selected Windows builds obtained separately from [python-build-standalone](https://github.com/astral-sh/python-build-standalone), with their accompanying notices |
| uv | Fixed-version environment acquisition tool | [Astral uv](https://github.com/astral-sh/uv), MIT/Apache-2.0; separately acquired |
| PowerShell | Windows task launcher and process controls | [PowerShell](https://github.com/PowerShell/PowerShell), MIT; separately acquired |
| Node.js | Optional source-rendering runtime | [Node.js](https://nodejs.org/), including its bundled notices; separately acquired |
| sharp / marked / Playwright | Optional Scalable Vector Graphics (SVG) and Portable Network Graphics (PNG) rendering, Markdown parsing and browser driving | Supplier metadata identifies Apache-2.0 / MIT / Apache-2.0 respectively; installed separately, not bundled |
| Browser | Optional Hypertext Markup Language (HTML) and Markdown rendering | Existing licensed browser or [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/); its terms apply; a new browser acquisition is not a validated runtime here |
| Times New Roman | Required report typeface | [Microsoft supplying-product and licensing information](https://learn.microsoft.com/en-us/typography/font-list/times-new-roman); no standalone font binary is redistributed |

Existing figure metadata identifies the plotting software. Report Portable Document Format (PDF) files keep the
fonts embedded by their original generators; the separately licensed font files
remain external prerequisites. Names/student identifiers/contact details in the
approved reports are authorised report fields, not a licence for other uses or
for publication of identity master records.

Public availability of a source URL does not prove installation or compatibility.
The [installation guide](docs/installation-unverified.md) and
[validation scope](docs/reader-acceptance.md) state the unverified boundaries.
