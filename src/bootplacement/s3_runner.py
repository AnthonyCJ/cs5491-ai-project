"""Full-instance orchestration with immutable evidence and explicit failures.

The S2 formulation, reconstructor, independent audit and reference loader are
reused unchanged. This module adds coverage, a persistent case ledger and
cross-file validation; it does not define a new optimisation objective.
"""

import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform

from .audit import require
from .reference import load_reference
from .s2_model import METHOD, solve_placement
from .s2_runner import (ROOT, ResourceSample, baseline_for, digest, git_state,
                        original_graph, read_json, read_json_value, run_examples,
                        verify_baseline_files, write_json)
from .s2_validation import validate_solution

INSTANCES = tuple((module, level) for module in ("mlp", "attention") for level in range(15))
CASE_IDS = tuple(f"{module}-L{level:02}" for module, level in INSTANCES)
S2 = ROOT / "results/S2-OPT-001"
OUTCOMES = {"improved", "not_improved", "no_solution", "error"}


def now():
    """Return an observation timestamp, independent of human authorisation."""
    return datetime.now(timezone.utc).isoformat()


def validate_config(config):
    """Reject partial coverage, duplicates and invalid numerical settings."""
    require(config.get("schema_version") == 1 and config.get("stage") == "S3", "Expected S3 configuration")
    require(type(config.get("l_max")) is int and config["l_max"] == 14, "L_max must be 14")
    instances = config.get("instances", {})
    require(set(instances) == {"mlp", "attention"}, "Both required modules must be present")
    for module in ("mlp", "attention"):
        levels = instances[module]
        require(isinstance(levels, list) and all(type(x) is int for x in levels), "Integer input levels required")
        require(len(levels) == 15 and sorted(levels) == list(range(15)), "Each module must contain all 15 levels exactly once")
    settings = config.get("solver", {})
    require(set(settings) == {"time_limit_seconds", "workers", "seed"}, "Unexpected solver settings")
    limit = settings["time_limit_seconds"]
    require(type(limit) in (int, float) and math.isfinite(limit) and limit > 0, "Invalid time limit")
    require(type(settings["workers"]) is int and settings["workers"] == 1, "S3 requires one CPU search worker")
    require(type(settings["seed"]) is int and settings["seed"] >= 0, "Invalid seed")
    require(config.get("tiny_examples") is True, "S3 requires the tiny-example evidence")
    require(isinstance(config.get("run_class"), str) and config["run_class"], "Missing run scope")
    return INSTANCES


def verify_manifest(directory):
    """Check complete file membership, safe paths and original artifact bytes."""
    directory = Path(directory).resolve()
    manifest = read_json(directory / "artifacts.sha256.json")
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob("*")
              if p.is_file() and p.name != "artifacts.sha256.json"}
    require(actual == set(manifest), "Artifact coverage differs from manifest")
    for name, expected in manifest.items():
        path = (directory / name).resolve()
        require(path.is_relative_to(directory), "Artifact path escapes its run")
        require(digest(path) == expected, f"Artifact hash mismatch: {name}")


def preserved_s2():
    """Check S2 bytes and identify the historical comparison without rerunning it."""
    verify_manifest(S2)
    record = read_json(S2 / "run.json")
    for name, expected in record["source_version"]["files"].items():
        require(digest(ROOT / name) == expected, f"Preserved S2 source changed: {name}")
    return {"run_id": record["run_id"], "run_sha256": digest(S2 / "run.json"),
            "artifact_manifest_sha256": digest(S2 / "artifacts.sha256.json"),
            "source_sha256": record["source_version"]["sha256"]}


def source_version(config_path):
    """Hash numeric execution, configuration and tests; figures have own provenance."""
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / "src/bootplacement").glob("*.py")
             if not p.name.endswith("_figures.py")}
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "tests").glob("test_*.py"))
    names.update({"run_baselines.py", "run_optimizer.py", "run_s3.py", "requirements.txt",
                  "requirements-s2.txt", "vendor/dag_builder.py", "configs/s1-baselines.json",
                  "configs/s2-mlp-attention.json", config_path.relative_to(ROOT).as_posix()})
    hashes = {name: digest(ROOT / name) for name in sorted(names)}
    return {"sha256": hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest(), "files": hashes}


def comparison(cost, baseline):
    """Compute improvement using exact decimal costs, never rounded display values."""
    cost, baseline = Decimal(cost), Decimal(baseline)
    return {"improved": cost < baseline, "reduction_decimal_ms": str(baseline - cost),
            "reduction_percent": str(100 * (baseline - cost) / baseline), "same_module_and_input": True}


