"""Run or verify the S1 teacher-baseline calibration from the repository root."""

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
sys.path.insert(0, str(ROOT / "src"))

from bootplacement.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
