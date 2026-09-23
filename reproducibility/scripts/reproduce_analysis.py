"""One-command archival reproduction: rebuild derived summaries, statistics, and reconciliation
from the frozen rollout ledger. Fails if any manuscript claim does not reconcile.
"""
from __future__ import annotations

import runpy
import sys
from pathlib import Path

REPRO = Path(__file__).resolve().parents[1]
ANALYSIS = REPRO / "analysis"

STEPS = [
    ANALYSIS / "01_build_unit_summaries.py",
    ANALYSIS / "02_compute_statistics.py",
    ANALYSIS / "03_reconcile_manuscript_claims.py",
]


def main() -> int:
    for step in STEPS:
        print(f"\n=== running {step.name} ===")
        try:
            runpy.run_path(str(step), run_name="__main__")
        except SystemExit as e:
            if e.code not in (0, None):
                print(f"[reproduce_analysis] {step.name} exited {e.code}")
                return int(e.code)
    print("\n[reproduce_analysis] analysis reproduced from ledger; see reports/result_reconciliation.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
