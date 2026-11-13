"""Verify one frozen T2 condition, including a fresh teacher-baseline score.

Uses the preserved numerical audit and verifier. This entry performs no search.
The output is an independent new check file; the original run is not modified.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import json
import os
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
sys.path.insert(0, str(ROOT / "src"))
from bootplacement.audit import audit_baseline, require
from bootplacement.reference import load_reference
from bootplacement.s2_runner import digest, original_graph, read_json, verify


def breakdown(nodes, audit):
    parts = {"ordinary_ms": Decimal(0), "bootstrap1_ms": Decimal(0),
             "bootstrap2_ms": Decimal(0), "modswitch_ms": Decimal(0)}
    kinds = {"Bootstrap1": "bootstrap1_ms", "Bootstrap2": "bootstrap2_ms", "Modswitch": "modswitch_ms"}
    require(len({n[0] for n in nodes}) == len(nodes), "Repeated node identity")
    require(set(audit["node_latency_decimal_ms"]) == {n[0] for n in nodes}, "Incomplete node cost coverage")
    for node in nodes:
        parts[kinds.get(node[1], "ordinary_ms")] += Decimal(audit["node_latency_decimal_ms"][node[0]])
    parts["total_ms"] = sum(parts.values())
    require(parts["total_ms"] == Decimal(audit["latency_decimal_ms"]), "Full cost sum differs")
    return {key: str(value) for key, value in parts.items()}


def check(output, check_output):
    require(not check_output.exists(), "Refusing to overwrite a check")
    started = datetime.now(timezone.utc).isoformat()
    start_wall, start_cpu = time.perf_counter(), time.process_time()
    record = verify(output)
    require(record["cases_expected"] == record["cases_completed"] == 1, "Exactly one condition required")
    case_files = list((output / "cases").glob("*.json"))
    require(len(case_files) == 1, "One saved case required")
    case = read_json(case_files[0])
    case_id = case["case_id"]
    expected = {"time_limit_seconds": 60.0, "workers": 1, "seed": 5491}
    require(record["config"]["solver"] == expected, "Frozen solver settings differ")
    require(record["config"]["tiny_examples"] is False, "No tiny searches permitted")
    solution = case["solution"]
    require(solution["status"] == "OPTIMAL" and solution["optimality_proven_for_formulation"], "No optimality proof")
    require(Decimal(str(solution["best_bound_scaled"])) == Decimal(solution["objective_scaled"])
            and solution["relative_gap"] == 0, "Nonzero bound gap")
    require(solution["settings"]["relative_gap_limit"] == 0 and solution["settings"]["absolute_gap_limit"] == 0,
            "Gap settings differ")
    require(solution["settings"]["validated_baseline_hint_and_upper_bound"] is True, "Missing validated baseline hint")
    require(solution["solve_wall_seconds"] <= 60, "Solver time exceeded")
    require(case["comparison"]["improved"] is True, "No strict improvement")
    history_path = ROOT / "results/S3-OPT-001/cases" / (case_id + ".json")
    history = read_json(history_path)
    require(Decimal(solution["objective_decimal_ms"]) == Decimal(history["solution"]["objective_decimal_ms"]),
            "Historical exact objective differs; do not substitute the old result")
    baseline_path = ROOT / "results/S1-BL-001/cases" / (case_id + ".json")
    baseline = read_json(baseline_path)
    reference = load_reference()
    original_nodes, original_edges = original_graph(reference, case["module"])
    baseline_start_wall, baseline_start_cpu = time.perf_counter(), time.process_time()
    audit = audit_baseline(original_nodes, original_edges, baseline["nodes"], baseline["edges"], case["l_init"])
    score = reference.evaluate_dag(baseline["nodes"], baseline["edges"], case["l_init"], 14)
    require(score is not None, "Teacher rejected baseline")
    exact = Decimal(audit["latency_decimal_ms"])
    require(exact == Decimal(baseline["independent_audit"]["latency_decimal_ms"])
            == Decimal(case["baseline_decimal_ms"]), "Baseline exact cost differs")
    error = abs(Decimal(str(score["latency"])) - exact)
    require(error <= Decimal("0.0000001"), "Baseline teacher cost differs")
    require(score["l_in"] == audit["l_in"] and score["l_out"] == audit["l_out"], "Baseline node levels differ")
    require(score["edge_lvl"] == {(e["from"], e["to"]): e["level"] for e in audit["edge_levels"]},
            "Baseline edge levels differ")
    require(reference.depth_of(baseline["nodes"], baseline["edges"]) == audit["depth"], "Baseline depth differs")
    require(tuple(reference.budget_of(baseline["nodes"], baseline["edges"], case["l_init"], 14)) ==
            (audit["n_b1"], audit["n_b2"], audit["budget"]), "Baseline budget/counts differ")
    baseline_wall, baseline_cpu = time.perf_counter() - baseline_start_wall, time.process_time() - baseline_start_cpu
    new_cost = breakdown(case["validated"]["nodes"], case["validated"]["audit"])
    base_cost = breakdown(baseline["nodes"], audit)
    require(Decimal(new_cost["total_ms"]) == Decimal(solution["objective_decimal_ms"]) < exact,
            "Complete-cost comparison differs")
    result = {"schema_version": 1, "case_id": case_id, "status": "passed", "started_at_utc": started,
              "solver_calls": 0, "saved_solution_verified_once_without_search": True,
              "baseline_freshly_audited_and_teacher_scored": True,
              "baseline_run_id": "S1-BL-001", "baseline_case_sha256": digest(baseline_path),
              "historical_case_sha256": digest(history_path), "run_json_sha256": digest(output / "run.json"),
              "case_sha256": digest(case_files[0]), "checker_sha256": digest(Path(__file__)),
              "source_fingerprint": record["source_version"]["sha256"],
              "baseline_audit": audit, "baseline_teacher_latency_ms": score["latency"],
              "baseline_teacher_absolute_error_ms": str(error),
              "current_costs": new_cost, "baseline_costs": base_cost,
              "historical_exact_objective_matched": True,
              "optimised_teacher_absolute_error_ms": case["validated"]["reference_decimal_absolute_error_ms"],
              "baseline_check_wall_seconds": baseline_wall, "baseline_check_cpu_seconds": baseline_cpu,
              "verification_body_wall_seconds": time.perf_counter() - start_wall,
              "verification_body_cpu_seconds": time.process_time() - start_cpu,
              "timing_scope": "No-search verification body; baseline check is nested; excludes imports, output writing and process exit. Outer receipts cover complete attempt.",
              "completed_before_write_at_utc": datetime.now(timezone.utc).isoformat()}
    check_output.parent.mkdir(parents=True, exist_ok=True)
    check_output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    require(read_json(check_output) == result, "Check file readback differs")
    print(f"T2 CHECK PASSED: {case_id}; fresh baseline score and complete cost; no search", flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check-output", type=Path, required=True)
    arguments = parser.parse_args()
    check(arguments.output.resolve(), arguments.check_output.resolve())
