# Data Validation Report

Ledger: `data/raw/rollout_ledger.csv` (3000 controller rollout rows).

## Hard invariants

- Terminal-status invariant (success+collision+timeout==1): PASS (0 violations)
- status string / flag consistency: PASS
- Per-controller totals: {'H0': 1000, 'H1': 1000, 'H2': 1000} (expected 1000 each)
- Per controller-map cells == 250: PASS
- Efficiency NA on failures: PASS

## Seed arithmetic

- Declared slots per unit: 50 (5 base seeds x 10 episodes)
- Unique effective numerical seeds: **32** (range 1009-1040)
- Overlapping numerical seeds (appear in >1 slot): 16 values
  - 1013(x2), 1014(x2), 1015(x2), 1016(x2), 1017(x2), 1018(x2), 1019(x2), 1020(x2), 1021(x3), 1022(x3), 1023(x2), 1024(x2), 1025(x2), 1026(x2), 1027(x2), 1028(x2)

## Pseudoreplication check (duplicate numerical seed within a unit)

- Units checked: 60
- Duplicate-seed rollout instances with byte-identical outcome signature: 1080
- Example: unit `H0_A2C_map-barrier-01_seed101_steps5000000` numerical seed 1013 appears in two slots with identical status/steps/clearance/jitter.

**Interpretation.** Because a duplicate numerical seed re-seeds the same environment reset and wind stream and the evaluation policy is deterministic, the overlapping slots are exact repeats. Each unit therefore contains 50 rollout rows but only 32 numerically distinct rollouts. Reported per-unit rates are computed over 50 slots (as in the manuscript); this repetition is a pseudoreplication limitation that must be disclosed.
