# REPORT — ICAI-FAI 2026 revision (AUDITED, STORY-LOCKED)

Deadline: 2026-09-30. Parent protocol: `vnict-rigorous-2026` (FAIR 2026, rejected). Frozen artifacts: `results/rigorous/` (read-only).
Pre-audit snapshot preserved at `REPORT_ICAI2026_REVISION.pre-audit.md`.

## 0. AUDIT STATUS and SOURCE-OF-TRUTH hierarchy

Audit executed 2026-09-28: full numerical reconciliation (150 automated checks, 0 failures), direct APF
activation measurement, H3 representation audit, status hygiene, and wording audit.
Checker: `scripts/icai2026_consistency_check.py` → `results/icai2026/consistency_check.json`
(currently **150 PASS / 0 FAIL**). Master numbers: `results/icai2026/MASTER_RESULTS.json`.
Every manuscript number must be copied from MASTER_RESULTS.json or from the tables below, never from prose.

Priority order when sources disagree (brief B):
1. raw machine-readable CSV/JSON in `results/icai2026/`;
2. per-run ledgers / trajectory logs / action logs;
3. analysis scripts recomputing statistics (`icai2026_analyze.py`, `icai2026_consistency_check.py`);
4. `experiments/icai2026_manifest.json`;
5. this report;
6. ICAI manuscript;
7. FAIR manuscript.
FAIR numbers and ICAI numbers are kept separate everywhere; FAIR values are labelled "FAIR (old schedule)".

## 1. Repository and implementation facts

- Canonical interpreter: `C:\Users\N4G\AppData\Local\Programs\Python\Python313\python.exe`
  (torch 2.6.0+cu124, SB3 2.7.0, gymnasium 1.2.0, numpy 2.1.1). The PATH-default python 3.14 has no torch.
- Environment repair performed during this revision: Python313 `mpmath` was corrupted
  (missing `libmp/gammazeta.py`), breaking `import torch`; fixed by
  `pip install --force-reinstall --no-deps mpmath==1.3.0`; verified by exact ledger replay of an H0 checkpoint.
- Obstacles per map: random 6, corridor 8, barrier 2, mixed 6 (`build_map`, `scripts/run_rigorous_manifest.py`).
- AABBs stored as dicts of `(x, y, z)` interval tuples; K = 8 padded slots cover every training and held-out map.
- Measured training throughput 2983 steps/s per job at OMP=4 (≈28 min per 5M-step unit solo; 2192 steps/s and
  ≈38 min/unit under 6-way contention). H3: 20/20 units completed, mean 2281.5 s/unit.
- APF distance/d0: `scripts/a2c_new.py:194-212` (center basis, d0 default 6). λ: `a2c_new.py:303-307`.
- FAIR 50→32 seed collapse: bases {1009,1013,1019,1021,1031} + episode 0..9 overlap; union 1009..1040.

## 2. Reviewer issue → experiment mapping (internal; must NOT appear in the manuscript)

| # | Reviewer issue | Experiment | Priority | Status |
|---|---|---|---|---|
| 1 | H0−H1 confounds APF with privileged obstacle information | H3 geometry-aware A2C, no APF | P0 | complete |
| 2 | H2 baseline questionable; d0/distance sensitivity requested | basis × d0 grid, all 8 reported | P0 | complete |
| 3 | Ceiling on 4 fixed maps; held-out / wind requested | wind sweep + same-family held-out | P0/P1 | complete |
| 4 | Adaptive vs fixed blending | evaluation-time blend sensitivity (labelled) | P2 | complete as sensitivity; causal training ablation dropped |
| 5 | Wording, pseudoreplication, action logs, reproducibility | unique seeds 2001–2050; step-level logs; manifest + checker | — | complete |

## 3. Configurations and the H3 representation

| Config | Learned? | Geometry to learned policy | Geometry to APF | APF analytical action | Adaptive blend | Budget |
|---|---|---|---|---|---|---|
| H0 hybrid | A2C | no | centers | yes | yes | 5M/unit |
| H1 blind | A2C | no | no | no | no | 5M/unit |
| H2 APF-only | no | n/a | grid | yes (grid) | n/a | 0 |
| H3 geometry-aware | A2C | yes, 68-D padded raw AABB | no | no | no | 5M/unit |

