# ICAI-FAI 2026 — MANUSCRIPT BLUEPRINT (architecture + evidence-to-claim)

Phase: architecture only. **No manuscript prose, no main.tex edits, no new PDF.**
Sources of truth: `REPORT_ICAI2026_REVISION.md` (audited) and `results/icai2026/MASTER_RESULTS.json`.
Checker status at blueprint time: **150 PASS / 0 FAIL**; remaining warnings point only at `paper/icai2026/main.tex`
lines 66/68/70 (FAIR-mention removal) and 232/252/278/302/304 (wording), i.e. the pending rewrite list.

## 1. Final research question

> When an analytical APF channel is combined with A2C for wind-perturbed UAV navigation in cluttered
> 3-D environments, which observed effects persist against a geometry-aware learned baseline, what does the
> analytical channel actually contribute during execution, and where do those effects break down?

Sub-questions map 1:1 to the Results flow: RQ1 (persistence of reliability/variation effects),
RQ2 (execution-level mechanism), RQ3 (boundaries: wind, held-out layouts, blend weight).

## 2. Titles

| # | Title | Emphasizes | Reviewer expectation created | Overstatement risk |
|---|---|---|---|---|
| T1 (recommended) | An Empirical Audit of Obstacle Information and Analytical Guidance in Hybrid A2C–APF UAV Navigation under Wind | measurement honesty; two ingredients audited | rigorous protocol, explicit bounds, reusable artifacts | none identified: "audit" promises measurement, not causation |
| T2 | Auditing a Hybrid A2C–APF UAV Controller: Obstacle Information, Analytical Guidance, and Their Limits under Wind | limits/negative results | strong negative-result content | "Limits" is safe; slightly longer colon structure |
| T3 | What Does the Analytical Channel Contribute? An Execution-Level Audit of Hybrid A2C–APF UAV Guidance in Wind-Perturbed Clutter | mechanism | mechanistic evidence front and center | "Contribute" can read causally; mitigated only by "execution-level audit" |

Recommendation: **T1**. It matches framing B, uses audit vocabulary, and creates no causal or novelty expectation.
T2 is the fallback if a shorter title is preferred; T3 only if the venue tolerates question-form titles.

## 3. Exactly three contributions

- **C1 — Comparison infrastructure.** A geometry-aware A2C baseline (68-D observation = 12-D base + 56-D padded
  raw AABB geometry, K = 8 distance-sorted slots, no APF term) plus a corrected 50-unique-seed evaluation protocol
  with paired (map × training-run) inference, enabling a structured comparison of obstacle-blind, geometry-aware,
  and analytical-hybrid control at matched dynamics, reward, termination, and 5M-step budget.
- **C2 — Execution-level audit of the analytical channel.** Direct measurement that the shipped center-distance
  repulsion never activates on nominal trajectories (0/103,682 H0 timesteps; 0/475,015 H2 timesteps), step-level
  action-component diagnostics (‖a_APF‖ = k_att exactly), and a predeclared distance-basis × d0 sensitivity showing
  a collision→stagnation failure-mode shift for APF-only control.
- **C3 — Evidence boundary.** The sampled trajectory-variation contrast that persists against the geometry-aware
  baseline (H0−H3 jitter d_z = −1.970, acceleration d_z = −4.076, p < 0.001; H3−H1 null), against non-significant
  intermediate reliability contrasts; frozen-policy wind stress to 2× nominal; same-family held-out layouts
  including the mixed-family collapse (H0 50/250, H3 17/250, H1 0/250) that rules out layout generalization.

## 4. Four-level claim hierarchy

