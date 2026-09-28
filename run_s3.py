"""Explicit full-instance S3 run, verification, summary and plotting commands."""

import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache" / "matplotlib"))
sys.path.insert(0, str(ROOT / "src"))

from bootplacement.s3_runner import main

if __name__ == "__main__":
    main()