def row_for_case(case):
    """Derive a uniform row for successful, unsuccessful and failed attempts."""
    solution = case.get("solution") or {}
    resources = case.get("resources") or {}
    audit = (case.get("validated") or {}).get("audit", {})
    compared = case.get("comparison") or {}
    return {"case_id": case["case_id"], "module": case["module"], "l_init": case["l_init"],
            "outcome": case["outcome"], "solver_status": solution.get("status", "ERROR"),
            "latency_decimal_ms": audit.get("latency_decimal_ms", ""),
            "baseline_decimal_ms": case["baseline_decimal_ms"],
            "reduction_percent": compared.get("reduction_percent", ""),
            "improved": compared.get("improved", False),
            **{k: audit.get(k, "") for k in ("n_b1", "n_b2", "n_bootstrap", "depth", "budget", "utilisation")},
            "solve_wall_seconds": solution.get("solve_wall_seconds", ""),
            "best_bound_scaled": solution.get("best_bound_scaled", ""),
            "relative_gap": solution.get("relative_gap", ""),
            "process_cpu_seconds": resources.get("process_cpu_seconds", ""),
            "pipeline_wall_seconds": resources.get("pipeline_wall_seconds", ""),
            "sampled_peak_rss_bytes": resources.get("sampled_peak_rss_bytes", "")}


def summarise(cases):
    """Require all 30 explicit outcomes and derive success from saved evidence."""
    require(len(cases) == 30 and {c["case_id"] for c in cases} == set(CASE_IDS), "Full 30-case coverage required")
    require(all(c["outcome"] in OUTCOMES for c in cases), "Pending or unknown case outcome")
    for c in cases:
        require((c["outcome"] in {"improved", "not_improved"}) == (c.get("validated") is not None),
                "Outcome and validation disagree")
        if c.get("validated"):
            expected = comparison(c["validated"]["audit"]["latency_decimal_ms"], c["baseline_decimal_ms"])
            require(c.get("comparison") == expected, "Case comparison is inconsistent")
            require((c["outcome"] == "improved") == expected["improved"], "Outcome and improvement disagree")
    rows = [row_for_case(c) for c in cases]
    errors = sum(c["outcome"] == "error" for c in cases)
    valid = [c for c in cases if c.get("validated")]
    improved = sum(c["outcome"] == "improved" for c in cases)
    status = "failed" if errors else "passed" if improved == 30 else "gaps"
    return {"status": status, "cases_completed": len(cases), "cases_expected": 30,
            "cases_with_valid_solutions": len(valid), "cases_improved": improved,
            "cases_optimal_for_formulation": sum(c["solution"]["optimality_proven_for_formulation"] for c in valid),
            "cases_with_errors": errors,
            "solve_wall_seconds_sum": sum(float(r["solve_wall_seconds"]) for r in rows if r["solve_wall_seconds"] != ""),
            "maximum_sampled_rss_bytes": max((r["sampled_peak_rss_bytes"] for r in rows if r["sampled_peak_rss_bytes"] != ""), default=None),
            "module_summaries": {m: {"cases": sum(c["module"] == m for c in cases),
                "valid": sum(c["module"] == m for c in valid),
                "improved": sum(c["module"] == m and c["outcome"] == "improved" for c in cases),
                "minimum_reduction_percent": min((c["comparison"]["reduction_percent"] for c in valid if c["module"] == m), key=Decimal, default=None),
                "maximum_reduction_percent": max((c["comparison"]["reduction_percent"] for c in valid if c["module"] == m), key=Decimal, default=None)} for m in ("mlp", "attention")}}


