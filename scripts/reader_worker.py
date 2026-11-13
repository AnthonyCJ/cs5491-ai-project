"""Repository-only reader tasks. Launch with reader-run.ps1, not directly.

The launcher supplies a fresh process-local temporary root and observes the
waiting worker's actual image/token before authorizing business. Python child
creation is refused; optional Git metadata falls back to the original runner's
source-hash record. No function in the frozen scientific code is replaced.
"""
import argparse
import atexit
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import runpy
import shutil
import sys
import tempfile
import time
import traceback


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


class Reader:
    def __init__(self, args):
        self.args = args
        self.receipt = Path(args.receipt)  # Record before any strict resolution.
        self.root = Path(args.root)
        self.temp = self.receipt / "process-temp"
        self.stage = "bootstrap"
        self.resolving_temp = False
        self.keepalive = []
        self.denials = []
        self.cache_directories = []

    def save(self, name, value):
        path = self.receipt / name
        require(not path.exists(), "Refusing to replace an existing receipt: " + name)
        temporary = path.with_suffix(path.suffix + ".pending")
        with temporary.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=True, allow_nan=False)
            stream.write("\n")
        temporary.rename(path)

    def audit(self, event, args):
        if event in ("subprocess.Popen", "os.system", "os.posix_spawn", "os.spawn", "os.exec", "_winapi.CreateProcess"):
            item = {"event": event, "arguments": repr(args)[:8192],
                    "outcome": "policy_refused_before_creation", "created": False,
                    "at": datetime.now(timezone.utc).isoformat()}
            self.denials.append(item)
            with (self.receipt / "creation-denials.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(item) + "\n")
            raise PermissionError("Reader tasks refuse Python child processes; see creation-denials.jsonl")
        if event == "open" and self.resolving_temp and not isinstance(args[0], int):
            path, _, flags = args
            if flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
                require(Path(os.path.abspath(os.fsdecode(path))).is_relative_to(self.temp),
                        "Temporary-directory fallback outside the declared root refused")
        if event == "tempfile.mkdtemp":
            name = os.fsdecode(args[0])
            require(Path(os.path.abspath(name)).is_relative_to(self.temp), "TemporaryDirectory escaped its root")
            self.cache_directories.append(name)
        if event == "os.chmod" and isinstance(args[0], (str, bytes)):
            if Path(os.path.abspath(os.fsdecode(args[0]))).is_relative_to(self.temp):
                raise RuntimeError("Temporary cleanup permission adjustment refused; retain original failure")

    def launch_gate(self):
        self.save("bootstrap.json", {"pid": os.getpid(), "parent_pid": os.getppid(),
            "input_root": self.args.root, "input_receipt": self.args.receipt,
            "python": sys.version, "executable": sys.executable,
            "temporary_environment": {k: os.environ.get(k) for k in ("TMPDIR", "TEMP", "TMP", "MPLCONFIGDIR")},
            "initial_tempfile_cache": tempfile.tempdir, "stage": self.stage})
        sys.addaudithook(self.audit)
        self.save("ready.json", {"pid": os.getpid(), "parent_pid": os.getppid(), "business_started": False})
        until = time.monotonic() + 15
        while not (self.receipt / "go.json").exists():
            if (self.receipt / "stop.json").exists():
                raise RuntimeError("Launcher stopped the task before business authorization")
            require(time.monotonic() < until, "Launcher did not authorize business within 15 seconds")
            time.sleep(0.02)
        go = read(self.receipt / "go.json")
        require(go["worker_pid"] == os.getpid() and go["boundary_verified"], "Authorization does not match this worker")
        self.stage = "strict_path_resolution"
        self.save("path-request.json", {"stage": self.stage, "root": str(self.root), "temp": str(self.temp)})
        require(self.root.resolve(strict=True) == self.root, "Repository path differs from strict real path")
        require(self.temp.resolve(strict=True) == self.temp, "Temporary root differs from strict real path")
        require(Path.cwd().resolve() == self.root, "Worker current directory differs")
        require(tempfile.tempdir is None, "Initial tempfile cache was unexpectedly initialized")
        require(all(Path(os.environ[k]).resolve(strict=True) == self.temp for k in ("TMPDIR", "TEMP", "TMP")),
                "Temporary environment differs")
        self.resolving_temp = True
        try:
            selected = tempfile.gettempdir()
        finally:
            self.resolving_temp = False
        require(Path(selected).resolve(strict=True) == self.temp, "Temporary selection used a fallback")
        self.stage = "dependency_versions"
        docs = self.args.task in ("proposal", "milestone")
        expected_python = (3, 12, 14) if docs else (3, 13, 9)
        require(sys.version_info[:3] == expected_python, "Exact interpreter patch version differs")
        req = self.root / ("requirements-docs-lock.txt" if docs else "requirements-s2.txt")
        versions = {}
        for line in req.read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#"):
                name, version = line.split("==")
                actual = importlib.metadata.version(name)
                require(actual == version, "Dependency differs: " + name)
                versions[name] = actual
        self.save("environment.json", {"python": sys.version, "versions": versions,
            "requirements_sha256": digest(req), "actual_temp": selected,
            "business_boundary": go, "subprocess_policy": "deny all Python child creation; original optional Git metadata fallback retained"})

    def cli(self, entry, arguments):
        old = sys.argv[:]
        sys.argv = [str(self.root / entry), *map(str, arguments)]
        try:
            try:
                runpy.run_path(str(self.root / entry), run_name="__main__")
            except SystemExit as error:
                if error.code not in (None, 0):
                    raise
        finally:
            sys.argv = old

    def cache_probe(self):
        self.stage = "cache_context"
        with tempfile.TemporaryDirectory(prefix="t3-matplotlib-") as name:
            directory = Path(name)
            data = directory / "lifecycle.bin"
            with data.open("xb") as stream:
                stream.write(b"reader cache lifecycle\n")
                stream.flush()
                os.fsync(stream.fileno())
            require(stream.closed and data.read_bytes() == b"reader cache lifecycle\n", "File close/readback differs")
            data.unlink()
            os.environ["MPLCONFIGDIR"] = name
            self.stage = "font_cache_import"
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            from matplotlib import cbook, font_manager
            import ortools.sat.python.cp_model  # Actual dependency import, no solve.
            require(Path(matplotlib.get_cachedir()).resolve(strict=True) == directory, "Matplotlib cache fallback")
            font = directory / f"fontlist-v{font_manager.FontManager.__version__}.json"
            require(bool(read(font)), "Font cache was not written")
            target = directory / "lock-test.json"
            lock = directory / "lock-test.json.matplotlib-lock"
            with cbook._lock_path(target):
                require(lock.is_file(), "Actual matplotlib lock is missing")
                with target.open("x", encoding="utf-8") as stream:
                    json.dump({"written": True}, stream)
            require(stream.closed and not lock.exists() and read(target)["written"], "Lock/close/readback failed")
            target.unlink()
            plt.close("all")
            self.save("cache-context.json", {"directory": name, "font_bytes": font.stat().st_size,
                "font_sha256": digest(font), "lock_created_and_released": True,
                "file_created_closed_read_deleted": True, "context_cleanup_pending": True})
        require(not directory.exists(), "Original context cleanup did not remove its directory")
        shutdown = tempfile.TemporaryDirectory(prefix="reader-normal-exit-")
        self.keepalive.append(shutdown)  # Original weakref cleanup at interpreter exit.
        (Path(shutdown.name) / "exit.txt").write_text("normal exit cleanup\n", encoding="utf-8")
        self.save("cache-lifecycle.json", {"context_removed": True,
            "shutdown_directory": shutdown.name, "normal_exit_cleanup_pending": True})

    def input_run(self):
        value = self.args.input_run or "results/T2-FORMAL-20261004-004/runs/mlp-L00-R201"
        result = (self.root / value).resolve()
        require(result.is_relative_to(self.root / "results"), "Saved input is outside repository results")
        return result

    def task(self):
        task = self.args.task
        self.stage = task
        if task == "preflight":
            self.cache_probe()
            return "completed"
        if task == "timeout-fixture":
            self.save("timeout-entered.json", {"pid": os.getpid(), "waiting_for_actual_stop": True})
            while not (self.receipt / "stop.json").exists():
                time.sleep(0.01)
            return "stopped"
        with tempfile.TemporaryDirectory(prefix="reader-mpl-") as cache:
            os.environ["MPLCONFIGDIR"] = cache
            if task in ("saved-score", "missing-input", "tampered-result"):
                source = self.input_run()
                if task == "missing-input":
                    source = self.receipt / "never-created-input"
                if task == "tampered-result":
                    target = self.receipt / "tampered-copy"
                    shutil.copytree(source, target)
                    case_file = next((target / "cases").glob("*.json"))
                    case = read(case_file)
                    case["solution"]["objective_scaled"] += 1
                    case_file.write_text(json.dumps(case), encoding="utf-8")
                    source = target
                try:
                    self.cli("experiments/t2_formal_check.py", ["--output", source, "--check-output", self.receipt / "saved-check.json"])
                except (FileNotFoundError, ValueError) as error:
                    expected = ((task == "missing-input" and isinstance(error, FileNotFoundError)) or
                                (task == "tampered-result" and "Result hash mismatch: cases/" in str(error)))
                    if not expected:
                        raise
                    require(not (self.receipt / "saved-check.json").exists(), "Refused input produced a successful check")
                    self.save("expected-failure.json", {"task": task, "error_type": type(error).__name__,
                        "message": str(error), "traceback": traceback.format_exc(), "business_passed": False,
                        "fixture_expectation_met": True, "source": str(source)})
                    return "expected_refusal"
                require(task == "saved-score", "Negative fixture unexpectedly succeeded")
                require(read(self.receipt / "saved-check.json")["status"] == "passed", "Saved check failed")
            elif task == "formal":
                self.cli("scripts/reproduce.py", ["--output", self.receipt / "local-formal"])
            elif task == "s3":
                out = self.receipt / "local-s3"
                self.cli("run_s3.py", ["run", "--config", "configs/s3-all-instances.json", "--output", out])
                self.cli("run_s3.py", ["verify", "--output", out])
            elif task == "formal-figures":
                out = self.receipt / "local-figures"
                self.cli("analysis/generate_t3.py", ["--output", out])
                self.cli("analysis/check_t3.py", ["--package", out])
            elif task in ("s3-saved-figures", "s3-fresh-figures"):
                source = self.root / "results/S3-OPT-001" if task == "s3-saved-figures" else self.input_run()
                if task == "s3-fresh-figures":
                    require(bool(self.args.input_run), "Fresh S3 plotting needs --input-run")
                self.cli("run_s3.py", ["plot", "--output", source, "--figures", self.receipt / "local-figures"])
            elif task in ("proposal", "milestone"):
                version = "P-D1-ID-v1" if task == "proposal" else "M-MAINLINE-ID-v2"
                base = f"reports/{task}/versions/{version}"
                out = self.receipt
                self.cli(f"{base}/build_{task}.py", ["--output", out / f"{task}.pdf", "--font-dir", self.args.font_dir])
                self.cli(f"{base}/check_{task}.py", ["--directory", out])
                # pdfplumber already requires this pinned renderer; no external binary.
                import pypdfium2
                pages = []
                with pypdfium2.PdfDocument(out / f"{task}.pdf") as pdf:
                    for index in range(len(pdf)):
                        page = pdf[index]
                        bitmap = page.render(scale=150/72)
                        image = bitmap.to_pil()
                        path = out / f"page-{index+1}.png"
                        image.save(path)
                        pages.append({"file": path.name, "sha256": digest(path)})
                        image.close(); bitmap.close(); page.close()
                self.save("render.json", {"renderer": "pypdfium2", "version": importlib.metadata.version("pypdfium2"), "dpi": 150, "pages": pages, "actual_visual_inspection": "required separately"})
            else:
                raise ValueError("Unknown reader task")
            if "matplotlib.pyplot" in sys.modules:
                sys.modules["matplotlib.pyplot"].close("all")
        return "completed"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--input-run", default="")
    parser.add_argument("--font-dir", default="C:/Windows/Fonts")
    args = parser.parse_args()
    reader = Reader(args)
    sys.stdout = (reader.receipt / "stdout.txt").open("x", encoding="utf-8", buffering=1)
    sys.stderr = (reader.receipt / "stderr.txt").open("x", encoding="utf-8", buffering=1)
    started = time.perf_counter()
    result = {"task": args.task, "pid": os.getpid(), "status": "failed", "gate_passed": False}
    code = 1
    try:
        reader.launch_gate()
        status = reader.task()
        result.update(status=status, gate_passed=status in ("completed", "expected_refusal"))
        code = 124 if status == "stopped" else 0
    except BaseException as error:
        result.update(error_type=type(error).__name__, error=str(error), traceback=traceback.format_exc(), stage=reader.stage)
        reader.save("failure.json", result)
        traceback.print_exc()
    finally:
        result.update(wall_seconds=time.perf_counter()-started, last_stage=reader.stage,
                      denied_creations=len(reader.denials), temporary_directories=reader.cache_directories,
                      cleanup_evidence="launcher checks after OS-confirmed normal exit")
        reader.save("worker-result.json", result)
        sys.stdout.flush(); sys.stderr.flush()
    # Keep the Reader alive during interpreter shutdown for the real finalizer test.
    atexit.register(lambda keep=reader: None)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
