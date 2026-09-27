# REPORT — ICAI-FAI 2026 revision (deadline 2026-09-30)

Protocol: `experiments/icai2026_manifest.json` (declared 2026-09-28, before any new result was inspected).
Parent protocol: `vnict-rigorous-2026` (FAIR 2026 submission, rejected). Frozen artifacts: `results/rigorous/` (read-only).
Status: **RUNNING** — H3 training pool and frozen-policy evaluations launched 2026-09-28 ~00:35 local. Results sections are filled as jobs complete; nothing below is interpolated.

---

## 1. Repository state and implementation facts (inspection, section D of the brief)

Interpreter: `C:\Users\N4G\AppData\Local\Programs\Python\Python313\python.exe` (Python 3.13.3, torch 2.6.0+cu124,
SB3 2.7.0, gymnasium 1.2.0, numpy 2.1.1). The default `python` on PATH (3.14) has **no torch** and must not be used.

**Environment repair (blocking, now fixed).** The Python313 `mpmath 1.3.0` installation was corrupted
(`mpmath/libmp/gammazeta.py` missing), which broke `import sympy` → `import torch` → every experiment.
Fixed with `python -m pip install --force-reinstall --no-deps mpmath==1.3.0`. Verified afterwards:
loading an H0 checkpoint and replaying evaluation seeds 1009–1013 on `map-random-01` reproduces the
ledger statuses exactly (`success ×5` = ledger `success ×5`).

| Fact asked in brief D.2 | Finding | Evidence |
|---|---|---|
| Obstacles per map | random 6, corridor 8, barrier 2, mixed 6 (count = max(4, round(8·density)) = 6 at density 0.8; corridor doubles it, mixed adds 2 fixed boxes) | `scripts/run_rigorous_manifest.py:104-133` (`build_map`) |
| AABB storage | list of dicts `{'x': (x0,x1), 'y': (y0,y1), 'z': (z0,z1)}` floats | `scripts/a2c_new.py:100-101`, `_box` at `run_rigorous_manifest.py:100` |
| Fixed padded vector feasible? | **Yes.** Max 8 obstacles over all layouts; held-out maps use the same generator/density so ≤ 8. K = 8 slots chosen. Option A (raw geometry) adopted | `build_map`; `scripts/icai2026_experiments.py:GEO_K` |
| Training wall-clock | **2983 steps/s** per job at `OMP_NUM_THREADS=4` (probe: 100k steps in 33.5 s) ⇒ 5M steps ≈ **28 min/unit**. 20 H3 units ⇒ ~9.3 h serial, ~2–5 h wall at 6-way parallelism on 32 logical cores | probe run 2026-09-28; `nproc` = 32 |
| Saved H0/H1 re-evaluable without retrain? | **Yes.** `run_one(..., evaluation_only=True)` loads `checkpoints/model.zip`; `wind_multiplier`/`use_wind` are constructor params; maps come from `build_map(spec)`. Verified by exact ledger replay | `scripts/a2c_new.py:252-263`; `run_rigorous_manifest.py:271-275`; replay test above |
| APF distance & d0 location | center-distance at `scripts/a2c_new.py:200-204`; `d0` parameter default 6.0 at `:194`; normalize-then-clip at `:208-212` | `apf_action` |
| λ implementation | `apf_w = clamp(1 − dist/300, 0.15, 0.55)` when `apf_weight is None`, else fixed `clamp(apf_weight,0,1)` | `scripts/a2c_new.py:303-307` |
| Why 50 slots → 32 seeds | bases {1009,1013,1019,1021,1031} + episode 0..9 produce overlapping windows; union = 1009..1040 = 32 values, 18 exact repeats per unit | `experiments/rigorous_manifest.json` `evaluation.seeds`; `reproducibility/docs/seed_provenance.md` |

Checkpoints: `results/rigorous/artifacts/<run>/checkpoints/model.zip` (SB3 zip, 12-D obs for H0/H1),
50 episode rows each in `episodes.csv`, 50 trajectory `.npz` each.

## 2. Reviewer issue → experiment/change mapping