def validate_case(case, reference):
    """Reconstruct and independently rescore a record, including status semantics."""
    require(type(case["l_init"]) is int and (case["module"], case["l_init"]) in INSTANCES, "Invalid case parameters")
    require(case["case_id"] == f"{case['module']}-L{case['l_init']:02}" and case["l_max"] == 14, "Case identity mismatch")
    nodes, edges = original_graph(reference, case["module"])
    base = baseline_for(nodes, edges, case["module"], case["l_init"])
    require(Decimal(case["baseline_decimal_ms"]) == Decimal(base["latency_decimal_ms"]), "Baseline comparison mismatch")
    solution = case.get("solution")
    if case["outcome"] == "error":
        require(case.get("validated") is None and case.get("comparison") is None and bool(case.get("error")), "Invalid error record")
        return
    require(solution is not None and solution["l_init"] == case["l_init"] and solution["l_max"] == 14, "Solution input mismatch")
    resources = case["resources"]
    for value in (solution["solve_wall_seconds"], resources["pipeline_wall_seconds"], resources["process_cpu_seconds"]):
        require(math.isfinite(value) and value >= 0, "Invalid observed time")
    require(type(resources["sampled_peak_rss_bytes"]) is int and resources["sampled_peak_rss_bytes"] > 0, "Invalid RSS observation")
    if solution["has_solution"]:
        checked = validate_solution(nodes, edges, solution, reference)
        require(read_json_value(checked) == case["validated"], "Saved DAG or validation differs from reconstructed solution")
        expected = comparison(checked["audit"]["latency_decimal_ms"], base["latency_decimal_ms"])
        require(case.get("comparison") == expected, "Saved comparison differs")
        require(case["outcome"] == ("improved" if expected["improved"] else "not_improved"), "Invalid feasible outcome")
    else:
        require(solution["status"] in {"UNKNOWN", "INFEASIBLE", "MODEL_INVALID"}, "Invalid no-solution status")
        require(case["outcome"] == "no_solution" and case.get("validated") is None and case.get("comparison") is None,
                "Unsolved case must not report a placement or score")


def history_comparison(cases):
    """Compare exact costs on the 18 historically observed S2 instances."""
    current = {c["case_id"]: c for c in cases}
    rows = []
    for path in sorted((S2 / "cases").glob("*.json")):
        old = read_json(path)
        new = current[old["case_id"]]
        old_cost = old["validated"]["audit"]["latency_decimal_ms"]
        new_cost = (new.get("validated") or {}).get("audit", {}).get("latency_decimal_ms")
        rows.append({"case_id": old["case_id"], "s2_decimal_ms": old_cost, "s3_decimal_ms": new_cost,
                     "same_exact_score": new_cost is not None and Decimal(old_cost) == Decimal(new_cost)})
    return {"cases_compared": len(rows), "matching_exact_scores": sum(r["same_exact_score"] for r in rows),
            "note": "Numerical continuity only; equal-cost graphs may differ. No historical record was changed.", "cases": rows}


