"""Check this proposal's content, saved evidence, provenance and PDF layout.

Requires the pinned document verification packages. This reads saved experiment
files only. Rendering and actual visual inspection remain separate checks.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
import importlib.util
from pathlib import Path
import re

import pdfplumber
from pypdf import PdfReader

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[3]


def normalise(text):
    """Ignore wrapping and spacing while comparing complete source paragraphs."""
    return re.sub(r"\s+", "", text)


def check(directory):
    """Write document checks for the specified original or regeneration."""
    spec = importlib.util.spec_from_file_location("mainline_builder", DIRECTORY / "build_proposal.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    support, source, source_index, index, summary, rows, identity, artifact_counts = builder.checked_inputs()
    info_path = directory / "build-info.json"
    info = support.read_json(info_path)
    pdf = directory / info["pdf_file"]
    expected_hashes = {
        "source": (source, "source_sha256"),
        "pdf": (pdf, "pdf_sha256"),
        "generator": (DIRECTORY / "build_proposal.py", "generator_sha256"),
        "source_index": (source_index, "source_index_sha256"),
        "identity": (DIRECTORY / "identity.json", "identity_sha256"),
        "formal_summary": (ROOT / builder.FORMAL / "summary.json", "formal_summary_sha256"),
        "formal_protocol": (ROOT / builder.FORMAL / "protocol.json", "formal_protocol_sha256"),
        "analysis_manifest": (ROOT / builder.ANALYSIS / "artifacts.sha256.json", "analysis_manifest_sha256")
    }
    checks = {name: support.digest(path) == info[key] for name, (path, key) in expected_hashes.items()}
    checks.update(
        version=info["artifact_version"] == builder.VERSION,
        new_document=info["record_kind"] == "newly generated terminology revision",
        source_path=info["source_path"] == source.relative_to(ROOT).as_posix(),
        formal_experiment=info["formal_experiment"] == "T2-FORMAL-20261004-004",
        saved_packages=info["saved_package_artifact_hashes_checked"] == artifact_counts,
        scope=info["method_scope"] == index["method_scope"],
        saved_rows=len(rows) == info["saved_formal_rows_checked"] == 30,
        dependency_hashes=info["generator_dependencies_sha256"] == index["generator_dependencies_sha256"]
    )
    if not all(checks.values()):
        raise ValueError(f"Provenance mismatch: {[k for k, v in checks.items() if not v]}")
    if any(info[k] for k in ("new_search_or_scoring", "historical_tests_rerun",
                            "formal_submission_ready", "submission_authorized", "submitted")):
        raise ValueError("Unexpected execution or submission state")
    if not info["identity_complete"] or info["human_review"] != "pending":
        raise ValueError("This candidate must retain complete identities and pending human review")
    prose = source.read_text(encoding="utf-8")
    if not prose.isascii() or re.search(r"\[(ID|Email|Confirmed English name)\]|\{\{", prose):
        raise ValueError("English source has unresolved placeholders")
    if re.search(r"(?im)^##?\s+(abstract|references)\b", prose):
        raise ValueError("Proposal must have no abstract/reference list")
    if re.search(r"\b(local[- ]search|constructive|candidate)\b", prose, re.I):
        raise ValueError("Proposal contains text outside its declared method scope")
    if re.search(r"\b[ST][1-7](?:-[A-Z0-9-]+)?\b|P-(?:MAINLINE|D1|TERMS)-ID", prose):
        raise ValueError("Internal stage/run/version labels belong in companions")
    identity_lines = [
        f"Member {i}: {m['confirmed_english_name']} | Student ID: {m['student_id']}"
        for i, m in enumerate(identity["members"], 1)
    ] + ["Contact email: " + identity["contact_email"]]
    if len(identity["members"]) != 3 or not all(line in prose for line in identity_lines):
        raise ValueError("Source identity pairings do not match")
    ranges = {}
    for module in ("mlp", "attention"):
        reductions = [Decimal(row["reduction_percent"]) for row in rows if row["module"] == module]
        if len(reductions) != 15:
            raise ValueError("Incomplete saved module coverage")
        ranges[module] = f"{min(reductions):.2f}-{max(reductions):.2f}%"
        if ranges[module] not in prose:
            raise ValueError("Displayed reduction range differs from the saved formal comparison")
    margin = 72 * 2.5 / 2.54
    a4 = (72 * 210 / 25.4, 72 * 297 / 25.4)
    fonts, sizes, pitches, extracted, page_checks = set(), set(), Counter(), [], []
    with pdfplumber.open(pdf) as document:
        if len(document.pages) != 1:
            raise ValueError("Proposal is not one page")
        for number, page in enumerate(document.pages, 1):
            if any(abs(a - b) > .02 for a, b in zip((page.width, page.height), a4)):
                raise ValueError("PDF is not A4")
            chars = [c for c in page.chars if c.get("text", "").strip()]
            if not chars:
                raise ValueError("Empty page")
            for char in chars:
                fonts.add(char["fontname"])
                sizes.add(round(char["size"], 4))
                if "TimesNewRoman" not in char["fontname"] or abs(char["size"] - 12) > .001:
                    raise ValueError("Actual text is not Times New Roman 12 pt")
                if (char["x0"] < margin - .1 or char["x1"] > page.width - margin + .1
                        or char["top"] < margin - .1 or char["bottom"] > page.height - margin + .1):
                    raise ValueError("Text exceeds 2.5 cm margins")
            tops = sorted(set(round(c["top"], 2) for c in chars))
            pitches.update(round(b-a, 2) for a, b in zip(tops, tops[1:]) if b-a >= 1)
            page_checks.append({"page": number, "size_points": [page.width, page.height],
                                "text_bbox_points": [min(c["x0"] for c in chars), min(c["top"] for c in chars),
                                                     max(c["x1"] for c in chars), max(c["bottom"] for c in chars)]})
            extracted.append(page.extract_text(x_tolerance=2, y_tolerance=2) or "")
    text = normalise("\n".join(extracted))
    blocks = [re.sub(r"^#{1,2} ", "", block) for block in prose.strip().split("\n\n")]
    if not all(normalise(block) in text for block in blocks + identity_lines):
        raise ValueError("Source paragraph or identity pairing is missing from PDF")
    reader = PdfReader(pdf)
    embedded = {}
    for page in reader.pages:
        for resource in page["/Resources"]["/Font"].get_object().values():
            font = resource.get_object()
            name = str(font.get("/BaseFont", "")).lstrip("/")
            if name in fonts:
                descriptor = font.get("/FontDescriptor")
                embedded[name] = bool(descriptor and any(key in descriptor.get_object()
                                      for key in ("/FontFile", "/FontFile2", "/FontFile3")))
    if set(embedded) != fonts or not all(embedded.values()):
        raise ValueError("Used fonts must be embedded")
    if builder.VERSION not in str(reader.metadata.get("/Subject", "")):
        raise ValueError("PDF metadata has a stale version")
    if reader.attachments:
        raise ValueError("The submission PDF must not contain embedded attachments")
    if re.search(r"private-work|private-submission|[CD]:[/\\]", str(reader.metadata), re.I):
        raise ValueError("Private paths must not appear in PDF metadata")
    expected_author = "; ".join(m["confirmed_english_name"] for m in identity["members"])
    if reader.metadata.get("/Author") != expected_author:
        raise ValueError("PDF author differs from the approved identity input")
    expected_format = {"paper": "A4", "font": "Times New Roman", "font_pt": 12,
                       "margins_cm": [2.5] * 4, "body_leading_pt": 12}
    if info["format"] != expected_format or 12.0 not in pitches:
        raise ValueError("Single spacing or configured format changed")
    output = directory / "format-check.json"
    old = support.read_json(output) if output.exists() else {}
    visual = old.get("visual_review") if old.get("pdf_sha256") == support.digest(pdf) else None
    receipt = {
        "artifact_version": builder.VERSION, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "checker_sha256": support.digest(Path(__file__)), "source_sha256": support.digest(source),
        "pdf_sha256": support.digest(pdf), "build_info_sha256": support.digest(info_path),
        "page_count": 1, "page_size": "A4", "font_sizes_points": sorted(sizes),
        "used_fonts_embedded": embedded, "configured_margins_cm": [2.5] * 4,
        "all_text_inside_margins": True, "configured_body_leading_points": 12,
        "observed_line_top_differences_points": dict(sorted(pitches.items())),
        "page_checks": page_checks, "all_source_prose_found": True,
        "all_identity_lines_and_pairings_found": True, "formal_identity_complete": True,
        "provenance_checks": checks, "displayed_reduction_ranges": ranges,
        "automated_checks_passed": True, "no_embedded_attachments": True,
        "metadata_has_no_private_paths": True,
        "visual_review": visual or {"passed": False, "status": "awaiting full-page inspection"},
        "formal_submission_ready": False, "latest_canvas_requirements_verified": False,
        "submission_authorized": False, "submitted": False,
        "human_review": "pending",
        "limits": "Document and saved-file checks; no new optimisation, scoring, S6 reproduction or human acceptance."
    }
    support.write_json(output, receipt)
    print(f"Checked {builder.VERSION}: one page; content, identities, evidence, fonts and geometry pass")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=DIRECTORY)
    args = parser.parse_args()
    check(args.directory.resolve())
