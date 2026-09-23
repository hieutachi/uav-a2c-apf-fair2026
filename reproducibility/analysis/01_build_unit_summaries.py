"""Build unit-level summaries from the canonical rollout ledger ONLY.

Outputs:
    data/derived/controller_summary.csv         (per controller aggregate)
    data/derived/map_controller_summary.csv     (per controller x map)
    data/derived/map_training_run_summary.csv   (per controller x map x training run = inferential unit)

All numbers are recomputed from data/raw/rollout_ledger.csv; nothing is copied from the manuscript.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

REPRO = Path(__file__).resolve().parents[1]
LEDGER = REPRO / "data" / "raw" / "rollout_ledger.csv"
DERIVED = REPRO / "data" / "derived"

CONT = {
    "clearance": "minimum_signed_clearance_m",
    "steps": "transitions",
    "jitter": "mean_jitter_index_mps3",
    "acceleration": "mean_acceleration_index_mps2",
}


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def mean(xs): return sum(xs) / len(xs) if xs else float("nan")


def std(xs, ddof=0):
    if len(xs) - ddof <= 0:
        return float("nan")
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - ddof))


def median(xs):
    if not xs:
        return float("nan")
    s = sorted(xs); n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def quantile(xs, q):
    if not xs:
        return float("nan")
    s = sorted(xs); idx = q * (len(s) - 1)
    lo = int(math.floor(idx)); hi = int(math.ceil(idx))
    if lo == hi:
        return s[lo]
    return s[lo] + (s[hi] - s[lo]) * (idx - lo)


def load():
    return list(csv.DictReader(open(LEDGER, encoding="utf-8")))


def main() -> int:
    rows = load()
    DERIVED.mkdir(parents=True, exist_ok=True)
    controllers = sorted({r["controller_id"] for r in rows})

    # ---- controller_summary.csv ----
    with open(DERIVED / "controller_summary.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "controller_id", "n_rollouts", "success", "collision", "timeout",
            "success_rate", "wilson_lo", "wilson_hi", "collision_rate", "timeout_rate",
            "metric", "metric_n", "mean", "sd", "median", "iqr", "min", "max", "missing", "conditioning",
        ])
        for c in controllers:
            sub = [r for r in rows if r["controller_id"] == c]
            n = len(sub)
            s = sum(int(r["success"]) for r in sub)
            col = sum(int(r["collision"]) for r in sub)
            to = sum(int(r["timeout"]) for r in sub)
            lo, hi = wilson(s, n)
            base = [c, n, s, col, to, s / n, lo, hi, col / n, to / n]
            # efficiency (successful only)
            eff = [float(r["efficiency"]) for r in sub if r["success"] == "1" and r["efficiency"] not in ("", "nan")]
            w.writerow(base + [
                "efficiency_success", len(eff), mean(eff), std(eff), median(eff),
                quantile(eff, .75) - quantile(eff, .25), min(eff) if eff else "", max(eff) if eff else "",
                n - len(eff), "successful rollouts only",
            ])
            for name, col_key in CONT.items():
                vals = [float(r[col_key]) for r in sub if r[col_key] not in ("", "nan")]
                w.writerow(base + [
                    name, len(vals), mean(vals), std(vals), median(vals),
                    quantile(vals, .75) - quantile(vals, .25), min(vals), max(vals),
                    n - len(vals), "all rollouts",
                ])

    # ---- map_controller_summary.csv ----
    with open(DERIVED / "map_controller_summary.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["controller_id", "map_id", "n", "success", "collision", "timeout",
                    "success_rate", "wilson_lo", "wilson_hi"])
        maps = sorted({r["map_id"] for r in rows})
        for c in controllers:
            for m in maps:
                sub = [r for r in rows if r["controller_id"] == c and r["map_id"] == m]
                if not sub:
                    continue
                n = len(sub); s = sum(int(r["success"]) for r in sub)
                col = sum(int(r["collision"]) for r in sub); to = sum(int(r["timeout"]) for r in sub)
                lo, hi = wilson(s, n)
                w.writerow([c, m, n, s, col, to, s / n, lo, hi])

    # ---- map_training_run_summary.csv (inferential unit) ----
    with open(DERIVED / "map_training_run_summary.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["controller_id", "map_id", "training_seed_label", "training_run_id", "n_rollouts",
                    "success", "success_rate", "n_successful", "efficiency_success_mean",
                    "clearance_mean", "steps_mean", "jitter_mean", "acceleration_mean"])
        units = sorted({(r["controller_id"], r["map_id"], int(r["training_seed_label"]), r["training_run_id"]) for r in rows})
        for c, m, ts, tr in units:
            sub = [r for r in rows if r["controller_id"] == c and r["map_id"] == m and int(r["training_seed_label"]) == ts]
            n = len(sub); s = sum(int(r["success"]) for r in sub)
            eff = [float(r["efficiency"]) for r in sub if r["success"] == "1" and r["efficiency"] not in ("", "nan")]
            w.writerow([
                c, m, ts, tr, n, s, s / n, len(eff),
                mean(eff) if eff else "",
                mean([float(r["minimum_signed_clearance_m"]) for r in sub]),
                mean([float(r["transitions"]) for r in sub]),
                mean([float(r["mean_jitter_index_mps3"]) for r in sub]),
                mean([float(r["mean_acceleration_index_mps2"]) for r in sub]),
            ])

    print("[01] wrote controller_summary.csv, map_controller_summary.csv, map_training_run_summary.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
