# Manuscript Revision Plan

Precise, minimal edits. Do not silently rewrite the PDF; apply these in
`FAIR2026/ReviewPackage/Paper_Final/latex/vnict_hybrid_main.tex` and rebuild. Each item lists Location /
Original / Replacement / Reason / Evidence.

---

### R1 — Do not claim APF is isolated
- **Location:** Abstract + Results (H0–H1 framing)
- **Original text:** "...isolates the contribution of the APF component / measures the APF contribution by removing APF guidance."
- **Replacement text:** "...evaluates an APF-informed guidance channel together with its privileged obstacle-geometry input. Because the A2C observation carries no obstacle geometry, the H0–H1 contrast does not isolate potential-field computation from the value of the additional obstacle information."
- **Reason:** Information asymmetry — A2C observation is 12-D with no obstacle features; H0 gets geometry via APF, H1 does not.
- **Evidence:** `docs/experimental_design.md`; `tests/test_controller_semantics.py::test_observation_is_12d_no_obstacles`; governing principle 7.

### R2 — "matched A2C-only"
- **Location:** Methods / Results (H1 description)
- **Original text:** "matched A2C-only configuration"
- **Replacement text:** "budget- and protocol-matched A2C-only configuration (matched in training budget, maps, and evaluation realizations, but not in obstacle information)"
- **Reason:** H1 shares budget/maps/eval seeds with H0 but not obstacle geometry.
- **Evidence:** `docs/experimental_design.md`.

### R3 — "checkpoint" → independent training run/model
- **Location:** Protocol, tables, captions (every "checkpoint")
- **Original text:** "five checkpoints per map" / "map–checkpoint pairs"
- **Replacement text:** "five independently trained runs (models) per map" / "map–training-run pairs"
- **Reason:** The five objects are fresh models trained from distinct seeds, not periodic checkpoints of one run.
- **Evidence:** `train_model` re-seeds and trains from scratch; `docs/experimental_design.md`.

### R4 — Smoothness claim scope
- **Location:** Results / Discussion (jitter & acceleration)
- **Original text:** "smoother control / smoother flight."
- **Replacement text:** "lower finite-difference acceleration and jerk indices computed from sampled point-mass trajectories. These indices do not establish actuator feasibility, motor effort, attitude smoothness, passenger comfort, or physical flight readiness."
- **Reason:** Metrics are kinematic finite differences of a point-mass sim.
- **Evidence:** `jitter_index`/`acceleration_index` in `vnict_hybrid_experiments.py`; `docs/limitations.md`.

### R5 — Evidence-level labeling of outcomes
- **Location:** Results intro
- **Original text:** (implicit mixing of aggregate and paired claims)
- **Replacement text:** "Aggregate success/collision/timeout counts are rollout-level descriptive statistics over 1,000 rollouts per configuration; H0–H1 significance is paired inference over 20 (map, training-run) units."
- **Reason:** Separate evidence levels (principle 6).
- **Evidence:** `reports/result_reconciliation.md`; `analysis/02`.

### R6 — Prespecification / exploratory p-values
- **Location:** Statistics paragraph
- **Original text:** "significant / not significant" applied across all six metrics.
- **Replacement text:** "Primary outcomes were not prespecified as a confirmatory family; p-values across the six component metrics are reported as exploratory and are not multiplicity-corrected."
- **Reason:** No preregistration; six paired tests.
- **Evidence:** `data/derived/statistical_results.csv` (no correction applied).

### R7 — H4 to appendix
- **Location:** Wherever H4 appears as a result
- **Original text:** H4 presented alongside controllers.
- **Replacement text:** Move H4 to an appendix / supplementary paragraph described as "a numerical post-processing pipeline check (cubic-spline resampling of executed H0 trajectories); it is not a controller and not a closed-loop smoothing ablation."
- **Reason:** H4 is diagnostic, reuses H0 trajectories.
- **Evidence:** manifest H4 (`reuse_checkpoint_from: H0`, `train:false`); `run_h4_diagnostic`.

### R8 — Equation (6) horizon
- **Location:** Equation (6)
- **Original text:** (stale/ambiguous horizon; any "H = 500").
- **Replacement text:** `H = ⌊ (D_xy / (v_ref · Δt)) · 1.8 ⌋ + 300` with `v_ref = 5 m/s, Δt = 0.1 s`; for the nominal 300 m maps `D_xy = √(300² + 150²) = 335.4 m`, giving `H = 1507`.
- **Reason:** Match code exactly, show nominal value.
- **Evidence:** `tests/test_reward_and_horizon.py::test_horizon_nominal_300m`.

### R9 — APF distance basis + inactive altitude penalty
- **Location:** Model description (APF and reward)
- **Original text:** APF repulsion described generically; altitude penalty listed as active.
- **Replacement text:** "APF repulsion uses Euclidean distance to the obstacle AABB center (not nearest surface), which under-repels wide obstacles. The reward's altitude penalty is inactive under the evaluation protocol because altitude is hard-clamped to [5,6] m before the reward is evaluated. Reported clearance uses nearest-surface signed distance."
- **Reason:** Prevent conflating two distance definitions; disclose dead reward term.
- **Evidence:** `docs/implementation_traceability.md` (#13,#14,#19); `reports/implementation_audit.md`.

### R10 — Seed overlap / effective replication
- **Location:** Protocol (evaluation seeds)
- **Original text:** "50 rollouts per unit."
- **Replacement text:** "Each unit uses 50 evaluation slots (five base seeds × ten episode offsets), but seed windows overlap so only 32 numerical seeds are distinct; 18 slots per unit are exact repeats under the deterministic policy. Rates are reported over the 50 slots; this repetition is a pseudoreplication limitation."
- **Reason:** Honest reporting of effective sample size.
- **Evidence:** `reports/data_validation.md` (1080 identical duplicate instances); `data/derived/evaluation_seed_slots.csv`.

### R11 — Reproducibility statement
- **Location:** New short paragraph (or footnote) before References
- **Replacement text:** "Code, configuration, the frozen rollout ledger, the pinned software environment, and a result-lock certificate are released at <REPO_URL> (release tag <TAG>). All reported numbers are regenerated from the ledger by the released analysis scripts."
- **Reason:** Principle 4 / README requirement.
- **Evidence:** `reproducibility/` package; `reports/result_lock_certificate.md`.

---

## No numeric edits required

All 69 audited numbers reconcile (`reports/result_reconciliation.md`: 29 EXACT, 40 ROUNDING, 0 mismatch).
The revisions above are **wording/scoping** changes, not value corrections. Rebuild the PDF after applying
R1–R11 and re-run `analysis/03` if any table value is touched.