| # | Reviewer issue | Response experiment | Priority | Status |
|---|---|---|---|---|
| 1 | H0−H1 confounds APF with privileged obstacle information; requested an A2C baseline WITH obstacle info and WITHOUT APF | **H3 geometry-aware A2C** (68-D obs = 12-D base + 56-D padded raw AABB geometry; no APF force, no blend) | P0 | training RUNNING |
| 2 | H2's 55/1000 may be an artifact of center-distance + d0 = 6 | **APF sensitivity**: basis {center, surface} × d0 {4,6,8,12}, all 8 reported | P0 | DONE (aggregating) |
| 3 | Ceiling effect on 4 fixed maps; requested held-out layouts and/or wind intensities | **wind sweep** {0,0.5,1,1.5,2} on frozen policies + **held-out maps** (4 new procedural seeds) | P0/P1 | DONE / DONE (aggregating) |
| 4 | Adaptive vs fixed blending | Deferred (P2). If time remains: evaluation-time blend sensitivity, labelled as such, NOT a causal ablation | P2 | not started |
| 5a | "trajectory variation" wording | manuscript wording change (section 11) | — | planned |
| 5b | evaluation-seed pseudoreplication | **unique 50-seed schedule 2001–2050**, shared across configs; FAIR numbers kept separate | P0 | DONE (aggregating) |
| 5c | log A2C/APF action components | **action logging** on H0 with mechanistic diagnostics only | P1 | DONE (aggregating) |
| 5d | reproducibility | this manifest + per-run JSON/CSV + launcher scripts; parent package already 69/69 reconciled | — | DONE |
| R2 | null results on efficiency/clearance/speed | preserved verbatim; not hidden | — | enforced in wording rules |

## 3. Exact new configurations

Controller matrix (makes the asymmetry visible, per brief O):

| Config | Learned? | Geometry to learned policy? | Geometry to APF? | APF analytical action? | Adaptive blend? | Budget |
|---|---|---|---|---|---|---|
| H0 hybrid | yes (A2C) | **no** | yes (centers) | yes | yes λ∈[0.15,0.55] | 5M/unit |
| H1 A2C-only | yes (A2C) | **no** | no | no | no | 5M/unit |
| H2 APF-only | no | n/a | yes (grid) | yes (grid) | n/a (weight 1) | 0 |
| H3 A2C-Geo | yes (A2C) | **yes (68-D raw padded)** | no | no | no | 5M/unit |

H3 observation spec (Option A): per obstacle slot, sorted by distance to UAV ascending,
`[rel_center/300 (3), half_extents/300 (3), valid (1)]`, K = 8 slots, zero-padded; concatenated after the
12-D base vector. Raw geometry only — the APF resultant is **never** an observation.

## 4. Exact seed protocol

- Training seeds (H3): 101, 211, 307, 401, 503 (same labels as FAIR; new models).
- Evaluation: `numerical_seed = base + episode`, bases {2001, 2011, 2021, 2031, 2041}, episode 0..9
  ⇒ **50 unique seeds 2001–2050**, identical set for H0/H1/H2/H3 and for every wind scale, so pairing is meaningful.
- Inference unit remains `(map_id, training_seed)`; rollouts are descriptive only. Wilson intervals descriptive only.
- Seeding improvements vs FAIR: H3 additionally calls `model.set_random_seed(seed)` (explicit torch seeding).
  Bitwise determinism is **not** claimed for FAIR models (unchanged); H3 seeding is documented per run JSON.

## 5. Runtime / training budget

Measured 2983 steps/s per job (OMP=4). H3 = 20 units × 5M steps ≈ 9.3 h serial; launched 6-way parallel
(`scripts/icai2026_train_h3.sh`, 24 of 32 logical cores). Frozen-policy evaluations run in a separate
single process with OMP=4 (`scripts/icai2026_run_cheap.sh`) so they never block on H3.

## 6. New results

> Filled from `results/icai2026/**/*.csv` as jobs finish. FAIR numbers are reported separately and are NOT overwritten.

### 6.1 Corrected-seed re-evaluation (H0/H1, wind 1.0) — DONE
Source: `results/icai2026/icai_eval_unique/icai_eval_unique_H0_H1.csv` (50 unique seeds 2001–2050 per unit).

