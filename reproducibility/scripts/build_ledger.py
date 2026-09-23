"""Build the canonical, append-only rollout ledger from immutable raw artifacts.

Source of truth (never edited in place):
    results/rigorous/canonical/episode_audit.csv

The canonical evidence set is exactly the runs whose run_id ends in 'steps5000000'.
The single non-canonical smoke run 'H0_A2C_map-random-01_seed101_steps64' is excluded.

Output:
    reproducibility/data/raw/rollout_ledger.csv

Usage:
    python reproducibility/scripts/build_ledger.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# repo_root/reproducibility/scripts/build_ledger.py -> repo_root
REPO_ROOT = Path(__file__).resolve().parents[2]
REPRO = REPO_ROOT / "reproducibility"
AUDIT_CSV = REPO_ROOT / "results" / "rigorous" / "canonical" / "episode_audit.csv"
RUNS_DIR = REPO_ROOT / "results" / "rigorous" / "runs"
ARTIFACTS_DIR = REPO_ROOT / "results" / "rigorous" / "artifacts"
ENV_LOCK = REPO_ROOT / "environment-lock.txt"
OUT_LEDGER = REPRO / "data" / "raw" / "rollout_ledger.csv"

CANONICAL_SUFFIX = "steps5000000"
DT = 0.1
GOAL = (300.0, 150.0, 5.0)     # target = (distance, distance*0.5, 5.0), distance=300
START = (0.0, 0.0, 5.0)        # nominal start before +/-0.5 reset perturbation
CONTROLLERS = {"H0", "H1", "H2"}  # H4 is a post-processing diagnostic, not a controller

SCHEMA_VERSION = "1.0.0"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git_head() -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
            text=True,
        ).strip()
    except Exception:
        return "UNKNOWN"


def load_run_meta(run_id: str) -> dict:
    """Read the per-unit run JSON for checkpoint/map hashes (cached by caller)."""
    p = RUNS_DIR / f"{run_id}.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_unit_traj_hashes(run_id: str) -> dict:
    """Parse the per-unit SHA256SUMS to map trajectory filename -> sha256."""
    sums = ARTIFACTS_DIR / run_id / "SHA256SUMS"
    out: dict[str, str] = {}
    if not sums.exists():
        return out
    for line in sums.read_text(encoding="utf-8", errors="surrogateescape").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        digest, rel = parts[0], parts[-1]
        name = rel.replace("\\", "/").split("/")[-1]
        out[name] = digest
    return out


def main() -> int:
    if not AUDIT_CSV.exists():
        raise SystemExit(f"missing canonical ledger source: {AUDIT_CSV}")

    source_commit = git_head()
    env_hash = sha256_file(ENV_LOCK) if ENV_LOCK.exists() else "MISSING"
    created = datetime.now(timezone.utc).isoformat()

    rows = list(csv.DictReader(open(AUDIT_CSV, encoding="utf-8")))
    canonical = [r for r in rows if r["run_id"].endswith(CANONICAL_SUFFIX)]
    excluded = [r["run_id"] for r in rows if not r["run_id"].endswith(CANONICAL_SUFFIX)]

    run_meta_cache: dict[str, dict] = {}
    traj_hash_cache: dict[str, dict] = {}

    # First pass: count numerical seeds per unit to flag duplicates.
    seed_counts: dict[tuple, dict] = {}
    for r in canonical:
        unit = (r["run_id"],)
        num_seed = int(r["eval_seed"]) + int(r["episode"])
        seen = seed_counts.setdefault(unit, {})
        seen[num_seed] = seen.get(num_seed, 0) + 1

    fields = [
        "schema_version", "run_id", "controller_id", "map_id", "map_hash",
        "training_run_id", "training_seed_label", "model_artifact_path", "model_sha256",
        "evaluation_seed_slot", "evaluation_base_seed", "episode_index",
        "numerical_episode_seed", "reset_seed", "wind_seed", "full_condition_hash",
        "is_duplicate_numerical_seed",
        "start_x", "start_y", "start_z", "goal_x", "goal_y", "goal_z",
        "status", "success", "collision", "timeout", "transitions", "simulated_time_s",
        "final_goal_distance_m", "minimum_signed_clearance_m", "path_length_m", "efficiency",
        "mean_acceleration_index_mps2", "mean_jitter_index_mps3",
        "trajectory_artifact_path", "trajectory_sha256",
        "software_environment_hash", "source_commit", "created_at_utc",
    ]

    OUT_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(OUT_LEDGER, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in canonical:
            run_id = r["run_id"]
            controller = r["hypothesis"]
            if controller not in CONTROLLERS:
                continue  # H4 diagnostic rows excluded from the controller ledger
            base = int(r["eval_seed"])
            ep = int(r["episode"])
            num_seed = base + ep
            train_seed = int(r["train_seed"])
            map_id = r["map_id"]

            meta = run_meta_cache.setdefault(run_id, load_run_meta(run_id))
            th = traj_hash_cache.setdefault(run_id, load_unit_traj_hashes(run_id))

            map_hash = meta.get("map_sha256", "")
            model_sha = meta.get("provenance", {}).get("checkpoint_sha256", "") if isinstance(meta.get("provenance"), dict) else ""
            if controller == "H2":
                model_sha = ""  # non-learned controller: no model
            traj_name = r.get("trajectory_file", "")
            traj_sha = th.get(traj_name, "")
            traj_rel = f"results/rigorous/artifacts/{run_id}/trajectories/{traj_name}" if traj_name else ""
            model_rel = f"results/rigorous/artifacts/{run_id}/checkpoints/model.zip" if (controller in {"H0", "H1"} and model_sha) else ""

            status = r["status"]
            success = int(r["success"]); collision = int(r["collision"]); timeout = int(r["timeout"])
            eff = r.get("path_efficiency", "")
            eff_out = ""
            if success == 1 and eff not in ("", "nan", "NaN", None):
                try:
                    eff_out = f"{float(eff):.10g}"
                except ValueError:
                    eff_out = ""
            transitions = int(float(r["steps"]))
            fch = sha256_text(f"{map_hash}|{controller}|{num_seed}")
            is_dup = seed_counts[(run_id,)][num_seed] > 1

            w.writerow({
                "schema_version": SCHEMA_VERSION,
                "run_id": run_id,
                "controller_id": controller,
                "map_id": map_id,
                "map_hash": map_hash,
                "training_run_id": f"{controller}_{map_id}_seed{train_seed}",
                "training_seed_label": train_seed,
                "model_artifact_path": model_rel,
                "model_sha256": model_sha,
                "evaluation_seed_slot": f"{base}+{ep}",
                "evaluation_base_seed": base,
                "episode_index": ep,
                "numerical_episode_seed": num_seed,
                "reset_seed": num_seed,
                "wind_seed": num_seed,
                "full_condition_hash": fch,
                "is_duplicate_numerical_seed": str(is_dup).lower(),
                "start_x": START[0], "start_y": START[1], "start_z": START[2],
                "goal_x": GOAL[0], "goal_y": GOAL[1], "goal_z": GOAL[2],
                "status": status, "success": success, "collision": collision, "timeout": timeout,
                "transitions": transitions,
                "simulated_time_s": f"{transitions * DT:.4f}",
                "final_goal_distance_m": r["final_dist_m"],
                "minimum_signed_clearance_m": r["min_obstacle_distance_m"],
                "path_length_m": r["path_length_m"],
                "efficiency": eff_out,
                "mean_acceleration_index_mps2": r["acceleration_index"],
                "mean_jitter_index_mps3": r["jitter_index"],
                "trajectory_artifact_path": traj_rel,
                "trajectory_sha256": traj_sha,
                "software_environment_hash": env_hash,
                "source_commit": source_commit,
                "created_at_utc": created,
            })
            n += 1

    print(f"[build_ledger] wrote {n} rollout rows -> {OUT_LEDGER}")
    print(f"[build_ledger] excluded non-canonical runs: {sorted(set(excluded))}")
    print(f"[build_ledger] source_commit={source_commit} env_hash={env_hash[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
