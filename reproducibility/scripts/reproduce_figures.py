"""One-command figure/table generation from the frozen ledger (wraps analysis/04)."""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "analysis" / "04_generate_tables_and_figures.py"


def main() -> int:
    try:
        runpy.run_path(str(TARGET), run_name="__main__")
    except SystemExit as e:
        return int(e.code) if e.code not in (0, None) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
