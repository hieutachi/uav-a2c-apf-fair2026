#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Numerical reconciliation + consistency checker + MASTER_RESULTS.json (brief C, D, S).

Source-of-truth hierarchy (brief B): raw CSVs > ledgers/logs > analysis scripts >
manifest > report > ICAI manuscript > FAIR manuscript. Every claim below is
recomputed from the raw CSVs; nothing is taken from prose.

Outputs:
  results/icai2026/consistency_check.json   (PASS/FAIL/WARN detail)
  results/icai2026/MASTER_RESULTS.json      (canonical values for the manuscript)
Exit code 1 if any FAIL.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
ICAI = ROOT / "results" / "icai2026"

SUITES = {
    "eval_unique": "icai_eval_unique/icai_eval_unique_H0_H1.csv",
    "eval_unique_h3": "icai_eval_unique_h3/icai_eval_unique_h3_H3.csv",
    "wind": "icai_wind_sweep/icai_wind_sweep_H0_H1.csv",
    "wind_h3": "icai_wind_sweep_h3/icai_wind_sweep_h3_H3.csv",
    "heldout": "icai_heldout/icai_heldout_H0_H1.csv",
    "heldout_h3": "icai_heldout_h3/icai_heldout_h3_H3.csv",
    "sensitivity": "icai_apf_sensitivity/apf_sensitivity.csv",
    "action_log": "icai_action_log/icai_action_log_H0.csv",
    "fixed_lambda": {f"lam{lam}": f"icai_fixed_lambda_{lam}/icai_fixed_lambda_{lam}_H0.csv"
                     for lam in ("0.15", "0.35", "0.55")},
}

FAIL, WARN, PASS = [], [], []


def load(rel):
    return list(csv.DictReader((ICAI / rel).open(encoding="utf-8")))


def check(ok, cid, detail):
    (PASS if ok else FAIL).append({"id": cid, "detail": detail})
    return ok


def totals(rows, keyfn):
    g = defaultdict(lambda: [0, 0, 0, 0])
    for r in rows:
        k = keyfn(r)
        g[k][0] += 1
        g[k][1] += int(r["success"])
        g[k][2] += int(r["collision"])
        g[k][3] += int(r["timeout"])
    return g


# ---------------------------------------------------------------- load all --
D = {}
for name, rel in SUITES.items():
    if isinstance(rel, dict):
        D[name] = {k: load(v) for k, v in rel.items()}
    else:
        D[name] = load(rel)

# ------------------------------------------- C/D: arithmetic consistency ----
for name in ("eval_unique", "eval_unique_h3", "wind", "wind_h3", "heldout",
             "heldout_h3", "sensitivity"):
    rows = D[name]
    g = totals(rows, lambda r: (r["config"] if "config" in r else r.get("apf_basis"),
                                r.get("map_id", "ALL"), r.get("wind_scale", ""),
                                r.get("apf_d0", "")))
    for k, (n, s, c, t) in g.items():
        check(s + c + t == n, f"sum:{name}:{k}",
              f"success+collision+timeout={s + c + t} vs n={n}")
    # per-map sums equal config totals
    gm = totals(rows, lambda r: (r["config"] if "config" in r else r.get("apf_basis"),
                                 r.get("map_id", "ALL")))
    gt = totals(rows, lambda r: (r["config"] if "config" in r else r.get("apf_basis"),))
    for (cfg, mp), v in gm.items():
        if mp == "ALL":
            continue
    for (cfg,), v in gt.items():
        parts = [vv for (c2, mp), vv in gm.items() if c2 == cfg and mp != "ALL"]
        check(sum(p[1] for p in parts) == v[1] and sum(p[0] for p in parts) == v[0],
              f"mapsum:{name}:{cfg}", f"per-map sums {sum(p[1] for p in parts)}/{sum(p[0] for p in parts)} vs total {v[1]}/{v[0]}")

# seed uniqueness per unit in corrected suites
for name in ("eval_unique", "eval_unique_h3", "wind", "wind_h3", "heldout", "heldout_h3"):
    per = defaultdict(set)
    for r in D[name]:
        per[(r["config"], r["map_id"], r["unit"])].add(r["eval_seed"])
    bad = {k: len(v) for k, v in per.items() if len(v) != 50}
    check(not bad, f"seeds:{name}", f"units without 50 unique seeds: {bad if bad else 'none'}")

