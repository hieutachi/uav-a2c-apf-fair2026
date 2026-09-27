#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit of the H3 geometry representation (brief G). Evaluation-only.

Verifies and documents: K, slot definition, normalization, zero padding,
validity mask, sorting criterion, per-timestep re-sorting, slot-swap events
(and the distance gaps at which they occur), observation bounds, and that all
training + held-out maps fit within K = 8.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
from stable_baselines3 import A2C

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.icai2026_experiments import (GEO_K, OBS_DIM, GeoDroneEnv,
                                            HELDOUT_MAPS, TRAIN_MAPS,
                                            checkpoint_map_for, geo_features)
from scripts.run_rigorous_manifest import build_map

EPS_GAP = 1e-6


def centers_of(obstacles):
    return np.array([[(o["x"][0] + o["x"][1]) / 2, (o["y"][0] + o["y"][1]) / 2,
                      (o["z"][0] + o["z"][1]) / 2] for o in obstacles], float)


def main():
    out = {"K": GEO_K, "obs_dim": OBS_DIM,
           "slot_definition": "per slot: rel_center/300 (3), half_extents/300 (3), valid (1); "
                              "slots sorted by Euclidean distance UAV->obstacle center, ascending; "
                              "unused slots zero-filled with valid=0",
           "resorted_every_timestep": True,
           "observation_space_bounds": "gymnasium.spaces.Box(-inf, +inf, (68,)); SB3 MlpPolicy "
                                       "does not normalize inputs",
           "maps": {}, "slot_swaps": {}, "component_ranges": {}}
    centers_cache = {}
    for spec in TRAIN_MAPS + HELDOUT_MAPS:
        obs = build_map(spec)
        centers_cache[spec["id"]] = centers_of(obs)
        out["maps"][spec["id"]] = {"n_obstacles": len(obs), "fits_K": len(obs) <= GEO_K,
                                   "layout": spec["layout"], "seed": spec["seed"]}

    # replay frozen H3 policies and watch slot permutations + component ranges
    for spec in TRAIN_MAPS:
        ckpt = (ROOT / "results/icai2026/h3_train" /
                f"H3_A2C_{spec['id']}_seed101_steps5000000.zip")
        model = A2C.load(str(ckpt), device="cpu")
        obstacles = build_map(spec)
        centers = centers_cache[spec["id"]]
        env = GeoDroneEnv(obstacles, target=(spec["distance_m"], spec["distance_m"] * 0.5, 5.0))
        swaps = steps = 0
        min_gap_at_swap = None
        min_boundary_gap = np.inf
        comp_min = np.full(GEO_K * 7, np.inf)
        comp_max = np.full(GEO_K * 7, -np.inf)
        prev_slots = None
        for seed in [2001 + e for e in range(10)]:
            o, _ = env.reset(seed=seed)
            done = trunc = False
            while not (done or trunc):
                pos = env.drone.state[:3].copy()
                d = np.linalg.norm(centers - pos, axis=1)
                order = np.argsort(d)
                slots = tuple(order[:GEO_K])
                if prev_slots is not None:
                    steps += 1
                    if slots != prev_slots:
                        swaps += 1
                        gs = np.sort(d)[:GEO_K + 1]
                        gap = float(gs[-1] - gs[-2]) if len(gs) > GEO_K else float("nan")
                        min_gap_at_swap = gap if min_gap_at_swap is None else min(min_gap_at_swap, gap)
                    if len(d) > GEO_K:
                        gs = np.sort(d)
                        min_boundary_gap = min(min_boundary_gap, float(gs[GEO_K] - gs[GEO_K - 1]))
                gf = geo_features(pos, obstacles)
                comp_min = np.minimum(comp_min, gf)
                comp_max = np.maximum(comp_max, gf)
                prev_slots = slots
                o, _, done, trunc, _ = env.step(model.predict(o, deterministic=True)[0])
        env.close()
        out["slot_swaps"][spec["id"]] = {
            "steps_compared": steps, "swap_events": swaps,
            "swap_rate": round(swaps / steps, 5) if steps else None,
            "min_sorted_gap_at_swap_m": (round(min_gap_at_swap, 4)
                                          if min_gap_at_swap is not None else None),
            "min_K_boundary_gap_m": (round(min_boundary_gap, 4)
                                     if np.isfinite(min_boundary_gap) else None),
        }
        out["component_ranges"][spec["id"]] = {
            "min": [round(float(x), 4) for x in comp_min],
            "max": [round(float(x), 4) for x in comp_max],
        }
        print(spec["id"], out["slot_swaps"][spec["id"]], flush=True)

    out["threat_statement"] = (
        "H3 slots are re-sorted by distance at every timestep, so the observation is permutation-"
        "discontinuous when two obstacle distances cross: the same physical scene can map to different "
        "slot orders on consecutive steps, and the MLP has no permutation invariance. Measured swap rates "
        "are reported per map; where the swap rate is non-zero this is a representation discontinuity, not "
        "a physical event. H3 is therefore a geometry-aware A2C baseline, NOT a perfectly information-matched "
        "counterpart of H0: H0 consumes geometry through an analytic center-distance channel while H3 "
        "consumes padded raw surface-agnostic box geometry through learned features.")
    dest = ROOT / "results/icai2026/h3_representation_audit.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("wrote", dest)


if __name__ == "__main__":
    main()
