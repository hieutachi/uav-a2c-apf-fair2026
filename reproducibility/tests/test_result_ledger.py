import csv
from collections import Counter
from pathlib import Path

REPRO = Path(__file__).resolve().parents[1]
LEDGER = REPRO / "data" / "raw" / "rollout_ledger.csv"


def _rows():
    return list(csv.DictReader(open(LEDGER, encoding="utf-8")))


def test_terminal_status_invariant():
    for r in _rows():
        assert int(r["success"]) + int(r["collision"]) + int(r["timeout"]) == 1


def test_status_string_matches_flags():
    for r in _rows():
        st = r["status"]
        assert (st == "success" and r["success"] == "1") or \
               (st == "collision" and r["collision"] == "1") or \
               (st == "timeout" and r["timeout"] == "1")


def test_controller_totals_and_cells():
    rows = _rows()
    per = Counter(r["controller_id"] for r in rows)
    assert per == Counter({"H0": 1000, "H1": 1000, "H2": 1000})
    cell = Counter((r["controller_id"], r["map_id"]) for r in rows)
    assert all(v == 250 for v in cell.values())
    assert len(cell) == 12  # 3 controllers x 4 maps


def test_efficiency_na_on_failures():
    for r in _rows():
        if r["success"] != "1":
            assert r["efficiency"] in ("", "nan"), r["run_id"]


def test_smoke_run_excluded():
    for r in _rows():
        assert not r["run_id"].endswith("steps64")


def test_paired_pairing_is_genuine():
    rows = _rows()
    h0 = {(r["map_id"], r["training_seed_label"]) for r in rows if r["controller_id"] == "H0"}
    h1 = {(r["map_id"], r["training_seed_label"]) for r in rows if r["controller_id"] == "H1"}
    assert h0 == h1 and len(h0) == 20
