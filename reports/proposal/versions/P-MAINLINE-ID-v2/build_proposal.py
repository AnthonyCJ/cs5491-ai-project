"""Build the CP-SAT proposal from pinned saved evidence, without project runs.

Use ReportLab 4.4.9 and licensed Times New Roman fonts. Existing PDFs and
build records are never overwritten. Regeneration uses results/local-*.
"""

import argparse
from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import platform
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[3]
VERSION = "P-MAINLINE-ID-v2"


def saved_support():
    """Load only the preserved report reader; it imports no project solver."""
    spec = importlib.util.spec_from_file_location("proposal_saved_evidence", ROOT / "reports/w01_support.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checked_inputs():
    """Verify source, identities, historical evidence and preserved helpers."""
    support = saved_support()
    source, source_index = DIRECTORY / "proposal.md", DIRECTORY / "sources.json"
    index = support.read_json(source_index)
    if index["artifact_version"] != VERSION or support.digest(source) != index["source_sha256"]:
        raise ValueError("Source/version differs from its pinned evidence index")
    if support.digest(DIRECTORY / "identity.json") != index["identity_sha256"]:
        raise ValueError("Identity input changed")
    for group in ("predecessor_files_sha256", "generator_dependencies_sha256"):
        for name, expected in index[group].items():
            if support.digest(ROOT / name) != expected:
                raise ValueError(f"Preserved input changed: {name}")
    run, cases, _ = support.checked_s3(source_index)
    identity = support.read_json(DIRECTORY / "identity.json")
    return support, source, source_index, index, run, cases, identity


def build(output, font_dir):
    """Create a one-page report and its own generation provenance."""
    support, source, source_index, index, run, cases, identity = checked_inputs()
    output = output.resolve()
    if output != DIRECTORY / "proposal.pdf":
        relative = output.relative_to(ROOT / "results")
        if len(relative.parts) != 2 or not relative.parts[0].startswith("local-"):
            raise ValueError("Use a fresh results/local-*/proposal.pdf output")
    info_path = output.parent / "build-info.json"
    if output.exists() or info_path.exists():
        raise FileExistsError("Preserve existing artifacts; select a fresh output directory")
    loader = support.load_module("preserved_proposal_fonts", "reports/proposal/build_proposal.py")
    loader.register_fonts(font_dir)
    prose = source.read_text(encoding="utf-8")
    if "CS5491 Artificial Intelligence Project Proposal" not in prose or not prose.isascii():
        raise ValueError("Expected the current English source")
    body = ParagraphStyle("Body", fontName="TNR", fontSize=12, leading=12,
                          alignment=TA_LEFT, spaceAfter=7, allowWidows=0, allowOrphans=0)
    heading = ParagraphStyle("Heading", parent=body, fontName="TNRBold",
                             spaceBefore=4, spaceAfter=5, keepWithNext=True)
    title = ParagraphStyle("Title", parent=body, fontName="TNRBold", spaceAfter=5, keepWithNext=True)
    authors = ParagraphStyle("Authors", parent=body, keepWithNext=True)
    story = []
    for block in prose.strip().split("\n\n"):
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
                          author="; ".join(m["confirmed_english_name"] for m in identity["members"]),
                          subject=f"Project proposal {VERSION}")
    frame = Frame(margin, margin, A4[0] - 2 * margin, A4[1] - 2 * margin,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="Proposal", frames=[frame]))
    doc.build(story)
    if doc.page != 1:
        raise ValueError(f"Expected one page, got {doc.page}; revise prose, not required typography")
    info = {
        "artifact_version": VERSION, "record_kind": "newly generated content-review draft",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "predecessor": index["predecessor"], "evidence_cutoff": index["evidence_cutoff"],
        "method_scope": index["method_scope"], "path_root": "repository root",
        "source_path": source.relative_to(ROOT).as_posix(), "source_sha256": support.digest(source),
        "pdf_file": output.name, "pdf_sha256": support.digest(output),
        "generator_path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": support.digest(Path(__file__)),
        "source_index_path": source_index.relative_to(ROOT).as_posix(),
        "source_index_sha256": support.digest(source_index),
        "identity_path": (DIRECTORY / "identity.json").relative_to(ROOT).as_posix(),
        "identity_sha256": support.digest(DIRECTORY / "identity.json"),
        "generator_dependencies_sha256": index["generator_dependencies_sha256"],
        "source_run": run["run_id"], "source_run_sha256": support.digest(ROOT / "results/S3-OPT-001/run.json"),
        "numeric_source_commit": run["git"]["head_at_run"],
        "numeric_source_sha256": run["source_version"]["sha256"],
        "saved_result_hashes_checked": len(support.read_json(ROOT / "results/S3-OPT-001/artifacts.sha256.json")),
        "saved_case_records_checked": len(cases),
        "new_search_or_scoring": False, "historical_tests_rerun": False,
        "identity_complete": True, "formal_submission_ready": False,
        "submission_authorized": False, "submitted": False, "human_review": "pending",
        "document_runtime": {"python": platform.python_version(), "reportlab": reportlab.Version},
        "page_count": doc.page,
        "format": {"paper": "A4", "font": "Times New Roman", "font_pt": 12,
                   "margins_cm": [2.5] * 4, "body_leading_pt": 12}
    }
    support.write_json(info_path, info)
    print(f"Created {VERSION}: {doc.page} page; saved evidence only")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--font-dir", type=Path, default=Path("C:/Windows/Fonts"))
    args = parser.parse_args()
    build(args.output, args.font_dir)
