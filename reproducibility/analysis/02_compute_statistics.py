"""Paired H0-H1 inferential analysis, recomputed from the unit summaries.

Pairing unit: (map_id, training_seed_label). H0 and H1 share the same four maps and the
same five training seed labels (101,211,307,401,503) -> 20 paired units.

Direction convention: difference = H1 - H0.

Outputs:
    data/derived/paired_h0_h1_differences.csv
    data/derived/statistical_results.csv
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

from scipy import stats  # scipy 1.15.2 (recorded in environment)

REPRO = Path(__file__).resolve().parents[1]
DERIVED = REPRO / "data" / "derived"
UNIT = DERIVED / "map_training_run_summary.csv"

METRICS = [
    ("success", "success_rate"),
    ("efficiency", "efficiency_success_mean"),
    ("clearance", "clearance_mean"),
    ("steps", "steps_mean"),
    ("jitter", "jitter_mean"),
    ("acceleration", "acceleration_mean"),
]


def mean(xs): return sum(xs) / len(xs)


def std(xs, ddof=1):
    m = mean(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - ddof))


def hodges_lehmann(diffs):
    walsh = [(diffs[i] + diffs[j]) / 2 for i in range(len(diffs)) for j in range(i, len(diffs))]
    walsh.sort()
    n = len(walsh)
    return walsh[n // 2] if n % 2 else (walsh[n // 2 - 1] + walsh[n // 2]) / 2


def rank_biserial(diffs):
    """Matched-pairs rank-biserial r from Wilcoxon signed-rank (nonzero diffs)."""
    nz = [d for d in diffs if d != 0]
    if not nz:
        return float("nan")
    ranks = stats.rankdata([abs(d) for d in nz])
    w_pos = sum(r for d, r in zip(nz, ranks) if d > 0)
    w_neg = sum(r for d, r in zip(nz, ranks) if d < 0)
    total = w_pos + w_neg
    return (w_pos - w_neg) / total if total else float("nan")


def main() -> int:
    rows = list(csv.DictReader(open(UNIT, encoding="utf-8")))
    h0 = {(r["map_id"], r["training_seed_label"]): r for r in rows if r["controller_id"] == "H0"}
    h1 = {(r["map_id"], r["training_seed_label"]): r for r in rows if r["controller_id"] == "H1"}
    keys = sorted(set(h0) & set(h1))

    # verify pairing keys match exactly
    assert set(h0) == set(h1), "H0/H1 unit keys differ; pairing not genuine"

    diff_rows = []
    for k in keys:
        row = {"map_id": k[0], "training_seed_label": k[1]}
        for name, col in METRICS:
            a = h0[k][col]; b = h1[k][col]
            if a in ("", "nan") or b in ("", "nan"):
                row[f"diff_{name}"] = ""
            else:
                row[f"diff_{name}"] = float(b) - float(a)
        diff_rows.append(row)

    with open(DERIVED / "paired_h0_h1_differences.csv", "w", encoding="utf-8", newline="") as f:
        cols = ["map_id", "training_seed_label"] + [f"diff_{n}" for n, _ in METRICS]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in diff_rows:
            w.writerow(r)

    results = []
    excluded_efficiency = []
    for name, _ in METRICS:
        diffs = [r[f"diff_{name}"] for r in diff_rows if r[f"diff_{name}"] != ""]
        if name == "efficiency":
            excluded_efficiency = [
                f"{r['map_id']}/seed{r['training_seed_label']}"
                for r in diff_rows if r["diff_efficiency"] == ""
            ]
        n = len(diffs)
        md = mean(diffs); sd = std(diffs, ddof=1)
        dz = md / sd if sd else float("nan")
        try:
            w_stat, wp = stats.wilcoxon(diffs, alternative="two-sided", zero_method="wilcox", mode="auto")
        except Exception as e:
            w_stat, wp = float("nan"), float("nan")
        t_stat, tp = stats.ttest_1samp(diffs, 0.0)
        results.append({
            "metric": name, "n_pairs": n, "mean_diff_H1_minus_H0": md, "sd_diff": sd,
            "cohen_dz": dz, "wilcoxon_stat": float(w_stat), "wilcoxon_p": float(wp),
            "ttest_p": float(tp), "rank_biserial_r": rank_biserial(diffs),
            "hodges_lehmann_median_diff": hodges_lehmann(diffs),
        })

    with open(DERIVED / "statistical_results.csv", "w", encoding="utf-8", newline="") as f:
        cols = ["metric", "n_pairs", "mean_diff_H1_minus_H0", "sd_diff", "cohen_dz",
                "wilcoxon_stat", "wilcoxon_p", "ttest_p", "rank_biserial_r", "hodges_lehmann_median_diff"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in results:
            w.writerow(r)

    print(f"[02] paired units: {len(keys)}; efficiency excluded pairs ({len(excluded_efficiency)}): {excluded_efficiency}")
    print(f"[02] scipy={stats.__name__} version check via wilcoxon mode=auto")
    for r in results:
        print(f"    {r['metric']:>12}: n={r['n_pairs']} dz={r['cohen_dz']:.4f} wilcoxon_p={r['wilcoxon_p']:.6g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