# ------------------------------------------- headline claims vs raw CSV ----
CLAIMS = [
    ("H0 corrected total", D["eval_unique"], ("H0",), (1000, 0, 0)),
    ("H1 corrected total", D["eval_unique"], ("H1",), (848, 45, 107)),
    ("H3 corrected total", D["eval_unique_h3"], ("H3",), (938, 62, 0)),
    ("H1 random", D["eval_unique"], ("H1", "map-random-01"), (157, 36, 57)),
    ("H1 corridor", D["eval_unique"], ("H1", "map-corridor-01"), (241, 9, 0)),
    ("H1 barrier", D["eval_unique"], ("H1", "map-barrier-01"), (200, 0, 50)),
    ("H1 mixed", D["eval_unique"], ("H1", "map-mixed-01"), (250, 0, 0)),
    ("H3 random", D["eval_unique_h3"], ("H3", "map-random-01"), (233, 17, 0)),
    ("H3 corridor", D["eval_unique_h3"], ("H3", "map-corridor-01"), (250, 0, 0)),
    ("H3 barrier", D["eval_unique_h3"], ("H3", "map-barrier-01"), (222, 28, 0)),
    ("H3 mixed", D["eval_unique_h3"], ("H3", "map-mixed-01"), (233, 17, 0)),
    ("H0 wind0", D["wind"], ("H0", "0.0"), (1000, 0, 0)),
    ("H0 wind2", D["wind"], ("H0", "2.0"), (986, 14, 0)),
    ("H3 wind2", D["wind_h3"], ("H3", "2.0"), (915, 85, 0)),
    ("H1 wind2", D["wind"], ("H1", "2.0"), (866, 49, 85)),
    ("sens center d0=6", D["sensitivity"], ("center", "6.0"), (21, 172, 7)),
    ("sens surface d0=6", D["sensitivity"], ("surface", "6.0"), (88, 0, 112)),
    ("heldout H0 mixed", D["heldout"], ("H0", "map-mixed-ho1"), (50, 200, 0)),
    ("heldout H3 mixed", D["heldout_h3"], ("H3", "map-mixed-ho1"), (17, 233, 0)),
    ("heldout H3 random", D["heldout_h3"], ("H3", "map-random-ho1"), (203, 47, 0)),
    ("heldout H1 mixed", D["heldout"], ("H1", "map-mixed-ho1"), (0, 250, 0)),
    ("fixed lambda 0.55", D["fixed_lambda"]["lam0.55"], ("H0",), (606, 390, 4)),
    ("fixed lambda 0.35", D["fixed_lambda"]["lam0.35"], ("H0",), (795, 157, 48)),
    ("fixed lambda 0.15", D["fixed_lambda"]["lam0.15"], ("H0",), (990, 6, 4)),
]
for cid, rows, key, expect in CLAIMS:
    if len(key) == 1:
        g = totals(rows, lambda r: (r["config"],))
        got = g.get(key, [None])
        got = (got[1], got[2], got[3]) if got[0] else None
    elif len(key) == 2 and key[1].startswith("map-"):
        g = totals(rows, lambda r: (r["config"], r["map_id"]))
        got = g.get(key)
        got = (got[1], got[2], got[3]) if got else None
    elif len(key) == 2 and key[0] in ("center", "surface"):
        g = totals(rows, lambda r: (r["apf_basis"], r["apf_d0"]))
        got = g.get(key)
        got = (got[1], got[2], got[3]) if got else None
    else:
        g = totals(rows, lambda r: (r["config"], r["wind_scale"]))
        got = g.get(key)
        got = (got[1], got[2], got[3]) if got else None
    check(got == expect, f"claim:{cid}", f"expected {expect}, recomputed {got}")

# percentage spot checks
g = totals(D["heldout_h3"], lambda r: (r["config"], r["map_id"]))
n, s, _, _ = g[("H3", "map-random-ho1")]
check(abs(s / n - 0.812) < 0.001, "pct:H3 heldout random", f"{s}/{n} = {s/n:.4f} (81.2%)")

# ------------------------------------------- paired stats recomputation ----
METRICS = ["success", "jitter_index", "acceleration_index", "path_efficiency",
           "min_obstacle_distance_m", "steps"]


def unit_means(rows):
    acc = defaultdict(lambda: defaultdict(list))
    for r in rows:
        k = (r["config"], r["map_id"], r["unit"].split("_seed")[-1])
        for m in METRICS:
            try:
                v = float(r[m])
            except (KeyError, TypeError, ValueError):
                continue
            if not math.isnan(v):
                acc[k][m].append(v)
    return {k: {m: float(np.mean(v)) for m, v in d.items() if v} for k, d in acc.items()}