| Config | Random | Corridor | Barrier | Mixed | Total |
|---|---|---|---|---|---|
| H0 | 250/250 | 250/250 | 250/250 | 250/250 | **1000/1000** |
| H1 | 157/250 | 241/250 | 200/250 | 250/250 | **848/1000** (36 coll, 107 timeout) |
| FAIR (old 32-seed schedule) | 140/250 | 240/250 | 200/250 | 250/250 | 830/1000 |

**Answer to S.1: yes.** With corrected unique seeds the H0−H1 reliability gap is −15.2 percentage points
(mean paired difference H1−H0 = −0.152, Cohen d_z = −0.491, two-sided Wilcoxon signed-rank p = 0.0156,
n = 20 units, 7 non-zero pairs). The gap is slightly smaller than FAIR's −17 pp (p = 0.0273) but the
conclusion is unchanged. H1's per-unit rates on `map-random-01` remain bimodal (0.02–0.98), i.e. the
failure structure is seed/model-dependent, not uniform.

### 6.2 Wind stress test — DONE (frozen policies, 1000 rollouts per config x scale)
Source: `results/icai2026/icai_wind_sweep/icai_wind_sweep_H0_H1.csv`; scale 1.0 from 6.1.
Wind rule: the whole wind velocity vector (base + gust) is multiplied by `wind_scale` every step
(`DroneEnv3D.wind_multiplier`); 1.0 reproduces the FAIR setting exactly.

| wind_scale | H0 success | H0 coll | H0 timeout | H1 success | H1 coll | H1 timeout |
|---|---|---|---|---|---|---|
| 0.0 | 1000/1000 | 0 | 0 | 845/1000 | 55 | 100 |
| 0.5 | 1000/1000 | 0 | 0 | 837/1000 | 50 | 113 |
| 1.0 | 1000/1000 | 0 | 0 | 848/1000 | 36 | 107 |
| 1.5 | 995/1000 | 5 | 0 | 848/1000 | 49 | 103 |
| 2.0 | 986/1000 | 14 | 0 | 866/1000 | 49 | 85 |

**Answer to S.4 (descriptive only):** H0's ceiling breaks only at 1.5x (99.5%) and 2.0x (98.6%), and every
failure is a collision, never a timeout. H1 is essentially FLAT and non-monotone across scales
(84.5% -> 86.6%), i.e. H1's deficit is geometry/control-driven, not wind-driven. We may say
"completion reliability of the hybrid degrades gracefully up to twice the training wind intensity";
we may NOT say "robust to wind" without qualification, and no significance tests are attached to this sweep.

### 6.3 APF sensitivity — DONE (all 8 predeclared settings reported; 200 rollouts each over 4 maps)
Source: `results/icai2026/icai_apf_sensitivity/apf_sensitivity.csv`.

| basis | d0 (m) | success/200 | collision | timeout | SR |
|---|---|---|---|---|---|
| center | 4 | 21 | 172 | 7 | 0.105 |
| center | 6 | 21 | 172 | 7 | 0.105 |
| center | 8 | 21 | 172 | 7 | 0.105 |
| center | 12 | 21 | 172 | 7 | 0.105 |
| surface | 4 | 88 | 0 | 112 | 0.440 |
| surface | 6 | 88 | 0 | 112 | 0.440 |
| surface | 8 | 85 | 0 | 115 | 0.425 |
| surface | 12 | 85 | 0 | 115 | 0.425 |

**Answer to S.6: yes, largely an implementation artifact — but the corrected controller is still insufficient.**
With center-distance the repulsive term is effectively DEAD on these maps: results are bit-identical across
d0 = 4..12 (repulsion never activates within d0 of any box center along the flown path), and 86% of episodes
end in collision. Switching to nearest-surface distance removes collisions ENTIRELY (0/200) and quadruples
success (0.105 -> 0.440), but the remaining 56% of failures are timeouts: surface-based APF-only stagnates.
Per-map detail (success of 50): surface d0=6 gives barrier 22, corridor 19, mixed 23, random 24, versus
center d0=6 giving 6, 0, 3, 12. Conclusion for the manuscript: H2's FAIR number (55/1000) measured a broken
distance convention, not the ceiling of potential-field guidance; APF-only remains an insufficient planner
(stagnation), which is the claim we can defend.