H3 observation = 12-D base + 56-D geometry block: K = 8 slots sorted ascending by distance from the UAV to each
obstacle center; per slot rel_center/300 (3), half_extents/300 (3), validity mask (1); unused slots zero with
mask 0. Raw geometry only — no APF force enters the observation. Terminology: **geometry-aware A2C baseline**;
it is NOT "perfectly information-matched" to H0 (different representation and different computation path).
Representation audit (section 8) documents per-timestep re-sorting and measured slot-permutation rates.

## 4. Seed protocol (corrected)

Evaluation seeds = base + episode with bases {2001, 2011, 2021, 2031, 2041}, episodes 0..9 ⇒ 50 unique seeds
(2001–2050) per unit, shared across configurations and wind scales. Training seeds 101/211/307/401/503.
Inference unit = (map, training run); rollouts are descriptive only; Wilson intervals descriptive only;
p-values exploratory, uncorrected, reported with exact values and Cohen's d_z. H3 additionally calls the library
seed setter (explicit torch seeding). Bitwise determinism is not claimed for FAIR checkpoints.

## 5. Runtime

H3: 20 units × 5M steps, 6-way parallel, ≈2.3 h wall. Frozen-policy evaluations: minutes each.
Fixed-λ sensitivity: 3 × 1000 episodes. Activation measurement: 4000 replayed episodes, evaluation-only.

## 6. Master result tables (corrected; conservative interpretation)

### 6.1 Corrected-seed outcomes, training maps (1000 rollouts per configuration)

| Config | random-01 | corridor-01 | barrier-01 | mixed-01 | Total (succ/coll/timeout) |
|---|---|---|---|---|---|
| H0 | 250/250 | 250/250 | 250/250 | 250/250 | 1000 / 0 / 0 |
| H3 | 233/250 | 250/250 | 222/250 | 233/250 | 938 / 62 / 0 |
| H1 | 157/250 | 241/250 | 200/250 | 250/250 | 848 / 45 / 107 |
| FAIR (old 32-seed schedule) | 140 | 240 | 200 | 250 | 830 / 58 / 112 |

Arithmetic verified: 848 + 45 + 107 = 1000; 938 + 62 + 0 = 1000. (The pre-audit report carried a wrong H1
collision total of 36; see correction log, C-1.)

### 6.2 Paired unit-level contrasts (20 units; efficiency 19–20)

| Contrast | metric | diff | d_z | p | reading |
|---|---|---|---|---|---|
| H0−H1 | success | +0.152 | +0.491 | 0.0156 | supported |
| H0−H1 | jitter | −27.237 | −1.746 | <0.001 | supported |
| H0−H1 | acceleration | −6.900 | −1.098 | 0.0049 | supported |
| H0−H1 | efficiency | −0.0057 | −0.060 | 0.768 | not supported |
| H0−H1 | clearance | −0.5627 | −0.066 | 0.927 | not supported |
| H0−H1 | steps | −128.495 | −0.293 | 0.143 | not supported |
| H3−H1 | success | +0.090 | +0.276 | 0.250 | not supported |
| H3−H1 | jitter | −1.125 | −0.070 | 0.898 | not supported |
| H3−H1 | acceleration | +1.9725 | +0.269 | 0.898 | not supported |
| H0−H3 | success | +0.062 | +0.410 | 0.125 | not supported |
| H0−H3 | jitter | −26.112 | −1.970 | <0.001 | supported |
| H0−H3 | acceleration | −8.8725 | −4.076 | <0.001 | supported |
| H0−H3 | steps | +26.865 | +1.372 | <0.001 | supported (H0 uses more steps) |

Interpretation (descriptive, not causal): the aggregate ordering is H1 < H3 < H0 in completion rate. The total
H0−H1 contrast is supported at the paired unit level; the two intermediate contrasts are not individually
significant. This is a **descriptive partition of the observed point-estimate gap** across obstacle-blind,
geometry-aware, and analytical-hybrid configurations — not a causal decomposition. The strongest statistically
supported effect associated with the analytical hybrid channel is reduced **sampled trajectory variation**
(finite-difference jerk and acceleration), and that effect survives information matching (H0−H3 significant,
H3−H1 null).

