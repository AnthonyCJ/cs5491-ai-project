"""Build the Proposal candidate using pinned saved evidence only.

Requires ReportLab 4.4.9 and licensed Times New Roman fonts. No optimizer,
scorer, project test or network operation is imported or executed.
"""

import argparse
from datetime import datetime, timezone
from decimal import Decimal
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
VERSION = "P-TERMS-ID-v1"
FORMAL = "results/T2-FORMAL-20261004-004"
ANALYSIS = "results/T3-ANALYSIS-20261005-001"


def saved_support():
    """Load the preserved document helper, which imports no project solver."""
    spec = importlib.util.spec_from_file_location("d1_saved_evidence", ROOT / "reports/w01_support.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checked_inputs():
    """Read pinned files and saved flags; this is not a new legality proof."""
    support = saved_support()
    source, source_index = DIRECTORY / "proposal.md", DIRECTORY / "sources.json"
    index = support.read_json(source_index)
    if index["artifact_version"] != VERSION or support.digest(source) != index["source_sha256"]:
        raise ValueError("Source/version differs from the pinned evidence index")
    if support.digest(DIRECTORY / "identity.json") != index["identity_sha256"]:
        raise ValueError("Approved identity input changed")
    for group in ("evidence_sha256", "predecessor_files_sha256", "generator_dependencies_sha256"):
        for name, expected in index[group].items():
            path = (ROOT / name).resolve()
            if not path.is_relative_to(ROOT) or support.digest(path) != expected:
                raise ValueError(f"Pinned input changed: {name}")
    artifact_counts = {}
    for package in (FORMAL, ANALYSIS):
        base = ROOT / package
        manifest = support.read_json(base / "artifacts.sha256.json")["files"]
        for name, expected in manifest.items():
            path = (base / name).resolve()
            if not path.is_relative_to(base) or support.digest(path) != expected:
                raise ValueError(f"Saved package file changed: {package}/{name}")
        artifact_counts[package] = len(manifest)
    summary = support.read_json(ROOT / FORMAL / "summary.json")
    rows = summary["numerical_results"]
    expected = {(module, level) for module in ("mlp", "attention") for level in range(15)}
    if len(rows) != 30 or {(r["module"], r["l_init"]) for r in rows} != expected:
        raise ValueError("Formal comparison does not cover all 30 conditions")
    for row in rows:
        if (row["l_max"] != 14 or row["state"] != "passed" or row["solver_status"] != "OPTIMAL"
                or Decimal(str(row["objective_scaled"])) != Decimal(str(row["best_bound_scaled"]))
                or Decimal(row["estimated_latency_ms"]) >= Decimal(row["baseline_estimated_latency_ms"])):
            raise ValueError(f"Saved formal result no longer supports the narrative: {row['case_id']}")
    protocol = support.read_json(ROOT / FORMAL / "protocol.json")
    if protocol["conditions"] != 30 or protocol["formal_repeats"] != 1:
        raise ValueError("Coverage or repeat count changed")
    analysis = support.read_json(ROOT / ANALYSIS / "analysis-summary.json")
    if analysis["selected"] != ["mlp-L13", "mlp-L14", "attention-L05", "attention-L06"]:
        raise ValueError("The four saved placement examples changed")
    identity = support.read_json(DIRECTORY / "identity.json")
    return support, source, source_index, index, summary, rows, identity, artifact_counts


def build(output, font_dir):
    """Create a fresh one-page PDF and its own provenance record."""
    support, source, source_index, index, summary, rows, identity, artifact_counts = checked_inputs()
    if reportlab.Version != "4.4.9":
        raise ValueError("Use the pinned ReportLab 4.4.9 document environment")
    output = output.resolve()
    if output != DIRECTORY / "proposal.pdf":
        relative = output.relative_to(ROOT / "results")
        if len(relative.parts) != 2 or not relative.parts[0].startswith("local-") or output.name != "proposal.pdf":
            raise ValueError("Use a fresh results/local-*/proposal.pdf output")
    info_path = output.parent / "build-info.json"
    if output.exists() or info_path.exists():
        raise FileExistsError("Preserve existing artifacts; choose a fresh output directory")
    loader = support.load_module("preserved_proposal_fonts", "reports/proposal/build_proposal.py")
    loader.register_fonts(font_dir)
    prose = source.read_text(encoding="utf-8")
    if not prose.isascii() or "CS5491 Artificial Intelligence Project Proposal" not in prose:
        raise ValueError("Expected the pinned English Proposal source")
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
        "artifact_version": VERSION, "record_kind": "newly generated terminology revision",
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
        "formal_experiment": "T2-FORMAL-20261004-004",
        "formal_summary_sha256": support.digest(ROOT / FORMAL / "summary.json"),
        "formal_protocol_sha256": support.digest(ROOT / FORMAL / "protocol.json"),
        "analysis_package": "T3-ANALYSIS-20261005-001",
        "analysis_manifest_sha256": support.digest(ROOT / ANALYSIS / "artifacts.sha256.json"),
        "saved_package_artifact_hashes_checked": artifact_counts,
        "saved_formal_rows_checked": len(rows),
        "historical_checks_scope": "Pinned saved bytes and recorded flags only; no new algorithm validation",
        "new_search_or_scoring": False, "historical_tests_rerun": False,
        "identity_complete": True, "formal_submission_ready": False,
        "latest_canvas_requirements_verified": False,
        "submission_authorized": False, "submitted": False, "human_review": "pending",
        "document_runtime": {"python": platform.python_version(), "reportlab": reportlab.Version},
        "page_count": doc.page,
        "format": {"paper": "A4", "font": "Times New Roman", "font_pt": 12,
                   "margins_cm": [2.5] * 4, "body_leading_pt": 12}
    }
    support.write_json(info_path, info)
    print(f"Created {VERSION}: {doc.page} page; pinned saved evidence only")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--font-dir", type=Path, default=Path("C:/Windows/Fonts"))
    args = parser.parse_args()
    build(args.output, args.font_dir)
