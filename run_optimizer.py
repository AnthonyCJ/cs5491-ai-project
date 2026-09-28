"""Command-line entry point for the S2 optimisation and verification workflow."""

from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
sys.path.insert(0, str(ROOT / "src"))

from bootplacement.s2_runner import main

if __name__ == "__main__":
    main()