**L1 System-level reliability.** Canonical: H0 1000/1000, H3 938/1000 (62 coll, 0 timeout), H1 848/1000
(45 coll, 107 timeout). Contrasts: H0−H1 +0.152 (d_z 0.491, p 0.0156); H3−H1 +0.090 (p 0.250);
H0−H3 +0.062 (p 0.125). Allowed: H0 more reliable than obstacle-blind H1 under the protocol; H3 descriptively
between; intermediate contrasts not individually supported. Forbidden: causal percentages, "APF independently
improves reliability", "H3 proves a decomposition".
**L2 Strongest component-level effect.** H0−H3 jitter −26.112 (d_z −1.970) and acceleration −8.8725 (d_z −4.076),
p < 0.001; H3−H1 variation null (p ≈ 0.90). Allowed phrasing: "the strongest statistically supported effect
associated with the analytical hybrid channel is reduced sampled trajectory variation, and this contrast persists
against the geometry-aware A2C baseline." Forbidden: physical stability, smoothness guarantee, actuator claims.
**L3 Mechanistic audit.** Zero center-distance repulsion activation (numbers above); surface basis activates on
30.55% of H2 timesteps (945/1000 episodes) with no collisions observed in 200 predeclared rollouts but 56–57.5%
timeouts; counterfactual surface on H0 paths 2.03% of timesteps / 549/1000 episodes. Allowed: repulsion inactive
under evaluated trajectories; active analytical contribution = attractive term + adaptive blending; distance
semantics change the APF-only failure mode. Forbidden: "broken APF", guarantees, "repulsion universally useless".
**L4 Boundaries.** Wind: H0 100/100/100/99.5/98.6% at scales 0/0.5/1/1.5/2 (graceful degradation over tested
range only); H1 non-monotone (no causal reading); H3 96.9→91.5%. Held-out: three families transfer, mixed family
collapses for all controllers. Fixed-λ: evaluation-time blend sensitivity only (1000/990/795/606; corridor 250/246/172/0).
All negatives stay visible.

## 5. Evidence-to-claim matrix

| Claim (bank color) | Source artifact | Statistic | Level |
|---|---|---|---|
| H0 > H1 completion under protocol (GREEN) | icai_eval_unique CSV | +0.152, d_z 0.491, p 0.0156, n 20 | L1 |
| H3 between H1 and H0 descriptively (GREEN) | + icai_eval_unique_h3 | 848 < 938 < 1000 per 1000 | L1 |
| Intermediate reliability contrasts unsupported (GREEN) | same | p 0.250 / 0.125 | L1 |
| Variation contrast vs geometry-aware baseline (YELLOW→GREEN with fixed phrasing) | same | jitter −26.112 d_z −1.970; accel −8.8725 d_z −4.076; p < 0.001 | L2 |
| H3−H1 variation null (GREEN) | same | −1.125 d_z −0.070 p 0.898 | L2 |
| Repulsion never activates, center basis (GREEN) | apf_activation.json | 0/103,682; 0/475,015; ε = 1e-8 | L3 |
| Distance semantics shift APF-only failure mode (GREEN) | icai_apf_sensitivity CSV | 21/200 vs 88/200, 0 collisions, 112–115 timeouts | L3 |
| Graceful wind degradation to 2× (YELLOW, range-limited) | icai_wind_sweep* CSV | 100→98.6% | L4 |
| No layout generalization (GREEN, negative) | icai_heldout* CSV | mixed-ho1 50/17/0 per 250 | L4 |
| Deployment blend sensitivity (YELLOW, labelled) | icai_fixed_lambda_* CSV | 990/795/606 | L4 |
| Efficiency/clearance/steps nulls (GREEN, negative) | icai_eval_unique CSV | p 0.768 / 0.927 / 0.143 | L1 |

## 6. Section architecture

I Introduction (0.9 p): problem → evaluation gap → bundled-ingredients problem → RQ + 3 contributions.
II Related work (0.5 p): four compressed categories (see §11).
III Controller and evaluation design (1.4 p): shared simulator equations; controller/information matrix (Table I);
H3 geometry-aware observation spec incl. sorting/padding/bounds; APF semantics incl. both distance bases;
wind model + scaling rule; reward/termination condensed.
IV Experimental protocol (0.8 p): maps (4 train + 4 same-family held-out), corrected seed schedule, units and
paired inference, metric definitions, predeclared grids, H4 note (one line), reproducibility artifacts.
V Results by research question (2.1 p): V-A RQ1 (Table II + Fig 1); V-B RQ2 (Fig 2 + action-log sentence);
V-C RQ3 (Fig 3 + fixed-λ sentence).
VI Discussion (0.9 p): what L1/L2/L3 establish; representation limitation of H3 (permutation rates, mismatch);
generalization boundary; wording discipline; open items (causal blend ablation, surface-distance hybrid).
VII Conclusion (0.25 p). References (0.8 p).

## 7. RQ-based Results flow

RQ1 "Does the hybrid advantage remain under corrected evaluation and against a geometry-aware baseline?"
→ outcomes table, paired contrasts (success + variation + nulls), Fig 1.
RQ2 "What is the analytical channel actually doing during execution?"
→ action diagnostics (‖a_APF‖ = k_att), activation measurement, distance-basis sensitivity, Fig 2.
RQ3 "How stable are these observations outside the nominal condition?"
→ wind sweep, same-family held-out (mixed collapse prominent), evaluation-time blend sensitivity as one
sentence with numbers, Fig 3.