um = unit_means(D["eval_unique"] + D["eval_unique_h3"])
recomputed = {}
for a, b in (("H1", "H0"), ("H1", "H3"), ("H3", "H0")):
    for m in METRICS:
        diffs = [um[(b, k[1], k[2])][m] - um[k][m]
                 for k in sorted(um) if k[0] == a and m in um[k]
                 and (b, k[1], k[2]) in um and m in um[(b, k[1], k[2])]]
        d = np.array(diffs)
        nz = d[d != 0]
        p = float(stats.wilcoxon(nz, alternative="two-sided").pvalue) if len(nz) else math.nan
        dz = float(d.mean() / d.std(ddof=1)) if len(d) > 1 and d.std(ddof=1) > 0 else math.nan
        recomputed[f"{b}-{a}|{m}"] = {"n": int(len(d)), "mean_diff": round(float(d.mean()), 6),
                                      "dz": round(dz, 4), "p": round(p, 6)}
stored = json.loads((ICAI / "stats_icai.json").read_text(encoding="utf-8"))
for r in stored["paired"]:
    key = f"{r['contrast']}|{r['metric']}"
    rc = recomputed.get(key)
    ok = rc and abs(rc["mean_diff"] - r["mean_diff"]) < 1e-4 and \
        abs(rc["dz"] - r["cohen_dz"]) < 1e-3 and abs(rc["p"] - r["wilcoxon_p"]) < 1e-4
    check(bool(ok), f"paired:{key}", f"stored {r['mean_diff']}/{r['cohen_dz']}/{r['wilcoxon_p']} vs recomputed {rc}")

# ------------------------------------------- action log summaries ----------
alog = D["action_log"]
act = {}
for key in ["log_a2c_norm", "log_apf_norm", "log_lambda_mean", "log_cosine_mean",
            "log_blend_change_mean"]:
    v = [float(r[key]) for r in alog if r.get(key) not in (None, "", "nan")]
    act[key] = {"n_episodes": len(v), "mean": round(float(np.mean(v)), 4),
                "sd": round(float(np.std(v, ddof=1)), 4)}
check(abs(act["log_apf_norm"]["mean"] - 0.04) < 1e-6 and act["log_apf_norm"]["sd"] < 1e-6,
      "actionlog:apf_norm==k_att", f"mean {act['log_apf_norm']['mean']} sd {act['log_apf_norm']['sd']}")

# ------------------------------------------- APF activation (brief F) ------
act_json = json.loads((ICAI / "apf_activation.json").read_text(encoding="utf-8"))
check(act_json["groups"]["H0_center"]["active_abs"] == 0,
      "activation:H0 center never active",
      f"{act_json['groups']['H0_center']['active_abs']}/{act_json['groups']['H0_center']['steps']}")
check(act_json["groups"]["H2_center"]["active_abs"] == 0,
      "activation:H2 center never active",
      f"{act_json['groups']['H2_center']['active_abs']}/{act_json['groups']['H2_center']['steps']}")

# ------------------------------------------- stale/causal language scan ----
BAD_STRINGS = {
    "arithmetic": ["36 coll", "89–100"],
    "stale_status": ["RUNNING", "aggregating", "PENDING", "TODO"],
    "causal_overreach": ["causal decomposition", "decomposes additively", "accounts for most",
                         "59%", "caused by obstacle information", "APF independently improves"],
    "apf_wording": ["broken distance convention", "broken APF", "defective",
                    "removes collisions entirely", "eliminates collisions"],
    "wind_wording": ["not wind-driven", "geometry- and control-driven"],
    "heldout_wording": ["same-layout held-out", "same-layout training map"],
}
targets = [ROOT / "REPORT_ICAI2026_REVISION.md",
           ROOT / "paper" / "icai2026" / "main.tex"]
# Sections whose job is to QUOTE the old/bad strings (correction log, checklists,
# title audit) must not be flagged; negated prose ("not a causal decomposition")
# is also exempt from the causal category.
QUOTE_SECTIONS = ("10. Correction log", "16. Title audit", "17. Manuscript rewrite checklist",
                  "18. GO / NO-GO gate")