### 6.3 Wind stress test (frozen policies; 1000 rollouts per config × scale)

| wind_scale | H0 | H3 | H1 |
|---|---|---|---|
| 0.0 | 1000 (0 coll) | 969 (31) | 845 (55) |
| 0.5 | 1000 (0) | 961 (39) | 837 (50) |
| 1.0 | 1000 (0) | 938 (62) | 848 (45) |
| 1.5 | 995 (5) | 926 (74) | 848 (49) |
| 2.0 | 986 (14) | 915 (85) | 866 (49) |

Scaling rule: the whole wind velocity vector (base + gust) multiplied by wind_scale each step; 1.0 reproduces
the training setting. Narrow reading: the frozen hybrid shows graceful completion degradation over the tested
range up to 2× nominal; H3 declines monotonically; **H1 shows no monotonic degradation over the tested wind
scaling, so increased wind magnitude alone does not explain its lower completion rate in this experiment.**
No robustness claim beyond the tested range.

### 6.4 APF-only sensitivity (200 rollouts per setting; all 8 predeclared settings)

| basis | d0 (m) | success | collision | timeout |
|---|---|---|---|---|
| center | 4 / 6 / 8 / 12 | 21 each | 172 each | 7 each |
| surface | 4 | 88 | 0 | 112 |
| surface | 6 | 88 | 0 | 112 |
| surface | 8 | 85 | 0 | 115 |
| surface | 12 | 85 | 0 | 115 |

The center-distance repulsive term was **never activated** under the evaluated trajectories (section 7), which
explains the d0-invariance. With the surface basis, **no collisions were observed in 200 evaluated rollouts**,
but 56–57.5% of episodes time out: APF-only remains an insufficient planner (stagnation). The FAIR H2 figure
(55/1000) therefore measured a distance convention under which repulsion never engaged, not a property of
potential-field guidance in general.

### 6.5 Same-family held-out layouts (250 rollouts per config × map; models frozen)

Each held-out layout is evaluated with the model trained on the training map of the same family. H0 receives
held-out geometry through APF and H3 through its observation: this is controller-level transfer with map
geometry available, not obstacle-free zero-shot navigation.

| held-out map | H0 | H3 | H1 |
|---|---|---|---|
| random-ho1 | 250/250 (100.0%) | 203/250 (81.2%) | 144/250 (57.6%) |
| corridor-ho1 | 250/250 (100.0%) | 250/250 (100.0%) | 241/250 (96.4%) |
| barrier-ho1 | 250/250 (100.0%) | 222/250 (88.8%) | 200/250 (80.0%) |
| mixed-ho1 | **50/250 (20.0%)** | **17/250 (6.8%)** | **0/250 (0.0%)** |

Transfer is strongly layout-dependent. The mixed-family collapse (all failures collisions, despite 233–250/250
on the training mixed map) rules out any generalization claim and is retained as a headline negative result.

### 6.6 Evaluation-time blend sensitivity (fixed λ; frozen H0 policies)

| blend | success/1000 | collision | timeout | corridor success/250 |
|---|---|---|---|---|
| adaptive (as trained) | 1000 | 0 | 0 | 250 |
| fixed 0.15 | 990 | 6 | 4 | 246 |
| fixed 0.35 | 795 | 157 | 48 | 172 |
| fixed 0.55 | 606 | 390 | 4 | 0 |

Label: **evaluation-time blend sensitivity**. Policies were trained under the adaptive schedule, so this is not
a causal ablation of adaptive blending; it supports only the narrower observation that deployment-time behavior
is sensitive to the blend weight.

### 6.7 Action-component diagnostics (H0, 1000 episodes, step-level)

| diagnostic | mean | sd |
|---|---|---|
| ‖a_A2C‖ | 1.4582 | 0.1321 |
| ‖a_APF‖ | 0.0400 | 0.0000 |
| λ_t | 0.3746 | 0.0293 |
| cosine(a_A2C, a_APF) | 0.5452 | 0.0542 |
| ‖Δ blended‖ per step | 0.1299 | 0.0312 |

