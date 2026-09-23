"""Release gate: validate raw artifacts against manifests/raw_artifacts.sha256.

Exit non-zero if any inventoried artifact is missing or its checksum changed.
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MAN = REPO / "reproducibility" / "manifests" / "raw_artifacts.sha256"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not MAN.exists():
        print(f"[validate_artifacts] FAIL: manifest missing {MAN}")
        return 2
    ok = miss = bad = 0
    for line in MAN.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        digest, rel = line.split(None, 1)
        p = REPO / rel
        if not p.exists():
            print(f"[MISSING] {rel}")
            miss += 1
            continue
        actual = sha256(p)
        if actual != digest:
            print(f"[CHANGED] {rel}\n   expected {digest}\n   actual   {actual}")
            bad += 1
        else:
            ok += 1
    print(f"[validate_artifacts] ok={ok} missing={miss} changed={bad}")
    return 0 if (miss == 0 and bad == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