### 6.4 Held-out maps — DONE (250 rollouts per config x map; models frozen)
Source: `results/icai2026/icai_heldout/icai_heldout_H0_H1.csv`.
Protocol: each held-out layout is evaluated with the model trained on the SAME-LAYOUT training map
(e.g. random-01 model on random-ho1); H0 receives the new geometry through APF, so this is
controller-level transfer with map geometry available, NOT obstacle-free zero-shot generalization.

| held-out map | H0 success | H0 coll | H1 success | H1 coll |
|---|---|---|---|---|
| random-ho1 | 250/250 | 0 | 144/250 | 49 |
| corridor-ho1 | 250/250 | 0 | 241/250 | 9 |
| barrier-ho1 | 250/250 | 0 | 200/250 | 0 |
| mixed-ho1 | **50/250** | **200** | **0/250** | **250** |

**Answer to S.5: NO, not uniformly.** Transfer holds on three of four unseen families (H0 100%), but the
unseen mixed layout collapses both controllers (H0 20%, H1 0%, all collisions). The hybrid degrades less
catastrophically than A2C-only on that layout, but a 200/250 collision rate on one unseen family forbids any
generalization claim. This is a headline negative result and must appear in the abstract-level limitations.

### 6.5 H3 geometry-aware A2C — DONE (20 units trained, 5M steps each, mean 2281 s/unit)
Sources: `results/icai2026/h3_train/` (20 checkpoints + per-run JSON),
`results/icai2026/icai_eval_unique_h3/icai_eval_unique_h3_H3.csv`,
`results/icai2026/icai_wind_sweep_h3/…`, `results/icai2026/icai_heldout_h3/…`.

Train maps, corrected seeds (success/250 per map):

| Config | random-01 | corridor-01 | barrier-01 | mixed-01 | Total |
|---|---|---|---|---|---|
| H0 | 250 | 250 | 250 | 250 | **1000/1000** |
| H3 | 233 | 250 | 222 | 233 | **938/1000** (62 coll, 0 timeout) |
| H1 | 157 | 241 | 200 | 250 | **848/1000** |

Paired inference on 20 (map, seed) units (corrected seeds):

| Contrast | Success diff | d_z | p | Jitter diff | d_z | p |
|---|---|---|---|---|---|---|
| H3 − H1 | +0.090 | +0.276 | 0.250 | −1.13 | −0.07 | 0.898 |
| H0 − H3 | +0.062 | +0.410 | 0.125 | −26.11 | −1.97 | <0.001 |
| H0 − H1 | +0.152 | +0.491 | 0.016 | −27.24 | −1.75 | <0.001 |

**Answers S.2 / S.3.** The 15.2-pp H0−H1 reliability gap decomposes additively into +9.0 pp associated with
obstacle information (H3−H1) and +6.2 pp associated with the analytic APF channel (H0−H3); **neither component
is individually significant at n = 20**, only the total is. By contrast, the trajectory-variation benefit does
NOT decompose this way: H0−H3 jitter/acceleration remain large and highly significant (d_z −1.97 / −4.08)
while H3−H1 is null (d_z −0.07 / +0.27, p ≈ 0.90). Interpretation: obstacle awareness accounts for most of the
point-estimate reliability gain, whereas the distinctive, statistically supported contribution of the analytic
channel is damping of sampled trajectory variation. H3 failures are 100% collisions (0 timeouts), a different
failure signature from the timeout-heavy barrier/random profile of H1.

### 6.6 Action-component diagnostics — DONE (H0, 1000 episodes, step-level logs)
Source: `results/icai2026/icai_action_log/icai_action_log_H0.csv`. Mechanistic diagnostics only.

| diagnostic (per-episode mean of step values) | mean | sd |
|---|---|---|
| ‖a_A2C‖ | 1.458 | 0.132 |
| ‖a_APF‖ | 0.0400 | 0.0000 |
| λ_t | 0.375 | 0.029 (episode-mean range 0.324–0.463) |
| cosine(a_A2C, a_APF) | 0.545 | 0.054 |
| ‖Δ blended action‖ per step | 0.130 | 0.031 |

