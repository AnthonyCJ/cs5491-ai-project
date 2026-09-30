# Public companion: regenerate into a fresh results/local-* directory.
# The approved PDF was imported unchanged; see import-info.json.
"""Build P-W01-ID-v1 from its English source and pinned saved S3 evidence.

Run from any directory with ReportLab 4.4.9 and licensed Times New Roman fonts.
This creates a new content-review draft; it never runs the optimiser or scorer.
"""

import argparse
import importlib.util
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph

ROOT = Path(__file__).resolve().parents[4]
VERSION = "P-W01-ID-v1"
spec = importlib.util.spec_from_file_location("w01_support", ROOT / "reports/identity_report_support.py")
support = importlib.util.module_from_spec(spec)
spec.loader.exec_module(support)


def build(source, output, font_dir):
    """Render one page and preserve source, evidence and generator provenance."""
    support.prepare_output(source, output)
    source_index = Path(__file__).with_name("sources.json")
    run, cases, index = support.checked_s3(source_index)
    loader = support.load_module("preserved_proposal_fonts", "reports/proposal/build_proposal.py")
    loader.register_fonts(font_dir)
    text = source.read_text(encoding="utf-8")
    if VERSION not in text or "## Abstract" in text or "## References" in text:
        raise ValueError("Check the proposal version and no-abstract/no-reference-list rule")
    body = ParagraphStyle("Body", fontName="TNR", fontSize=12, leading=12,
                          alignment=TA_LEFT, spaceAfter=7, allowWidows=0, allowOrphans=0)
    heading = ParagraphStyle("Heading", parent=body, fontName="TNRBold", spaceBefore=4,
                             spaceAfter=5, keepWithNext=True)
    title = ParagraphStyle("Title", parent=body, fontName="TNRBold", spaceAfter=5, keepWithNext=True)
    authors = ParagraphStyle("Authors", parent=body, keepWithNext=True)
    story = []
    for block in text.strip().split("\n\n"):
        if block.startswith("## "):
            value, style = block[3:], heading
        elif block.startswith("# "):
            value, style = block[2:], title
        else:
            value, style = block, authors if block.startswith("Member 1:") else body
        story.append(Paragraph(escape(value).replace("\n", "<br/>"), style))
    output.parent.mkdir(parents=True, exist_ok=True)
    margin = 2.5 * cm
    doc = BaseDocTemplate(str(output), pagesize=A4, leftMargin=margin, rightMargin=margin,
                          topMargin=margin, bottomMargin=margin,
                          title="Automated Bootstrapping Placement for Encrypted Inference",
                          author=support.author_line(source.parent),
                          subject=f"Project proposal {VERSION}; content-review draft; restricted user-supplied identities")
    frame = Frame(margin, margin, A4[0] - 2 * margin, A4[1] - 2 * margin,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="Proposal", frames=[frame]))
    doc.build(story)
    if doc.page != 1:
        raise ValueError(f"Expected one page, got {doc.page}; edit prose, not the required font size")
    info = support.provenance(VERSION, source, output, Path(__file__), source_index, run,
                              ["reports/proposal/build_proposal.py"])
    info.update(page_count=doc.page, source_file=source.name, pdf_file=output.name,
                predecessor="P-W01-v1", candidate_status="direction only; no design, implementation or inclusion decision")
    support.write_json(output.parent / "build-info.json", info)
    print(f"Created {output.name}: {doc.page} page; saved S3 evidence only")


if __name__ == "__main__":
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=directory / "proposal.md")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--font-dir", type=Path, default=Path("C:/Windows/Fonts"))
    args = parser.parse_args()
    build(args.source, args.output, args.font_dir)