‖a_APF‖ equals the attractive gain k_att = 0.04 with zero variance: on successful H0 flights the analytical
channel contributes a steady goal-directed bias; the repulsive component contributes nothing measurable
(confirmed directly in section 7).

## 7. APF repulsion activation — direct measurement (brief F)

Method: evaluation-only replay of frozen controllers; at every timestep the repulsive vector is recomputed for
the stated basis at d0 = 6 m and flagged active when ‖F_rep‖ > ε with ε = 1e-8 (a looser threshold at 1% of
k_att, 4e-4, gives the same zeros for the center basis). Source: `results/icai2026/apf_activation.json`,
script `scripts/icai2026_apf_activation.py`.

| group | timesteps | active | fraction | episodes with ≥1 activation |
|---|---|---|---|---|
| H0 trajectories, center basis | 103,682 | 0 | 0.000 | 0 / 1000 |
| H0 successful timesteps, center | (subset) | 0 | 0.000 | — |
| H2 trajectories, center basis | 475,015 | 0 | 0.000 | 0 / 1000 |
| H2 trajectories, surface basis | 1,324,280 | 404,615 | 0.3055 | 945 / 1000 |
| H0 trajectories, surface basis (COUNTERFACTUAL) | 103,682 | 2,103 | 0.0203 | 549 / 1000 |

Per-map and per-seed rates are in the JSON (all zero for the center basis). Conclusion, stated at the measured
strength: **the center-distance repulsive term was never activated under the evaluated trajectories**, on both
H0 and H2 paths; the surface-distance variant activates on ~30.6% of H2 timesteps and would have activated on
~2.0% of H0 timesteps (54.9% of episodes) had it been the shipped basis. The hybrid's nominal-map behavior is
therefore driven by its attractive bias and adaptive weighting, not by obstacle repulsion. The label
"A2C–APF obstacle-avoidance hybrid" overstates what the APF channel does on these maps: it is an
attractive-bias guidance channel whose repulsion is inactive under the evaluated geometry and trajectories.

## 8. H3 representation audit (brief G)

Source: `results/icai2026/h3_representation_audit.json`, script `scripts/icai2026_h3_audit.py`.
- K = 8; slot = [rel_center/300 (3), half_extents/300 (3), valid (1)]; zero padding with valid = 0;
  sorting by distance to obstacle center, ascending; re-sorted at every timestep (computed inside `_obs`).
- All training and held-out maps have ≤ 8 obstacles (max 8, corridor), so no obstacle is ever dropped and no
  K-boundary truncation occurs; slot changes are within-top-K permutations.
- Observation space is `Box(-inf, +inf, (68,))`; SB3 MlpPolicy does not normalize inputs. Measured component
  ranges per map are in the JSON (rel-center components within ±1.12, extents ≤ 0.07, mask ∈ {0,1}).
- Slot-permutation (discontinuity) rates over replayed H3 episodes: random-01 16.5%, corridor-01 18.6%,
  barrier-01 3.0%, mixed-01 16.8% of compared timesteps. Because the MLP is not permutation-invariant, the
  observation is discontinuous when two obstacle distances cross. This is a representation artifact, not a
  physical event.
- Threat-to-validity statement: H3 is a geometry-aware A2C baseline whose observation is permutation-discontinuous
  at distance crossings and whose geometry encoding differs from H0's analytic center-distance channel; H0−H3
  contrasts therefore compare different representations as well as different controllers. No retraining was
  performed for this audit, per the brief.

## 9. Statistical analysis plan (predeclared, unchanged)

Paired two-sided Wilcoxon signed-rank on (map, training-run) units; Cohen's d_z; exact p; efficiency paired on
units with successes in both arms; wind and held-out suites descriptive only; no post-hoc test families;
no multiplicity correction (labelled exploratory); no metric shopping.

## 10. Correction log

