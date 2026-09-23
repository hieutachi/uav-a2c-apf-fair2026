# Result Reconciliation Report

Every manuscript number recomputed from `data/raw/rollout_ledger.csv` via `analysis/01`, `analysis/02`. No manuscript value was copied into the recomputation.

## Summary

- EXACT_MATCH: 29
- ROUNDING_MATCH: 40
- SUPPORTED_WITH_REWORDING: 0
- MISMATCH: 0
- UNREPRODUCIBLE: 0
- NOT_APPLICABLE: 0

**69/69 claims reconcile** (EXACT/ROUNDING/SUPPORTED). MISMATCH=0, UNREPRODUCIBLE=0.

## Claim-by-claim

| claim_id | location | reported | recomputed | status | explanation |
|---|---|---:|---:|---|---|
| C-OUT-H0-succ | Table (aggregate outcomes) | 1000 | 1000 | EXACT_MATCH | identical |
| C-OUT-H0-coll | Table (aggregate outcomes) | 0 | 0 | EXACT_MATCH | identical |
| C-OUT-H0-time | Table (aggregate outcomes) | 0 | 0 | EXACT_MATCH | identical |
| C-OUT-H1-succ | Table (aggregate outcomes) | 830 | 830 | EXACT_MATCH | identical |
| C-OUT-H1-coll | Table (aggregate outcomes) | 58 | 58 | EXACT_MATCH | identical |
| C-OUT-H1-time | Table (aggregate outcomes) | 112 | 112 | EXACT_MATCH | identical |
| C-OUT-H2-succ | Table (aggregate outcomes) | 55 | 55 | EXACT_MATCH | identical |
| C-OUT-H2-coll | Table (aggregate outcomes) | 905 | 905 | EXACT_MATCH | identical |
| C-OUT-H2-time | Table (aggregate outcomes) | 40 | 40 | EXACT_MATCH | identical |
| C-MAP-H0-random | Table (map-level) | 250 | 250 | EXACT_MATCH | identical |
| C-MAP-H0-corridor | Table (map-level) | 250 | 250 | EXACT_MATCH | identical |
| C-MAP-H0-barrier | Table (map-level) | 250 | 250 | EXACT_MATCH | identical |
| C-MAP-H0-mixed | Table (map-level) | 250 | 250 | EXACT_MATCH | identical |
| C-MAP-H1-random | Table (map-level) | 140 | 140 | EXACT_MATCH | identical |
| C-MAP-H1-corridor | Table (map-level) | 240 | 240 | EXACT_MATCH | identical |
| C-MAP-H1-barrier | Table (map-level) | 200 | 200 | EXACT_MATCH | identical |
| C-MAP-H1-mixed | Table (map-level) | 250 | 250 | EXACT_MATCH | identical |
| C-MAP-H2-random | Table (map-level) | 50 | 50 | EXACT_MATCH | identical |
| C-MAP-H2-corridor | Table (map-level) | 0 | 0 | EXACT_MATCH | identical |
| C-MAP-H2-barrier | Table (map-level) | 5 | 5 | EXACT_MATCH | identical |
| C-MAP-H2-mixed | Table (map-level) | 0 | 0 | EXACT_MATCH | identical |
| C-CONT-H0-clear-mean | Table (continuous metrics) | 7.24 | 7.23716 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.0028371) |
| C-CONT-H0-clear-sd | Table (continuous metrics) | 5.24 | 5.23241 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00758788) |
| C-CONT-H0-steps-mean | Table (continuous metrics) | 104.4 | 104.4 | EXACT_MATCH | identical |
| C-CONT-H0-steps-sd | Table (continuous metrics) | 22.7 | 22.657 | ROUNDING_MATCH | within tolerance 0.1 (|delta|=0.0430364) |
| C-CONT-H0-jit-mean | Table (continuous metrics) | 28.53 | 28.5311 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00114403) |
| C-CONT-H0-jit-sd | Table (continuous metrics) | 9.03 | 9.02126 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00873775) |
| C-CONT-H0-acc-mean | Table (continuous metrics) | 16.08 | 16.0753 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.0047389) |
| C-CONT-H0-acc-sd | Table (continuous metrics) | 1.67 | 1.66637 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00362613) |
| C-CONT-H1-clear-mean | Table (continuous metrics) | 7.77 | 7.77038 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.000376804) |
| C-CONT-H1-clear-sd | Table (continuous metrics) | 6.28 | 6.27453 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00546672) |
| C-CONT-H1-steps-mean | Table (continuous metrics) | 237.8 | 237.771 | ROUNDING_MATCH | within tolerance 0.1 (|delta|=0.029) |
| C-CONT-H1-steps-sd | Table (continuous metrics) | 451.3 | 451.044 | ROUNDING_MATCH | within tolerance 0.5 (|delta|=0.255716) |
| C-CONT-H1-jit-mean | Table (continuous metrics) | 55.33 | 55.333 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00298119) |
| C-CONT-H1-jit-sd | Table (continuous metrics) | 14.68 | 14.6755 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.0044835) |
| C-CONT-H1-acc-mean | Table (continuous metrics) | 22.85 | 22.8481 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00190652) |
| C-CONT-H1-acc-sd | Table (continuous metrics) | 7.00 | 6.99205 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00794523) |
| C-CONT-H2-clear-mean | Table (continuous metrics) | 0.76 | 0.76247 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00247007) |
| C-CONT-H2-clear-sd | Table (continuous metrics) | 3.70 | 3.70093 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.000932404) |
| C-CONT-H2-steps-mean | Table (continuous metrics) | 408.0 | 408.04 | ROUNDING_MATCH | within tolerance 0.1 (|delta|=0.04) |
| C-CONT-H2-steps-sd | Table (continuous metrics) | 339.0 | 338.808 | ROUNDING_MATCH | within tolerance 0.5 (|delta|=0.192402) |
| C-CONT-H2-jit-mean | Table (continuous metrics) | 2.21 | 2.21098 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.000984003) |
| C-CONT-H2-jit-sd | Table (continuous metrics) | 0.82 | 0.820483 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.000483296) |
| C-CONT-H2-acc-mean | Table (continuous metrics) | 0.45 | 0.453486 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00348598) |
| C-CONT-H2-acc-sd | Table (continuous metrics) | 0.10 | 0.0951558 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.00484424) |
| C-PAIR-succ-diff | Paired H0-H1 (success) | -0.17 | -0.17 | ROUNDING_MATCH | within tolerance 0.005 (|delta|=2.77556e-17) |
| C-PAIR-succ-dz | Paired H0-H1 (success) | -0.509 | -0.509459 | ROUNDING_MATCH | within tolerance 0.005 (|delta|=0.000458653) |
| C-PAIR-succ-p | Paired H0-H1 (success) | 0.0273 | 0.0272812 | ROUNDING_MATCH | within tolerance 0.001 (|delta|=1.88285e-05) |
| C-PAIR-succ-n | Paired H0-H1 (success) | 20 | 20 | EXACT_MATCH | identical |
| C-PAIR-jit-diff | Paired H0-H1 (jitter) | 26.80 | 26.8018 | ROUNDING_MATCH | within tolerance 0.05 (|delta|=0.00183716) |
| C-PAIR-jit-dz | Paired H0-H1 (jitter) | 1.78 | 1.78027 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.000270146) |
| C-PAIR-jit-n | Paired H0-H1 (jitter) | 20 | 20 | EXACT_MATCH | identical |
| C-PAIR-acc-diff | Paired H0-H1 (acceleration) | 6.77 | 6.77283 | ROUNDING_MATCH | within tolerance 0.05 (|delta|=0.00283238) |
| C-PAIR-acc-dz | Paired H0-H1 (acceleration) | 1.07 | 1.07064 | ROUNDING_MATCH | within tolerance 0.01 (|delta|=0.000640475) |
| C-PAIR-acc-p | Paired H0-H1 (acceleration) | 0.006 | 0.00638962 | ROUNDING_MATCH | within tolerance 0.001 (|delta|=0.000389618) |
| C-PAIR-acc-n | Paired H0-H1 (acceleration) | 20 | 20 | EXACT_MATCH | identical |
| C-PAIR-eff-diff | Paired H0-H1 (efficiency) | 0.0142 | 0.0142027 | ROUNDING_MATCH | within tolerance 0.001 (|delta|=2.69639e-06) |
| C-PAIR-eff-dz | Paired H0-H1 (efficiency) | 0.156 | 0.156091 | ROUNDING_MATCH | within tolerance 0.005 (|delta|=9.07878e-05) |
| C-PAIR-eff-p | Paired H0-H1 (efficiency) | 0.417 | 0.417114 | ROUNDING_MATCH | within tolerance 0.005 (|delta|=0.000114258) |
| C-PAIR-eff-n | Paired H0-H1 (efficiency) | 18 | 18 | EXACT_MATCH | identical |
| C-PAIR-clear-diff | Paired H0-H1 (clearance) | 0.533 | 0.533214 | ROUNDING_MATCH | within tolerance 0.005 (|delta|=0.000213905) |
| C-PAIR-clear-dz | Paired H0-H1 (clearance) | 0.063 | 0.0629907 | ROUNDING_MATCH | within tolerance 0.005 (|delta|=9.28261e-06) |
| C-PAIR-clear-p | Paired H0-H1 (clearance) | 0.956 | 0.956329 | ROUNDING_MATCH | within tolerance 0.005 (|delta|=0.000329346) |
| C-PAIR-clear-n | Paired H0-H1 (clearance) | 20 | 20 | EXACT_MATCH | identical |
| C-PAIR-steps-diff | Paired H0-H1 (steps) | 133.37 | 133.371 | ROUNDING_MATCH | within tolerance 0.05 (|delta|=0.001) |
| C-PAIR-steps-dz | Paired H0-H1 (steps) | 0.300 | 0.300138 | ROUNDING_MATCH | within tolerance 0.005 (|delta|=0.000138356) |
| C-PAIR-steps-p | Paired H0-H1 (steps) | 0.123 | 0.123093 | ROUNDING_MATCH | within tolerance 0.005 (|delta|=9.26514e-05) |
| C-PAIR-steps-n | Paired H0-H1 (steps) | 20 | 20 | EXACT_MATCH | identical |
| C-SEED-unique | Seeds/protocol | 32 | 32 | EXACT_MATCH | identical |
