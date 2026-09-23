"""Test configuration: make repo scripts importable and neutralize the forced TkAgg backend."""
import os
import sys
from pathlib import Path

# Force a headless matplotlib backend BEFORE scripts import matplotlib and call use("TkAgg").
os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib  # noqa: E402
matplotlib.use("Agg", force=True)
# a2c_new.py calls matplotlib.use("TkAgg") at import; neutralize it for portability.
matplotlib.use = lambda *a, **k: None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
