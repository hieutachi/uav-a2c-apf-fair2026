# Tables

`generated/` holds LaTeX/CSV tables produced from the frozen ledger by
`analysis/04_generate_tables_and_figures.py`. They are regenerable and must not be hand-edited.

Generated tables:
- `table_outcomes.csv` / `.tex` — aggregate success/collision/timeout per controller with Wilson 95% CI.
- `table_map_outcomes.csv` — per controller × map success counts.
- `table_continuous.csv` — clearance/steps/jitter/acceleration mean ± sd per controller.
- `table_paired.csv` — paired H0−H1 differences, dz, Wilcoxon p, n, rank-biserial, Hodges–Lehmann.

Every value traces to `data/raw/rollout_ledger.csv`; see `reports/result_reconciliation.md`.
