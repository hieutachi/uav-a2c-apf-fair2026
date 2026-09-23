#!/usr/bin/env bash
# Verify the analysis environment matches the pinned versions used for the canonical results.
set -euo pipefail

python - <<'PY'
import sys
print("python", sys.version.split()[0])
need = {"numpy": "2.1.1", "scipy": "1.15.2"}
optional = {"matplotlib": "3.10.1", "pandas": "2.2.3",
            "gymnasium": "1.2.0", "stable_baselines3": "2.7.0", "torch": "2.6.0"}
import importlib
ok = True
for mod, want in need.items():
    try:
        m = importlib.import_module(mod)
        got = getattr(m, "__version__", "?")
        flag = "OK" if got.split("+")[0] == want else "MISMATCH"
        if flag != "OK":
            ok = False
        print(f"[required] {mod} {got} (want {want}) {flag}")
    except Exception as e:
        ok = False
        print(f"[required] {mod} MISSING ({e})")
for mod, want in optional.items():
    try:
        m = importlib.import_module(mod)
        print(f"[optional] {mod} {getattr(m,'__version__','?')} (ref {want})")
    except Exception:
        print(f"[optional] {mod} not installed (only needed for simulation/retraining)")
sys.exit(0 if ok else 1)
PY
echo "verify_environment: done"
