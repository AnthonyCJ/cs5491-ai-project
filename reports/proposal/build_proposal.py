"""Build the course proposal from Markdown using ReportLab and Times New Roman.

Fonts come from the operating system or --font-dir and are not redistributed.
This renderer supports the headings, paragraphs and author lines in proposal.md.
"""

import argparse
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph


def register_fonts(directory):
    """Require the actual Times New Roman family rather than substituting Times."""
    names = {"TNR": "times.ttf", "TNRBold": "timesbd.ttf", "TNRItalic": "timesi.ttf", "TNRBoldItalic": "timesbi.ttf"}
    for family, filename in names.items():
        path = directory / filename
        if not path.is_file():
            raise FileNotFoundError(f"Times New Roman font {filename} is required; pass its directory with --font-dir")
        pdfmetrics.registerFont(TTFont(family, str(path)))
    pdfmetrics.registerFontFamily("TNR", normal="TNR", bold="TNRBold", italic="TNRItalic", boldItalic="TNRBoldItalic")


def build(source, output, font_dir):
    """Use A4, 12 pt Times New Roman, 2.5 cm margins and single line spacing."""
    register_fonts(font_dir)
    body = ParagraphStyle("Body", fontName="TNR", fontSize=12, leading=12,
                          alignment=TA_LEFT, spaceAfter=7, textColor=colors.black,
                          allowWidows=0, allowOrphans=0)
    heading = ParagraphStyle("Heading", parent=body, fontName="TNRBold", spaceBefore=4, spaceAfter=5, keepWithNext=True)
    title = ParagraphStyle("Title", parent=body, fontName="TNRBold", spaceAfter=5, keepWithNext=True)
    authors = ParagraphStyle("Authors", parent=body, spaceAfter=7, keepWithNext=True)
    story = []
    for block in source.read_text(encoding="utf-8").strip().split("\n\n"):
        if block.startswith("## "):
            text, style = block[3:], heading
        elif block.startswith("# "):
            text, style = block[2:], title
        else:
            text, style = block, authors if block.startswith("Member 1:") else body
        story.append(Paragraph(escape(text).replace("\n", "<br/>"), style))
    margin = 2.5 * cm
    doc = BaseDocTemplate(str(output), pagesize=A4, leftMargin=margin, rightMargin=margin,
                          topMargin=margin, bottomMargin=margin, allowSplitting=1,
                          title="Automated Bootstrapping Placement for Encrypted Inference",
                          author="CS5491 Project Team", subject="Project proposal P-S2-v1 with public identity placeholders")
    frame = Frame(margin, margin, A4[0] - 2 * margin, A4[1] - 2 * margin,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="Proposal", frames=[frame]))
    doc.build(story)


if __name__ == "__main__":
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=directory / "proposal.md")
    parser.add_argument("--output", type=Path, default=directory / "proposal.pdf")
    parser.add_argument("--font-dir", type=Path, default=Path("C:/Windows/Fonts"))
    args = parser.parse_args()
    build(args.source, args.output, args.font_dir)
    print(f"Created {args.output.name}")
