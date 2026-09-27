#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publication figures for the ICAI-FAI 2026 revision.

Reads only results/icai2026/**/*.csv (machine-readable outputs of the frozen
protocol) and writes paper/icai2026/figures/*.png. Re-run after H3 finishes:
the wind-sweep panel picks up H3 automatically if its CSV exists.
"""
from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ICAI = ROOT / "results" / "icai2026"
FIG = ROOT / "paper" / "icai2026" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

C = {"H0": "#2e7d32", "H1": "#ef6c00", "H2": "#c62828", "H3": "#1565c0"}
LBL = {"H0": "H0 hybrid", "H1": "H1 A2C-only", "H2": "H2 APF-only", "H3": "H3 A2C-Geo"}
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5, "axes.edgecolor": "#dfe4ea",
    "axes.grid": True, "grid.color": "#dfe4ea", "grid.linewidth": .7,
    "axes.axisbelow": True, "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight",
})


def load(rel):
    p = ICAI / rel
    if not p.exists():
        return []
    return list(csv.DictReader(p.open(encoding="utf-8")))


def group(rows, keys):
    g = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        k = tuple(r[k] for k in keys)
        g[k][0] += 1
        g[k][1] += int(r["success"])
        g[k][2] += int(r["collision"])
        g[k][3] += int(r["timeout"])
    return g


def save(fig, name):
    fig.savefig(FIG / name, dpi=300)
    plt.close(fig)
    print("  [fig]", name)


# ------------------------------------------------------- fig 1: wind sweep --
rows = load("icai_wind_sweep/icai_wind_sweep_H0_H1.csv") + \
       load("icai_eval_unique/icai_eval_unique_H0_H1.csv") + \
       load("icai_eval_unique_h3/icai_eval_unique_h3_H3.csv")
g = group(rows, ["config", "wind_scale"])
scales = sorted({float(k[1]) for k in g})
fig, ax = plt.subplots(figsize=(7.4, 4.0))
for cfg in ("H0", "H1", "H3"):
    xs, ys = [], []
    for s in scales:
        if (cfg, f"{s:.1f}") in g or (cfg, s) in g:
            key = (cfg, s) if (cfg, s) in g else (cfg, f"{s:.1f}")
            n, succ, _, _ = g[key]
            xs.append(s); ys.append(100.0 * succ / n)
    if xs:
        ax.plot(xs, ys, marker="o", linewidth=2.2, color=C[cfg], label=LBL[cfg])
        for x, y in zip(xs, ys):
            ax.annotate(f"{y:.1f}", (x, y), textcoords="offset points",
                        xytext=(0, 8), ha="center", fontsize=8.4, color=C[cfg])
ax.set_xlabel("wind_scale (1.0 = cường độ gió của bản FAIR)")
ax.set_ylabel("Tỉ lệ hoàn thành (%)")
ax.set_ylim(0, 108)
ax.set_title("Stress test gió trên policy đông cứng: H0 suy giảm mượt từ 1.5x", fontweight="bold", loc="left")
ax.legend(frameon=False, fontsize=9.5)
save(fig, "fig_wind_sweep.png")

# ------------------------------------------------- fig 2: APF sensitivity ---
rows = load("icai_apf_sensitivity/apf_sensitivity.csv")
g = group(rows, ["apf_basis", "apf_d0"])
combos = sorted(g, key=lambda k: (k[0], float(k[1])))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.8, 3.9), width_ratios=[1.15, 1])
labels = [f"{'c' if b == 'center' else 's'}{float(d):.0f}" for b, d in combos]
sr = [100.0 * g[k][1] / g[k][0] for k in combos]
cols = [C["H2"] if k[0] == "center" else C["H3"] for k in combos]
a1.bar(range(len(combos)), sr, color=cols, edgecolor="white")
for i, v in enumerate(sr):
    a1.text(i, v + 1.2, f"{v:.1f}", ha="center", fontsize=8.6, fontweight="bold")
a1.set_xticks(range(len(combos)))
a1.set_xticklabels(labels, fontsize=9)
a1.set_xlabel("c = khoảng cách tâm, s = khoảng cách bề mặt; số sau là d0 (m)", fontsize=9)
a1.set_ylabel("Tỉ lệ hoàn thành (%)")
a1.set_ylim(0, 55)
a1.set_title("APF-only: surface gấp ~4 lần center", fontweight="bold", loc="left", fontsize=10.5)
x = np.arange(len(combos))
a2.bar(x, [g[k][2] for k in combos], 0.62, label="Va chạm", color=C["H2"], edgecolor="white")
a2.bar(x, [g[k][3] for k in combos], 0.62, bottom=[g[k][2] for k in combos],
       label="Hết giờ", color="#ef6c00", edgecolor="white")
a2.set_xticks(x)
a2.set_xticklabels(labels, fontsize=9)
a2.set_xlabel("c = khoảng cách tâm, s = khoảng cách bề mặt; số sau là d0 (m)", fontsize=9)
a2.set_ylabel("Số episode (trong 200)")
a2.set_title("Surface xóa va chạm nhưng còn trì trệ", fontweight="bold", loc="left", fontsize=10.5)
a2.legend(frameon=False, fontsize=9)
save(fig, "fig_apf_sensitivity.png")

# ------------------------------------------------------ fig 3: held-out -----
rows = load("icai_heldout/icai_heldout_H0_H1.csv")
g = group(rows, ["config", "map_id"])
maps = sorted({k[1] for k in g})
fig, ax = plt.subplots(figsize=(7.6, 4.0))
x = np.arange(len(maps))
for i, cfg in enumerate(("H0", "H1")):
    vals = [100.0 * g[(cfg, m)][1] / g[(cfg, m)][0] for m in maps]
    b = ax.bar(x + (i - 0.5) * 0.36, vals, 0.36, color=C[cfg], label=LBL[cfg], edgecolor="white")
    for rect, m in zip(b, maps):
        n, s, c, _ = g[(cfg, m)]
        ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 2,
                f"{s}/{n}", ha="center", fontsize=8.2, color=C[cfg], fontweight="bold")
ax.set_xticks(x)
ax.set_xticklabels([m.replace("map-", "").replace("-ho1", "") for m in maps])
ax.set_ylabel("Tỉ lệ hoàn thành (%)")
ax.set_ylim(0, 118)
ax.set_title("Map held-out: chuyển giao giữ được ở 3/4 họ layout, sụp ở mixed-ho1",
             fontweight="bold", loc="left")
ax.legend(frameon=False, fontsize=9.5)
ax.grid(axis="x", visible=False)
save(fig, "fig_heldout.png")

# ---------------------------------------- fig 4: corrected-seed comparison --
rows = load("icai_eval_unique/icai_eval_unique_H0_H1.csv")
g = group(rows, ["config", "map_id"])
fair = {"H0": [250, 250, 250, 250], "H1": [140, 240, 200, 250]}
maps = ["map-random-01", "map-corridor-01", "map-barrier-01", "map-mixed-01"]
fig, ax = plt.subplots(figsize=(7.8, 4.0))
x = np.arange(len(maps))
w = 0.2
new_h1 = [g[("H1", m)][1] for m in maps]
ax.bar(x - 1.5 * w, [250] * 4, w, color=C["H0"], label="H0 (cả hai lịch seed)")
ax.bar(x - 0.5 * w, fair["H1"], w, color="#f3c08b", label="H1 lịch seed FAIR (32 seed)")
ax.bar(x + 0.5 * w, new_h1, w, color=C["H1"], label="H1 lịch seed sửa (50 seed duy nhất)")
for i, m in enumerate(maps):
    ax.text(i + 0.5 * w, new_h1[i] + 4, f"{new_h1[i]}", ha="center", fontsize=8.6,
            color=C["H1"], fontweight="bold")
    ax.text(i - 0.5 * w, fair["H1"][i] + 4, f"{fair['H1'][i]}", ha="center", fontsize=8.6, color="#b45309")
ax.set_xticks(x)
ax.set_xticklabels([m.replace("map-", "") for m in maps])
ax.set_ylabel("Số episode thành công (trong 250)")
ax.set_ylim(0, 285)
ax.set_title("Lịch seed sửa đổi làm H1 tốt hơn một chút (848 vs 830) nhưng kết luận không đổi",
             fontweight="bold", loc="left", fontsize=10.5)
ax.legend(frameon=False, fontsize=9)
ax.grid(axis="x", visible=False)
save(fig, "fig_corrected_seeds.png")

print("Xong. Figures:", sorted(p.name for p in FIG.glob("*.png")))

# --------------------------------------- fig 5: disentanglement contrasts --
import json as _json
sp = ICAI / "stats_icai.json"
if sp.exists():
    pairs = _json.loads(sp.read_text(encoding="utf-8"))["paired"]
    metrics = ["success", "jitter_index", "acceleration_index"]
    contrasts = ["H3-H1", "H0-H3", "H0-H1"]
    fig, axes = plt.subplots(1, 3, figsize=(10.6, 3.6), sharey=False)
    for ax, m in zip(axes, metrics):
        vals, errs, labs, cols = [], [], [], []
        for c in contrasts:
            r = next((x for x in pairs if x["contrast"] == c and x["metric"] == m), None)
            if not r:
                continue
            vals.append(r["mean_diff"]); errs.append(r["cohen_dz"]); labs.append(c)
            cols.append("#9aa5b1" if (r["wilcoxon_p"] or 1) >= 0.05 else C["H3"])
        ax.bar(range(len(vals)), vals, 0.6, color=cols, edgecolor="white")
        for i, (v, dz, lb) in enumerate(zip(vals, errs, labs)):
            ax.text(i, v + (0.004 if m == "success" else abs(v) * 0.04),
                    f"{v:+.3f} (d_z {dz:+.2f})", ha="center", fontsize=8.0)
        ax.axhline(0, color="#1b2430", linewidth=0.9)
        ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs, fontsize=9)
        title = {"success": "Tỉ lệ hoàn thành", "jitter_index": "Jitter (m/s³)",
                 "acceleration_index": "Accel (m/s²)"}[m]
        ax.set_title(f"Hiệu ghép cặp — {title}", fontweight="bold", loc="left", fontsize=10.5)
        ax.grid(axis="x", visible=False)
    fig.suptitle("Xám = không đáng kể (p ≥ 0.05), xanh = đáng kể. Độ tin cậy gắn với thông tin vật cản; "
                 "độ mượt gắn với kênh giải tích.", fontsize=9.6, y=1.06)
    save(fig, "fig_disentanglement.png")