Key mechanistic observation: ‖a_APF‖ equals the attractive gain k_att = 0.04 with zero variance, i.e. during
successful H0 flights the repulsive term essentially never activates (consistent with 6.3: center-distance
repulsion is dead on these maps). The APF channel therefore contributes a small, steady, goal-directed bias
blended at λ ≈ 0.37, moderately aligned with the policy action (cosine 0.55). This is consistent with — but
does not prove — the hypothesis that the channel damps abrupt policy commands; a causal claim would require
the fixed-lambda / no-attraction ablations that remain out of scope.

### 6.7 Evaluation-time blend sensitivity (fixed λ) — DONE, labelled as sensitivity not causal ablation
Source: `results/icai2026/icai_fixed_lambda_0.15|0.35|0.55/…csv`. Frozen H0 policies (trained under the
adaptive schedule) re-evaluated with a constant blend weight:

| blend | success/1000 | collision | timeout | corridor success/250 |
|---|---|---|---|---|
| adaptive (as trained) | 1000 | 0 | 0 | 250 |
| fixed λ = 0.15 | 990 | 6 | 4 | 246 |
| fixed λ = 0.35 | 795 | 157 | 48 | 172 |
| fixed λ = 0.55 | 606 | 390 | 4 | **0** |

Monotone degradation with constant weight, and total corridor collapse at λ = 0.55, indicate that the
distance-adaptive schedule matters at deployment time. Because the policies were trained under the adaptive
schedule, this is **evaluation-time blend sensitivity**, not a causal ablation of adaptive blending (brief K).

## 7. Statistical analysis plan (predeclared)

- H0−H1, H0−H3, H3−H1: two-sided Wilcoxon signed-rank on the 20 `(map, seed)` units; Cohen d_z; exact p.
- Efficiency paired on units with successes in both arms (n reported per metric).
- Wind sweep and held-out: descriptive per-config curves and per-map/per-model summaries; no post-hoc test family.
- No multiplicity correction is applied; all six-plus component metrics are labelled exploratory, as in FAIR.
- No metric shopping: every predeclared metric is reported for every predeclared configuration.

## 8. Unexpected / negative results

- **Held-out mixed family collapses every controller**: mixed-ho1 gives H0 50/250, H3 17/250, H1 0/250, all
  collisions, although all three reach 233–250/250 on the TRAINING mixed map. A single unseen layout family
  therefore invalidates any generalization claim; reported as a headline limitation.
- **Center-distance repulsion is dead on the evaluated maps**: APF-only results are identical for
  d0 = 4/6/8/12 (21/200), i.e. the repulsive term never activates; the FAIR H2 number measured a broken
  distance convention. Nearest-surface APF removes all collisions (0/200) but times out in 56% of episodes.
- **H3 does not significantly beat H1 on success** (p = 0.250) despite a +9 pp point estimate; the reliability
  decomposition is therefore reported as point estimates with explicit non-significance.
- **Fixed-λ deployment collapses corridor performance** (0/250 at λ = 0.55) even though the same policies reach
  250/250 under the adaptive schedule.
- All FAIR null results (efficiency, clearance, steps) are carried forward unchanged.
- Environment corruption (mpmath) discovered and fixed; recorded because it blocked all computation.

## 9. Claims now supported / still unsupported

Supported (under the evaluated simulator and protocol):
- With corrected unique seeds, the hybrid completes more rollouts than obstacle-blind A2C (−15.2 pp, p = 0.016).
- Most of that reliability point-estimate is associated with obstacle information available to the controller
  (H3 recovers +9.0 pp of it); the residual analytic-channel reliability increment (+6.2 pp) is NOT significant.
- The statistically supported contribution of the analytic channel is lower sampled trajectory variation
  (H0−H3 jitter d_z = −1.97, accel d_z = −4.08, p < 0.001), and this is NOT explained by obstacle information
  (H3−H1 null).