| ID | old value | corrected value | source artifact | reason |
|---|---|---|---|---|
| C-1 | H1 corrected-seed collisions = 36 (report 6.1 total) | 45 | `icai_eval_unique/icai_eval_unique_H0_H1.csv` | 36 is the random-map-only collision count; it was promoted to the total during manual table entry. Per-map values were already correct (36+9+0+0 = 45). |
| C-2 | "H3 89–100%" on non-collapsed held-out families | 81.2–100.0% (203/250, 250/250, 222/250) | `icai_heldout_h3/icai_heldout_h3_H3.csv` | 203/250 = 81.2%, not 89%; range mis-stated in pre-audit section 13. |
| C-3 | statuses "RUNNING / DONE (aggregating) / PENDING" | final states (complete) | job logs + CSV presence | stale labels left from the execution phase. |
| C-4 | "decomposes additively", "accounts for most", "59%" | descriptive partition language; components labelled non-significant | paired stats in MASTER_RESULTS.json | wording overstated causal separation. |
| C-5 | "broken distance convention", "removes collisions entirely" | "repulsive term never activated under the evaluated trajectories"; "no collisions observed in 200 evaluated rollouts" | `apf_activation.json`, sensitivity CSV | mechanism now directly measured; guarantee-language removed. |
| C-6 | "H1 deficit is geometry/control-driven, not wind-driven" | "H1 shows no monotonic degradation over the tested wind scaling…" | wind CSV | causal inference from a non-monotonic descriptive trend. |
| C-7 | "same-layout held-out maps" | "same-family held-out layouts" | manifest map specs | held-out maps are new layouts from the same family. |

Downstream occurrences of C-1: pre-audit report §6.1 total row only (manuscript table already used 45).
Downstream occurrences of C-2: pre-audit report §13 answer 5 only. Both fixed in this document; the manuscript
never contained either wrong value but does contain wording items C-4..C-7 (see removal/rewrite checklist).

## 11. Consistency checker

`python scripts/icai2026_consistency_check.py` recomputes every headline number from raw CSVs, checks
success+collision+timeout = n per group and per-map sums = totals, 50-unique-seed accounting per unit, paired
statistics against `stats_icai.json`, action-log summaries, activation zeros, and scans report+manuscript for
stale status, arithmetic, causal-overreach, APF/wind/held-out wording, and FAIR mentions. Current status:
**150 PASS / 0 FAIL**; warnings list = the wording/removal items tracked in sections 10 and 17.

## 12. Supported / unsupported / negative-null

Supported (under the evaluated simulator and protocol):
- H0 > H1 completion on corrected seeds (−15.2 pp, p = 0.0156) and lower sampled trajectory variation (p < 0.001).
- The variation effect survives information matching (H0−H3 significant; H3−H1 null).
- Graceful frozen-hybrid degradation to 2× nominal wind; deployment-time blend sensitivity.
- Center-distance repulsion inactive on evaluated trajectories (direct measurement); surface basis changes H2's
  failure mode from collision to stagnation.
Unsupported:
- Any causal claim that obstacle information or the analytic channel alone improves reliability (components ns).
- Generalization (mixed-family collapse); physical flyability; superiority over PPO/SAC/RRT; efficiency/clearance/steps gains.
Negative-null results retained visibly: H3−H1 null variation; H0−H3 ns success; held-out mixed collapse;
H2 surface stagnation; fixed-λ corridor collapse; all FAIR nulls (efficiency, clearance, steps).

## 13. Threats to validity

Information/representation mismatch (H0 analytic centers vs H3 padded raw boxes); permutation-discontinuous H3
observation; held-out transfer supplies geometry to H0/H3 channels; wind sweep is a one-factor stress test;
point-mass dynamics and 1-m altitude slab; finite-difference variation metrics are not actuator/comfort measures;
success-only efficiency/clearance survivor composition; exploratory uncorrected p-values; retraining not bitwise
reproducible; n = 20 units limits power for the intermediate contrasts (the non-significance of H3−H1 and H0−H3
may reflect power, not absence of effect — stated as such, never as evidence of equality).

## 14. Story memo (brief N)

