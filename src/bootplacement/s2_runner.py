"""Bounded experiments, immutable result directories and saved-evidence verification."""

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import threading
import time

import psutil

from .audit import audit_baseline, require
from .reference import load_reference
from .s2_model import METHOD, solve_placement
from .s2_oracle import enumerate_tiny, tiny_examples
from .s2_validation import validate_solution

ROOT = Path(__file__).resolve().parents[2]
BASELINES = ROOT / "results" / "S1-BL-001"


def read_json(path):
    """Read UTF-8 JSON consistently across Windows and POSIX."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    """Write a stable, readable JSON record with explicit Unicode handling."""
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def digest(path):
    """Hash file bytes, including their original line endings."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_baseline_files():
    """Check preserved S1 source/results without rerunning its experiment."""
    record = read_json(BASELINES / "run.json")
    for name, expected in record["source_version"]["files"].items():
        require(digest(ROOT / name) == expected, f"Preserved S1 source changed: {name}")
    for name, expected in read_json(BASELINES / "artifacts.sha256.json").items():
        require(digest(BASELINES / name) == expected, f"Preserved S1 result changed: {name}")
    return record["source_version"]["sha256"]


def source_version(config_path):
    """Record exact executable, test and configuration bytes for this S2 run."""
    names = set(read_json(BASELINES / "run.json")["source_version"]["files"])
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "src/bootplacement").glob("s2_*.py"))
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("test_*.py"))
    names.update({"run_optimizer.py", "requirements-s2.txt", config_path.relative_to(ROOT).as_posix()})
    hashes = {name: digest(ROOT / name) for name in sorted(names)}
    return {"sha256": hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(), "files": hashes}


