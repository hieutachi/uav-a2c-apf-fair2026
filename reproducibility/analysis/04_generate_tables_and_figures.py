"""Generate manuscript tables (and optional figures) from the frozen ledger / derived summaries.

Tables are always written (CSV + LaTeX). Figures are written only if matplotlib is available.
"""
from __future__ import annotations

import csv
from pathlib import Path

REPRO = Path(__file__).resolve().parents[1]
DERIVED = REPRO / "data" / "derived"
TABLES = REPRO / "tables" / "generated"
FIGS = REPRO / "figures" / "generated"


def load(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def write_outcomes():
    rows = load(DERIVED / "controller_summary.csv")
    seen = {}
    for r in rows:
        c = r["controller_id"]
        if c not in seen:
            seen[c] = r  # first metric row carries the counts
    out = TABLES / "table_outcomes.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["controller", "n", "success", "collision", "timeout",
                    "success_rate", "wilson_lo", "wilson_hi"])
        for c, r in seen.items():
            w.writerow([c, r["n_rollouts"], r["success"], r["collision"], r["timeout"],
                        f'{float(r["success_rate"]):.4f}', f'{float(r["wilson_lo"]):.4f}',
                        f'{float(r["wilson_hi"]):.4f}'])
    with open(TABLES / "table_outcomes.tex", "w", encoding="utf-8") as f:
        f.write("% auto-generated from data/raw/rollout_ledger.csv\n")
        f.write("\\begin{tabular}{lrrrrr}\n\\toprule\n")
        f.write("Controller & Success & Collision & Timeout & Rate & 95\\% CI \\\\\n\\midrule\n")
        for c, r in seen.items():
            f.write(f"{c} & {r['success']} & {r['collision']} & {r['timeout']} & "
                    f"{float(r['success_rate']):.3f} & [{float(r['wilson_lo']):.3f}, {float(r['wilson_hi']):.3f}] \\\\\n")
        f.write("\\bottomrule\n\\end{tabular}\n")


def write_continuous():
    rows = load(DERIVED / "controller_summary.csv")
    out = TABLES / "table_continuous.csv"
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["controller", "metric", "n", "mean", "sd", "median", "iqr", "min", "max", "conditioning"])
        for r in rows:
            w.writerow([r["controller_id"], r["metric"], r["metric_n"],
                        f'{float(r["mean"]):.4f}', f'{float(r["sd"]):.4f}',
                        f'{float(r["median"]):.4f}', f'{float(r["iqr"]):.4f}',
                        r["min"], r["max"], r["conditioning"]])


def write_map_outcomes():
    rows = load(DERIVED / "map_controller_summary.csv")
    with open(TABLES / "table_map_outcomes.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["controller", "map", "n", "success", "collision", "timeout", "success_rate"])
        for r in rows:
            w.writerow([r["controller_id"], r["map_id"], r["n"], r["success"], r["collision"],
                        r["timeout"], f'{float(r["success_rate"]):.4f}'])


def write_paired():
    rows = load(DERIVED / "statistical_results.csv")
    with open(TABLES / "table_paired.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "n_pairs", "mean_diff_H1_minus_H0", "cohen_dz",
                    "wilcoxon_p", "rank_biserial_r", "hodges_lehmann_median_diff"])
        for r in rows:
            w.writerow([r["metric"], r["n_pairs"], f'{float(r["mean_diff_H1_minus_H0"]):.4f}',
                        f'{float(r["cohen_dz"]):.4f}', f'{float(r["wilcoxon_p"]):.6g}',
                        f'{float(r["rank_biserial_r"]):.4f}', f'{float(r["hodges_lehmann_median_diff"]):.4f}'])


def maybe_figures():
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as e:
        print(f"[04] matplotlib unavailable, skipping figures ({e})")
        return
    rows = load(DERIVED / "map_controller_summary.csv")
    controllers = ["H0", "H1", "H2"]
    maps = sorted({r["map_id"] for r in rows})
    import numpy as np
    data = np.zeros((len(controllers), len(maps)))
    for r in rows:
        if r["controller_id"] in controllers:
            data[controllers.index(r["controller_id"]), maps.index(r["map_id"])] = float(r["success_rate"])
    fig, ax = plt.subplots(figsize=(6, 3))
    im = ax.imshow(data, vmin=0, vmax=1, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(maps))); ax.set_xticklabels([m.replace("map-", "").replace("-01", "") for m in maps], rotation=30)
    ax.set_yticks(range(len(controllers))); ax.set_yticklabels(controllers)
    for i in range(len(controllers)):
        for j in range(len(maps)):
            ax.text(j, i, f"{data[i, j]*100:.0f}%", ha="center", va="center", color="w", fontsize=8)
    ax.set_title("Success rate by controller x map (from ledger)")
    fig.colorbar(im, ax=ax, label="success rate")
    fig.tight_layout()
    FIGS.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGS / "reliability_by_map.png", dpi=150)
    print(f"[04] wrote {FIGS / 'reliability_by_map.png'}")


def main() -> int:
    TABLES.mkdir(parents=True, exist_ok=True)
    write_outcomes(); write_continuous(); write_map_outcomes(); write_paired()
    print(f"[04] wrote tables to {TABLES}")
    maybe_figures()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
