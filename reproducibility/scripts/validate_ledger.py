"""Ledger validation gate + seed-slot enumeration + pseudoreplication check.

Outputs:
    data/derived/evaluation_seed_slots.csv
    reports/data_validation.md   (findings written by this script)
Exit non-zero if a hard invariant fails.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

REPRO = Path(__file__).resolve().parents[1]
LEDGER = REPRO / "data" / "raw" / "rollout_ledger.csv"
DERIVED = REPRO / "data" / "derived"
REPORTS = REPRO / "reports"

BASE_SEEDS = [1009, 1013, 1019, 1021, 1031]
EPISODES = list(range(10))


def main() -> int:
    rows = list(csv.DictReader(open(LEDGER, encoding="utf-8")))
    problems = []

    # 1. status invariant
    bad = [r for r in rows if int(r["success"]) + int(r["collision"]) + int(r["timeout"]) != 1]
    if bad:
        problems.append(f"{len(bad)} rows violate success+collision+timeout==1")

    # 2. status string matches flags
    for r in rows:
        st = r["status"]
        if not ((st == "success" and r["success"] == "1") or
                (st == "collision" and r["collision"] == "1") or
                (st == "timeout" and r["timeout"] == "1")):
            problems.append(f"status/flag mismatch in {r['run_id']} slot {r['evaluation_seed_slot']}")
            break

    # 3. per controller totals
    per_ctrl = Counter(r["controller_id"] for r in rows)
    # 4. per controller-map cell sums
    cell = Counter((r["controller_id"], r["map_id"]) for r in rows)
    bad_cells = {k: v for k, v in cell.items() if v != 250}

    # 5. efficiency conditioning: failures must be NA
    eff_on_fail = [r for r in rows if r["success"] != "1" and r["efficiency"] not in ("", "nan")]
    if eff_on_fail:
        problems.append(f"{len(eff_on_fail)} failed rollouts carry non-NA efficiency")

    # 6. seed-slot enumeration + duplicates
    slots = []
    numeric = []
    for b in BASE_SEEDS:
        for e in EPISODES:
            slots.append((f"{b}+{e}", b, e, b + e))
            numeric.append(b + e)
    numeric_counts = Counter(numeric)
    duplicates = sorted({s: c for s, c in numeric_counts.items() if c > 1}.items())
    unique_effective = len(set(numeric))

    DERIVED.mkdir(parents=True, exist_ok=True)
    with open(DERIVED / "evaluation_seed_slots.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["evaluation_seed_slot", "evaluation_base_seed", "episode_index",
                    "numerical_episode_seed", "is_duplicate_numerical_seed"])
        for slot, b, e, num in slots:
            w.writerow([slot, b, e, num, str(numeric_counts[num] > 1).lower()])

    # 7. pseudoreplication: within a unit, do duplicate numerical seeds produce identical metrics?
    identical_pairs = 0
    checked_units = 0
    example = None
    by_unit = defaultdict(list)
    for r in rows:
        by_unit[r["run_id"]].append(r)
    for run_id, rs in by_unit.items():
        checked_units += 1
        seen = {}
        for r in rs:
            ns = int(r["numerical_episode_seed"])
            sig = (r["status"], r["transitions"], r["final_goal_distance_m"],
                   r["minimum_signed_clearance_m"], r["mean_jitter_index_mps3"])
            if ns in seen:
                if seen[ns] == sig:
                    identical_pairs += 1
                    if example is None:
                        example = (run_id, ns)
            else:
                seen[ns] = sig

    REPORTS.mkdir(parents=True, exist_ok=True)
    with open(REPORTS / "data_validation.md", "w", encoding="utf-8") as f:
        f.write("# Data Validation Report\n\n")
        f.write(f"Ledger: `data/raw/rollout_ledger.csv` ({len(rows)} controller rollout rows).\n\n")
        f.write("## Hard invariants\n\n")
        f.write(f"- Terminal-status invariant (success+collision+timeout==1): "
                f"{'PASS' if not bad else 'FAIL'} ({len(bad)} violations)\n")
        f.write(f"- status string / flag consistency: {'PASS' if not any('status/flag' in p for p in problems) else 'FAIL'}\n")
        f.write(f"- Per-controller totals: {dict(per_ctrl)} (expected 1000 each)\n")
        f.write(f"- Per controller-map cells == 250: {'PASS' if not bad_cells else f'FAIL {bad_cells}'}\n")
        f.write(f"- Efficiency NA on failures: {'PASS' if not eff_on_fail else 'FAIL'}\n\n")
        f.write("## Seed arithmetic\n\n")
        f.write(f"- Declared slots per unit: {len(slots)} (5 base seeds x 10 episodes)\n")
        f.write(f"- Unique effective numerical seeds: **{unique_effective}** "
                f"(range {min(numeric)}-{max(numeric)})\n")
        f.write(f"- Overlapping numerical seeds (appear in >1 slot): {len(duplicates)} values\n")
        f.write("  - " + ", ".join(f"{s}(x{c})" for s, c in duplicates) + "\n\n")
        f.write("## Pseudoreplication check (duplicate numerical seed within a unit)\n\n")
        f.write(f"- Units checked: {checked_units}\n")
        f.write(f"- Duplicate-seed rollout instances with byte-identical outcome signature: {identical_pairs}\n")
        if example:
            f.write(f"- Example: unit `{example[0]}` numerical seed {example[1]} appears in two slots "
                    f"with identical status/steps/clearance/jitter.\n")
        f.write("\n**Interpretation.** Because a duplicate numerical seed re-seeds the same environment "
                "reset and wind stream and the evaluation policy is deterministic, the overlapping slots "
                "are exact repeats. Each unit therefore contains 50 rollout rows but only 32 numerically "
                "distinct rollouts. Reported per-unit rates are computed over 50 slots (as in the "
                "manuscript); this repetition is a pseudoreplication limitation that must be disclosed.\n")

    print(f"[validate] rows={len(rows)} per_ctrl={dict(per_ctrl)} bad_cells={bad_cells} "
          f"unique_seeds={unique_effective} identical_dup_instances={identical_pairs}")
    if problems:
        print("[validate] PROBLEMS:", problems)
        return 1
    print("[validate] all hard invariants PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
