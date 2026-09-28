# Milestone M-S3-v1

The [four-page PDF](milestone.pdf) is a public content/format draft derived from
[S3-OPT-001](../../results/S3-OPT-001/README.md). Its editable source is
[milestone.md](milestone.md); [resolved-source.md](resolved-source.md) exposes
the numerical fields used in the rendered version.

The report covers the problem, original formulation and reconstruction,
correctness evidence, experiment configuration, all 30 preliminary results,
interpretation, resource observations and remaining work. It preserves the
earlier Proposal and S1/S2 evidence. It does not claim S4 frozen experiments,
S6 independent reproduction, public hosting or actual submission.

The PDF uses A4, actual embedded Times New Roman at 12 pt, 2.5 cm margins and
12 pt single-line leading. The native vector chart and table labels also use
12 pt Times New Roman. Figures and captions are included in its four pages.
See [format-check.json](format-check.json) and [build-info.json](build-info.json).

## Rebuild

In a separate report-generation environment containing the pinned dependency:

```powershell
python -m pip install -r reports/milestone/requirements.txt
python -B reports/milestone/build_milestone.py
```

The report builder reads saved results and checks their hashes; it does not
search. Numeric fields, grouped results and all 30 plotted points come from
the saved run. It rejects changes to the reported score ranges so that an old
narrative is not silently paired with new results. A new reproduction can be
selected using `--run results/local-s3-reproduction` and a separate `--output`.
The report takes about a second to build in the observed local environment;
this is approximate tool wall time, not a benchmark. PDF timestamps may differ.

The default fonts are read from `C:/Windows/Fonts`. Elsewhere pass `--font-dir`
with licensed `times.ttf`, `timesbd.ttf`, `timesi.ttf` and `timesbi.ttf`. No font
files are distributed. The preserved Proposal builder supplies font registration.
Text, page count, font embedding, margins and every rendered page must be
checked after edits, especially after completing identities.

## Submission requirements still pending

- Three official English names and student IDs, and one group contact email,
  in a restricted submission copy followed by another content/format check.
- Instructor-code redistribution permission or an approved acquisition method.
- An actual public online repository URL and the revision to be graded.
- Authorisation for, and completion of, the actual course submission.

The milestone deadline in the supplied course snapshot is 2026-11-19 23:59
Beijing time. Later Canvas updates have not been independently checked.
Local content/format readiness is separate from complete submission readiness.
