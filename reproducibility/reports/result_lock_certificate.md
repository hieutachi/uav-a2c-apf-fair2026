# Result-Lock Certificate

**Paper:** Component Evaluation of Hybrid A2C–APF Guidance in Wind-Perturbed UAV Simulation

## Provenance

| Field | Value |
|---|---|
| Source commit | `c88b02b45631047e5994c8ca15e8d6226d004e2b` (branch `main`) |
| Raw-ledger checksum (`data/raw/rollout_ledger.csv`) | `fa1334708c16277a04923ca6078a960255ac5a938673acc085d39192e9d1f6ec` |
| `analysis/01_build_unit_summaries.py` | `340a56f68711944a678b243c421e39405a95e67bf0f1f9a33442b32decb06131` |
| `analysis/02_compute_statistics.py` | `4fb754b04a8f5c85b2b5f9bc43b907b25f65331fb6742f36ad2e7ddb61feca33` |
| `analysis/03_reconcile_manuscript_claims.py` | `11555fec3e9eccd284d3d9403351f96495f465c7235ea4741f6f4b5120cfe4e9` |
| Software environment hash (`environment-lock.txt`) | `4db4040795bc5117f10354691336690c051e520f5acc81d0515d94f64518f7ed` |
| Certificate UTC timestamp | `2026-08-16T10:41:41Z` |
| Raw-artifact inventory | `manifests/raw_artifacts.sha256` (182 artifacts, all validated) |
| Release-package inventory | `manifests/release_artifacts.sha256` (65 files) |

## Reconciliation status (69 audited claims)

- **EXACT_MATCH:** 29
- **ROUNDING_MATCH:** 40 (manuscript rounds to 2 decimals; recomputed within tolerance)
- **SUPPORTED_WITH_REWORDING:** 0
- **MISMATCH:** 0
- **UNREPRODUCIBLE:** 0

All claim IDs and per-claim status: `reports/reconciliation.csv` / `reports/result_reconciliation.md`.
Claim families: aggregate outcome counts (H0/H1/H2), map-level success counts (12 cells), continuous metrics
(clearance/steps/jitter/acceleration mean±sd), paired H0−H1 inference (success/efficiency/clearance/steps/
jitter/acceleration: mean diff, dz, Wilcoxon p, n), and the 32-unique-seed count. **Every audited number is
regenerated from the ledger; none copied.**

## Gates (see `reports/`, `tests/`)

| Gate | Result |
|---|---|
| Raw artifacts checksum-validated | PASS (182/182) |
| One and only one terminal status per row | PASS (0 violations) |
| Controller counts = 1000 each | PASS |
| Every controller×map cell = 250 | PASS |
| H0/H1 paired units share map+training-run IDs | PASS (20 genuine pairs) |
| Tables/figures generated from the ledger | PASS (`analysis/04`) |
| All numeric claims EXACT/ROUNDING/SUPPORTED | PASS |
| No MISMATCH/UNREPRODUCIBLE | PASS |
| Unit + gate tests | PASS (25/25) |
| Clean-env smoke test | PASS |
| No secrets/keys/credentials in release | PASS (see `.gitignore`, README §11) |

## Unresolved limitations (do not block archival reproduction)

1. **Information asymmetry** in H0−H1 (APF channel carries privileged obstacle geometry; A2C observation does
   not). Interpretation is scoped accordingly; wording fixes in `docs/manuscript_revision_plan.md` (R1).
2. **Retraining is not bitwise reproducible** (PyTorch not explicitly seeded; no CUDA determinism flags).
   Archival reproduction and checkpoint re-evaluation are deterministic.
3. **Pseudoreplication:** 50 evaluation slots per unit collapse to 32 distinct numerical seeds (18 exact
   repeats; 1080 identical instances verified). Rates are reported over 50 slots as in the manuscript.
4. **Large binaries not redistributed** here: 40 checkpoints + 4000 trajectory `.npz`. They are checksummed in
   the research repo and required only for re-evaluation/illustrative figures, not for the reported numbers.
5. **Scope:** only A2C H0/H1 and non-learned H2 are evidence; no PPO/SAC/RRT claims; H3/H5 and `map-random-02`
   excluded from the evidence set.

## Release decision

```
CONDITIONAL PASS
```

**Rationale.** All core results reconcile exactly and the analysis reproduces from a clean environment against
the frozen ledger (PASS conditions on results and toolchain are met). The decision is **CONDITIONAL** rather
than full PASS solely because (a) some large binary models/trajectories are not publicly redistributed in this
package and must be fetched with the recorded checksums, and (b) from-scratch retraining is not bitwise
reproducible by design. Neither affects the reproducibility of any reported number. Independent reviewers can
fully reproduce every table, figure, and statistic from `data/raw/rollout_ledger.csv` using the released scripts.
