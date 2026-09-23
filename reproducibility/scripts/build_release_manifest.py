"""Checksum every file in the release package -> manifests/release_artifacts.sha256.

Also prints key checksums used by the result-lock certificate.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

REPRO = Path(__file__).resolve().parents[1]
OUT = REPRO / "manifests" / "release_artifacts.sha256"
EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git"}
EXCLUDE_NAMES = {"release_artifacts.sha256"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    files = []
    for p in sorted(REPRO.rglob("*")):
        if p.is_dir():
            continue
        if any(part in EXCLUDE_DIRS for part in p.parts):
            continue
        if p.name in EXCLUDE_NAMES:
            continue
        files.append(p)

    lines = []
    key = {}
    for p in files:
        digest = sha256(p)
        rel = p.relative_to(REPRO).as_posix()
        lines.append(f"{digest}  {rel}")
        key[rel] = digest

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[release] checksummed {len(files)} files -> {OUT}")
    print("KEY:ledger", key.get("data/raw/rollout_ledger.csv", ""))
    for a in ["analysis/01_build_unit_summaries.py", "analysis/02_compute_statistics.py",
              "analysis/03_reconcile_manuscript_claims.py"]:
        print(f"KEY:{a}", key.get(a, ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
