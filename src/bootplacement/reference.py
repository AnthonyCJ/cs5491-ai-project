"""Load the byte-verified course handout without running its demonstration."""

import hashlib
import importlib.util
from pathlib import Path

REFERENCE_SHA256 = "47a63fd1698da64731f8b9e77067f3ef7e0889534c4e7659bb7fc113ce97acee"
ROOT = Path(__file__).resolve().parents[2]


def load_reference():
    """Reject a changed handout before executing it as a Python module."""
    path = ROOT / "vendor" / "dag_builder.py"
    if hashlib.sha256(path.read_bytes()).hexdigest() != REFERENCE_SHA256:
        raise ValueError("Course handout checksum differs from the calibrated version")
    spec = importlib.util.spec_from_file_location("course_dag_builder", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
