"""Check a W01 report's saved source, PDF geometry, fonts and provenance.

Requires pdfplumber and pypdf. This is a report check, not an experiment or a
rerun of project tests. Page rendering and visual review are separate steps.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def normalise(text):
    return re.sub(r"\s+", "", text)


def check(directory):
    """Fail on a missing prose block, stale derivation, wrong font or overflow."""
    info = json.loads((directory / "build-info.json").read_text(encoding="utf-8"))
    source = ROOT / info["source_path"]
    pdf = directory / info["pdf_file"]
    kind = "proposal" if info["artifact_version"].startswith("P-") else "milestone"
    generator = ROOT / info["generator_path"]
    source_index = ROOT / info["source_index_path"]
    checks = {"source": digest(source) == info["source_sha256"],
              "pdf": digest(pdf) == info["pdf_sha256"],
              "generator": digest(generator) == info["generator_sha256"],
              "support": digest(ROOT / "reports/w01_support.py") == info["support_sha256"],
              "source_index": digest(source_index) == info["source_index_sha256"]}
    for name, expected in info["legacy_helper_sha256"].items():
        checks[name] = digest(ROOT / name) == expected
    sources = json.loads(source_index.read_text(encoding="utf-8"))
    for name, expected in sources["evidence_sha256"].items():
        checks[name] = digest(ROOT / name) == expected
    if not all(checks.values()):
        raise ValueError(f"Stale report provenance: {[n for n, ok in checks.items() if not ok]}")
    text_source = source if kind == "proposal" else directory / "resolved-source.md"
    if kind == "milestone" and digest(text_source) != info["resolved_source_sha256"]:
        raise ValueError("Resolved source changed")
    prose = text_source.read_text(encoding="utf-8")
    if "{{" in prose:
        raise ValueError("Unresolved source placeholder")
    margin = 72 * 2.5 / 2.54
    expected_size = (72 * 210 / 25.4, 72 * 297 / 25.4)
    page_checks, fonts, sizes, pitches, extracted = [], set(), set(), Counter(), []
    with pdfplumber.open(pdf) as document:
        expected_pages = 1 if kind == "proposal" else 4
        if len(document.pages) != expected_pages:
            raise ValueError("Unexpected page count")
        for number, page in enumerate(document.pages, 1):
            if any(abs(a - b) > 0.02 for a, b in zip((page.width, page.height), expected_size)):
                raise ValueError("Page is not A4")
            chars = [c for c in page.chars if c.get("text", "").strip()]
            for char in chars:
                fonts.add(char["fontname"])
                sizes.add(round(char["size"], 4))
                if "TimesNewRoman" not in char["fontname"] or abs(char["size"] - 12) > 0.001:
                    raise ValueError("Actual text does not use Times New Roman 12 pt")
                if (char["x0"] < margin - .1 or char["x1"] > page.width - margin + .1
                        or char["top"] < margin - .1 or char["bottom"] > page.height - margin + .1):
                    raise ValueError(f"Text outside 2.5 cm margins on page {number}")
            tops = sorted(set(round(c["top"], 2) for c in chars))
            pitches.update(round(b-a, 2) for a,b in zip(tops,tops[1:]) if b-a >= 1)
            page_checks.append({"page": number, "size_points": [page.width, page.height],
                                "text_bbox_points": [min(c["x0"] for c in chars),min(c["top"] for c in chars),
                                                     max(c["x1"] for c in chars),max(c["bottom"] for c in chars)]})
            extracted.append(page.extract_text(x_tolerance=2, y_tolerance=2) or "")
    full_text = normalise("\n".join(extracted))
    missing = []
    for block in prose.strip().split("\n\n"):
        if block == "<!-- pagebreak -->" or block.startswith("[Vector chart:"):
            continue
        if kind == "milestone" and block.startswith("Block, inputs |"):
            for row in block.splitlines():
                for cell in row.split(" | "):
                    if normalise(cell) not in full_text:
                        missing.append(cell)
            continue
        block = re.sub(r"^#{1,2} ", "", block)
        if normalise(block) not in full_text:
            missing.append(block[:120])
    if missing:
        raise ValueError(f"Source text missing from rendered PDF: {missing}")
    reader = PdfReader(pdf)
    embedded = {}
    for page in reader.pages:
        for resource in page["/Resources"]["/Font"].get_object().values():
            font = resource.get_object()
            name = str(font.get("/BaseFont", "")).lstrip("/")
            if name not in fonts:
                continue
            descriptor = font.get("/FontDescriptor")
            embedded[name] = bool(descriptor and any(k in descriptor.get_object() for k in ("/FontFile", "/FontFile2", "/FontFile3")))
    if set(embedded) != fonts or not all(embedded.values()):
        raise ValueError("A used Times New Roman font is not embedded")
    if info["artifact_version"] not in str(reader.metadata.get("/Subject", "")):
        raise ValueError("PDF subject has a stale version")
    if kind == "proposal" and re.search(r"(?im)^##?\s+(abstract|references)\b", prose):
        raise ValueError("Proposal must have no abstract/reference list")
    output = directory / "format-check.json"
    previous = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    visual = previous.get("visual_review", {"passed": False, "status": "awaiting full-page visual inspection"})
    if previous.get("pdf_sha256") != digest(pdf):
        visual = {"passed": False, "status": "awaiting full-page visual inspection"}
    receipt = {"artifact_version": info["artifact_version"], "checked_at_utc": datetime.now(timezone.utc).isoformat(),
               "checker_sha256": digest(Path(__file__)), "source_sha256": digest(source),
               "pdf_sha256": digest(pdf), "generator_sha256": digest(generator),
               "build_info_sha256": digest(directory / "build-info.json"),
               "page_count": len(page_checks), "page_size": "A4", "font_sizes_points": sorted(sizes),
               "used_fonts_embedded": embedded, "configured_margins_cm": [2.5]*4,
               "all_text_inside_margins": True, "configured_body_leading_points": 12,
               "observed_line_top_differences_points": dict(sorted(pitches.items())),
               "page_checks": page_checks, "all_source_prose_found": True,
               "provenance_checks": checks, "automated_checks_passed": True, "visual_review": visual,
               "formal_identity_complete": False, "formal_submission_ready": False,
               "submission_authorized": False, "submitted": False, "human_review": "pending",
               "limits": "Document checks only; saved stage evidence is not a new experiment, S6 reproduction or human acceptance."}
    output.write_text(json.dumps(receipt, indent=2)+"\n",encoding="utf-8",newline="\n")
    print(f"Checked {info['artifact_version']}: {len(page_checks)} pages; source, fonts, geometry and provenance pass")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    check(parser.parse_args().directory.resolve())