## 8. Table and figure plan

| Item | Purpose | Exact data | Claim supported | Essential |
|---|---|---|---|---|
| Table I | make information structure explicit | 4 configs × 7 matrix columns | C1; asymmetry visibility | essential |
| Table II | main corrected-seed evidence | per-config totals (succ/coll/timeout) + 6 paired contrasts with d_z, p, support flag | L1, L2 | essential |
| Fig 1 | three-way comparison at a glance | panel a: success/250 per map × {H0,H3,H1}; panel b: paired d_z for success/jitter/accel with significance shading | L1, L2 | essential |
| Fig 2 | mechanism | panel a: activation fractions (H0 center 0, H2 center 0, H2 surface 30.55%, H0 counterfactual 2.03%); panel b: sensitivity success/collision/timeout by basis | L3 | essential |
| Fig 3 | boundaries | panel a: wind curves H0/H3/H1; panel b: held-out success/250 per family | L4 | essential |
| Table III | optional boundary table | wind + held-out counts if Fig 3 panels feel crowded | L4 | optional (decide at layout) |
| fixed-λ | deployment sensitivity | 4 numbers in one sentence | L4 | text-only |

New asset needed at writing time: activation panel of Fig 2 from `apf_activation.json`
(extend `scripts/icai2026_figures.py`); Fig 1/3 reuse `fig_disentanglement.png`-style panels regenerated from
MASTER_RESULTS.json so no number is hand-copied.

## 9. Abstract skeleton (six sentences; no polished prose)

S1 context: hybrid RL + reactive guidance is attractive for cluttered UAV navigation, but reported effects confound
the analytical law with the obstacle information it consumes. Allowed: none of our numbers. Avoid: novelty claims.
S2 gap/RQ: it is unclear which effects persist against a geometry-aware learned baseline and what the analytical
channel contributes during execution. Allowed: RQ wording. Avoid: "reviewers", "prior work failed".
S3 design: four configurations (obstacle-blind, geometry-aware 68-D, hybrid, APF-only), 4 maps × 5 runs × 5M steps,
corrected 50-unique-seed protocol, paired unit inference, predeclared sensitivity grids, frozen-policy stress tests.
Allowed: protocol facts. Avoid: implementation minutiae.
S4 main result: H0 1000/1000 vs H3 938/1000 vs H1 848/1000; H0−H1 +0.152 p 0.0156 while H3−H1 (+0.090, p 0.250)
and H0−H3 (+0.062, p 0.125) are not individually supported; the variation contrast persists against H3
(jitter d_z −1.970, accel d_z −4.076, p < 0.001). Avoid: causal percentages, "disentangling".
S5 mechanism + boundary: center-distance repulsion never activated (0/103,682 timesteps); surface basis shifts
APF-only from collision to stagnation; wind degradation graceful to 2×; one held-out family collapses all controllers.
Avoid: "guarantee", "broken", "generalizes".
S6 conservative conclusion: the hybrid's supported component-level effect is reduced sampled trajectory variation;
reliability ordering is descriptive at the intermediate level; all nulls reported. Avoid: superiority language.

## 10. Introduction argument map (five paragraphs)

P1 thesis: cluttered low-altitude UAV navigation needs goal progress, collision avoidance, and non-abrupt control
under wind; hybrid RL + analytical guidance is a natural design. Evidence/citations: APF origin [Khatib], RL control
[A2C/PPO/SAC/DDPG], wind-aware control [Neural-Fly, DATT]. Prohibited: survey of path planning; hardware claims.
P2 thesis: hybrid evaluations are hard to interpret because controller descriptions, observation contents, and
evaluation accounting diverge. Evidence: Henderson 2018; reproducibility literature. Prohibited: blaming prior authors.
P3 thesis: the specific empirical problem — obstacle information and analytical computation are bundled whenever the
learned observation lacks geometry, so "APF contribution" is undefined without a geometry-aware baseline; and
implementation semantics (distance basis, blend schedule) can dominate measured behavior. Evidence: our activation
measurement previewed in one clause; APF local-minima literature. Prohibited: FAIR/reviewer narrative.
P4 thesis: our design answers it — three learned configurations differing only in information/analytical structure,
corrected seed protocol, execution-level instrumentation, predeclared sensitivity and stress tests. Evidence: protocol facts.
Prohibited: algorithm-novelty framing.
P5 thesis: three contributions (C1–C3) and explicit non-claims. Prohibited: more than three bullets; superiority language.