1. FAIR claim: an APF-informed guidance channel inside a fixed A2C controller increased completion reliability
   and reduced sampled trajectory variation versus obstacle-blind A2C, with the information asymmetry disclosed.
2. Correct confound: H0−H1 mixed the analytic channel with privileged obstacle geometry.
3. H3 establishes: a geometry-aware, APF-free baseline sits between H1 and H0 in completion rate; obstacle
   information is associated with most of the point-estimate gap; the variation benefit of the hybrid survives
   information matching.
4. H3 does NOT establish: a significant reliability increment for either ingredient alone; causal attribution;
   equivalence of representations.
5. Strongest statistically supported new finding: H0−H3 reduction in sampled trajectory variation
   (jitter d_z = −1.97, acceleration d_z = −4.08, p < 0.001) with H3−H1 null — plus the direct measurement that
   center-distance repulsion never activates.
6. Mechanism of H0 on nominal maps: a steady attractive bias (‖a_APF‖ = k_att exactly) blended adaptively;
   repulsion inactive; deployment behavior sensitive to λ.
7. The label "A2C–APF obstacle-avoidance hybrid" is inaccurate for the nominal maps: avoidance (repulsion) does
   not engage; what engages is attraction plus adaptive weighting.
8. Surface-distance sensitivity reinterprets old H2: its collision catastrophe was a distance-convention artifact;
   with surface distance APF-only stops colliding but stagnates — APF-alone remains insufficient.
9. Wind sweep establishes narrowly: graceful frozen-hybrid degradation to 2× nominal; nothing about H1's deficit
   cause; nothing beyond the tested range.
10. Held-out mixed failure rules out layout generalization for all three controllers.
11. Nulls that must stay visible: component non-significance; H3−H1 variation null; mixed collapse; surface
    stagnation; fixed-λ collapse; FAIR efficiency/clearance/steps nulls.
12. Smallest defensible contribution set: (i) geometry-aware baseline + corrected-seed protocol; (ii) direct
    activation measurement showing the shipped repulsion is inactive; (iii) variation effect surviving
    information matching; (iv) sensitivity/held-out/wind evidence bounding all claims.

## 15. Three candidate framings (brief O)

A. Information-asymmetry / geometry-aware comparison. Question: how much of hybrid reliability is associated
with obstacle information? Evidence: H0/H1/H3 triangle. Strongest claim: descriptive partition with a
significant total and non-significant components. Limitation: components under-powered at n = 20; representation
mismatch. Interesting: rare matched-information ablation in RL navigation. Reviewer risk: "your headline
decomposition is not significant".
B. Empirical audit of hybrid RL + analytical guidance. Question: what does each ingredient of a shipped hybrid
actually do under measurement? Evidence: activation measurement (repulsion never fires), blend sensitivity,
variation effect surviving matching, sensitivity grid, held-out collapse. Strongest claim: the analytic channel's
measured contribution on nominal maps is an attractive bias plus adaptive weighting, and its statistically
supported benefit is reduced sampled trajectory variation. Limitation: single simulator family; audit is
descriptive by design. Interesting: implementation-level auditing is exactly the reproducibility critique line
(Henderson 2018) and is rare in UAV RL. Reviewer risk: "audit without a positive methodological contribution" —
mitigated by the protocol/checker artifacts.
C. Failure-mechanism / APF-distance-semantics study. Question: why does APF-only fail, and which convention
matters? Evidence: d0-invariance, zero center activation, surface zero-collision/stagnation, mixed-family
collapse. Strongest claim: distance semantics, not gain tuning, determine APF-only failure mode. Limitation:
narrow; says little about the hybrid. Interesting: clean mechanistic result. Reviewer risk: "incremental,
known APF weakness".
Recommendation: **B**, with A as its experimental spine and C as a results subsection. B matches what the data
actually support at significance level, minimizes claim stretching, keeps all negatives visible, and fits ICAI
topics (AI applications; autonomous systems) as a rigorous empirical study with reusable audit artifacts.

## 16. Title audit (brief P)

