"""Reproducible calibration with immutable run directories and checksum evidence."""

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import importlib.metadata
import json
import platform
from pathlib import Path
import subprocess
import time

from . import __version__
from .audit import audit_baseline, require
from .reference import load_reference, REFERENCE_SHA256, ROOT

CONFIG = ROOT / "configs" / "s1-baselines.json"


def digest(path):
    """Return a SHA-256 digest of the file bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    """Write portable UTF-8 JSON with stable formatting."""
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def source_version():
    """Identify executable sources, checks, configuration and dependency pins."""
    files = [ROOT / "run_baselines.py", ROOT / "requirements.txt", CONFIG, ROOT / "vendor" / "dag_builder.py"]
    files += sorted((ROOT / "src").rglob("*.py")) + sorted((ROOT / "tests").glob("*.py"))
    hashes = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    fingerprint = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    return {"package_version": __version__, "sha256": fingerprint, "files": hashes}


def display_ms(value):
    """Use explicit decimal rounding at the precision shown in the handout."""
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def calibration_checks(block, level, audit, reference, reference_depth, reference_budget, tolerance):
    """Compare independent rules, reference metrics and published PDF anchors."""
    exact = Decimal(audit["latency_decimal_ms"])
    error = abs(Decimal(str(reference["latency"])) - exact)
    require(error <= Decimal(str(tolerance)), "Reference/decimal latency mismatch")
    require(display_ms(exact) == display_ms(reference["latency"]), "Rounded reference mismatch")
    require(reference["l_in"] == audit["l_in"] and reference["l_out"] == audit["l_out"], "Node level mismatch")
    independent_edges = {(e["from"], e["to"]): e["level"] for e in audit["edge_levels"]}
    require(reference["edge_lvl"] == independent_edges, "Edge level mismatch")
    require(reference_depth == audit["depth"], "Reference depth mismatch")
    require(tuple(reference_budget) == (audit["n_b1"], audit["n_b2"], audit["budget"]), "Reference budget mismatch")
    expected = (5, 4, 26, 122 + level) if block == "mlp" else (9, 8, 62, 230 + level)
    require((audit["n_b1"], audit["n_b2"], audit["depth"], audit["budget"]) == expected, "PDF count/depth/budget mismatch")
    target = {0: "28129.69", 6: "28130.65", 14: "28131.93"}.get(level) if block == "mlp" else "53558.17"
    if target is not None:
        require(display_ms(exact) == target, "Published PDF latency mismatch")
    if block == "mlp":
        require(Decimal("28129.69") <= Decimal(display_ms(exact)) <= Decimal("28131.93"), "Outside PDF MLP latency range")
    return {"reference_decimal_absolute_error_ms": float(error), "pdf_latency_anchor_ms": target,
            "pdf_latency_check": "matched" if target else "within published range; no individual PDF row",
            "reference_agrees_with_independent_check": True, "pdf_counts_depth_budget_match": True}


def render_report(rows, metadata):
    """Build an English report from the actual case records."""
    lines = ["# S1 teacher-baseline calibration", "", f"Run: `{metadata['run_id']}`. Experiment: `S1-BL-001`.", "",
             f"Source fingerprint: `{metadata['source_version']['sha256']}`.", "",
             "These are executed scores of the fixed teacher placements, not optimisation results.",
             "Latency is the fitted estimate of encrypted inference; it is not measured inference time.",
             "All 30 cases passed independent structure/level/cost checks and reference calibration.", "",
             "| Module | Input level | Estimated latency (ms) | B1 | B2 | Depth | Budget | Utilisation |",
             "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        lines.append(f"| {r['module']} | {r['l_init']} | {r['latency_display_ms']} | {r['n_b1']} | {r['n_b2']} | {r['depth']} | {r['budget']} | {r['utilisation']:.6f} |")
    lines += ["", "B1 counts ciphertexts; B2 counts ciphertext pairs. A shared inserted node is charged once.",
              "The budget is 14 * B1 + 13 * B2 + input level. Inserted operations contribute zero to depth.", "",
              "## Evidence", "", "- `summary.csv`: all scalar scores and reference-evaluation wall times.",
              "- `cases/`: every placed DAG, inserted chain, node/edge level and exact-decimal node cost.",
              "- `calibration.json`: all comparisons against the independent check and published PDF anchors.",
              "- `run.json`: configuration, source hashes, package versions and resource measurement scope.",
              "- `artifacts.sha256.json`: hashes of all result files except the manifest itself.", "",
              "## Limits", "", "One local CPU run; no optimisation search, GPU work or real FHE evaluation occurred.",
              "The MLP PDF gives a range and the level-6 anchor, not 15 individually printed scores.",
              "Cross-device reproduction and a separate clean environment are not validated by this run.",
              "Resource measurements describe baseline evaluation, not the future optimiser.", ""]
    return "\n".join(lines)


def run(output):
    """Execute exactly 30 fixed placements and retain all raw and audit evidence."""
    import psutil

    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    require(config["modules"] == ["mlp", "attention"] and config["l_init"] == list(range(15)), "S1 requires exactly both blocks and all 15 levels")
    require(config["l_max"] == 14 and config["placement_search_performed"] is False, "Unsupported S1 configuration")
    require(not output.exists(), "Output already exists; select a new run directory")
    version = source_version()
    start = time.perf_counter()
    cpu_start = time.process_time()
    created = datetime.now(timezone.utc).isoformat()
    process = psutil.Process()
    rss_samples = [process.memory_info().rss]
    db = load_reference()
    import_seconds = time.perf_counter() - start
    rss_samples.append(process.memory_info().rss)
    output.mkdir(parents=True)
    (output / "cases").mkdir()
    rows, checks = [], []
    builders = {
        "mlp": (db.get_mlp_empty, db.get_mlp_baseline_inserted),
        "attention": (db.get_attn_empty, db.get_attn_baseline_inserted),
    }
    for block in config["modules"]:
        empty_nodes, empty_edges = builders[block][0]()
        nodes, edges = builders[block][1]()
        for level in config["l_init"]:
            case_id = f"{block}-L{level:02d}"
            audit = audit_baseline(empty_nodes, empty_edges, nodes, edges, level, config["l_max"])
            t0 = time.perf_counter()
            reference = db.evaluate_dag(nodes, edges, level, config["l_max"])
            require(reference is not None, f"Reference level underflow: {case_id}")
            ref_depth = db.depth_of(nodes, edges)
            ref_budget = db.budget_of(nodes, edges, level, config["l_max"])
            score_seconds = time.perf_counter() - t0
            check = calibration_checks(block, level, audit, reference, ref_depth, ref_budget, config["reference_absolute_tolerance_ms"])
            record = {"case_id": case_id, "module": block, "l_init": level, "l_max": config["l_max"],
                      "method": config["method"], "status": "passed", "nodes": nodes, "edges": edges,
                      "reference_latency_ms": reference["latency"], "reference_evaluation_wall_seconds": score_seconds,
                      "independent_audit": audit, "calibration": check}
            write_json(output / "cases" / f"{case_id}.json", record)
            rows.append({"case_id": case_id, "module": block, "l_init": level, "l_max": config["l_max"],
                         "latency_reference_raw_ms": reference["latency"], "latency_decimal_ms": audit["latency_decimal_ms"],
                         "latency_display_ms": display_ms(audit["latency_decimal_ms"]),
                         **{k: audit[k] for k in ("n_b1", "n_b2", "n_bootstrap", "depth", "budget", "utilisation")},
                         "reference_evaluation_wall_seconds": score_seconds, "status": "passed"})
            checks.append({"case_id": case_id, **check})
            rss_samples.append(process.memory_info().rss)
    # This follows from the input-dependent Conjugate cost, not a PDF row lookup.
    mlp = [Decimal(r["latency_decimal_ms"]) for r in rows if r["module"] == "mlp"]
    attn = [Decimal(r["latency_decimal_ms"]) for r in rows if r["module"] == "attention"]
    require(all(b - a == Decimal("0.16") for a, b in zip(mlp, mlp[1:])), "Unexpected MLP level dependence")
    require(len(set(attn)) == 1, "Unexpected Attention level dependence")
    with (output / "summary.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    write_json(output / "calibration.json", {"status": "passed", "cases_passed": len(rows), "cases": checks,
               "mlp_increment_ms": "0.16", "attention_constant_over_input_levels": True})
    mem = process.memory_info()
    try:
        git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
        commit = git.stdout.strip() if git.returncode == 0 else None
    except OSError:
        commit = None
    metadata = {
        "schema_version": 1, "run_id": output.name, "created_at_utc": created, "status": "passed",
        "config": config, "source_version": version, "git_head_at_run": commit,
        "reference_sha256": REFERENCE_SHA256, "python": platform.python_version(),
        "platform": {"system": platform.system(), "machine": platform.machine()},
        "dependencies": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
        "resources": {"reference_import_wall_seconds": import_seconds,
                      "import_and_30_case_pipeline_wall_seconds": time.perf_counter() - start,
                      "process_cpu_seconds": time.process_time() - cpu_start,
                      "reference_evaluation_wall_seconds_sum": sum(r["reference_evaluation_wall_seconds"] for r in rows),
                      "sampled_max_rss_bytes": max(rss_samples + [mem.rss]),
                      "windows_peak_working_set_bytes": getattr(mem, "peak_wset", None),
                      "measurement_scope": "Current process only; pipeline includes reference import, audits, scoring and case/summary writes; excludes interpreter startup and final report/manifest writes. RSS sampled after import and each case; Windows peak is process-lifetime high water mark when available.",
                      "gpu_used": False, "optimisation_search_performed": False,
                      "actual_encrypted_inference_performed": False},
    }
    write_json(output / "run.json", metadata)
    (output / "README.md").write_text(render_report(rows, metadata), encoding="utf-8")
    artifacts = {p.relative_to(output).as_posix(): digest(p) for p in sorted(output.rglob("*")) if p.is_file()}
    write_json(output / "artifacts.sha256.json", artifacts)
    verify(output)
    print(f"PASS: 30/30 teacher baselines calibrated. Results: results/{output.name}")
    return 0


def verify(output):
    """Read saved evidence without re-running the teacher scorer."""
    manifest = json.loads((output / "artifacts.sha256.json").read_text(encoding="utf-8"))
    actual_files = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file() and p.name != "artifacts.sha256.json"}
    require(actual_files == set(manifest), "Result file list differs from manifest")
    for name, expected in manifest.items():
        path = (output / name).resolve()
        require(path.is_relative_to(output), "Manifest path escapes result directory")
        require(digest(path) == expected, f"Changed result artifact: {name}")
    metadata = json.loads((output / "run.json").read_text(encoding="utf-8"))
    require(metadata["source_version"] == source_version(), "Sources changed: saved results need version review")
    with (output / "summary.csv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    expected_cases = {(b, str(l)) for b in ("mlp", "attention") for l in range(15)}
    require(len(rows) == 30 and {(r["module"], r["l_init"]) for r in rows} == expected_cases, "Missing or duplicate cases")
    require(len(list((output / "cases").glob("*.json"))) == 30, "Wrong case-file count")
    for r in rows:
        record = json.loads((output / "cases" / f"{r['case_id']}.json").read_text(encoding="utf-8"))
        require(record["status"] == r["status"] == "passed", "Failed stored case")
        require(record["independent_audit"]["latency_decimal_ms"] == r["latency_decimal_ms"], "Summary/case mismatch")
        require(record["calibration"]["reference_agrees_with_independent_check"], "Uncalibrated case")
    calibration = json.loads((output / "calibration.json").read_text(encoding="utf-8"))
    require(calibration["status"] == "passed" and calibration["cases_passed"] == 30, "Calibration incomplete")
    return 0


def main():
    """Parse run/verify commands and keep outputs inside this repository's results."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "verify"))
    parser.add_argument("--output", type=Path, default=Path("results/local-reproduction"))
    args = parser.parse_args()
    output = args.output.resolve()
    require(output.is_relative_to((ROOT / "results").resolve()) and output != (ROOT / "results").resolve(), "Select a run directory under results/")
    if args.command == "run":
        return run(output)
    verify(output)
    print(f"PASS: saved artifacts, source version and all 30 case records verified: results/{output.name}")
    return 0
