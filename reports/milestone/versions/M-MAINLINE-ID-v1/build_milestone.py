"""Build a Milestone from pinned saved evidence, without project runs.

Requires ReportLab 4.4.9 and licensed Times New Roman fonts. Old report bytes
are preserved. Use a fresh results/local-* directory for regeneration.
"""
import argparse
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import platform
import re
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, Frame, PageBreak, PageTemplate, Paragraph, Table, TableStyle

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[3]
VERSION = "M-MAINLINE-ID-v1"


def checked_inputs():
    """Verify document inputs and saved evidence without invoking project code."""
    spec = importlib.util.spec_from_file_location("milestone_evidence", ROOT / "reports/w01_support.py")
    support = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(support)
    source, source_index = DIRECTORY / "milestone.md", DIRECTORY / "sources.json"
    index = support.read_json(source_index)
    if index["artifact_version"] != VERSION or support.digest(source) != index["source_sha256"]:
        raise ValueError("Source/version differs from its pinned index")
    if support.digest(DIRECTORY / "identity.json") != index["identity_sha256"]:
        raise ValueError("Identity input changed")
    for group in ("predecessor_files_sha256", "generator_dependencies_sha256"):
        for name, expected in index[group].items():
            if support.digest(ROOT / name) != expected:
                raise ValueError(f"Preserved input changed: {name}")
    run, cases, _ = support.checked_s3(source_index)
    identity = support.read_json(DIRECTORY / "identity.json")
    return support, source, source_index, index, run, cases, identity


def content_values(support, source, run, cases):
    """Resolve numeric fields and reuse the preserved chart/table presentation."""
    legacy = support.load_module("preserved_milestone_chart", "reports/milestone/versions/M-W01-ID-v1/build_milestone.py")
    rows = legacy.grouped_rows(cases)
    context = {"SOLVE_SUM": f"{run['solve_wall_seconds_sum']:.4f}",
               "RSS_MIB": f"{run['maximum_sampled_rss_bytes'] / 1048576:.2f}"}
    for module, prefix in (("mlp", "MLP"), ("attention", "ATTN")):
        times = [c["solution"]["solve_wall_seconds"] for c in cases if c["module"] == module]
        context[prefix + "_MIN"], context[prefix + "_MAX"] = f"{min(times):.4f}", f"{max(times):.4f}"
    prose = source.read_text(encoding="utf-8")
    if not prose.isascii() or "CS5491 Artificial Intelligence Project Milestone" not in prose:
        raise ValueError("Expected the current English source")
    for key, value in context.items():
        prose = prose.replace("{{" + key + "}}", value)
    if set(re.findall(r"\{\{([^}]+)\}\}", prose)) != {"RESULTS_TABLE", "LATENCY_FIGURE"}:
        raise ValueError("Unresolved report field")
    resolved = prose.replace("{{RESULTS_TABLE}}", "\n".join(" | ".join(row) for row in rows))
    resolved = resolved.replace("{{LATENCY_FIGURE}}", "[Vector chart: all 30 saved baseline and optimised latency points.]")
    return legacy, rows, context, prose, resolved


