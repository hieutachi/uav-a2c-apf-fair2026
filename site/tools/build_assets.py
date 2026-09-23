#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_assets.py — sinh toàn bộ biểu đồ (PNG) và sơ đồ (SVG) cho trang web
hệ thống hóa kiến thức paper:

  "Component Evaluation of Hybrid A2C-APF Guidance in Wind-Perturbed UAV Simulation"
  (FAIR 2026)

Nguyên tắc:
  * Mọi biểu đồ số liệu đọc trực tiếp từ các bảng ĐÃ ĐƯỢC LEDGER SINH RA ở
    reproducibility/tables/generated/*.csv — không gõ tay số vào code.
  * Hình nào là MÔ PHỎNG MINH HỌA (không phải dữ liệu thí nghiệm) đều được ghi
    chú ngay trên hình.
Chạy:  python site/tools/build_assets.py
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

# ---------------------------------------------------------------- paths ----
HERE = Path(__file__).resolve().parent            # site/tools
SITE = HERE.parent                                # site/
REPO = SITE.parent                                # repo root
TABLES = REPO / "reproducibility" / "tables" / "generated"
CHARTS = SITE / "assets" / "charts"
DIAGRAMS = SITE / "assets" / "diagrams"
CHARTS.mkdir(parents=True, exist_ok=True)
DIAGRAMS.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- style ----
C = {
    "H0": "#2e7d32",
    "H1": "#ef6c00",
    "H2": "#c62828",
    "ok": "#2e7d32",
    "warn": "#ef6c00",
    "bad": "#c62828",
    "ink": "#1b1f23",
    "muted": "#5b6672",
    "grid": "#dfe4ea",
    "accent": "#1565c0",
    "accent_soft": "#e3f0fb",
}
CTRL_COLOR = {"H0": C["H0"], "H1": C["H1"], "H2": C["H2"]}
CTRL_LABEL = {
    "H0": "H0 Hybrid (A2C+APF)",
    "H1": "H1 Chỉ A2C",
    "H2": "H2 Chỉ APF",
}
MAP_ORDER = ["map-random-01", "map-corridor-01", "map-barrier-01", "map-mixed-01"]
MAP_LABEL = {
    "map-random-01": "Random",
    "map-corridor-01": "Corridor",
    "map-barrier-01": "Barrier",
    "map-mixed-01": "Mixed",
}

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 10.5,
        "axes.edgecolor": C["grid"],
        "axes.labelcolor": C["ink"],
        "axes.titlecolor": C["ink"],
        "text.color": C["ink"],
        "xtick.color": C["muted"],
        "ytick.color": C["muted"],
        "axes.grid": True,
        "grid.color": C["grid"],
        "grid.linewidth": 0.7,
        "axes.axisbelow": True,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
    }
)


def read_csv(name: str) -> list[dict]:
    with (TABLES / name).open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def finish(fig, name: str, dpi: int = 200) -> None:
    out = CHARTS / name
    fig.savefig(out, dpi=dpi)
    plt.close(fig)
    print(f"  [chart] {name}  ({out.stat().st_size/1024:.0f} KB)")


# ============================================================== CHARTS ====
outcomes = read_csv("table_outcomes.csv")
map_out = read_csv("table_map_outcomes.csv")
cont = read_csv("table_continuous.csv")
paired = read_csv("table_paired.csv")


def chart_success_by_map() -> None:
    fig, ax = plt.subplots(figsize=(8.2, 4.1))
    width = 0.26
    x = np.arange(len(MAP_ORDER))
    for k, ctrl in enumerate(["H0", "H1", "H2"]):
        vals = []
        for m in MAP_ORDER:
            row = next(r for r in map_out if r["controller"] == ctrl and r["map"] == m)
            vals.append(float(row["success_rate"]) * 100)
        bars = ax.bar(x + (k - 1) * width, vals, width, label=CTRL_LABEL[ctrl],
                      color=CTRL_COLOR[ctrl], edgecolor="white", linewidth=0.6)
        for b, row in zip(bars, MAP_ORDER):
            r = next(rr for rr in map_out if rr["controller"] == ctrl and rr["map"] == row)
            v = b.get_height()
            if v >= 30:
                ax.text(b.get_x() + b.get_width() / 2, v - 3.5, f"{r['success']}/250",
                        ha="center", va="top", fontsize=8.4, color="white", fontweight="bold")
            else:
                ax.text(b.get_x() + b.get_width() / 2, v + 1.6, f"{r['success']}/250",
                        ha="center", va="bottom", fontsize=8.4, color=CTRL_COLOR[ctrl], fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels([MAP_LABEL[m] for m in MAP_ORDER])
    ax.set_ylabel("Tỉ lệ hoàn thành (%)")
    ax.set_ylim(0, 116)
    ax.set_title("Tỉ lệ hoàn thành theo từng map — 250 rollout mỗi ô", fontweight="bold", loc="left")
    ax.legend(frameon=False, ncol=3, fontsize=9.4, loc="upper center", bbox_to_anchor=(0.5, -0.09))
    ax.grid(axis="x", visible=False)
    finish(fig, "success_by_map.png")


def chart_outcome_stack(ctrl: str, name: str, title: str) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 3.9))
    x = np.arange(len(MAP_ORDER))
    bottom = np.zeros(len(MAP_ORDER))
    series = [("success", "Thành công", C["ok"]), ("collision", "Va chạm", C["bad"]), ("timeout", "Hết giờ", C["warn"])]
    for key, label, color in series:
        vals = np.array(
            [float(next(r for r in map_out if r["controller"] == ctrl and r["map"] == m)[key]) for m in MAP_ORDER]
        )
        ax.bar(x, vals, 0.58, bottom=bottom, label=label, color=color, edgecolor="white", linewidth=0.7)
        for xi, (v, b) in enumerate(zip(vals, bottom)):
            if v >= 12:
                ax.text(xi, b + v / 2, f"{int(v)}", ha="center", va="center", fontsize=9,
                        color="white", fontweight="bold")
        bottom += vals
    ax.set_xticks(x)
    ax.set_xticklabels([MAP_LABEL[m] for m in MAP_ORDER])
    ax.set_ylabel("Số rollout (trong 250)")
    ax.set_ylim(0, 268)
    ax.set_title(title, fontweight="bold", loc="left")
    ax.legend(frameon=False, ncol=3, fontsize=9.4, loc="upper center", bbox_to_anchor=(0.5, -0.09))
    ax.grid(axis="x", visible=False)
    finish(fig, name)


def chart_effect_sizes() -> None:
    order = ["success", "efficiency", "clearance", "steps", "acceleration", "jitter"]
    label = {
        "success": "Tỉ lệ hoàn thành",
        "efficiency": "Efficiency (n=18)",
        "clearance": "Clearance",
        "steps": "Số bước",
        "acceleration": "Acceleration",
        "jitter": "Jitter",
    }
    rows = {r["metric"]: r for r in paired}
    dz = [float(rows[m]["cohen_dz"]) for m in order]
    ps = [float(rows[m]["wilcoxon_p"]) for m in order]
    ns = [int(rows[m]["n_pairs"]) for m in order]
    colors = [C["accent"] if p < 0.05 else "#9aa5b1" for p in ps]

    fig, ax = plt.subplots(figsize=(8.4, 4.0))
    y = np.arange(len(order))
    ax.barh(y, dz, 0.6, color=colors, edgecolor="white", linewidth=0.6)
    for yi, (d, p, n) in enumerate(zip(dz, ps, ns)):
        ptxt = "p < 0.001" if p < 1e-3 else f"p = {p:.3f}"
        txt = f"d_z = {d:+.3f}   {ptxt}   n = {n}"
        if d >= 0:
            ax.text(d + 0.07, yi, txt, va="center", ha="left", fontsize=8.8,
                    color=C["ink"] if p < 0.05 else C["muted"])
        else:
            ax.text(0.14, yi, txt, va="center", ha="left", fontsize=8.8,
                    color=C["ink"] if p < 0.05 else C["muted"])
    ax.axvline(0, color=C["ink"], linewidth=0.9)
    for g, st in [(0.2, ":"), (0.5, "--"), (0.8, "-.")]:
        ax.axvline(g, color=C["grid"], linestyle=st, linewidth=0.9)
        ax.axvline(-g, color=C["grid"], linestyle=st, linewidth=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels([label[m] for m in order])
    ax.invert_yaxis()
    ax.set_xlim(-0.9, 2.8)
    ax.set_xlabel("Cohen's $d_z$ của hiệu ghép cặp (H1 − H0) trên 20 đơn vị (map × training run)")
    ax.set_title("Cỡ hiệu ứng ghép cặp — đường nét đứt là mốc |d_z| = 0.2 / 0.5 / 0.8",
                 fontweight="bold", loc="left")
    ax.grid(axis="y", visible=False)
    ax.text(0.02, -0.235, "Dương = H1 (không có kênh APF) kém thuận lợi hơn; riêng success mang dấu âm vì H1 có tỉ lệ thấp hơn.",
            transform=ax.transAxes, fontsize=8.6, color=C["muted"])
    finish(fig, "effect_sizes.png")


def chart_steps_distribution() -> None:
    fig, ax = plt.subplots(figsize=(8.0, 3.9))
    y = np.arange(3)
    for i, ctrl in enumerate(["H0", "H1", "H2"]):
        r = next(x for x in cont if x["controller"] == ctrl and x["metric"] == "steps")
        median, mean, iqr = float(r["median"]), float(r["mean"]), float(r["iqr"])
        lo, hi = median - iqr / 2, median + iqr / 2
        ax.barh(i, median, 0.5, color=CTRL_COLOR[ctrl], alpha=0.85, edgecolor="white")
        ax.plot([lo, hi], [i, i], color=C["ink"], linewidth=1.6, solid_capstyle="butt")
        ax.plot([mean], [i], marker="D", markersize=8, color="white",
                markeredgecolor=CTRL_COLOR[ctrl], markeredgewidth=2.0, zorder=5)
        ax.text(mean + 14, i, f"mean {mean:.1f}", va="center", fontsize=8.8, color=CTRL_COLOR[ctrl], fontweight="bold")
        ax.text(median + 4, i - 0.31, f"median {median:.0f} · IQR {iqr:.0f} · max {float(r['max']):.0f}",
                va="center", fontsize=8.4, color=C["muted"])
    ax.set_yticks(y)
    ax.set_yticklabels([CTRL_LABEL[c] for c in ["H0", "H1", "H2"]])
    ax.invert_yaxis()
    ax.set_xlabel("Số transition của một episode (trần chân trời H = 1507)")
    ax.set_xlim(0, 620)
    ax.set_title("Mean ≠ median: vì sao không được kết luận 'H0 bay nhanh hơn'", fontweight="bold", loc="left")
    ax.grid(axis="y", visible=False)
    ax.text(0.02, -0.30, "H1 là hỗn hợp ba chế độ (thành công ngắn / va chạm sớm / chạy tới trần 1507 bước) nên mean bị kéo lên, SD = 451.0.",
            transform=ax.transAxes, fontsize=8.6, color=C["muted"])
    finish(fig, "steps_mean_vs_median.png")


def chart_lambda_schedule() -> None:
    d = np.linspace(0, 400, 801)
    raw = 1 - d / 300.0
    lam = np.clip(raw, 0.15, 0.55)
    fig, ax = plt.subplots(figsize=(8.0, 3.9))
    ax.plot(d, raw, color="#9aa5b1", linestyle="--", linewidth=1.3, label="1 − ‖g−p‖/300 (chưa clip)")
    ax.plot(d, lam, color=C["accent"], linewidth=2.4, label=r"$\lambda_t$ thực tế = clip(·, 0.15, 0.55)")
    ax.axhspan(0.15, 0.55, color=C["accent_soft"], alpha=0.55, zorder=0)
    pts = [(335.41, "khởi đầu danh định\n335.4 m"), (255, "255 m"), (180, "180 m"), (135, "135 m"), (0, "tại đích")]
    for x0, lab in pts:
        y0 = float(np.clip(1 - x0 / 300.0, 0.15, 0.55))
        ax.plot([x0], [y0], "o", color=C["accent"], markersize=5.5, zorder=6)
        ax.annotate(f"{lab}\nλ = {y0:.2f}", (x0, y0), textcoords="offset points",
                    xytext=(6, 12 if x0 < 300 else -26), fontsize=8.4, color=C["ink"])
    ax.set_xlabel("Khoảng cách tới đích ‖g − p$_t$‖ (m)")
    ax.set_ylabel(r"Trọng số APF  $\lambda_t$")
    ax.set_xlim(0, 400)
    ax.set_ylim(0.0, 0.75)
    ax.set_title("Lịch trộn thích ứng: xa đích thì tin A2C, gần đích thì tin APF (CT-15)",
                 fontweight="bold", loc="left")
    ax.legend(frameon=False, fontsize=9, loc="lower left")
    finish(fig, "lambda_schedule.png")


def chart_wind_ar1() -> None:
    """Minh họa quá trình gió AR(1) theo CT-19..CT-22. KHÔNG phải dữ liệu thí nghiệm."""
    dt, tau, sigma, base = 0.1, 0.9, 1.2, 2.0
    phi = math.exp(-dt / tau)
    amp = sigma * math.sqrt(1 - phi ** 2)
    rng = np.random.default_rng(20260923)
    n = 400
    theta = rng.uniform(0, 2 * math.pi)
    w_base = np.array([base * math.cos(theta), base * math.sin(theta), 0.0])
    # L: corr ngang 0.35, dọc độc lập, tỉ lệ std dọc 0.3
    rho = 0.35
    L = np.array([[1.0, 0.0, 0.0], [rho, math.sqrt(1 - rho ** 2), 0.0], [0.0, 0.0, 0.3]])
    g = np.zeros((n, 3))
    for t in range(1, n):
        g[t] = phi * g[t - 1] + amp * (L @ rng.standard_normal(3))
    w = w_base + g
    t = np.arange(n) * dt

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.6, 3.6), gridspec_kw={"width_ratios": [2.05, 1]})
    for i, (lab, col) in enumerate(zip(["$w_x$", "$w_y$", "$w_z$"], [C["accent"], C["H0"], C["warn"]])):
        ax1.plot(t, w[:, i], color=col, linewidth=1.35, label=f"{lab}  (std mẫu {w[:, i].std():.2f})")
    ax1.axhline(w_base[0], color=C["accent"], linestyle=":", linewidth=1)
    ax1.set_xlabel("Thời gian mô phỏng (s)")
    ax1.set_ylabel("Vận tốc gió (m/s)")
    ax1.set_title("Một realization gió: nền 2 m/s + giật AR(1)", fontweight="bold", loc="left", fontsize=10.5)
    ax1.legend(frameon=False, fontsize=8.6, loc="upper right")

    speed = np.linalg.norm(w[:, :2], axis=1)
    ax2.hist(speed, bins=26, color=C["accent"], alpha=0.85, edgecolor="white")
    ax2.axvline(speed.mean(), color=C["bad"], linewidth=1.6,
                label=f"|w$_{{xy}}$| trung bình {speed.mean():.2f} m/s")
    ax2.set_xlabel("Tốc độ gió ngang (m/s)")
    ax2.set_ylabel("Số bước")
    ax2.set_title(f"Phân bố tốc độ gió ngang (φ = {phi:.4f})", fontweight="bold", loc="left", fontsize=10.5)
    ax2.legend(frameon=False, fontsize=8.4)
    fig.suptitle("MÔ PHỎNG MINH HỌA theo CT-19 → CT-22 (seed 20260923) — KHÔNG phải dữ liệu thí nghiệm của paper",
                 fontsize=9.2, color=C["bad"], y=1.045, fontweight="bold")
    finish(fig, "wind_ar1_illustrative.png")


def chart_seed_slots() -> None:
    bases = [1009, 1013, 1019, 1021, 1031]
    seen: dict[int, tuple[int, int]] = {}
    dup = []
    for bi, b in enumerate(bases):
        for e in range(10):
            s = b + e
            if s in seen:
                dup.append((bi, e, s, seen[s]))
            else:
                seen[s] = (bi, e)

    fig, ax = plt.subplots(figsize=(9.4, 3.9))
    ax.set_xlim(-0.6, 10.4)
    ax.set_ylim(-1.25, 5.25)
    for e in range(10):
        ax.text(e + 0.5, 4.72, f"ep {e}", ha="center", va="center", fontsize=9, color=C["muted"])
    first_of = {}
    for bi, b in enumerate(bases):
        for e in range(10):
            s = b + e
            is_dup = s in first_of
            if not is_dup:
                first_of[s] = (bi, e)
            fc = "#ffd9d3" if is_dup else C["accent_soft"]
            ec = C["bad"] if is_dup else C["accent"]
            ax.add_patch(FancyBboxPatch((e + 0.07, bi - 0.34), 0.86, 0.68,
                                        boxstyle="round,pad=0.012,rounding_size=0.07",
                                        facecolor=fc, edgecolor=ec, linewidth=1.15))
            ax.text(e + 0.5, bi, str(s), ha="center", va="center", fontsize=8.6,
                    color=C["bad"] if is_dup else C["ink"],
                    fontweight="bold" if not is_dup else "normal")
        ax.text(-0.45, bi, f"base {b}", ha="right", va="center", fontsize=9, color=C["muted"])
    ax.set_yticks([])
    ax.set_xticks([])
    ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title("numerical_seed = base_seed + episode_index  →  50 slot nhưng chỉ 32 seed phân biệt",
                 fontweight="bold", loc="left")
    ax.text(-0.45, -0.62,
            f"Ô xanh = seed lần đầu xuất hiện (32 ô)     Ô đỏ = LẶP Y HỆT (18 ô) — cùng map, cùng model, "
            f"cùng seed, policy tất định ⇒ rollout trùng khớp từng byte\n"
            f"Toàn chiến dịch: 18 × 60 đơn vị = 1080 instance trùng (validate_ledger.py). "
            f"Đây là pseudoreplication — paper vẫn báo cáo tỉ lệ trên 50 slot nhưng KHÔNG dùng rollout làm đơn vị suy luận.",
            fontsize=8.8, color=C["ink"], va="top")
    finish(fig, "seed_slots.png")


def chart_outcomes_overall() -> None:
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ctrls = ["H0", "H1", "H2"]
    x = np.arange(3)
    w = 0.55
    succ = [int(next(r for r in outcomes if r["controller"] == c)["success"]) for c in ctrls]
    coll = [int(next(r for r in outcomes if r["controller"] == c)["collision"]) for c in ctrls]
    to = [int(next(r for r in outcomes if r["controller"] == c)["timeout"]) for c in ctrls]
    ax.bar(x, succ, w, color=C["ok"], label="Thành công", edgecolor="white")
    ax.bar(x, coll, w, bottom=succ, color=C["bad"], label="Va chạm", edgecolor="white")
    ax.bar(x, to, w, bottom=np.array(succ) + np.array(coll), color=C["warn"], label="Hết giờ", edgecolor="white")
    for i, c in enumerate(ctrls):
        r = next(rr for rr in outcomes if rr["controller"] == c)
        ax.text(i, 1015, f"{r['success']}/1000", ha="center", fontsize=10.5, fontweight="bold", color=CTRL_COLOR[c])
        ax.text(i, 968, f"CI {float(r['wilson_lo']):.3f}–{float(r['wilson_hi']):.3f}", ha="center",
                fontsize=8.2, color=C["muted"])
    ax.set_xticks(x)
    ax.set_xticklabels([CTRL_LABEL[c] for c in ctrls])
    ax.set_ylim(0, 1090)
    ax.set_ylabel("Số rollout (trong 1000)")
    ax.set_title("Accounting đầy đủ: mỗi rollout đúng một trạng thái kết thúc", fontweight="bold", loc="left")
    ax.legend(frameon=False, ncol=3, fontsize=9.2, loc="upper center", bbox_to_anchor=(0.5, -0.1))
    ax.grid(axis="x", visible=False)
    finish(fig, "outcomes_overall.png")


# ============================================================ DIAGRAMS ====
FF = "Segoe UI, Roboto, Helvetica Neue, Arial, sans-serif"
MONO = "Cascadia Mono, Consolas, SFMono-Regular, Menlo, monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Svg:
    def __init__(self, w: int, h: int, title: str):
        self.w, self.h = w, h
        self.parts: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'role="img" aria-label="{esc(title)}" font-family="{FF}">',
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#5b6672"/></marker>'
            '<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#1565c0"/></marker></defs>',
            f'<rect width="{w}" height="{h}" fill="#ffffff"/>',
        ]

    def box(self, x, y, w, h, lines, fill="#ffffff", stroke="#c9d2dc", r=10,
            fs=12.5, bold_first=True, color=None, mono=False, stroke_w=1.3, align="middle"):
        color = color or C["ink"]
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" ry="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_w}"/>'
        )
        if isinstance(lines, str):
            lines = [lines]
        n = len(lines)
        lh = fs * 1.42
        y0 = y + h / 2 - (n - 1) * lh / 2
        for i, ln in enumerate(lines):
            weight = ' font-weight="600"' if (i == 0 and bold_first) else ""
            fam = f' font-family="{MONO}"' if mono else ""
            size = fs if i == 0 else fs - 1.2
            anchor = "middle" if align == "middle" else "start"
            tx = x + w / 2 if align == "middle" else x + 12
            self.parts.append(
                f'<text x="{tx}" y="{y0 + i * lh + size * 0.35:.1f}" text-anchor="{anchor}" '
                f'font-size="{size}" fill="{color}"{weight}{fam}>{esc(ln)}</text>'
            )

    def arrow(self, x1, y1, x2, y2, label=None, color="#5b6672", dashed=False, fs=10.5,
              marker="ah", lx=None, ly=None, lcolor=None):
        dash = ' stroke-dasharray="5,4"' if dashed else ""
        self.parts.append(
            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5"{dash} '
            f'marker-end="url(#{marker})"/>'
        )
        if label:
            tx = (lx if lx is not None else (x1 + x2) / 2)
            ty = (ly if ly is not None else (y1 + y2) / 2 - 6)
            self.parts.append(
                f'<text x="{tx}" y="{ty}" text-anchor="middle" font-size="{fs}" '
                f'fill="{lcolor or C["muted"]}">{esc(label)}</text>'
            )

    def text(self, x, y, s, fs=12, color=None, weight=None, anchor="start", mono=False):
        wattr = f' font-weight="{weight}"' if weight else ""
        fam = f' font-family="{MONO}"' if mono else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{fs}" '
            f'fill="{color or C["ink"]}"{wattr}{fam}>{esc(s)}</text>'
        )

    def save(self, name: str) -> None:
        self.parts.append("</svg>")
        out = DIAGRAMS / name
        out.write_text("\n".join(self.parts), encoding="utf-8")
        print(f"  [diagram] {name}  ({out.stat().st_size/1024:.0f} KB)")


def diagram_hierarchy() -> None:
    s = Svg(980, 560, "Hệ thống phân cấp thực nghiệm")
    s.text(24, 34, "Cấu trúc lồng nhau của một cấu hình — và số học của mẫu", fs=17, weight="600")
    s.text(24, 56, "Mỗi tầng là một đơn vị lấy mẫu khác nhau; tầng (map × training run) là ĐƠN VỊ SUY LUẬN.",
           fs=11.5, color=C["muted"])

    s.box(330, 78, 320, 46, ["Configuration", "H0 hybrid · H1 chỉ A2C · H2 chỉ APF"], fill="#eef4fb", stroke=C["accent"])
    s.arrow(490, 124, 490, 152)
    s.box(300, 154, 380, 46, ["Map — 4 layout 300 m (density 0.8)", "random-01 · corridor-01 · barrier-01 · mixed-01"],
          fill="#f5f9f5", stroke=C["H0"])
    s.arrow(490, 200, 490, 228)
    s.box(280, 230, 420, 52, ["Training run / model — 5 model độc lập mỗi map",
                             "seed 101 · 211 · 307 · 401 · 503   (5M bước mỗi model)"],
          fill="#fff8ef", stroke=C["H1"])
    s.arrow(490, 282, 490, 310)
    s.box(262, 312, 456, 52, ["Evaluation seed slot — 50 slot mỗi unit",
                              "base {1009,1013,1019,1021,1031} × episode 0..9"],
          fill="#fdf3f3", stroke=C["H2"])
    s.arrow(490, 364, 490, 392)
    s.box(300, 394, 380, 44, ["Rollout — 1 episode tất định", "success / collision / timeout"],
          fill="#f7f7f9", stroke="#8b95a1")

    # bên phải: số đếm
    s.box(730, 154, 226, 46, ["× 4", "4 map"], fill="#ffffff", stroke=C["grid"], color=C["muted"])
    s.box(730, 236, 226, 46, ["× 5 = 20 unit", "đơn vị suy luận"], fill="#ffffff", stroke=C["grid"], color=C["muted"])
    s.box(730, 318, 226, 46, ["× 50 = 1000", "rollout / cấu hình"], fill="#ffffff", stroke=C["grid"], color=C["muted"])
    s.box(730, 400, 226, 38, ["3 × 1000 = 3000", "H4 tái dùng quỹ đạo H0"], fill="#ffffff", stroke=C["grid"], color=C["muted"])

    # bên trái: ghi chú
    s.box(24, 154, 250, 46, ["Mỗi map có map_sha256", "H0 và H1 dùng chung map"], fill="#ffffff", stroke=C["grid"], fs=11)
    s.box(24, 236, 250, 46, ["H2: 5 nhãn seed chỉ là", "bookkeeping — không học"], fill="#fff5f5", stroke=C["bad"], fs=11)
    s.box(24, 318, 250, 46, ["50 slot → chỉ 32 seed thật", "18 slot lặp y hệt"], fill="#fff5f5", stroke=C["bad"], fs=11)
    s.box(24, 400, 250, 38, ["Policy deterministic", "→ rollout lặp lại giống hệt"], fill="#ffffff", stroke=C["grid"], fs=11)

    s.box(24, 470, 932, 66,
          ["Đọc sơ đồ này thế nào: ghép cặp H0–H1 được thực hiện ở TẦNG 3 (map × training run), không phải ở tầng rollout.",
           "Vì vậy n của kiểm định Wilcoxon là 20 (18 với efficiency), còn 1000 rollout chỉ dùng để MÔ TẢ (Wilson CI)."],
          fill="#eef4fb", stroke=C["accent"], fs=11.8, bold_first=False)
    s.save("hierarchy.svg")


def diagram_episode_flow() -> None:
    s = Svg(980, 470, "Luồng kết thúc một episode")
    s.text(24, 34, "Một transition của episode: từ lệnh điều khiển tới trạng thái kết thúc", fs=17, weight="600")
    s.text(24, 56, "Collision được xét TRƯỚC success; mỗi episode nhận đúng một nhãn.", fs=11.5, color=C["muted"])

    s.box(24, 92, 150, 62, ["Bước t", "state sₜ = [p,v,g−p,w]"], fill="#eef4fb", stroke=C["accent"], fs=11.5)
    s.arrow(174, 123, 214, 123)
    s.box(216, 92, 176, 62, ["A2C policy", "aₜᴬ²ᶜ ∈ [−1,1]³"], fill="#ffffff", stroke="#8b95a1", fs=11.5)
    s.arrow(392, 123, 432, 123)
    s.box(434, 92, 176, 62, ["APF (chỉ H0/H2)", "aₜᴬᴾᶠ từ tâm AABB"], fill="#ffffff", stroke="#8b95a1", fs=11.5)
    s.arrow(610, 123, 650, 123)
    s.box(652, 92, 150, 62, ["Blend λₜ", "uₜ (CT-14)"], fill="#fff8ef", stroke=C["H1"], fs=11.5)
    s.arrow(802, 123, 842, 123)
    s.box(844, 92, 112, 62, ["Dynamics", "CT-3…CT-7"], fill="#f5f9f5", stroke=C["H0"], fs=11.5)

    s.arrow(900, 154, 900, 190)
    s.box(700, 192, 256, 40, ["pₜ₊₁ sau tích phân + clamp độ cao"], fill="#ffffff", stroke="#8b95a1", fs=11.5)
    s.arrow(700, 212, 640, 212)

    # decision 1
    s.box(430, 186, 208, 52, ["swept AABB pₜ → pₜ₊₁ ?", "va chạm vật cản?"], fill="#fff5f5", stroke=C["bad"], fs=11.5)
    s.arrow(534, 238, 534, 274, label="có", color=C["bad"], lcolor=C["bad"])
    s.box(430, 276, 208, 46, ["COLLISION", "reward −200, episode dừng"], fill=C["bad"], stroke=C["bad"], color="#ffffff", fs=11.5)

    s.arrow(430, 212, 300, 212, label="không", lx=365, ly=203)
    s.box(120, 186, 178, 52, ["‖g − pₜ₊₁‖ < 3 m ?", "đã tới đích?"], fill="#f5f9f5", stroke=C["H0"], fs=11.5)
    s.arrow(209, 238, 209, 274, label="có", color=C["H0"], lcolor=C["H0"])
    s.box(105, 276, 208, 46, ["SUCCESS", "thưởng Bₜ = max(80, 150(1−n/H))"], fill=C["H0"], stroke=C["H0"], color="#ffffff", fs=11.5)

    s.arrow(120, 212, 60, 212)
    s.box(24, 186, 36, 52, ["t = H ?", "H = 1507"], fill="#fff8ef", stroke=C["warn"], fs=10)
    s.arrow(42, 238, 42, 350, label="có", color=C["warn"], lcolor=C["warn"], lx=58, ly=300)
    s.box(24, 352, 208, 44, ["TIMEOUT", "không thưởng, không −200"], fill=C["warn"], stroke=C["warn"], color="#ffffff", fs=11.5)

    s.arrow(209, 186, 209, 150, label="không → bước t+1", lx=250, ly=168)
    s.box(240, 92, 0, 0, [""], fill="#ffffff", stroke="#ffffff")  # spacer no-op

    s.box(300, 352, 656, 92,
          ["Vì sao thứ tự này quan trọng:",
           "• Nếu UAV chạm vật cản đúng lúc vào trong 3 m → nhãn là COLLISION, không phải SUCCESS (collision có ưu tiên).",
           "• Tổng ba nhãn luôn bằng 1000 cho mỗi cấu hình: 1000+0+0 · 830+58+112 · 55+905+40 — gate test kiểm tra tự động.",
           "• Bán kính phồng UAV = 0 và phép thử slab trên cả đoạn giúp chống 'xuyên hầm' vật cản mỏng."],
          fill="#f7f9fb", stroke=C["grid"], fs=11.5, bold_first=True, align="start")
    s.save("episode_flow.svg")


def diagram_pairing() -> None:
    s = Svg(980, 430, "Ghép cặp H0 và H1")
    s.text(24, 34, "Ghép cặp H0 – H1: cái gì khớp và cái gì không", fs=17, weight="600")
    s.text(24, 56, "Hai hàng cuối là lý do paper không thể tuyên bố 'APF tốt hơn học thuần túy'.", fs=11.5, color=C["muted"])

    s.box(60, 86, 340, 44, ["H0 — Hybrid", "A2C + APF blend (λₜ ∈ [0.15, 0.55])"], fill="#f5f9f5", stroke=C["H0"])
    s.box(580, 86, 340, 44, ["H1 — Chỉ A2C", "policy_mode = 'a2c', apf_weight = 0"], fill="#fff8ef", stroke=C["H1"])
    s.text(490, 113, "ghép cặp", fs=11.5, color=C["muted"], anchor="middle")
    s.arrow(400, 108, 580, 108, dashed=True)

    rows = [
        ("Map (hình học vật cản)", "KHỚP", "cùng map_sha256", True),
        ("Nhãn training seed", "KHỚP", "101 · 211 · 307 · 401 · 503", True),
        ("Ngân sách huấn luyện", "KHỚP", "5.000.000 bước / unit", True),
        ("Realization reset + gió AR(1)", "KHỚP", "cùng numerical_seed → env.reset(seed=…)", True),
        ("Số rollout mỗi unit", "KHỚP", "50 slot (32 seed phân biệt)", True),
        ("Trọng số policy đã học", "KHÔNG", "hai model khác nhau — đây là đối tượng so sánh", False),
        ("Thông tin vật cản đầu vào", "KHÔNG", "H0 có qua APF · H1 không có → BẤT ĐỐI XỨNG", False),
    ]
    y = 152
    for lab, verdict, note, ok in rows:
        fill = "#f5f9f5" if ok else "#fff5f5"
        stroke = C["H0"] if ok else C["bad"]
        s.box(60, y, 300, 34, [lab], fill="#ffffff", stroke=C["grid"], fs=11.8, align="start")
        s.box(372, y, 96, 34, [verdict], fill=fill, stroke=stroke, fs=11.5,
              color=stroke, bold_first=True)
        s.box(480, y, 440, 34, [note], fill="#ffffff", stroke=C["grid"], fs=11, color=C["muted"], align="start")
        y += 38

    s.box(60, y + 6, 860, 52,
          ["Hệ quả diễn giải: H0 − H1 đo giá trị của CẢ kênh APF cùng với đầu vào hình học đặc quyền của nó.",
           "Muốn cô lập 'phép tính trường thế năng', cần một H1b nhận đặc trưng vật cản tương đương mà không có blend APF."],
          fill="#fff5f5", stroke=C["bad"], fs=11.8, bold_first=False)
    s.save("pairing.svg")


def diagram_repro_pipeline() -> None:
    s = Svg(980, 470, "Pipeline tái lập kết quả")
    s.text(24, 34, "Pipeline tái lập: từ ledger tới từng con số trong paper", fs=17, weight="600")
    s.text(24, 56, "Chạy `make analysis` — dưới 30 giây, không cần GPU, độc lập máy. Mọi số đều tái sinh, không copy.",
           fs=11.5, color=C["muted"])

    steps = [
        ("episode_audit.csv", "904 KB · 3000 rollout\nmỗi dòng đúng 1 nhãn", "#eef4fb", C["accent"]),
        ("rollout_ledger.csv", "SHA-256 đã khóa\nfa133470…e9d1f6ec", "#eef4fb", C["accent"]),
        ("01_build_unit_summaries", "20 đơn vị (map × run)\ncho mỗi controller", "#f5f9f5", C["H0"]),
        ("02_compute_statistics", "Wilson · Wilcoxon\nd_z · Hodges–Lehmann", "#f5f9f5", C["H0"]),
        ("03_reconcile_claims", "69 claim ↔ paper\n29 exact · 40 rounding", "#fff8ef", C["H1"]),
        ("04_tables_and_figures", "5 bảng + biểu đồ\nsinh từ ledger", "#fff8ef", C["H1"]),
    ]
    x = 24
    for i, (title, sub, fill, stroke) in enumerate(steps):
        s.box(x, 90, 148, 78, [title] + sub.split("\n"), fill=fill, stroke=stroke, fs=11.2)
        if i < len(steps) - 1:
            s.arrow(x + 148, 129, x + 168, 129)
        x += 168

    gates = [
        ("Gate 1 — checksum", "182/182 artifact thô xác thực bằng SHA-256; 65 file trong gói release.", C["H0"]),
        ("Gate 2 — accounting", "Mỗi dòng đúng một nhãn kết thúc; mỗi controller 1000 rollout; mỗi ô controller×map = 250.", C["H0"]),
        ("Gate 3 — pairing", "H0 và H1 chia sẻ đúng 20 cặp (map, training-run) — assert trên tập khóa, không phải trùng nhãn.", C["accent"]),
        ("Gate 4 — đối soát", "0 MISMATCH · 0 UNREPRODUCIBLE trên 69 claim; 25/25 test unit + gate PASS.", C["H1"]),
    ]
    y = 206
    for t, d, col in gates:
        s.box(24, y, 190, 46, [t], fill="#ffffff", stroke=col, fs=12)
        s.box(226, y, 694, 46, [d], fill="#ffffff", stroke=C["grid"], fs=11.4, color=C["muted"], align="start")
        y += 52

    s.box(24, y + 4, 896, 74,
          ["Quyết định release: CONDITIONAL PASS",
           "Điều kiện (a) 40 checkpoint + 4000 file .npz không phân phối trong gói (chỉ cần cho đánh giá lại / vẽ hình minh họa, KHÔNG cần để tái sinh số liệu);",
           "Điều kiện (b) huấn luyện lại từ đầu không tái lập bitwise vì PyTorch không được seed tường minh. Cả hai không ảnh hưởng bất kỳ con số nào đã báo cáo."],
          fill="#fff8ef", stroke=C["H1"], fs=11.6)
    s.save("repro_pipeline.svg")


def diagram_research_loop() -> None:
    s = Svg(980, 300, "Vòng nghiên cứu của paper")
    s.text(24, 34, "Vòng nghiên cứu: paper này là một 'component evaluation', không phải một 'system paper'", fs=17, weight="600")

    steps = [
        ("1. Câu hỏi hẹp", "Kênh APF thêm được gì\nvào một A2C cố định?"),
        ("2. Đặc tả implementation", "obs 12-D · lực 12 N/trục\nAPF theo tâm · λ theo khoảng cách"),
        ("3. Thiết kế đối chứng", "H0 vs H1 (khớp ngân sách)\nH2 tham chiếu · H4 chẩn đoán"),
        ("4. Đo + audit", "3000 rollout · ledger\n69 claim đối soát"),
        ("5. Phạm vi tuyên bố", "Chỉ nói những gì dữ liệu\nủng hộ; khai báo asymmetry"),
    ]
    x = 24
    for i, (t, sub) in enumerate(steps):
        s.box(x, 74, 176, 84, [t] + sub.split("\n"), fill="#eef4fb" if i in (0, 4) else "#ffffff",
              stroke=C["accent"] if i in (0, 4) else C["grid"], fs=12)
        if i < 4:
            s.arrow(x + 176, 116, x + 194, 116)
        x += 194

    s.box(24, 190, 932, 76,
          ["Vì sao vòng này đáng học: bước 5 không phóng đại kết quả của bước 4.",
           "Ba chỉ số có bằng chứng (success p = 0.027 · acceleration p = 0.006 · jitter p < 0.001) được tách bạch với ba chỉ số KHÔNG được ủng hộ",
           "(efficiency p = 0.417 · clearance p = 0.956 · steps p = 0.123) — và cả sáu đều là p-value khám phá, chưa hiệu chỉnh đa bội."],
          fill="#f5f9f5", stroke=C["H0"], fs=11.8)
    s.save("research_loop.svg")


# ------------------------------------------------------------------ run ----
if __name__ == "__main__":
    print("Charts (từ reproducibility/tables/generated/*.csv):")
    chart_outcomes_overall()
    chart_success_by_map()
    chart_outcome_stack("H1", "h1_outcome_stack.png", "H1 (chỉ A2C): thành phần kết cục theo map — cùng một tỉ lệ, hai cơ chế khác nhau")
    chart_outcome_stack("H2", "h2_outcome_stack.png", "H2 (chỉ APF): thành phần kết cục theo map — thất bại chủ yếu là va chạm")
    chart_effect_sizes()
    chart_steps_distribution()
    chart_lambda_schedule()
    chart_wind_ar1()
    chart_seed_slots()
    print("Diagrams (SVG tự sinh):")
    diagram_hierarchy()
    diagram_episode_flow()
    diagram_pairing()
    diagram_repro_pipeline()
    diagram_research_loop()
    print("Xong. Charts:", len(list(CHARTS.glob("*.png"))), " Diagrams:", len(list(DIAGRAMS.glob("*.svg"))))