Current: "Disentangling Obstacle Information and APF Guidance in Hybrid A2C–APF UAV Navigation under Wind".
Reasons to retain: matches the three-way design; signals the matched-information contribution; keywords align
with ICAI topics. Reasons to soften: "disentangling" implies achieved causal separation, while the reliability
components are non-significant and H0/H3 consume geometry through different representations; the word invites
exactly the overclaim objection the audit removed elsewhere. Alternatives:
1. "An Empirical Audit of Obstacle Information and Analytical Guidance in Hybrid A2C–APF UAV Navigation under Wind"
2. "What Does the Analytical Channel Do? A Geometry-Aware Evaluation of Hybrid A2C–APF UAV Guidance under Wind"
3. "Component and Information Ablations for Hybrid A2C–APF UAV Guidance: Reliability, Trajectory Variation, and Failure Mechanisms"
4. "Reliability and Sampled Trajectory-Variation Effects of an APF Guidance Channel in Wind-Perturbed UAV Navigation"
5. "Geometry-Aware Baselines for Auditing Hybrid Reinforcement-Learning UAV Guidance under Wind"
Direction: 1 or 3 (audit vocabulary, no causal separation implied, no novelty language).

## 17. Manuscript rewrite checklist (execute only after approval)

1. Remove FAIR/reviewer/revision sentences: `main.tex` lines 66, 68, 70 (intro paragraph 2) — full list in
   `consistency_check.json` under `fair_mentions_in_manuscript`.
2. Replace causal wording: line 302 ("accounts for most…") → descriptive-partition phrasing; line 252
   ("removes collisions entirely") → "no collisions were observed in 200 evaluated rollouts"; line 278
   ("same-layout training map") → "training map of the same layout family"; line 232 wind sentence → the
   no-monotonic-degradation phrasing.
3. Insert activation-rate results (section 7 of this report) as a results subsection; relabel the APF channel's
   nominal-map role (attractive bias + adaptive weighting).
4. Insert H3 representation threat (permutation discontinuity, representation mismatch).
5. Pull every number from `MASTER_RESULTS.json`; re-run the checker after edits; verify ≤ 8 pages.
6. Adopt title direction 1 or 3; keep H4 removal note; keep all null results.

## 18. GO / NO-GO gate

**READY_FOR_MANUSCRIPT_REWRITE = YES.**
- Canonical headline numbers: H0 1000/1000, H3 938/1000, H1 848/1000 (corrected seeds); H0−H1 success +0.152
  (d_z 0.491, p 0.0156); H3−H1 +0.090 (p 0.250); H0−H3 +0.062 (p 0.125); H0−H3 jitter −26.11 (d_z −1.97,
  p < 0.001) and acceleration −8.87 (d_z −4.08, p < 0.001); H3−H1 variation null; activation 0/103,682 (H0 center);
  wind 100/100/100/99.5/98.6% (H0); held-out mixed 50/17/0 per 250; fixed-λ 990/795/606.
- Chosen framing: B (empirical audit), with A as experimental spine, C as subsection.
- Claim hierarchy: (1) variation effect surviving information matching; (2) direct activation measurement;
  (3) descriptive reliability ordering with significant total only; (4) bounded stress-test evidence;
  (5) all nulls visible.
- Title direction: audit vocabulary (alternative 1 or 3); current "Disentangling…" title to be softened.
- FAIR paper sections to retain: simulator/dynamics/reward specification, metric definitions, statistical
  protocol discipline, threats-to-validity style. To replace: abstract, intro framing, results narrative,
  discussion (all rewritten around the audit). ICAI draft sections to discard: intro paragraph 2 (rebuttal
  voice), any "disentangling/causal decomposition" phrasing, the H3 "89–100%" style summaries.
No manuscript rewrite is performed in this phase; awaiting explicit approval.

## Appendix — commands and inventory

Recompute everything: `python scripts/icai2026_consistency_check.py` (also rewrites MASTER_RESULTS.json).
Activation: `python scripts/icai2026_apf_activation.py`. H3 audit: `python scripts/icai2026_h3_audit.py`.
Figures: `python scripts/icai2026_figures.py`. Raw suites: `results/icai2026/icai_*/`.
Tables: `results/icai2026/tables/`. Logs: `results/icai2026/logs/`.
