"""Small, read-only evidence helpers for the two W01 content-review reports.

These helpers read saved JSON and hashes. They never import the optimiser,
reference scorer or project tests, and never write into result directories.
"""

from decimal import Decimal
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    """Identify exact saved bytes."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    """Read one UTF-8 JSON document without importing project code."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_module(name, relative_path):
    """Load a preserved report helper; its command-line main is not executed."""
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def checked_s3(source_index):
    """Check pinned sources and saved S3 fields, without rerunning validation.

Byte identity preserves the applicability of historical checks; the saved
check flags are not a new independent proof of graph legality or optimality.
"""
    index = read_json(source_index)
    for name, expected in index["evidence_sha256"].items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or digest(path) != expected:
            raise ValueError(f"Source changed; review the report before rebuilding: {name}")
    run_dir = ROOT / "results/S3-OPT-001"
    manifest = read_json(run_dir / "artifacts.sha256.json")
    for name, expected in manifest.items():
        path = (run_dir / name).resolve()
        if not path.is_relative_to(run_dir) or digest(path) != expected:
            raise ValueError(f"Saved S3 artifact changed: {name}")
    run = read_json(run_dir / "run.json")
    if run["stage"] != "S3" or run["status"] != "passed":
        raise ValueError("This narrative requires the preserved passed S3 run")
    for field in ("cases_expected", "cases_completed", "cases_with_valid_solutions",
                  "cases_improved", "cases_optimal_for_formulation"):
        if run[field] != 30:
            raise ValueError(f"The narrative's 30-case statement changed: {field}")
    cases = [read_json(run_dir / name) for name in sorted(manifest) if name.startswith("cases/")]
    required = {(module, level) for module in ("mlp", "attention") for level in range(15)}
    if len(cases) != 30 or {(c["module"], c["l_init"]) for c in cases} != required:
        raise ValueError("Expected exactly both blocks and all 15 input levels")
    for case in cases:
        solution, audit = case["solution"], case["validated"]["audit"]
        if (case["outcome"] != "improved" or not case["comparison"]["improved"]
                or solution["status"] != "OPTIMAL"
                or solution["objective_scaled"] != solution["best_bound_scaled"]
                or not audit["structural_and_level_checks_passed"]
                or Decimal(audit["latency_decimal_ms"]) >= Decimal(case["baseline_decimal_ms"])):
            raise ValueError("A saved result no longer supports the report's stage claims")
    return run, cases, index


def provenance(version, source, output, generator, source_index, run, legacy_files):
    """Associate a new report with its own bytes and its historical evidence."""
    import reportlab
    return {
        "artifact_version": version,
        "purpose": "content-review draft",
        "evidence_cutoff": "S3-OPT-001 and method-choice analysis, 2026-09-29; no candidate experiment",
        "source_sha256": digest(source), "pdf_sha256": digest(output),
        "source_path": Path(source).resolve().relative_to(ROOT).as_posix(),
        "generator_path": Path(generator).resolve().relative_to(ROOT).as_posix(),
        "source_index_path": Path(source_index).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": digest(generator), "support_sha256": digest(Path(__file__)),
        "source_index_sha256": digest(source_index),
        "legacy_helper_sha256": {name: digest(ROOT / name) for name in legacy_files},
        "source_run": run["run_id"], "source_run_sha256": digest(ROOT / "results/S3-OPT-001/run.json"),
        "source_manifest_sha256": digest(ROOT / "results/S3-OPT-001/artifacts.sha256.json"),
        "numeric_source_commit": run["git"]["head_at_run"],
        "numeric_source_sha256": run["source_version"]["sha256"],
        "reportlab_version": reportlab.Version,
        "saved_result_hashes_checked": 36, "saved_case_records_checked": 30,
        "new_search_or_scoring": False, "historical_tests_rerun": False,
        "identity_complete": False, "formal_submission_ready": False,
        "submission_authorized": False, "submitted": False, "human_review": "pending",
        "format": {"paper": "A4", "font": "Times New Roman", "font_pt": 12,
                   "margins_cm": [2.5, 2.5, 2.5, 2.5], "body_leading_pt": 12}
    }


def write_json(path, value):
    """Write only a report-side metadata file selected by the caller."""
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
