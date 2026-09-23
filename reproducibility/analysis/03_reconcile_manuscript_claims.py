"""Reconcile every manuscript numeric claim against values recomputed from the ledger.

Inputs:
    data/raw/manuscript_claims.csv
    data/derived/controller_summary.csv
    data/derived/map_controller_summary.csv
    data/derived/statistical_results.csv
    data/raw/rollout_ledger.csv (for seed count)

Outputs:
    reports/reconciliation.csv
    reports/result_reconciliation.md
"""
from __future__ import annotations

import csv
from pathlib import Path

REPRO = Path(__file__).resolve().parents[1]
DERIVED = REPRO / "data" / "derived"
RAW = REPRO / "data" / "raw"
REPORTS = REPRO / "reports"


def load(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def build_lookup():
    lut = {}
    # controller_summary: counts + continuous metric stats
    for r in load(DERIVED / "controller_summary.csv"):
        c = r["controller_id"]
        lut[f"count::{c}::success"] = float(r["success"])
        lut[f"count::{c}::collision"] = float(r["collision"])
        lut[f"count::{c}::timeout"] = float(r["timeout"])
        m = r["metric"]
        lut[f"cont::{c}::{m}::mean"] = float(r["mean"])
        lut[f"cont::{c}::{m}::sd"] = float(r["sd"])
    for r in load(DERIVED / "map_controller_summary.csv"):
        lut[f"mapcount::{r['controller_id']}::{r['map_id']}::success"] = float(r["success"])
    for r in load(DERIVED / "statistical_results.csv"):
        m = r["metric"]
        lut[f"paired::{m}::mean_diff"] = float(r["mean_diff_H1_minus_H0"])
        lut[f"paired::{m}::dz"] = float(r["cohen_dz"])
        lut[f"paired::{m}::wilcoxon_p"] = float(r["wilcoxon_p"])
        lut[f"paired::{m}::n"] = float(r["n_pairs"])
    # unique effective numerical seeds
    led = load(RAW / "rollout_ledger.csv")
    uniq = len({int(r["numerical_episode_seed"]) for r in led})
    lut["seeds::unique_effective"] = float(uniq)
    return lut


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    lut = build_lookup()
    claims = load(RAW / "manuscript_claims.csv")

    out = []
    counts = {"EXACT_MATCH": 0, "ROUNDING_MATCH": 0, "SUPPORTED_WITH_REWORDING": 0,
              "MISMATCH": 0, "UNREPRODUCIBLE": 0, "NOT_APPLICABLE": 0}
    for c in claims:
        key = c["recompute_key"]
        reported = float(c["reported_value"])
        tol = float(c["tolerance"])
        if key not in lut:
            status = "UNREPRODUCIBLE"
            recomputed = ""
            explanation = "no recompute path found for key"
        else:
            recomputed = lut[key]
            delta = abs(recomputed - reported)
            if delta == 0:
                status = "EXACT_MATCH"
                explanation = "identical"
            elif delta <= tol:
                status = "ROUNDING_MATCH"
                explanation = f"within tolerance {tol} (|delta|={delta:.6g})"
            else:
                status = "MISMATCH"
                explanation = f"exceeds tolerance {tol} (|delta|={delta:.6g})"
        counts[status] += 1
        out.append({
            "claim_id": c["claim_id"], "manuscript_location": c["manuscript_location"],
            "recompute_key": key, "reported_value": c["reported_value"],
            "recomputed_value": (f"{recomputed:.6g}" if recomputed != "" else ""),
            "status": status, "tolerance": c["tolerance"],
            "explanation": explanation, "action_required": ("none" if status in
            ("EXACT_MATCH", "ROUNDING_MATCH", "SUPPORTED_WITH_REWORDING") else "review"),
        })

    with open(REPORTS / "reconciliation.csv", "w", encoding="utf-8", newline="") as f:
        cols = ["claim_id", "manuscript_location", "reported_value", "recomputed_value",
                "status", "tolerance", "explanation", "action_required", "recompute_key"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in out:
            w.writerow({k: r.get(k, "") for k in cols})

    with open(REPORTS / "result_reconciliation.md", "w", encoding="utf-8") as f:
        f.write("# Result Reconciliation Report\n\n")
        f.write("Every manuscript number recomputed from `data/raw/rollout_ledger.csv` via "
                "`analysis/01`, `analysis/02`. No manuscript value was copied into the recomputation.\n\n")
        f.write("## Summary\n\n")
        for k, v in counts.items():
            f.write(f"- {k}: {v}\n")
        total = len(out)
        ok = counts["EXACT_MATCH"] + counts["ROUNDING_MATCH"] + counts["SUPPORTED_WITH_REWORDING"]
        f.write(f"\n**{ok}/{total} claims reconcile** (EXACT/ROUNDING/SUPPORTED). "
                f"MISMATCH={counts['MISMATCH']}, UNREPRODUCIBLE={counts['UNREPRODUCIBLE']}.\n\n")
        f.write("## Claim-by-claim\n\n")
        f.write("| claim_id | location | reported | recomputed | status | explanation |\n")
        f.write("|---|---|---:|---:|---|---|\n")
        for r in out:
            f.write(f"| {r['claim_id']} | {r['manuscript_location']} | {r['reported_value']} | "
                    f"{r['recomputed_value']} | {r['status']} | {r['explanation']} |\n")

    print(f"[03] reconciled {len(out)} claims: {counts}")
    return 0 if counts["MISMATCH"] == 0 and counts["UNREPRODUCIBLE"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