def report(metadata, rows):
    """Render an English evidence table from the same rows as the CSV."""
    lines = [f"# {metadata['run_id']}: full-instance S3 evidence", "",
             f"Method: `{METHOD}`. {metadata['config']['run_class']}.",
             "Actual CPU searches; fitted inference scores are not real FHE timings.",
             f"Execution commit: `{metadata['git']['head_at_run']}`.",
             f"Source SHA-256: `{metadata['source_version']['sha256']}`.", "",
             "| Case | Status | Estimated latency (ms) | Baseline (ms) | Reduction (%) | B1 / B2 | Depth | Budget | Utilisation | Solve (s) |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for r in rows:
        if r["latency_decimal_ms"] == "":
            lines.append(f"| {r['case_id']} | {r['outcome']} / {r['solver_status']} | unavailable | {r['baseline_decimal_ms']} | - | - | - | - | - | {r['solve_wall_seconds']} |")
        else:
            lines.append(f"| {r['case_id']} | {r['solver_status']} | {Decimal(r['latency_decimal_ms']):.4f} | {Decimal(r['baseline_decimal_ms']):.4f} | {Decimal(r['reduction_percent']):.4f} | {r['n_b1']} / {r['n_b2']} | {r['depth']} | {r['budget']} | {r['utilisation']:.6f} | {r['solve_wall_seconds']:.6f} |")
    lines += ["", "B1 counts individual ciphertexts; B2 counts pairs. Shared operations are counted once.",
              "OPTIMAL and its matching bound apply to the encoded handout model. FEASIBLE alone is not an optimality proof.",
              "Cases, summary.json, tiny-examples.json and the hash manifest preserve decisions, full DAGs, scores, bounds and resource observations.",
              "s2-comparison.json compares the 18 earlier exact scores without rewriting S2. Timing and tied placements may change.",
              "The independent audit and teacher scorer are applied to every accepted placement. Failures are retained, never silently replaced by a baseline.",
              "S4 frozen experiments, S6 independent reproduction, public hosting and formal submission remain separate work."]
    return "\n".join(lines) + "\n"


def run(config_path, output):
    """Run all 30 cases once, persisting each attempt and a not-run ledger first."""
    config = read_json(config_path)
    validate_config(config)
    require(not output.exists(), "Refusing to overwrite an existing run")
    baseline_source = verify_baseline_files()
    s2 = preserved_s2()
    locked = {line.split("==")[0]: line.split("==")[1] for line in
              (ROOT / "requirements-s2.txt").read_text(encoding="utf-8").splitlines() if "==" in line}
    installed = {name: importlib.metadata.version(name) for name in locked}
    require(installed == locked, "Installed dependencies differ from the pinned S2 environment")
    reference = load_reference()
    metadata = {"schema_version": 1, "run_id": output.name, "stage": "S3", "method": METHOD,
                "created_at_utc": now(), "status": "running", "config": config,
                "config_path": config_path.relative_to(ROOT).as_posix(), "source_version": source_version(config_path),
                "git": git_state(), "baseline_run_id": "S1-BL-001", "baseline_source_sha256": baseline_source,
                "s2_history": s2, "python": platform.python_version(),
                "platform": {"system": platform.system(), "machine": platform.machine()}, "dependencies": installed,
                "gpu_used": False, "actual_encrypted_inference_performed": False,
                "cases_expected": 30, "cases_completed": 0, "case_states": {c: "not_run" for c in CASE_IDS}}
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases").mkdir()
    write_json(output / "run.json", metadata)
    cases = []
    for module, level in INSTANCES:
        case_id = f"{module}-L{level:02}"
        base_record = read_json(ROOT / "results/S1-BL-001/cases" / f"{case_id}.json")
        case = {"case_id": case_id, "module": module, "l_init": level, "l_max": 14,
                "baseline_decimal_ms": base_record["independent_audit"]["latency_decimal_ms"],
                "outcome": "error", "solution": None, "validated": None, "comparison": None, "resources": None}
        observation = ResourceSample()
        try:
            nodes, edges = original_graph(reference, module)
            baseline = baseline_for(nodes, edges, module, level)
            with observation:
                solution = solve_placement(nodes, edges, level, baseline=baseline, **config["solver"])
                case["solution"] = solution
                if solution["has_solution"]:
                    checked = validate_solution(nodes, edges, solution, reference)
                    case["validated"] = read_json_value(checked)
                    case["comparison"] = comparison(checked["audit"]["latency_decimal_ms"], case["baseline_decimal_ms"])
                    case["outcome"] = "improved" if case["comparison"]["improved"] else "not_improved"
                else:
                    case["outcome"] = "no_solution"
            case["resources"] = observation.record
            validate_case(case, reference)
        except Exception as exc:
            case.update({"outcome": "error", "validated": None, "comparison": None,
                         "error": {"type": type(exc).__name__, "message": str(exc).replace(str(ROOT), "<repository>").replace(ROOT.as_posix(), "<repository>")},
                         "resources": getattr(observation, "record", None)})
        write_json(output / "cases" / f"{case_id}.json", case)
        cases.append(case)
        metadata["cases_completed"] = len(cases)
        metadata["case_states"][case_id] = case["outcome"]
        write_json(output / "run.json", metadata)
        row = row_for_case(case)
        print(f"{case_id}: {row['solver_status']}; {case['outcome']}; latency_ms={row['latency_decimal_ms'] or 'unavailable'}", flush=True)
    try:
        write_json(output / "tiny-examples.json", run_examples(reference))
    except Exception as exc:
        metadata.update({"status": "failed", "evidence_error": {"type": type(exc).__name__, "message": "Tiny-example validation failed"}})
        write_json(output / "run.json", metadata)
        raise
    totals = summarise(cases)
    metadata.update(totals)
    metadata["completed_at_utc"] = now()
    write_json(output / "run.json", metadata)
    write_json(output / "summary.json", totals)
    write_json(output / "s2-comparison.json", history_comparison(cases))
    rows = [row_for_case(c) for c in cases]
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / "README.md").write_text(report(metadata, rows), encoding="utf-8", newline="\n")
    write_json(output / "artifacts.sha256.json", {p.relative_to(output).as_posix(): digest(p)
               for p in sorted(output.rglob("*")) if p.is_file()})
    print(f"{totals['status'].upper()}: {totals['cases_improved']}/30 instances improved", flush=True)
    return metadata