def build(output, font_dir):
    """Create a report, resolved source and provenance tied to the saved run."""
    support, source, source_index, index, run, cases, identity = checked_inputs()
    output = output.resolve()
    if output != DIRECTORY / "milestone.pdf":
        relative = output.relative_to(ROOT / "results")
        if len(relative.parts) != 2 or not relative.parts[0].startswith("local-") or output.name != "milestone.pdf":
            raise ValueError("Use a fresh results/local-*/milestone.pdf output")
    info_path, resolved_path = output.parent / "build-info.json", output.parent / "resolved-source.md"
    if any(p.exists() for p in (output, info_path, resolved_path)):
        raise FileExistsError("Preserve existing artifacts; choose a fresh output directory")
    fonts = support.load_module("preserved_report_fonts", "reports/proposal/build_proposal.py")
    fonts.register_fonts(font_dir)
    legacy, rows, context, prose, resolved = content_values(support, source, run, cases)
    body = ParagraphStyle("Body", fontName="TNR", fontSize=12, leading=12,
                          spaceAfter=7, allowWidows=0, allowOrphans=0)
    heading = ParagraphStyle("Heading", parent=body, fontName="TNRBold", spaceBefore=4, spaceAfter=6, keepWithNext=True)
    title = ParagraphStyle("Title", parent=body, fontName="TNRBold", spaceAfter=6, keepWithNext=True)
    cell = ParagraphStyle("Cell", parent=body, spaceAfter=0)
    headcell = ParagraphStyle("Headcell", parent=cell, fontName="TNRBold")
    margin, width = 2.5 * cm, A4[0] - 5 * cm
    story = []
    for block in prose.strip().split("\n\n"):
        if block == "<!-- pagebreak -->":
            story.append(PageBreak())
        elif block == "{{RESULTS_TABLE}}":
            data = [[Paragraph(escape(v), headcell if i == 0 else cell) for v in row] for i, row in enumerate(rows)]
            table = Table(data, colWidths=[115, 110, 138, width-363], repeatRows=1, hAlign="LEFT")
            table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP"),
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#edf1f4")),
                ("LINEBELOW", (0,0), (-1,0), .7, colors.black),
                ("LINEBELOW", (0,1), (-1,-1), .3, colors.HexColor("#bcc8d0")),
                ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
                ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
            table.spaceAfter = 7
            story.append(table)
        elif block == "{{LATENCY_FIGURE}}":
            story.append(legacy.chart(cases, width))
        else:
            style = heading if block.startswith("## ") else title if block.startswith("# ") else body
            value = block[3:] if block.startswith("## ") else block[2:] if block.startswith("# ") else block
            story.append(Paragraph(escape(value).replace("\n", "<br/>"), style))
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(output), pagesize=A4, leftMargin=margin, rightMargin=margin,
                          topMargin=margin, bottomMargin=margin+20,
                          title="Automated Bootstrapping Placement for Encrypted Inference",
                          author="; ".join(m["confirmed_english_name"] for m in identity["members"]),
                          subject=f"Project milestone {VERSION}")
    frame = Frame(margin, margin+20, width, A4[1]-2*margin-20,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    def footer(canvas, document):
        canvas.setFont("TNR", 12)
        canvas.drawCentredString(A4[0]/2, margin+3, str(document.page))
    doc.addPageTemplates(PageTemplate(id="Milestone", frames=[frame], onPage=footer))
    doc.build(story)
    if doc.page != 4:
        raise ValueError(f"Expected four pages, got {doc.page}; revise content/layout, not typography")
    resolved_path.write_text(resolved, encoding="utf-8", newline="\n")
    info = {
        "artifact_version": VERSION, "record_kind": "newly generated content-review draft",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "predecessor": index["predecessor"], "evidence_cutoff": index["evidence_cutoff"],
        "method_scope": index["method_scope"], "path_root": "repository root",
        "source_path": source.relative_to(ROOT).as_posix(), "source_sha256": support.digest(source),
        "pdf_file": output.name, "pdf_sha256": support.digest(output),
        "resolved_source_sha256": support.digest(resolved_path),
        "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": support.digest(Path(__file__)),
        "source_index_path": source_index.relative_to(ROOT).as_posix(),
        "source_index_sha256": support.digest(source_index),
        "identity_path": (DIRECTORY/"identity.json").relative_to(ROOT).as_posix(),
        "identity_sha256": support.digest(DIRECTORY/"identity.json"),
        "generator_dependencies_sha256": index["generator_dependencies_sha256"],
        "source_run": run["run_id"], "source_run_sha256": support.digest(ROOT/"results/S3-OPT-001/run.json"),
        "numeric_source_commit": run["git"]["head_at_run"],
        "numeric_source_sha256": run["source_version"]["sha256"],
        "saved_result_hashes_checked": len(support.read_json(ROOT/"results/S3-OPT-001/artifacts.sha256.json")),
        "saved_case_records_checked": len(cases), "new_search_or_scoring": False,
        "historical_tests_rerun": False, "identity_complete": True, "formal_submission_ready": False,
        "submission_authorized": False, "submitted": False, "human_review": "pending",
        "document_runtime": {"python": platform.python_version(), "reportlab": reportlab.Version},
        "page_count": doc.page, "result_rows": rows, "resolved_fields": context,
        "chart_font_pt": 12, "figure_points": 30,
        "format": {"paper": "A4", "font": "Times New Roman", "font_pt": 12,
                   "margins_cm": [2.5]*4, "body_leading_pt": 12}
    }
    support.write_json(info_path, info)
    print(f"Created {VERSION}: {doc.page} pages; saved evidence only")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--font-dir", type=Path, default=Path("C:/Windows/Fonts"))
    args = parser.parse_args()
    build(args.output, args.font_dir)