NEGATIONS = ("not a causal decomposition", "NOT a causal", "no causal decomposition")
lang_hits = defaultdict(list)
for t in targets:
    section = ""
    for i, line in enumerate(t.read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].strip()
        in_quote_section = any(section.startswith(q) for q in QUOTE_SECTIONS)
        negated = any(n in line for n in NEGATIONS)
        for cat, pats in BAD_STRINGS.items():
            if in_quote_section and cat != "fair_mentions":
                continue
            if cat == "causal_overreach" and negated:
                continue
            for pat in pats:
                if pat in line:
                    lang_hits[cat].append(f"{t.name}:{i}: {pat}")
for cat, hits in lang_hits.items():
    WARN.append({"category": cat, "hits": hits})

FAIR_PATTERNS = ["FAIR", "prior submission", "Reviewer", "reviewer", "This revision",
                 "revision answers", "rejected"]
fair_hits = []
tex = (ROOT / "paper" / "icai2026" / "main.tex").read_text(encoding="utf-8")
for i, line in enumerate(tex.splitlines(), 1):
    for pat in FAIR_PATTERNS:
        if pat in line:
            fair_hits.append(f"main.tex:{i}: {pat}")
WARN.append({"category": "fair_mentions_in_manuscript (removal list, brief Q)", "hits": fair_hits})

# ------------------------------------------- MASTER_RESULTS.json -----------
def suite_outcome(rows, keyfn, label):
    g = totals(rows, keyfn)
    return {json.dumps(k, ensure_ascii=False): {"n": v[0], "success": v[1], "collision": v[2],
                                                "timeout": v[3],
                                                "success_pct": round(100.0 * v[1] / v[0], 2)}
            for k, v in sorted(g.items(), key=lambda kv: str(kv[0]))}


master = {
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "generator": {
        "script": "scripts/icai2026_consistency_check.py",
        "sha256": hashlib.sha256((ROOT / "scripts" / "icai2026_consistency_check.py")
                                 .read_bytes()).hexdigest()[:16],
    },
    "source_of_truth": ["raw CSVs in results/icai2026/", "apf_activation.json",
                        "stats recomputed by this script"],
    "corrected_seed_outcomes": {
        "H0": suite_outcome(D["eval_unique"], lambda r: (r["config"], r["map_id"]), "x"),
        "H1": suite_outcome(D["eval_unique"], lambda r: (r["config"], r["map_id"]), "x"),
        "H3": suite_outcome(D["eval_unique_h3"], lambda r: (r["config"], r["map_id"]), "x"),
    },
    "paired_contrasts": recomputed,
    "wind_sweep": suite_outcome(D["wind"] + D["wind_h3"] + D["eval_unique"] + D["eval_unique_h3"],
                                lambda r: (r["config"], r["wind_scale"]), "x"),
    "apf_sensitivity": suite_outcome(D["sensitivity"],
                                     lambda r: (r["apf_basis"], r["apf_d0"], r["map_id"]), "x"),
    "heldout": suite_outcome(D["heldout"] + D["heldout_h3"],
                             lambda r: (r["config"], r["map_id"]), "x"),
    "fixed_lambda": {k: suite_outcome(v, lambda r: (r["config"],), "x")
                     for k, v in D["fixed_lambda"].items()},
    "action_diagnostics": act,
    "apf_activation": {k: {kk: vv for kk, vv in g.items()
                           if kk in ("steps", "active_abs", "active_rel",
                                     "fraction_all_steps", "fraction_success_steps",
                                     "episodes", "episodes_with_activation",
                                     "fraction_episodes_with_activation")}
                       for k, g in act_json["groups"].items()},
    "apf_activation_epsilon": {"absolute": act_json["epsilon_absolute"],
                               "relative_to_k_att": act_json["epsilon_relative_to_k_att"]},
}
(ICAI / "MASTER_RESULTS.json").write_text(json.dumps(master, indent=2), encoding="utf-8")

report = {"n_pass": len(PASS), "n_fail": len(FAIL), "fail": FAIL, "warn": WARN}
(ICAI / "consistency_check.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(f"PASS {len(PASS)}  FAIL {len(FAIL)}")
for f in FAIL:
    print("  FAIL", f["id"], f["detail"])
for w in WARN:
    print(f"  WARN [{w['category']}] {len(w['hits'])} hits")
    for h in w["hits"][:12]:
        print("     ", h)
print("master written:", ICAI / "MASTER_RESULTS.json")
sys.exit(1 if FAIL else 0)