def verify(output):
    """Verify file provenance, all 30 DAGs, summaries and historical comparison; no search."""
    verify_manifest(output)
    record = read_json(output / "run.json")
    validate_config(record["config"])
    require(record["stage"] == "S3" and record["method"] == METHOD, "Run identity mismatch")
    src = record["source_version"]
    require(hashlib.sha256(json.dumps(src["files"], sort_keys=True).encode()).hexdigest() == src["sha256"], "Source fingerprint mismatch")
    for name, expected in src["files"].items():
        path = (ROOT / name).resolve()
        require(path.is_relative_to(ROOT), "Source path escapes repository")
        require(digest(path) == expected, f"Executed source differs: {name}; use the recorded execution commit")
    require(read_json(ROOT / record["config_path"]) == record["config"], "Saved and source configurations differ")
    require(verify_baseline_files() == record["baseline_source_sha256"] and record["baseline_run_id"] == "S1-BL-001", "Baseline version mismatch")
    require(preserved_s2() == record["s2_history"], "S2 history version mismatch")
    files = sorted((output / "cases").glob("*.json"))
    require({p.stem for p in files} == set(CASE_IDS), "Saved case coverage differs")
    by_id = {p.stem: read_json(p) for p in files}
    require(all(c["case_id"] == name for name, c in by_id.items()), "Case filename mismatch")
    cases = [by_id[name] for name in CASE_IDS]
    reference = load_reference()
    for case in cases:
        validate_case(case, reference)
        if case["solution"]:
            require(all(case["solution"]["settings"][k] == v for k, v in record["config"]["solver"].items()), "Case solver settings differ")
    totals = summarise(cases)
    require(totals == read_json(output / "summary.json"), "Summary JSON differs from cases")
    require(all(record[k] == value for k, value in totals.items()), "Run totals differ from cases")
    require(record["case_states"] == {c["case_id"]: c["outcome"] for c in cases}, "Persistent case ledger differs")
    rows = [row_for_case(c) for c in cases]
    with (output / "summary.csv").open(encoding="utf-8", newline="") as stream:
        saved_rows = list(csv.DictReader(stream))
    require(saved_rows == [{k: str(v) for k, v in row.items()} for row in rows], "Summary CSV differs from cases")
    require((output / "README.md").read_text(encoding="utf-8") == report(record, rows), "Result README differs from cases")
    require(read_json(output / "s2-comparison.json") == history_comparison(cases), "Historical score comparison differs")
    examples = read_json(output / "tiny-examples.json")
    from .s2_oracle import tiny_examples
    definitions = {e["id"]: e for e in tiny_examples()}
    require(examples["status"] == "passed" and len(examples["examples"]) == len(definitions)
            and {e["id"] for e in examples["examples"]} == set(definitions), "Tiny-example coverage mismatch")
    for e in examples["examples"]:
        require(all(e[k] == read_json_value(v) for k, v in definitions[e["id"]].items()), "Tiny-example definition changed")
        checked = validate_solution(e["nodes"], e["edges"], e["solution"], reference)
        require(read_json_value(checked) == e["validated"] and e["passed"], "Stored tiny-example DAG differs")
        require(e["solution"]["status"] == "OPTIMAL" and Decimal(checked["audit"]["latency_decimal_ms"])
                == Decimal(e["oracle"]["minimum_decimal_ms"]) == Decimal(e["hand_cost_ms"]), "Tiny-example score disagreement")
    print(f"VERIFIED: {totals['cases_with_valid_solutions']}/30 valid placements; {totals['cases_improved']}/30 improved; no optimisation search")
    return record


def main():
    """Expose a single S3 command family with explicit, repository-local outputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run_parser = sub.add_parser("run", help="Execute all 30 cases into a new directory")
    run_parser.add_argument("--config", type=Path, default=Path("configs/s3-all-instances.json"))
    for name in ("verify", "summary", "plot"):
        p = sub.add_parser(name, help={"verify": "Check saved evidence without search", "summary": "Verify and print aggregate metrics", "plot": "Verify and draw stage figures"}[name])
        p.add_argument("--output", type=Path, required=True)
        if name == "plot":
            p.add_argument("--figures", type=Path, required=True)
    run_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    require(output.is_relative_to(ROOT / "results") and output != ROOT / "results", "Use a run directory inside results")
    if args.command == "run":
        config = args.config.resolve()
        require(config.is_relative_to(ROOT), "Configuration must be inside the repository")
        record = run(config, output)
    else:
        record = verify(output)
        if args.command == "summary":
            print(json.dumps(read_json(output / "summary.json"), indent=2))
        elif args.command == "plot":
            from .s3_figures import make_figures
            make_figures(output, args.figures.resolve())
    if record["status"] != "passed":
        raise SystemExit(2)
