# Public companion: regenerate into a fresh results/local-* directory.
# The approved PDF was imported unchanged; see import-info.json.
"""Build M-W01-ID-v1 from its English content-review source and saved S3 evidence.

All text, including vector chart labels, uses actual Times New Roman at 12 pt.
Fonts are read from the operating system or --font-dir and are not redistributed.
This builder never solves a placement or modifies an experiment directory.
"""

import argparse
from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from xml.sax.saxutils import escape

import reportlab
from reportlab.graphics.shapes import Circle, Drawing, Line, PolyLine, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Table, TableStyle

ROOT = Path(__file__).resolve().parents[4]
VERSION = "M-W01-ID-v1"
spec = importlib.util.spec_from_file_location("w01_support", ROOT / "reports/identity_report_support.py")
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)


def read_json(path):
    """Read only saved UTF-8 evidence."""
    return json.loads(path.read_text(encoding="utf-8"))


def digest(path):
    """Identify exact artifact bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font_registration(font_dir):
    """Reuse the preserved Proposal font loader, with explicit provenance."""
    path = ROOT / "reports/proposal/build_proposal.py"
    spec = importlib.util.spec_from_file_location("proposal_fonts", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.register_fonts(font_dir)


def chart(cases, width):
    """Draw two full curves at final page dimensions; label fonts remain 12 pt."""
    d = Drawing(width, 232)
    blue, teal, grey = colors.HexColor("#356dad"), colors.HexColor("#087f73"), colors.HexColor("#d5dce2")
    def text(x, y, value, anchor="start", bold=False):
        d.add(String(x, y, value, fontName="TNRBold" if bold else "TNR", fontSize=12, textAnchor=anchor))
    text(0, 220, "Estimated latency (ms)")
    d.add(Line(190, 224, 206, 224, strokeColor=blue, strokeWidth=1.1, strokeDashArray=[3, 2]))
    text(210, 220, "Teacher baseline")
    d.add(Line(348, 224, 364, 224, strokeColor=teal, strokeWidth=1.1))
    text(369, 220, "CP-SAT")
    for module, left, low, high, ticks, label in (
        ("mlp", 44, 21000, 29000, (22000, 25000, 28000), "MLP"),
        ("attention", 276, 40000, 55000, (42000, 48000, 54000), "Attention")):
        right, bottom, top = left + 160, 40, 176
        text((left + right) / 2, 193, label, "middle", True)
        d.add(Line(left, bottom, right, bottom, strokeColor=colors.black, strokeWidth=0.5))
        d.add(Line(left, bottom, left, top, strokeColor=colors.black, strokeWidth=0.5))
        def x(level):
            return left + level / 14 * (right - left)
        def y(value):
            return bottom + (float(value) - low) / (high - low) * (top - bottom)
        for value in ticks:
            d.add(Line(left, y(value), right, y(value), strokeColor=grey, strokeWidth=0.4))
            text(left - 5, y(value) - 4, f"{value:,}", "end")
        for level in (0, 6, 14):
            text(x(level), 24, str(level), "middle")
        text((left + right) / 2, 7, "Input level", "middle")
        subset = sorted((c for c in cases if c["module"] == module), key=lambda c: c["l_init"])
        baseline = [(x(c["l_init"]), y(c["baseline_decimal_ms"])) for c in subset]
        ours = [(x(c["l_init"]), y(c["validated"]["audit"]["latency_decimal_ms"])) for c in subset]
        d.add(PolyLine(baseline, strokeColor=blue, strokeWidth=1, strokeDashArray=[3, 2]))
        d.add(PolyLine(ours, strokeColor=teal, strokeWidth=1.2))
        for px, py in ours:
            d.add(Circle(px, py, 1.7, fillColor=teal, strokeColor=teal))
    return d


def grouped_rows(cases):
    """Check the four reported ranges against every constituent saved case."""
    rows = [["Block, inputs", "Latency (ms)", "Reduction (%)", "B1 / B2"]]
    for module, levels, expected in (("mlp", range(14), "26069.9524"), ("mlp", [14], "21911.5924"),
                                    ("attention", range(6), "45698.2664"), ("attention", range(6, 15), "41537.6664")):
        subset = [c for c in cases if c["module"] == module and c["l_init"] in levels]
        assert len(subset) == len(levels)
        assert all(Decimal(c["validated"]["audit"]["latency_decimal_ms"]) == Decimal(expected) for c in subset), "Results changed; revise the report narrative"
        counts = {(c["validated"]["audit"]["n_b1"], c["validated"]["audit"]["n_b2"]) for c in subset}
        assert len(counts) == 1
        b1, b2 = counts.pop()
        reduction = sorted(Decimal(c["comparison"]["reduction_percent"]) for c in subset)
        displayed = f"{reduction[0]:.4f}" if reduction[0] == reduction[-1] else f"{reduction[0]:.4f}-{reduction[-1]:.4f}"
        span = str(min(levels)) if len(levels) == 1 else f"{min(levels)}-{max(levels)}"
        rows.append([("MLP" if module == "mlp" else "Attention") + ", " + span, expected, displayed, f"{b1} / {b2}"])
    return rows


def build(source, output, run_dir, font_dir):
    """Resolve numeric placeholders, create the PDF and save derivation metadata."""
    font_registration(font_dir)
    if run_dir.resolve() != (ROOT / "results/S3-OPT-001").resolve():
        raise ValueError("M-W01-ID-v1 is tied to the preserved S3 evidence, not a new run")
    support.prepare_output(source, output)
    source_index = Path(__file__).with_name("sources.json")
    run, cases, index = support.checked_s3(source_index)
    assert not run["git"]["worktree_dirty_at_run"], "Report clean-source statement needs revision"
    context = {"RUN_ID": run["run_id"], "SOURCE_COMMIT": run["git"]["head_at_run"],
               "SOLVE_SUM": f"{run['solve_wall_seconds_sum']:.4f}",
               "RSS_MIB": f"{run['maximum_sampled_rss_bytes'] / 1048576:.2f}"}
    for module, prefix in (("mlp", "MLP"), ("attention", "ATTN")):
        times = [c["solution"]["solve_wall_seconds"] for c in cases if c["module"] == module]
        context[prefix + "_MIN"], context[prefix + "_MAX"] = f"{min(times):.4f}", f"{max(times):.4f}"
    text = source.read_text(encoding="utf-8")
    if VERSION not in text:
        raise ValueError("Source must identify M-W01-ID-v1")
    for key, value in context.items():
        text = text.replace("{{" + key + "}}", value)
    assert set(re.findall(r"\{\{([^}]+)\}\}", text)) == {"RESULTS_TABLE", "LATENCY_FIGURE"}, "Unresolved report field"
    body = ParagraphStyle("Body", fontName="TNR", fontSize=12, leading=12, spaceAfter=7,
                          allowWidows=0, allowOrphans=0)
    heading = ParagraphStyle("Heading", parent=body, fontName="TNRBold", spaceBefore=4, spaceAfter=6, keepWithNext=True)
    title = ParagraphStyle("Title", parent=body, fontName="TNRBold", spaceAfter=6, keepWithNext=True)
    cell = ParagraphStyle("Cell", parent=body, spaceAfter=0)
    headcell = ParagraphStyle("Headcell", parent=cell, fontName="TNRBold")
    margin, width = 2.5 * cm, A4[0] - 5 * cm
    rows = grouped_rows(cases)
    story = []
    for block in text.strip().split("\n\n"):
        if block == "<!-- pagebreak -->":
            story.append(PageBreak())
        elif block == "{{RESULTS_TABLE}}":
            data = [[Paragraph(escape(v), headcell if i == 0 else cell) for v in row] for i, row in enumerate(rows)]
            table = Table(data, colWidths=[115, 110, 138, width - 363], repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                      ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf1f4")),
                                      ("LINEBELOW", (0, 0), (-1, 0), 0.7, colors.black),
                                      ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#bcc8d0")),
                                      ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                                      ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
            table.spaceAfter = 7
            story.append(table)
        elif block == "{{LATENCY_FIGURE}}":
            story.append(chart(cases, width))
        else:
            style = heading if block.startswith("## ") else title if block.startswith("# ") else body
            value = block[3:] if block.startswith("## ") else block[2:] if block.startswith("# ") else block
            story.append(Paragraph(escape(value).replace("\n", "<br/>"), style))
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(output), pagesize=A4, leftMargin=margin, rightMargin=margin,
                          topMargin=margin, bottomMargin=margin + 20,
                          title="Automated Bootstrapping Placement for Encrypted Inference",
                          author=support.author_line(source.parent), subject="Milestone M-W01-ID-v1; content-review draft; restricted user-supplied identities")
    frame = Frame(margin, margin + 20, width, A4[1] - 2 * margin - 20,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    def footer(canvas, document):
        canvas.setFont("TNR", 12)
        canvas.drawCentredString(A4[0] / 2, margin + 3, str(document.page))
    doc.addPageTemplates(PageTemplate(id="Milestone", frames=[frame], onPage=footer))
    doc.build(story)
    assert doc.page == 4, f"Expected four pages, got {doc.page}; review source layout"
    resolved = text.replace("{{RESULTS_TABLE}}", "\n".join(" | ".join(row) for row in rows)).replace("{{LATENCY_FIGURE}}", "[Vector chart: all 30 saved baseline and optimised latency points.]")
    (output.parent / "resolved-source.md").write_text(resolved, encoding="utf-8", newline="\n")
    info = support.provenance(VERSION, source, output, Path(__file__), source_index, run,
                              ["reports/milestone/build_milestone.py", "reports/proposal/build_proposal.py"])
    info.update(page_count=doc.page, source_file=source.name, pdf_file=output.name,
                resolved_source_sha256=digest(output.parent / "resolved-source.md"),
                result_rows=rows, resolved_fields=context, chart_font_pt=12, figure_points=30,
                predecessor="M-W01-v1",
                candidate_status="direction only; no design, implementation or inclusion decision")
    support.write_json(output.parent / "build-info.json", info)
    print(f"Created {output.name}: {doc.page} pages")


if __name__ == "__main__":
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=directory / "milestone.md")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run", type=Path, default=ROOT / "results/S3-OPT-001")
    parser.add_argument("--font-dir", type=Path, default=Path("C:/Windows/Fonts"))
    args = parser.parse_args()
    build(args.source, args.output, args.run.resolve(), args.font_dir)