## 11. Related-work compression plan

1 APF + limitations: 2 sentences (Khatib; local minima/gain sensitivity + one 2024–25 hybrid-planner review).
2 DRL continuous UAV control: 2 sentences (A2C origin; PPO/SAC/DDPG as alternatives not compared).
3 Hybrid APF–RL: 3 sentences with 3 citations (reward shaping / action constraint / direct blend), positioning us
as evaluation rather than architecture.
4 Empirical rigor & reproducibility: 2 sentences (Henderson; real-world RL challenges) + one clause on audit-style
instrumentation.
5 Wind-aware control: 1 sentence (2 citations), only to justify the disturbance model.
Compressible to one sentence: categories 2 and 5. Citation gaps to search later (listed, not surveyed now):
(a) set-based/permutation-invariant observations for padded geometry (DeepSets/attention) to cite in Discussion;
(b) execution-level instrumentation or activation auditing precedents in RL, if any, to strengthen framing B.

## 12. FAIR retain / compress / discard map

RETAIN (rewrite into III/IV): point-mass dynamics equations; drag-on-relative-air-velocity statement; semi-implicit
Euler; altitude clamp + dead altitude penalty disclosure; swept-AABB collision and priority ordering; horizon
formula; reward terms and constants; metric definitions (Wilson descriptive, efficiency success-only, finite-difference
variation); paired-inference rationale and pseudoreplication discipline; threats-to-validity style.
COMPRESS: four-map geometry descriptions (one table row each); APF equations (keep center form + one-line surface
variant); related work; training hyperparameter prose (table).
DISCARD/REPLACE: H0/H1/H2-only narrative; H4 as named configuration (one-line note); old 32-seed schedule discussion
(replace with corrected protocol sentence + citation of our own artifact); old conclusion; every sentence treating
APF guidance as isolated; the "component evaluation of a guidance controller" title framing (replaced by audit framing).

## 13. ICAI-draft discard map (current main.tex; do NOT edit yet)

- Lines 66, 68, 70: rebuttal voice ("Our prior submission…", "Reviewers correctly identified…", "This revision answers…").
- Line 232: causal wind reading ("geometry- and control-driven, not wind-driven").
- Line 252: guarantee language ("removes collisions entirely").
- Line 278: "same-layout training map" → same-family wording.
- Lines 302, 304: "accounts for most…" and "survives information matching" → L1/L2 canonical phrasings.
- Abstract: result-dumping sentences and "disentangle" verb; replace per skeleton §9.
- Title: replace per §2 (T1).
- Section V ordering: replace experiment-log order with RQ1–RQ3 flow (§7).
- Any "H4" table row beyond the one-line note.

## 14. Claim bank

GREEN: "H0 completed 1000/1000 corrected-seed rollouts (Wilson 95% CI 0.996–1.000)." · "H3 completed 938/1000 and
H1 848/1000 under the same schedule." · "The H0−H1 success contrast is +0.152 (d_z 0.491, Wilcoxon p = 0.0156, n = 20)."
· "H3−H1 (+0.090, p = 0.250) and H0−H3 (+0.062, p = 0.125) are not individually statistically supported."
· "No center-distance repulsion activation was measured on 103,682 nominal H0 timesteps (ε = 1e-8)."
· "No collisions were observed in 200 evaluated rollouts of the surface-distance APF-only variant; 112–115 of them timed out."
· "On the mixed held-out family, H0/H3/H1 achieved 50/17/0 successes per 250 rollouts."
· "Efficiency, clearance, and step-count contrasts remain unsupported (p = 0.768/0.927/0.143)."
YELLOW (only with the stated qualification): "Lower sampled trajectory variation was observed for H0 than for the
geometry-aware baseline (jitter d_z −1.970, acceleration d_z −4.076, p < 0.001); this is a finite-difference
trajectory-variation diagnostic, not a physical-stability measure." · "The frozen hybrid degrades gracefully over the
tested wind range up to 2× nominal." · "Deployment-time completion is sensitive to the blend weight (evaluation-time
sensitivity; policies trained under the adaptive schedule)." · "Obstacle information is associated with the larger
share of the point-estimate reliability ordering (H3−H1 = +9.0 pp vs H0−H3 = +6.2 pp), neither significant at n = 20."
RED: any causal-percentage statement; "APF improves reliability/safety"; "disentangling/causal decomposition";
"perfectly information-matched"; "physical stability/flight smoothness guarantee"; "surface APF guarantees collision
avoidance"; "generalizes to unseen environments"; "robust to wind" unqualified; "broken/defective APF";
comparisons to PPO/SAC/RRT; shorter/faster/clearer-path claims.

