"""Repository-local companions for the approved W01 identity reports.

Approved source/PDF bytes are imports, not outputs of this adapted generator.
Regeneration uses a fresh results/local-* directory and has its own provenance.
Only saved evidence and preserved report helpers are read; no optimiser runs.
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("saved_w01_evidence", ROOT / "reports/w01_support.py")
public = importlib.util.module_from_spec(spec)
spec.loader.exec_module(public)
digest, read_json = public.digest, public.read_json
checked_s3, load_module, write_json = public.checked_s3, public.load_module, public.write_json


def author_line(directory):
    identity = read_json(Path(directory) / "identity.json")
    return "; ".join(member["confirmed_english_name"] for member in identity["members"])


def prepare_output(source, output):
    """Protect the approved files and every prior regenerated output."""
    source, output = Path(source).resolve(), Path(output).resolve()
    record = read_json(source.parent / "import-info.json")
    if source != ROOT / record["source_path"] or digest(source) != record["source_sha256"]:
        raise ValueError("Use the approved source; substantive edits require a new report version")
    relative = output.relative_to(ROOT / "results")
    if not relative.parts[0].startswith("local-") or len(relative.parts) < 2:
        raise ValueError("Regenerate into a fresh results/local-* directory")
    if output.parent.exists():
        raise ValueError("Output directory already exists; preserve it and choose a new one")


def provenance(version, source, output, generator, source_index, run, legacy_files):
    """Identify this newly generated verification copy, never the imported PDF."""
    import reportlab
    index = read_json(source_index)
    identity_path = Path(source).parent / "identity.json"
    identity = read_json(identity_path)
    for name, expected in index["base_artifact_sha256"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"Preserved anonymous report changed: {name}")
    if len(identity["members"]) != 3 or not identity["contact_email"]:
        raise ValueError("Missing approved report identities")
    return {
        "artifact_version": version,
        "record_kind": "regenerated verification copy",
        "packaging_version": "PUBLIC-PACKAGING-v1",
        "purpose": "Reproduce approved content using repository-local companions",
        "base_artifact_version": index["base_artifact_version"],
        "evidence_cutoff": index["evidence_cutoff"],
        "path_root": "repository root",
        "source_path": Path(source).resolve().relative_to(ROOT).as_posix(),
        "source_sha256": digest(source), "pdf_sha256": digest(output),
        "generator_path": Path(generator).resolve().relative_to(ROOT).as_posix(),
        "generator_sha256": digest(generator),
        "support_sha256": digest(Path(__file__)),
        "public_support_sha256": digest(ROOT / "reports/w01_support.py"),
        "source_index_path": Path(source_index).resolve().relative_to(ROOT).as_posix(),
        "source_index_sha256": digest(source_index),
        "identity_path": identity_path.resolve().relative_to(ROOT).as_posix(),
        "identity_sha256": digest(identity_path),
        "legacy_helper_sha256": {name: digest(ROOT / name) for name in legacy_files},
        "source_run": run["run_id"],
        "source_run_sha256": digest(ROOT / "results/S3-OPT-001/run.json"),
        "source_manifest_sha256": digest(ROOT / "results/S3-OPT-001/artifacts.sha256.json"),
        "numeric_source_commit": run["git"]["head_at_run"],
        "numeric_source_sha256": run["source_version"]["sha256"],
        "reportlab_version": reportlab.Version,
        "saved_result_hashes_checked": 36, "saved_case_records_checked": 30,
        "new_search_or_scoring": False, "historical_tests_rerun": False,
        "identity_complete": True, "formal_submission_ready": False,
        "submission_authorized": False, "submitted": False,
        "human_review": "Approved source content; this verification PDF is not separately human-reviewed",
        "format": {"paper": "A4", "font": "Times New Roman", "font_pt": 12,
                   "margins_cm": [2.5]*4, "body_leading_pt": 12}
    }
