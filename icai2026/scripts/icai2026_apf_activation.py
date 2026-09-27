#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Direct measurement of APF repulsion activation (brief F).

Replays FROZEN controllers (no retraining) and computes, at every environment
timestep, the repulsive vector norm for a given distance basis:

    repulsion_active_t = ||F_rep,t|| > EPS

EPS = 1e-8 (documented; a second, looser threshold at 1% of the attractive
magnitude, i.e. 4e-4, is also reported so the conclusion does not hinge on EPS).

Reported for: H0 trajectories (center basis), H2 center trajectories,
H2 surface trajectories, and — as a labelled COUNTERFACTUAL — the surface
basis evaluated along H0 trajectories. Evaluation-only.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from stable_baselines3 import A2C

from scripts.a2c_new import DroneEnv3D  # noqa: F401  (physics constants)
from scripts.icai2026_experiments import (EVAL_BASES, EPISODES_PER_BASE,
                                          TRAIN_MAPS, _nearest_surface,
                                          load_h0h1)
from scripts.vnict_hybrid_experiments import HybridConfig, VNICTDroneEnv

EPS = 1e-8
EPS_REL = 4e-4  # 1% of k_att = 0.04
K_ATT = 0.04
K_REP = 18.0
D0 = 6.0


def frep_center(pos, obstacles, d0=D0):
    f = np.zeros(3)
    for o in obstacles:
        c = np.array([(o["x"][0] + o["x"][1]) / 2, (o["y"][0] + o["y"][1]) / 2,
                      (o["z"][0] + o["z"][1]) / 2], float)
        d = float(np.linalg.norm(pos - c)) + 1e-6
        if d < d0:
            f += K_REP * (1.0 / d - 1.0 / d0) / (d ** 2) * (pos - c) / d
    return f


def frep_surface(pos, obstacles, d0=D0):
    f = np.zeros(3)
    for o in obstacles:
        d, dirv = _nearest_surface(np.asarray(pos, float), o)
        d = d + 1e-6
        if d < d0:
            f += K_REP * (1.0 / d - 1.0 / d0) / (d ** 2) * dirv
    return f


def unique_seeds():
    return [b + e for b in EVAL_BASES for e in range(EPISODES_PER_BASE)]


def replay(kind, basis, map_spec, seed, model):
    """Replay one episode; count timesteps with ||F_rep|| above thresholds.

    kind='H0': frozen hybrid policy; env applies its own adaptive blend.
    kind='H2': no learned policy; executed action is apf_action_v2 with `basis`.
    The measured repulsion always uses `basis` at d0=6 m.
    """
    from scripts.run_rigorous_manifest import build_map
    from scripts.icai2026_experiments import apf_action_v2
    from scripts.a2c_new import ARRIVE_DIST

    obstacles = build_map(map_spec)
    target = np.array([map_spec["distance_m"], map_spec["distance_m"] * 0.5, 5.0], float)
    if kind == "H0":
        cfg = HybridConfig(exp_id="H0", description="act", policy_mode="hybrid",
                           algorithm="A2C", use_wind=True, wind_multiplier=1.0,
                           apf_weight=None, timesteps=0, n_seeds=1, n_eval_episodes=1,
                           distance=int(map_spec["distance_m"]), n_envs=1)
    else:
        cfg = HybridConfig(exp_id="H2", description="act", policy_mode="a2c",
                           algorithm="APF", use_wind=True, wind_multiplier=1.0,
                           apf_weight=0.0, timesteps=0, n_seeds=1, n_eval_episodes=1,
                           distance=int(map_spec["distance_m"]), n_envs=1)
    env = VNICTDroneEnv(cfg, obstacles)
    obs, _ = env.reset(seed=seed)
    fn = frep_center if basis == "center" else frep_surface
    n_steps = n_act8 = n_actrel = 0
    done = trunc = collision = False
    while not (done or trunc):
        pos = env.drone.state[:3].copy()
        fr = fn(pos, obstacles)
        nrm = float(np.linalg.norm(fr))
        n_steps += 1
        n_act8 += int(nrm > EPS)
        n_actrel += int(nrm > EPS_REL)
        if kind == "H0":
            step_action, _ = model.predict(obs, deterministic=True)
        else:
            step_action = apf_action_v2(pos, target, obstacles, basis=basis, d0=D0)
        obs, _, done, trunc, info = env.step(step_action)
        collision = collision or bool(info.get("collision"))
    final_dist = float(np.linalg.norm(env.drone.state[:3] - target))
    success = (final_dist < ARRIVE_DIST) and (not collision)
    env.close()
    return n_steps, n_act8, n_actrel, success, (n_act8 > 0)