## 15. Page budget (8 pages incl. references)

Abstract + keywords 0.35 · I 0.90 · II 0.50 · III 1.40 · IV 0.80 · V 2.10 (Fig 1–3 as two double-column + one
single-column, Table I–II) · VI 0.85 · VII 0.25 · references 0.80 = **7.95**. Contingency: drop Table III (already
optional), move per-map reliability panel of Fig 1 into Table II if V overflows; never cut the mixed-family row.

## 16. Unresolved decisions (to settle at writing time, not now)

1. Fig 3 vs Table III for boundaries (layout-dependent).
2. Fixed-λ as sentence vs one table row (space-dependent; sentence is default).
3. Final title T1 vs T2 (length-dependent).
4. Whether the two citation gaps in §11 resolve to real citations (search later; Discussion can stand without them).

## 17. Manuscript-writing instructions (binding for the writing phase)

Consume numbers only from `MASTER_RESULTS.json`; after editing, run `scripts/icai2026_consistency_check.py` and
require 0 FAIL and zero warnings outside the documented removal list (which must then be empty). Apply the claim
bank verbatim in spirit: GREEN freely, YELLOW only with its qualification, RED never. No FAIR/reviewer/revision
mentions anywhere. Terminology fixed: "geometry-aware A2C baseline" (never perfectly information-matched),
"sampled trajectory variation / finite-difference jerk (jitter) / finite-difference acceleration" (never physical
stability), "same-family held-out layouts", "evaluation-time blend sensitivity", "the center-distance repulsive
term was never activated under the evaluated trajectories", "no collisions were observed in N evaluated rollouts".
Keep every null and the mixed-family collapse visible. ≤ 8 pages. Three contribution bullets only. Results ordered
by RQ1–RQ3. H4 as a one-line note. Reproducibility paragraph pointing to the public artifacts and checker.

## 18. Final quality check (brief S)

One story: audit of what each ingredient of a shipped hybrid does — yes. Not a rebuttal: no FAIR/reviewer tokens
remain in planned text — yes. No causal decomposition: L1 forbids it, bank RED lists it — yes. H3 not called
perfectly matched: §3/§6/§17 fix terminology; permutation rates in Discussion — yes. Variation not called physical
stability: bank + terminology list — yes. Mixed held-out failure visible: L4, C3, Fig 3, §15 contingency rule — yes.
Intermediate contrasts non-significant: L1 + Table II support flags — yes. Repulsion-never-activates stated
directly with denominators: L3, C2, Fig 2 — yes. Surface 0/200 not a guarantee: L3 wording + bank — yes.
Corrected seeds only: §5 matrix sources + checker seed accounting — yes. Fits 8 pages: §15 = 7.95 with contingency — yes.

**BLUEPRINT_READY = YES**

Planned paper in ten lines:
1. Audit-framed study (T1) of a hybrid A2C–APF UAV controller under wind, standing alone with no rebuttal voice.
2. Design: H0 hybrid, H1 obstacle-blind, H3 geometry-aware 68-D baseline, H2 APF-only; 4 maps × 5 runs × 5M steps;
   corrected 50-unique-seed protocol; paired unit inference; predeclared grids.
3. RQ1: H0 1000/1000 > H3 938 > H1 848; total contrast supported (p 0.0156), intermediates not (p 0.250/0.125).
4. RQ1 also: variation contrast persists against H3 (jitter d_z −1.970, accel d_z −4.076, p < 0.001); H3−H1 null.
5. RQ2: center-distance repulsion never activates (0/103,682 H0 steps); ‖a_APF‖ = k_att; surface basis shifts
   APF-only from collision (172/200) to stagnation (112–115/200 timeouts, 0 collisions observed).
6. RQ3: wind graceful to 2× (98.6%); same-family held-out transfers on 3/4 families; mixed family collapses all.
7. Fixed-λ reported as evaluation-time sensitivity (1000/990/795/606), one sentence.
8. Discussion carries H3 representation limits (slot permutations 3.0–18.6%) and all nulls.
9. Visuals: 2 tables + 3 figures, each tied to one claim level; 7.95/8 pages planned.
10. Writing phase bound to MASTER_RESULTS.json, the claim bank, and the checker at 0 FAIL.
