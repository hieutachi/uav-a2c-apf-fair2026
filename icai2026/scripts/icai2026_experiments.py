"""
ICAI-FAI 2026 revision experiments.

Implements the reviewer-driven experiment matrix for the revised manuscript:

  H3  = geometry-aware A2C WITHOUT APF (matched-information baseline)      [P0]
  UQ  = corrected evaluation schedule with 50 UNIQUE episode seeds         [P0]
  WS  = frozen-policy wind-intensity sweep  wind_scale in {0,.5,1,1.5,2}   [P0]
  AS  = APF-only sensitivity: distance basis {center, surface} x d0 grid   [P0]
  HO  = held-out procedurally generated maps (new map seeds)               [P1]
  AL  = A2C/APF action-component logging for H0 (mechanistic diagnostics)  [P1]

Design rules honoured here:
  * H3 exposes RAW padded AABB geometry (Option A), never the APF force.
  * Dynamics, reward, termination, optimizer and 5M-step budget are identical
    to the frozen FAIR protocol; only the observation vector differs.
  * Evaluation uses 50 unique numerical seeds (2001..2050) shared across
    configurations so pairing stays meaningful; rollouts are never treated as
    independent inferential units (inference stays at map x training-run).
  * Nothing in results/rigorous/ is modified by this module.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from stable_baselines3 import A2C
from stable_baselines3.common.env_util import make_vec_env

from scripts.a2c_new import (ARRIVE_DIST, DT, DroneEnv3D, apf_action,
                             aabb_signed_clearance)
from scripts.run_rigorous_manifest import build_map
from scripts.vnict_hybrid_experiments import (HybridConfig, VNICTDroneEnv,
                                              acceleration_index, jitter_index,
                                              min_obstacle_distance,
                                              path_length, smooth_trajectory)

OUT = ROOT / "results" / "icai2026"

GEO_K = 8            # padded obstacle slots; max obstacles over all layouts is 8
GEO_DIM = GEO_K * 7  # rel center (3) + half extents (3) + validity mask (1)
OBS_DIM = 12 + GEO_DIM
MAP_SCALE = 300.0

# corrected evaluation schedule: 5 bases x 10 episodes = 50 UNIQUE seeds
EVAL_BASES = [2001, 2011, 2021, 2031, 2041]
EPISODES_PER_BASE = 10

WIND_SCALES = [0.0, 0.5, 1.0, 1.5, 2.0]
D0_GRID = [4.0, 6.0, 8.0, 12.0]

TRAIN_MAPS = [
    {"id": "map-random-01", "seed": 7001, "layout": "random", "distance_m": 300, "density": 0.8},
    {"id": "map-corridor-01", "seed": 7013, "layout": "corridor", "distance_m": 300, "density": 0.8},
    {"id": "map-barrier-01", "seed": 7019, "layout": "barrier", "distance_m": 300, "density": 0.8},
    {"id": "map-mixed-01", "seed": 7027, "layout": "mixed", "distance_m": 300, "density": 0.8},
]
HELDOUT_MAPS = [
    {"id": "map-random-ho1", "seed": 7101, "layout": "random", "distance_m": 300, "density": 0.8},
    {"id": "map-corridor-ho1", "seed": 7113, "layout": "corridor", "distance_m": 300, "density": 0.8},
    {"id": "map-barrier-ho1", "seed": 7119, "layout": "barrier", "distance_m": 300, "density": 0.8},
    {"id": "map-mixed-ho1", "seed": 7127, "layout": "mixed", "distance_m": 300, "density": 0.8},
]
TRAIN_SEEDS = [101, 211, 307, 401, 503]


# --------------------------------------------------------------------- env --
def geo_features(pos, obstacles, k: int = GEO_K, scale: float = MAP_SCALE) -> np.ndarray:
    """Deterministic fixed-size padded raw AABB geometry, sorted by distance.

    Per slot: [rel_center/scale (3), half_extents/scale (3), valid (1)].
    Raw geometry only — no APF force, no potential-field computation.
    """
    out = np.zeros((k, 7), dtype=np.float32)
    if not obstacles:
        return out.ravel()
    centers = np.array([[(o["x"][0] + o["x"][1]) / 2.0,
                         (o["y"][0] + o["y"][1]) / 2.0,
                         (o["z"][0] + o["z"][1]) / 2.0] for o in obstacles], dtype=float)
    halves = np.array([[(o["x"][1] - o["x"][0]) / 2.0,
                        (o["y"][1] - o["y"][0]) / 2.0,
                        (o["z"][1] - o["z"][0]) / 2.0] for o in obstacles], dtype=float)
    order = np.argsort(np.linalg.norm(centers - pos, axis=1))
    for j, idx in enumerate(order[:k]):
        out[j, 0:3] = (centers[idx] - pos) / scale
        out[j, 3:6] = halves[idx] / scale
        out[j, 6] = 1.0
    return out.ravel()


class GeoDroneEnv(DroneEnv3D):
    """DroneEnv3D with a geometry-aware observation and NO APF in the loop.

    policy_mode is forced to "a2c" so the executed action is purely learned.
    """

    def __init__(self, obstacles, target, wind_multiplier=1.0, use_wind=True,
                 start=(0, 0, 5.0)):
        super().__init__(target=np.asarray(target, float), obstacles=obstacles,
                         start=start, policy_mode="a2c", apf_weight=0.0,
                         use_wind=use_wind, wind_multiplier=wind_multiplier)
        from gymnasium import spaces
        self.observation_space = spaces.Box(-np.inf, np.inf, (OBS_DIM,), np.float32)

    def _obs(self):
        st = self.drone.state
        rel = self.target - st[:3]
        geo = geo_features(st[:3], self.obstacles)
        return np.hstack((st, rel, self._wind, geo)).astype(np.float32)


# ------------------------------------------------------------------- train --
def train_h3(map_spec: dict, seed: int, steps: int, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    ckpt = out_dir / f"H3_A2C_{map_spec['id']}_seed{seed}_steps{steps}.zip"
    meta = out_dir / f"H3_A2C_{map_spec['id']}_seed{seed}_steps{steps}.json"
    if ckpt.exists() and meta.exists():
        return {"run_id": ckpt.stem, "skipped": True}
    obstacles = build_map(map_spec)
    random.seed(seed)
    np.random.seed(seed)

    def make_env():
        return GeoDroneEnv(obstacles, target=(map_spec["distance_m"],
                                              map_spec["distance_m"] * 0.5, 5.0))

    vec_env = make_vec_env(make_env, n_envs=1, seed=seed)
    t0 = time.perf_counter()
    model = A2C("MlpPolicy", vec_env, verbose=0, learning_rate=3e-4, n_steps=256,
                gamma=0.99, gae_lambda=0.95, ent_coef=0.02, max_grad_norm=0.5,
                device="cpu")
    model.set_random_seed(seed)          # explicit torch+numpy+python seeding (new vs FAIR)
    model.learn(total_timesteps=steps)
    train_s = time.perf_counter() - t0
    vec_env.close()
    model.save(str(ckpt))
    meta.write_text(json.dumps({
        "run_id": ckpt.stem, "hypothesis": "H3", "variant": "geometry_aware_a2c_no_apf",
        "observation": "12-D base + 56-D padded raw AABB geometry (K=8, distance-sorted)",
        "obs_dim": OBS_DIM, "map": map_spec, "train_seed": seed, "steps": steps,
        "training_seconds": train_s,
        "throughput_steps_s": steps / train_s if train_s else None,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "seeding": "random+numpy+vecenv+model.set_random_seed(seed); torch via SB3 set_random_seed",
    }, indent=2), encoding="utf-8")
    return {"run_id": ckpt.stem, "skipped": False, "training_seconds": train_s}


# -------------------------------------------------------------------- eval --
def unique_seeds() -> list[int]:
    return [b + e for b in EVAL_BASES for e in range(EPISODES_PER_BASE)]


def _nearest_surface(pos, o):
    lo = np.array([o["x"][0], o["y"][0], o["z"][0]], float)
    hi = np.array([o["x"][1], o["y"][1], o["z"][1]], float)
    q = np.clip(pos, lo, hi)
    if np.all(pos >= lo) and np.all(pos <= hi):
        pen = np.minimum(pos - lo, hi - pos)
        ax = int(np.argmin(pen))
        d = float(pen[ax])
        dirv = np.zeros(3)
        dirv[ax] = -1.0 if (pos[ax] - lo[ax]) <= (hi[ax] - pos[ax]) else 1.0
        return d, dirv
    diff = pos - q
    d = float(np.linalg.norm(diff))
    return d, diff / (d + 1e-9)


def apf_action_v2(pos, target, obstacles, basis="center", d0=6.0,
                  k_att=0.04, k_rep=18.0):
    diff_goal = np.asarray(target, float) - np.asarray(pos, float)
    f_att = k_att * diff_goal / (np.linalg.norm(diff_goal) + 1e-6)
    f_rep = np.zeros(3)
    for o in obstacles:
        if basis == "center":
            c = np.array([(o["x"][0] + o["x"][1]) / 2, (o["y"][0] + o["y"][1]) / 2,
                          (o["z"][0] + o["z"][1]) / 2], float)
            d = float(np.linalg.norm(pos - c)) + 1e-6
            dirv = (np.asarray(pos, float) - c) / d
        else:
            d, dirv = _nearest_surface(np.asarray(pos, float), o)
            d = d + 1e-6
        if d < d0:
            f_rep += k_rep * (1.0 / d - 1.0 / d0) / (d ** 2) * dirv
    f = f_att + f_rep
    if np.linalg.norm(f) > 1.0:
        f = f / np.linalg.norm(f)
    return np.clip(f, -1, 1).astype(np.float32)


def evaluate_unit(kind, model, map_spec, seed_tag, wind_scale=1.0,
                  basis=None, d0=None, log_actions=False, seeds=None,
                  fixed_lambda=None):
    """Run the 50-unique-seed schedule for one (config, map, model) unit."""
    obstacles = build_map(map_spec)
    target = np.array([map_spec["distance_m"], map_spec["distance_m"] * 0.5, 5.0], float)
    straight = float(np.linalg.norm(target - np.array([0, 0, 5.0])))
    seeds = seeds or unique_seeds()
    rows = []
    for seed in seeds:
        if kind == "H3":
            env = GeoDroneEnv(obstacles, target=target, wind_multiplier=wind_scale)
        else:
            cfg = HybridConfig(exp_id=kind, description="icai eval",
                               # H2 uses "a2c" passthrough so the caller-supplied
                               # APF variant (basis/d0) is the executed action;
                               # the env's own APF branch would override it.
                               policy_mode={"H0": "hybrid", "H1": "a2c",
                                            "H2": "a2c"}[kind],
                               algorithm="A2C" if kind != "H2" else "APF",
                               use_wind=True, wind_multiplier=wind_scale,
                               apf_weight=fixed_lambda if (kind == "H0" and fixed_lambda is not None)
                               else (None if kind == "H0" else 0.0),
                               timesteps=0, n_seeds=1, n_eval_episodes=1,
                               distance=int(map_spec["distance_m"]), n_envs=1)
            env = VNICTDroneEnv(cfg, obstacles)
        obs, _ = env.reset(seed=seed)
        traj = [env.drone.state[:3].copy()]
        done = trunc = collision = False
        act_log = []
        prev_blended = None
        while not (done or trunc):
            pos = env.drone.state[:3].copy()
            if kind == "H2":
                action = np.zeros(3, np.float32)
                blended = (apf_action_v2(pos, target, obstacles, basis or "center",
                                         d0 if d0 is not None else 6.0)
                           if basis else apf_action(pos, target, obstacles))
            else:
                action, _ = model.predict(obs, deterministic=True)
                blended = action
                if log_actions:
                    a_apf = apf_action(pos, target, obstacles)
                    dist = float(np.linalg.norm(target - pos))
                    lam = min(0.55, max(0.15, 1.0 - dist / 300.0))
                    act_log.append({
                        "a2c_norm": float(np.linalg.norm(action)),
                        "apf_norm": float(np.linalg.norm(a_apf)),
                        "lambda": lam,
                        "cosine": float(np.dot(action, a_apf) /
                                        (np.linalg.norm(action) * np.linalg.norm(a_apf) + 1e-9)),
                        "blend_change": (float(np.linalg.norm(blended - prev_blended))
                                         if prev_blended is not None else 0.0),
                    })
                    prev_blended = np.asarray(blended, float)
            obs, _, done, trunc, info = env.step(blended if kind == "H2" else action)
            traj.append(env.drone.state[:3].copy())
            collision = collision or bool(info.get("collision"))
        arr = np.asarray(traj)
        final_dist = float(np.linalg.norm(arr[-1] - target))
        success = final_dist < ARRIVE_DIST and not collision
        status = ("collision" if collision else
                  "success" if success else "timeout" if trunc else "failed_not_at_goal")
        plen = path_length(arr)
        metric_traj = smooth_trajectory(arr, max(20, len(arr)))
        row = {
            "config": kind, "map_id": map_spec["id"], "map_seed": map_spec["seed"],
            "unit": seed_tag, "eval_seed": seed, "wind_scale": wind_scale,
            "apf_basis": basis or ("center" if kind != "H2" else None),
            "apf_d0": d0, "status": status, "success": int(success),
            "collision": int(collision), "timeout": int(status == "timeout"),
            "steps": len(arr) - 1, "final_dist_m": final_dist, "path_length_m": plen,
            "path_efficiency": (min(1.0, straight / max(plen, 1e-9)) if success else math.nan),
            "min_obstacle_distance_m": min_obstacle_distance(arr, obstacles),
            "jitter_index": jitter_index(metric_traj, DT),
            "acceleration_index": acceleration_index(metric_traj, DT),
        }
        if act_log:
            row.update({
                "log_a2c_norm": float(np.mean([a["a2c_norm"] for a in act_log])),
                "log_apf_norm": float(np.mean([a["apf_norm"] for a in act_log])),
                "log_lambda_mean": float(np.mean([a["lambda"] for a in act_log])),
                "log_cosine_mean": float(np.mean([a["cosine"] for a in act_log])),
                "log_blend_change_mean": float(np.mean([a["blend_change"] for a in act_log])),
            })
        rows.append(row)
        env.close()
    return rows


def write_rows(rows, path: Path):
    if not rows:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return path


def load_h0h1(config: str, map_id: str, seed: int):
    ckpt = (ROOT / "results/rigorous/artifacts" /
            f"{config}_A2C_{map_id}_seed{seed}_steps5000000/checkpoints/model.zip")
    return A2C.load(str(ckpt), device="cpu")


def checkpoint_map_for(spec: dict) -> str:
    """Held-out transfer: a model trained on the training map of the SAME layout
    family is evaluated on the unseen held-out layout (controller-level transfer
    with map geometry available to H0 through APF)."""
    if spec in HELDOUT_MAPS or spec["id"].endswith("-ho1"):
        match = next(m for m in TRAIN_MAPS if m["layout"] == spec["layout"])
        return match["id"]
    return spec["id"]


# -------------------------------------------------------------------- cli --
def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("train-h3")
    t.add_argument("--map", required=True)
    t.add_argument("--seed", type=int, required=True)
    t.add_argument("--steps", type=int, default=5_000_000)

    e = sub.add_parser("eval")
    e.add_argument("--configs", nargs="+", default=["H0", "H1"])
    e.add_argument("--maps", nargs="+", default=["train"])
    e.add_argument("--seeds", nargs="+", type=int, default=TRAIN_SEEDS)
    e.add_argument("--wind-scales", nargs="+", type=float, default=[1.0])
    e.add_argument("--tag", default="eval_unique")
    e.add_argument("--steps", type=int, default=5_000_000,
                   help="training steps of the H3 checkpoint to load")
    e.add_argument("--log-actions", action="store_true")
    e.add_argument("--fixed-lambda", type=float, default=None,
                   help="H0 only: evaluation-time fixed blend weight (blend sensitivity, not a causal ablation)")

    a = sub.add_parser("apf-sensitivity")
    a.add_argument("--maps", nargs="+", default=["train"])
    a.add_argument("--tag", default="apf_sensitivity")

    args = p.parse_args()

    if args.cmd == "train-h3":
        spec = next(m for m in (TRAIN_MAPS + HELDOUT_MAPS) if m["id"] == args.map)
        print(json.dumps(train_h3(spec, args.seed, args.steps, OUT / "h3_train")))
        return

    maps = (TRAIN_MAPS if args.maps == ["train"] else
            HELDOUT_MAPS if args.maps == ["heldout"] else
            [m for m in (TRAIN_MAPS + HELDOUT_MAPS) if m["id"] in args.maps])

    if args.cmd == "eval":
        rows = []
        for config in args.configs:
            for spec in maps:
                for seed in args.seeds:
                    model = None
                    tag = f"{config}_{spec['id']}_seed{seed}"
                    if config != "H2":
                        if config == "H3":
                            ckpt_map = checkpoint_map_for(spec)
                            ckpt = (OUT / "h3_train" /
                                    f"H3_A2C_{ckpt_map}_seed{seed}_steps{args.steps}.zip")
                            if not ckpt.exists():
                                print(json.dumps({"skip": tag, "reason": "no H3 checkpoint"}))
                                continue
                            model = A2C.load(str(ckpt), device="cpu")
                        else:
                            model = load_h0h1(config, checkpoint_map_for(spec), seed)
                    for ws in args.wind_scales:
                        rows += evaluate_unit(config, model, spec, tag,
                                              wind_scale=ws,
                                              log_actions=args.log_actions,
                                              fixed_lambda=args.fixed_lambda)
                        print(json.dumps({"done": tag, "wind_scale": ws,
                                          "n": sum(1 for r in rows if r["unit"] == tag
                                                   and r["wind_scale"] == ws)}), flush=True)
        write_rows(rows, OUT / args.tag / f"{args.tag}_{'_'.join(args.configs)}.csv")
        return

    if args.cmd == "apf-sensitivity":
        rows = []
        for basis in ("center", "surface"):
            for d0 in D0_GRID:
                for spec in maps:
                    tag = f"H2_{basis}_d0{d0:g}_{spec['id']}"
                    rows += evaluate_unit("H2", None, spec, tag, basis=basis, d0=d0)
                    print(json.dumps({"done": tag,
                                      "success": sum(r["success"] for r in rows
                                                     if r["unit"] == tag)}), flush=True)
        write_rows(rows, OUT / args.tag / "apf_sensitivity.csv")


if __name__ == "__main__":
    main()