def git_state():
    """Read Git without changing index, trust configuration or global settings."""
    command = ["git", "--no-optional-locks", "-c", f"safe.directory={ROOT.as_posix()}", "-C", str(ROOT)]
    try:
        head = subprocess.check_output(command + ["rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True).strip()
        dirty = bool(subprocess.check_output(command + ["status", "--porcelain"], stderr=subprocess.DEVNULL, text=True).strip())
        return {"head_at_run": head, "worktree_dirty_at_run": dirty,
                "note": "Source fingerprint identifies executed bytes, including any uncommitted files."}
    except (OSError, subprocess.CalledProcessError):
        return {"head_at_run": None, "worktree_dirty_at_run": None,
                "note": "Git metadata unavailable; the complete source hash manifest identifies executed bytes."}


class ResourceSample:
    """Measure current-process CPU and RSS during one model/search/audit interval."""

    def __enter__(self):
        self.process = psutil.Process()
        self.start_cpu = sum(self.process.cpu_times()[:2])
        self.start_wall = time.perf_counter()
        self.peak = self.process.memory_info().rss
        self.stop = threading.Event()

        def sample():
            while not self.stop.wait(0.02):
                self.peak = max(self.peak, self.process.memory_info().rss)

        self.thread = threading.Thread(target=sample, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.stop.set()
        self.thread.join()
        memory = self.process.memory_info()
        self.peak = max(self.peak, memory.rss)
        self.record = {"pipeline_wall_seconds": time.perf_counter() - self.start_wall,
                       "process_cpu_seconds": sum(self.process.cpu_times()[:2]) - self.start_cpu,
                       "sampled_peak_rss_bytes": self.peak,
                       "windows_process_lifetime_peak_working_set_bytes": getattr(memory, "peak_wset", None),
                       "rss_sampling_interval_seconds": 0.02,
                       "scope": "Current process; model construction, solve, reconstruction and validation. Excludes reference import, baseline preparation and result writing. RSS includes resident imported packages. Windows peak, if available, covers process lifetime."}


def original_graph(reference, module):
    """Load only the separate required blocks, never the optional combined graph."""
    require(module in ("mlp", "attention"), "Unknown module")
    return reference.get_mlp_empty() if module == "mlp" else reference.get_attn_empty()


def baseline_for(nodes, edges, module, level):
    """Recheck a saved baseline to provide a trustworthy hint and upper bound."""
    case = read_json(BASELINES / "cases" / f"{module}-L{level:02}.json")
    require(case["module"] == module and case["l_init"] == level, "Baseline instance mismatch")
    audit = audit_baseline(nodes, edges, case["nodes"], case["edges"], level)
    require(Decimal(audit["latency_decimal_ms"]) == Decimal(case["independent_audit"]["latency_decimal_ms"]),
            "Saved baseline audit differs")
    audit["node_ops"] = {n[0]: n[1] for n in case["nodes"]}
    return audit


def run_examples(reference):
    """Save agreement between hand arithmetic, exhaustive search and CP-SAT."""
    examples = []
    for e in tiny_examples():
        oracle = enumerate_tiny(e["nodes"], e["edges"], e["level"])
        solution = solve_placement(e["nodes"], e["edges"], e["level"], time_limit_seconds=10)
        checked = validate_solution(e["nodes"], e["edges"], solution, reference)
        require(solution["status"] == "OPTIMAL", "Tiny example not solved to optimality")
        require(Decimal(oracle["minimum_decimal_ms"]) == Decimal(e["hand_cost_ms"]) ==
                Decimal(checked["audit"]["latency_decimal_ms"]), "Tiny example cross-check failed")
        examples.append({**e, "oracle": oracle, "solution": solution, "validated": checked, "passed": True})
    return {"status": "passed", "examples": examples,
            "scope": "Complete finite search of six tiny examples, not enumeration of the course blocks."}


def report(metadata, rows):
    """Write an English result report derived directly from saved numerical rows."""
    lines = [f"# {metadata['run_id']}: S2 optimisation evidence", "",
             f"Method: `{METHOD}`. Scope: {metadata['config']['run_class']}.", "",
             "These are actual CPU optimisation runs scored with fitted inference costs. No encrypted inference was executed.",
             "This S2 run does not replace S4 formal experiments or S6 independent reproduction.", "",
             f"Source fingerprint: `{metadata['source_version']['sha256']}`.", "",
             "| Case | Status | Estimated latency (ms) | Baseline (ms) | Reduction (%) | B1 / B2 | Depth | Budget | Utilisation | Solve (s) |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        if r["latency_decimal_ms"] == "":
            lines.append(f"| {r['case_id']} | {r['solver_status']} | no solution | {r['baseline_decimal_ms']} | - | - | - | - | - | {r['solve_wall_seconds']:.6f} |")
        else:
            lines.append(f"| {r['case_id']} | {r['solver_status']} | {Decimal(r['latency_decimal_ms']):.4f} | {Decimal(r['baseline_decimal_ms']):.4f} | {r['reduction_percent']:.4f} | {r['n_b1']} / {r['n_b2']} | {r['depth']} | {r['budget']} | {r['utilisation']:.6f} | {r['solve_wall_seconds']:.6f} |")
    lines += ["", "B1 counts ciphertexts; B2 counts ciphertext pairs. Shared nodes are charged once.",
              "`OPTIMAL` refers to the encoded handout model with exact integer costs and zero configured gap tolerances; it is not a claim about real FHE runtime.",
              "`FEASIBLE` is a valid incumbent without an optimality proof. Other statuses do not contain an accepted placement. No baseline fallback is presented as an improvement.",
              "", "The JSON case records include decisions, the reconstructed DAG, every level and node cost, independent checks, the raw reference score, solver bounds and resources.",
              "Timing and RSS are local observations. Resource scope is described in each case; process RSS includes imported libraries.",
              "Figures are generated separately from these immutable case files. See the repository README for exact commands."]
    return "\n".join(lines) + "\n"


def run(config_path, output):
    """Execute only configured instances and refuse to overwrite an existing run."""
    config = read_json(config_path)
    require(config["stage"] == "S2" and config["l_max"] == 14, "Expected S2 configuration with L_max=14")
    instances = [(module, level) for module, levels in config["instances"].items() for level in levels]
    require(bool(instances) and len(set(instances)) == len(instances), "Empty or repeated instance")
    for module, level in instances:
        require(module in ("mlp", "attention") and type(level) is int and 0 <= level <= 14, "Invalid instance")
    baseline_source = verify_baseline_files()
    reference = load_reference()
    metadata = {"schema_version": 1, "run_id": output.name, "method": METHOD, "status": "running",
                "created_at_utc": datetime.now(timezone.utc).isoformat(), "config": config,
                "config_path": config_path.relative_to(ROOT).as_posix(), "source_version": source_version(config_path),
                "git": git_state(), "baseline_run_id": "S1-BL-001", "baseline_source_sha256": baseline_source,
                "python": platform.python_version(), "platform": {"system": platform.system(), "machine": platform.machine()},
                "dependencies": {line.split("==")[0]: line.split("==")[1] for line in (ROOT / "requirements-s2.txt").read_text(encoding="utf-8").splitlines() if "==" in line},
                "actual_ortools_version": importlib.metadata.version("ortools"),
                "gpu_used": False, "actual_encrypted_inference_performed": False,
                "cases_completed": 0, "cases_expected": len(instances)}
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases").mkdir()
    write_json(output / "run.json", metadata)
    rows = []
    try:
        for module, level in instances:
            case_id = f"{module}-L{level:02}"
            nodes, edges = original_graph(reference, module)
            baseline = baseline_for(nodes, edges, module, level)
            with ResourceSample() as resources:
                solution = solve_placement(nodes, edges, level, baseline=baseline, **config["solver"])
                validated = validate_solution(nodes, edges, solution, reference) if solution["has_solution"] else None
            case = {"case_id": case_id, "module": module, "l_init": level, "l_max": 14,
                    "baseline_decimal_ms": baseline["latency_decimal_ms"], "solution": solution,
                    "validated": validated, "resources": resources.record}
            row = {"case_id": case_id, "module": module, "l_init": level, "solver_status": solution["status"],
                   "latency_decimal_ms": "", "baseline_decimal_ms": baseline["latency_decimal_ms"],
                   "reduction_percent": "", "improved": False, "n_b1": "", "n_b2": "", "depth": "",
                   "budget": "", "utilisation": "", "solve_wall_seconds": solution["solve_wall_seconds"],
                   "best_bound_scaled": solution["best_bound_scaled"], "relative_gap": solution.get("relative_gap", ""),
                   "sampled_peak_rss_bytes": resources.record["sampled_peak_rss_bytes"]}
            if validated:
                audit = validated["audit"]
                base = Decimal(baseline["latency_decimal_ms"])
                cost = Decimal(audit["latency_decimal_ms"])
                improvement = 100 * (base - cost) / base
                case["comparison"] = {"improved": cost < base, "reduction_decimal_ms": str(base - cost),
                                      "reduction_percent": str(improvement), "same_module_and_input": True}
                row.update({k: audit[k] for k in ("latency_decimal_ms", "n_b1", "n_b2", "depth", "budget", "utilisation")})
                row.update({"reduction_percent": float(improvement), "improved": cost < base})
            write_json(output / "cases" / f"{case_id}.json", case)
            rows.append(row)
            metadata["cases_completed"] = len(rows)
            write_json(output / "run.json", metadata)
            print(f"{case_id}: {solution['status']}; latency_ms={row['latency_decimal_ms'] or 'unavailable'}; improved={row['improved']}; solve_s={solution['solve_wall_seconds']:.3f}", flush=True)
        if config["tiny_examples"]:
            write_json(output / "tiny-examples.json", run_examples(reference))
        metadata.update({"status": "passed" if all(r["improved"] for r in rows) else "gaps",
                         "cases_with_valid_solutions": sum(r["latency_decimal_ms"] != "" for r in rows),
                         "cases_improved": sum(r["improved"] for r in rows),
                         "cases_optimal_for_formulation": sum(r["solver_status"] == "OPTIMAL" for r in rows),
                         "completed_at_utc": datetime.now(timezone.utc).isoformat()})
        write_json(output / "run.json", metadata)
        with (output / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        (output / "README.md").write_text(report(metadata, rows), encoding="utf-8")
        write_json(output / "artifacts.sha256.json", {p.relative_to(output).as_posix(): digest(p) for p in sorted(output.rglob("*")) if p.is_file()})
    except Exception as exc:
        metadata.update({"status": "failed", "error": str(exc), "cases_completed": len(rows)})
        write_json(output / "run.json", metadata)
        raise
    print(f"{metadata['status'].upper()}: {metadata['cases_improved']}/{len(rows)} instances improved. Saved {output.relative_to(ROOT).as_posix()}")
    return metadata


def verify(output, check_source=True):
    """Recheck saved placements and scores without running optimisation search."""
    manifest = read_json(output / "artifacts.sha256.json")
    actual = {p.relative_to(output).as_posix() for p in output.rglob("*") if p.is_file() and p.name != "artifacts.sha256.json"}
    require(actual == set(manifest), "Result file coverage differs from manifest")
    for name, expected in manifest.items():
        require(digest(output / name) == expected, f"Result hash mismatch: {name}")
    record = read_json(output / "run.json")
    if check_source:
        for name, expected in record["source_version"]["files"].items():
            require(digest(ROOT / name) == expected, f"Run source version differs: {name}")
    require(record["status"] in ("passed", "gaps"), "Incomplete or failed run")
    verify_baseline_files()
    reference = load_reference()
    expected = {f"{m}-L{l:02}" for m, levels in record["config"]["instances"].items() for l in levels}
    files = list((output / "cases").glob("*.json"))
    require({p.stem for p in files} == expected, "Instance coverage mismatch")
    validated_count = 0
    for path in files:
        case = read_json(path)
        require(case["case_id"] == path.stem, "Case ID mismatch")
        nodes, edges = original_graph(reference, case["module"])
        if case["solution"]["has_solution"]:
            checked = validate_solution(nodes, edges, case["solution"], reference)
            require(read_json_value(checked) == case["validated"], "Stored validation differs from reconstruction")
            base = baseline_for(nodes, edges, case["module"], case["l_init"])
            require(Decimal(base["latency_decimal_ms"]) == Decimal(case["baseline_decimal_ms"]), "Baseline comparison mismatch")
            require((Decimal(checked["audit"]["latency_decimal_ms"]) < Decimal(case["baseline_decimal_ms"])) == case["comparison"]["improved"], "Improvement flag mismatch")
            validated_count += 1
    require(validated_count == record["cases_with_valid_solutions"], "Validation count mismatch")
    print(f"PASS: {validated_count}/{len(files)} saved placements verified; no optimisation search performed.")
    return record


def read_json_value(value):
    """Normalize tuples as they appear after JSON serialization."""
    return json.loads(json.dumps(value))


def main():
    """Dispatch explicit run/verify/plot commands; no work occurs on import."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="Run the explicitly configured instances into a new directory")
    run_parser.add_argument("--config", type=Path, default=Path("configs/s2-mlp-attention.json"))
    run_parser.add_argument("--output", type=Path, required=True)
    verify_parser = sub.add_parser("verify", help="Recheck saved solutions without searching")
    verify_parser.add_argument("--output", type=Path, required=True)
    plot_parser = sub.add_parser("plot", help="Draw preliminary figures from verified case files")
    plot_parser.add_argument("--output", type=Path, required=True, help="Existing run directory")
    plot_parser.add_argument("--figures", type=Path, required=True, help="New figure directory")
    args = parser.parse_args()
    output = args.output.resolve()
    require(output.is_relative_to(ROOT / "results"), "Results must be inside this repository's results directory")
    if args.command == "run":
        config_path = args.config.resolve()
        require(config_path.is_relative_to(ROOT), "Configuration must be inside this repository")
        result = run(config_path, output)
        if result["status"] != "passed":
            raise SystemExit(2)
    elif args.command == "verify":
        verify(output)
    else:
        from .s2_figures import make_figures
        verify(output)
        make_figures(output, args.figures.resolve())
