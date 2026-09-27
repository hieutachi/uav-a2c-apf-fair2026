#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aggregate all ICAI-FAI 2026 revision outputs into tables + paired statistics.

Reads results/icai2026/**/*.csv, writes results/icai2026/tables/*.csv and
results/icai2026/stats_icai.json. Tolerates missing H3 outputs (they are filled
in by re-running this script after H3 evaluation completes).
Inference stays at the (map, training-run) unit; rollouts are descriptive only.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
ICAI = ROOT / "results" / "icai2026"
TAB = ICAI / "tables"
TAB.mkdir(parents=True, exist_ok=True)

METRICS = ["success", "jitter_index", "acceleration_index",
           "path_efficiency", "min_obstacle_distance_m", "steps"]


def load(rel: str):
    p = ICAI / rel
    if not p.exists():
        return []
    return list(csv.DictReader(p.open(encoding="utf-8")))


def fnum(x):
    try:
        v = float(x)
        return v if not math.isnan(v) else None
    except (TypeError, ValueError):
        return None


def unit_means(rows, config_key="config"):
    """{(config, map, seed): {metric: mean over rollouts}}; efficiency uses successes only."""
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        k = (r[config_key], r["map_id"], r["unit"].split("_seed")[-1])
        for m in METRICS:
            v = fnum(r.get(m))
            if v is not None:
                acc[k][m].append(v)
    return {k: {m: float(np.mean(v)) for m, v in d.items() if v} for k, d in acc.items()}


def paired(um, a, b, metric):
    diffs = []
    for k in sorted(um):
        if k[0] == a and metric in um[k]:
            partner = (b, k[1], k[2])
            if partner in um and metric in um[partner]:
                diffs.append(um[partner][metric] - um[k][metric])
    d = np.array(diffs, float)
    if len(d) == 0:
        return None
    nz = d[d != 0]
    p = float(stats.wilcoxon(nz, alternative="two-sided").pvalue) if len(nz) >= 1 else math.nan
    dz = float(d.mean() / d.std(ddof=1)) if len(d) > 1 and d.std(ddof=1) > 0 else math.nan
    return {"contrast": f"{b}-{a}", "metric": metric, "n_pairs": int(len(d)),
            "n_nonzero": int(len(nz)), "mean_diff": float(d.mean()),
            "cohen_dz": dz, "wilcoxon_p": p}


def totals(rows, keys):
    g = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        k = tuple(r[k] for k in keys)
        g[k][0] += 1
        g[k][1] += int(r["success"])
        g[k][2] += int(r["collision"])
        g[k][3] += int(r["timeout"])
    return g


def dump(rows, path: Path, fields):
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def main():
    uniq = load("icai_eval_unique/icai_eval_unique_H0_H1.csv")
    uniq_h3 = load("icai_eval_unique_h3/icai_eval_unique_h3_H3.csv")
    wind = load("icai_wind_sweep/icai_wind_sweep_H0_H1.csv")
    wind_h3 = load("icai_wind_sweep_h3/icai_wind_sweep_h3_H3.csv")
    held = load("icai_heldout/icai_heldout_H0_H1.csv")
    held_h3 = load("icai_heldout_h3/icai_heldout_h3_H3.csv")
    sens = load("icai_apf_sensitivity/apf_sensitivity.csv")
    alog = load("icai_action_log/icai_action_log_H0.csv")

    # ---- table: corrected outcomes per config x map (+ overall)
    out_rows = []
    for src, tag in ((uniq + uniq_h3, "train"), (held + held_h3, "heldout")):
        g = totals(src, ["config", "map_id"])
        for k in sorted(g):
            n, s, c, t = g[k]
            out_rows.append({"suite": tag, "config": k[0], "map_id": k[1], "n": n,
                             "success": s, "collision": c, "timeout": t,
                             "success_rate": round(s / n, 4)})
        g2 = totals(src, ["config"])
        for k in sorted(g2):
            n, s, c, t = g2[k]
            out_rows.append({"suite": tag, "config": k[0], "map_id": "ALL", "n": n,
                             "success": s, "collision": c, "timeout": t,
                             "success_rate": round(s / n, 4)})
    dump(out_rows, TAB / "table_outcomes_icai.csv",
         ["suite", "config", "map_id", "n", "success", "collision", "timeout", "success_rate"])

    # ---- paired statistics on the corrected unique-seed suite
    um = unit_means(uniq + uniq_h3)
    pairs = []
    for a, b in (("H1", "H0"), ("H1", "H3"), ("H3", "H0")):
        for m in METRICS:
            r = paired(um, a, b, m)
            if r:
                pairs.append(r)
    dump([{k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()} for r in pairs],
         TAB / "table_paired_icai.csv",
         ["contrast", "metric", "n_pairs", "n_nonzero", "mean_diff", "cohen_dz", "wilcoxon_p"])

    # ---- wind sweep descriptive table
    w_rows = []
    g = totals(wind + wind_h3 + uniq + uniq_h3, ["config", "wind_scale"])
    for k in sorted(g, key=lambda x: (x[0], float(x[1]))):
        n, s, c, t = g[k]
        w_rows.append({"config": k[0], "wind_scale": float(k[1]), "n": n, "success": s,
                       "collision": c, "timeout": t, "success_rate": round(s / n, 4)})
    dump(w_rows, TAB / "table_wind_icai.csv",
         ["config", "wind_scale", "n", "success", "collision", "timeout", "success_rate"])

    # ---- APF sensitivity table
    s_rows = []
    g = totals(sens, ["apf_basis", "apf_d0"])
    for k in sorted(g, key=lambda x: (x[0], float(x[1]))):
        n, s, c, t = g[k]
        s_rows.append({"basis": k[0], "d0_m": float(k[1]), "n": n, "success": s,
                       "collision": c, "timeout": t, "success_rate": round(s / n, 4)})
    g = totals(sens, ["apf_basis", "apf_d0", "map_id"])
    for k in sorted(g, key=lambda x: (x[0], float(x[1]), x[2])):
        n, s, c, t = g[k]
        s_rows.append({"basis": k[0], "d0_m": float(k[1]), "map_id": k[2], "n": n,
                       "success": s, "collision": c, "timeout": t,
                       "success_rate": round(s / n, 4)})
    dump(s_rows, TAB / "table_sensitivity_icai.csv",
         ["basis", "d0_m", "map_id", "n", "success", "collision", "timeout", "success_rate"])

    # ---- action log summary
    a_rows = []
    for key in ["log_a2c_norm", "log_apf_norm", "log_lambda_mean",
                "log_cosine_mean", "log_blend_change_mean"]:
        v = [fnum(r.get(key)) for r in alog]
        v = [x for x in v if x is not None]
        if v:
            a_rows.append({"diagnostic": key, "n_episodes": len(v),
                           "mean": round(float(np.mean(v)), 4),
                           "sd": round(float(np.std(v, ddof=1)), 4) if len(v) > 1 else 0.0,
                           "min": round(float(np.min(v)), 4), "max": round(float(np.max(v)), 4)})
    dump(a_rows, TAB / "table_action_log_icai.csv",
         ["diagnostic", "n_episodes", "mean", "sd", "min", "max"])

    summary = {
        "suites": {
            "corrected_unique_seeds": len(uniq), "h3_unique_seeds": len(uniq_h3),
            "wind_sweep": len(wind), "wind_sweep_h3": len(wind_h3),
            "heldout": len(held), "heldout_h3": len(held_h3),
            "apf_sensitivity": len(sens), "action_log": len(alog),
        },
        "paired": pairs,
    }
    (ICAI / "stats_icai.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary["suites"], indent=1))
    for r in pairs:
        if r["metric"] in ("success", "jitter_index", "acceleration_index"):
            print(f"{r['contrast']:7s} {r['metric']:22s} n={r['n_pairs']:2d} "
                  f"diff={r['mean_diff']:+.4f} dz={r['cohen_dz']:+.3f} p={r['wilcoxon_p']:.5f}")


if __name__ == "__main__":
    main()
