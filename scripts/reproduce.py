"""Reproduce the frozen 30 numerical conditions with the original entry points.

Runs the unchanged optimizer and saved-result checker in sequence, in this
interpreter. Each phase has a watchdog deadline. A timeout ends this process
with code 124 and preserves an incomplete record; it never fills missing cases
from historical results. This is a numerical reproduction, not a rerun of the
original Windows experimental controller or independent-environment evidence.
"""
import argparse
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import platform
import runpy
import sys
import threading
import time

ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "results/T2-FORMAL-20261004-004"
FORMAL_MANIFEST_SHA256 = "0c465b0e11b76c417aa731da2863ad5739a24629e7246d9663559c154472e1f1"


def read(path):
    """Read a repository JSON document, accepting a UTF-8 BOM."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    """Identify the exact source or evidence bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    """Replace only this new run's mutable progress document atomically."""
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def relative(path):
    return path.relative_to(ROOT).as_posix()


def fresh_destination(value):
    """Keep outputs in a new results/local-* directory; never reuse evidence."""
    path = Path(value)
    path = (path if path.is_absolute() else ROOT / path).resolve()
    if not path.is_relative_to(ROOT / "results") or not path.name.startswith("local-"):
        raise ValueError("Choose a new results/local-* directory inside this repository")
    if path.exists():
        raise FileExistsError("Refusing an existing output directory: " + relative(path))
    return path


def phase(entry, arguments, seconds, output, case_id, stage):
    """Execute an existing CLI in-process and enforce a bounded phase lifetime.

    The watchdog writes a separate failure marker before terminating the process.
    A hard timeout cannot promise complete child/process accounting; an external
    supervisor is needed for that evidence. Normal Git metadata calls are awaited
    by the preserved runner. No historical controller is a public dependency.
    """
    start = time.perf_counter()
    marker = output / "timeout.json"

    def expire():
        try:
            save(marker, {"status": "incomplete", "case_id": case_id, "phase": stage,
                          "limit_seconds": seconds, "exit_code": 124,
                          "note": "Watchdog expired; inspect partial output before any new attempt."})
        finally:
            os._exit(124)

    watchdog = threading.Timer(seconds, expire)
    watchdog.daemon = True
    previous = sys.argv[:]
    watchdog.start()
    try:
        sys.argv = [str(entry), *map(str, arguments)]
        runpy.run_path(str(entry), run_name="__main__")
    finally:
        watchdog.cancel()
        watchdog.join()
        sys.argv = previous
    return {"entry": relative(entry), "arguments": [str(a) for a in arguments],
            "wall_seconds": time.perf_counter() - start, "limit_seconds": seconds}


def reproduce(output):
    """Validate frozen inputs, then run and check every condition exactly once."""
    if digest(FORMAL / "artifacts.sha256.json") != FORMAL_MANIFEST_SHA256:
        raise ValueError("Formal evidence manifest differs")
    frozen = read(FORMAL / "inputs.sha256.json")
    for name, expected in frozen.items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or digest(path) != expected:
            raise ValueError("Frozen input differs: " + name)
    conditions = read(FORMAL / "conditions.json")
    expected_ids = [f"{module}-L{level:02}" for module in ("mlp", "attention") for level in range(15)]
    if [c["case_id"] for c in conditions] != expected_ids:
        raise ValueError("Expected exactly MLP 0..14, then Attention 0..14")
    for condition in conditions:
        config = read(ROOT / condition["config"])
        if config["tiny_examples"] is not False:
            raise ValueError("Reproduction must not add tiny-example searches")

    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    record = {"schema_version": 1, "kind": "same-configuration numerical reproduction",
              "formal_source": FORMAL.name, "source_manifest_sha256": FORMAL_MANIFEST_SHA256,
              "driver_sha256": digest(Path(__file__)), "python": platform.python_version(),
              "platform": platform.system(), "started_at_utc": datetime.now(timezone.utc).isoformat(),
              "status": "running", "conditions_expected": 30, "conditions_completed": 0,
              "conditions": [], "independent_environment_reproduction": False,
              "timing_scope": "Driver phases include input checks, metadata, computation and writes; shared imports may be reused. Not the original supervised experiment's timing."}
    progress = output / "reproduction.json"
    save(progress, record)
    try:
        for condition in conditions:
            case_id = condition["case_id"]
            run_output, check_output = output / case_id, output / (case_id + "-check.json")
            record["active_case"] = case_id
            record["active_phase"] = "run"
            save(progress, record)
            run_receipt = phase(ROOT / "run_optimizer.py",
                                ["run", "--config", condition["config"], "--output", relative(run_output)],
                                90, output, case_id, "run")
            record["active_phase"] = "verify"
            save(progress, record)
            check_receipt = phase(ROOT / "experiments/t2_formal_check.py",
                                  ["--output", relative(run_output), "--check-output", relative(check_output)],
                                  30, output, case_id, "verify")
            check = read(check_output)
            case = read(run_output / "cases" / (case_id + ".json"))
            if check["status"] != "passed" or check["case_id"] != case_id:
                raise ValueError("Saved-result check did not pass: " + case_id)
            reference = next(row for row in read(FORMAL / "summary.json")["numerical_results"] if row["case_id"] == case_id)
            if Decimal(check["current_costs"]["total_ms"]) != Decimal(str(reference["estimated_latency_ms"])):
                raise ValueError("Fresh cost differs from formal result: " + case_id)
            record["conditions"].append({"case_id": case_id, "status": "passed",
                "run": relative(run_output), "check": relative(check_output),
                "case_sha256": digest(run_output / "cases" / (case_id + ".json")),
                "check_sha256": digest(check_output), "objective_ms": check["current_costs"]["total_ms"],
                "solver_status": case["solution"]["status"],
                "solver_wall_seconds": case["solution"]["solve_wall_seconds"],
                "run_phase": run_receipt, "verification_phase": check_receipt})
            record["conditions_completed"] = len(record["conditions"])
            save(progress, record)
        record.update(status="passed", active_case=None, active_phase=None,
                      driver_wall_seconds=time.perf_counter() - started,
                      ended_at_utc=datetime.now(timezone.utc).isoformat())
        save(progress, record)
    except BaseException as error:
        record.update(status="failed", error_type=type(error).__name__, error=str(error),
                      driver_wall_seconds=time.perf_counter() - started,
                      ended_at_utc=datetime.now(timezone.utc).isoformat())
        save(progress, record)
        raise
    print("REPRODUCTION PASSED: 30/30 conditions; 30 saved-result checks", flush=True)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="New results/local-* directory")
    arguments = parser.parse_args()
    if Path.cwd().resolve() != ROOT:
        raise ValueError("Run this command from the repository root")
    reproduce(fresh_destination(arguments.output))


if __name__ == "__main__":
    main()
