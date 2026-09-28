# Proposal P-S2-v1

Prepared 2026-09-28. The editable source is [proposal.md](proposal.md); the
one-page rendered document is [proposal.pdf](proposal.pdf).

The public version contains identity placeholders. Confirmed English names,
all student IDs and one contact email must be supplied in a separate restricted
submission copy before formal submission. The public copy is not evidence that
the identity requirement has been met. No submission has occurred.

Technical statements refer to [S2-OPT-001](../../results/S2-OPT-001/README.md)
and [S1-BL-001](../../results/S1-BL-001/README.md). The remaining 12 Attention
inputs, S4 formal experiments and S6 clean-environment reproduction are future
work. The proposal does not claim those are complete.

## Format and regeneration

The PDF uses A4, Times New Roman 12 pt throughout, 2.5 cm page margins and
12 pt line leading (single spacing), with modest paragraph spacing. There is
no abstract or reference list. The intended course deadline is 2026-10-15
23:59 Beijing time, based on the supplied course snapshot.

PDF generation is separate from the optimiser environment. With a Python
environment containing the pinned report dependency:

```powershell
python -m pip install -r reports/proposal/requirements.txt
python reports/proposal/build_proposal.py --output reports/proposal/proposal.pdf
```

The default font directory is Windows' standard font directory. On another
system, provide `--font-dir <directory>` containing licensed `times.ttf`,
`timesbd.ttf`, `timesi.ttf` and `timesbi.ttf`. The script fails if the actual
Times New Roman files are missing; it does not silently substitute a different
font. Font files are not redistributed. Edit `proposal.md` and regenerate,
then recheck the one-page limit and rendering, particularly after inserting
full names and IDs. PDF timestamps may differ between builds.

The Markdown and generator are the editable source. No Word/LibreOffice
installation is required to build the PDF. Formatting checks are recorded in
[format-check.json](format-check.json).