- Frozen-hybrid reliability degrades gracefully up to twice the training wind intensity (98.6% at 2.0x).
- APF-only failure in FAIR was largely an implementation artifact (center distance); surface-based APF-only
  still stagnates (44% success, 0 collisions).
- The adaptive blend schedule matters at deployment time (evaluation-time sensitivity).

Still unsupported (and stated as such):
- Any claim that APF computation alone improves completion reliability (residual ns at n = 20).
- Generalization to unseen layouts (mixed-ho1 collapse).
- Physical flyability, actuator feasibility, comfort (finite-difference metrics only).
- Causal attribution of variation damping to the blend (no fixed-λ training ablation; P2 dropped).
- Superiority over PPO/SAC/RRT; shorter, clearer or faster successful paths.

## 10. Remaining threats to validity

- H3's padded geometry is a different representation than APF's center distances: H0−H3 still differs in HOW
  geometry enters (analytic channel vs learned features); H3−H1 isolates obstacle information, H0−H3 isolates
  the analytic channel given geometry-aware learning only indirectly. Interpretation must state this.
- Held-out evaluation gives H0 the new geometry through APF: controller-level transfer, not obstacle-free generalization.
- Wind sweep scales the whole wind vector (base + gust) with one factor; it is a stress test, not a calibrated turbulence study.
- Point-mass dynamics, 1-m altitude slab, finite-difference trajectory-variation metrics: unchanged from FAIR.
- H3 with 5 seeds × 5M steps matches FAIR budget; if any unit fails to finish before deadline, H3 is downgraded to
  3 seeds and labelled an exploratory matched-information ablation (brief E).

## 11. Manuscript wording recommendation (draft, to finalize with results)

- Use "sampled trajectory variation", never "physical stability".
- H3 completed robustly (20 units, full 5M budget) and the decomposition was measured, so the title
  **"Disentangling Obstacle Information and APF Guidance in Hybrid A2C-APF UAV Navigation under Wind"** is used.
- The honest headline is: most of the reliability point-estimate is associated with obstacle information
  (neither component significant alone), while the statistically supported contribution of the analytic channel
  is reduced sampled trajectory variation.
- H4 removed as a named configuration; one-line note at most.
- Controller matrix table (section 3) goes into the paper verbatim.

## 13. Answers to the final scientific questions (brief S)

1. **H0−H1 with corrected unique seeds?** Yes: −15.2 pp, d_z = −0.491, Wilcoxon p = 0.0156 (n = 20).
2. **How much does H3 recover relative to H1?** +9.0 pp point estimate (59% of the gap), d_z = 0.276, p = 0.250 — not significant.
3. **Incremental benefit of APF beyond sensing?** Reliability: +6.2 pp, p = 0.125 — not significant.
   Trajectory variation: yes, large and significant (jitter d_z = −1.97, accel d_z = −4.08, p < 0.001), with H3−H1 null.
4. **H0 outside default wind?** Yes, gracefully: 100 / 100 / 99.5 / 98.6% at scales 0 / 0.5–1.0 / 1.5 / 2.0;
   H3 declines more (96.9 → 91.5%), H1 flat.
5. **Reliability on unseen layouts?** On 3 of 4 families yes (H0 100%, H3 89–100%); on mixed-ho1 no (H0 20%, H3 7%, H1 0%).
6. **APF-only sensitivity to d0 and distance basis?** d0 irrelevant under center distance (identical 21/200 for 4–12 m);
   basis decisive: surface removes all collisions and quadruples success (88/200) but leaves 56% timeouts.
7. **Reviewer status:** #1 resolved (H3 + decomposition); #2 resolved (full grid reported); #3 mitigated
   (wind sweep + held-out; the ceiling on train maps remains for H0); #4 addressed as evaluation-time sensitivity
   (causal training ablation remains open, P2 dropped); #5 resolved (unique seeds, action logs,
   "trajectory variation" wording, reproducibility manifest).

## 12. Reproducible commands

See `experiments/icai2026_manifest.json` → `commands`, plus launchers
`scripts/icai2026_train_h3.sh` and `scripts/icai2026_run_cheap.sh`.
Logs: `results/icai2026/logs/h3_train.log`, `results/icai2026/logs/cheap.log`.