def main():
    out = {
        "epsilon_absolute": EPS,
        "epsilon_relative_to_k_att": EPS_REL,
        "note": "evaluation-only replay of frozen controllers; no retraining",
        "groups": {},
    }
    groups = defaultdict(lambda: {"steps": 0, "active_abs": 0, "active_rel": 0,
                                  "steps_success": 0, "active_abs_success": 0,
                                  "episodes": 0, "episodes_with_activation": 0,
                                  "per_map": defaultdict(lambda: [0, 0]),
                                  "per_seed": defaultdict(lambda: [0, 0])})
    for map_spec in TRAIN_MAPS:
        for seed in (101, 211, 307, 401, 503):
            model_h0 = load_h0h1("H0", map_spec["id"], seed)
            for kind, basis in (("H0", "center"), ("H2", "center"), ("H2", "surface"),
                                ("H0_counterfactual", "surface")):
                mdl = model_h0 if kind.startswith("H0") else None
                g = groups[f"{kind}_{basis}"]
                for s in unique_seeds():
                    n, a8, arel, succ, ep_act = replay(
                        "H0" if kind.startswith("H0") else "H2", basis, map_spec, s, mdl)
                    g["steps"] += n
                    g["active_abs"] += a8
                    g["active_rel"] += arel
                    g["episodes"] += 1
                    g["episodes_with_activation"] += int(ep_act)
                    if succ:
                        g["steps_success"] += n
                        g["active_abs_success"] += a8
                    g["per_map"][map_spec["id"]][0] += a8
                    g["per_map"][map_spec["id"]][1] += n
                    g["per_seed"][str(seed)][0] += a8
                    g["per_seed"][str(seed)][1] += n
                print(f"{kind:22s} {basis:8s} {map_spec['id']:16s} seed{seed} "
                      f"active {g['per_map'][map_spec['id']][0]}/{g['per_map'][map_spec['id']][1]}",
                      flush=True)
    for name, g in groups.items():
        g["per_map"] = {k: {"active": v[0], "steps": v[1],
                            "fraction": round(v[0] / v[1], 6) if v[1] else None}
                        for k, v in g["per_map"].items()}
        g["per_seed"] = {k: {"active": v[0], "steps": v[1],
                             "fraction": round(v[0] / v[1], 6) if v[1] else None}
                         for k, v in g["per_seed"].items()}
        g["fraction_all_steps"] = (round(g["active_abs"] / g["steps"], 6)
                                   if g["steps"] else None)
        g["fraction_success_steps"] = (round(g["active_abs_success"] / g["steps_success"], 6)
                                       if g["steps_success"] else None)
        g["fraction_episodes_with_activation"] = (round(g["episodes_with_activation"] /
                                                        g["episodes"], 6)
                                                  if g["episodes"] else None)
        out["groups"][name] = g
    dest = ROOT / "results" / "icai2026" / "apf_activation.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({k: {kk: vv for kk, vv in v.items()
                          if kk in ("steps", "active_abs", "fraction_all_steps",
                                    "fraction_success_steps",
                                    "fraction_episodes_with_activation")}
                      for k, v in out["groups"].items()}, indent=1))
    print("wrote", dest)


if __name__ == "__main__":
    main()
