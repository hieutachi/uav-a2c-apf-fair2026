#!/usr/bin/env bash
# ICAI-FAI 2026: cheap frozen-policy evaluations (no training).
# Runs sequentially in ONE process so it never starves the H3 training pool.
set -u
cd "$(dirname "$0")/.." || exit 1
PY="/c/Users/N4G/AppData/Local/Programs/Python/Python313/python.exe"
export OMP_NUM_THREADS=4
LOG=results/icai2026/logs/cheap.log
mkdir -p results/icai2026/logs
S="101 211 307 401 503"

echo "== $(date -u +%FT%TZ) eval_unique H0 H1 (wind 1.0, seeds 2001-2050)" >> $LOG
$PY scripts/icai2026_experiments.py eval --configs H0 H1 --maps train --seeds $S \
  --tag icai_eval_unique >> $LOG 2>&1

echo "== $(date -u +%FT%TZ) wind sweep H0 H1 (0.0 0.5 1.5 2.0)" >> $LOG
$PY scripts/icai2026_experiments.py eval --configs H0 H1 --maps train --seeds $S \
  --wind-scales 0.0 0.5 1.5 2.0 --tag icai_wind_sweep >> $LOG 2>&1

echo "== $(date -u +%FT%TZ) held-out maps H0 H1" >> $LOG
$PY scripts/icai2026_experiments.py eval --configs H0 H1 --maps heldout --seeds $S \
  --tag icai_heldout >> $LOG 2>&1

echo "== $(date -u +%FT%TZ) action-component logging H0" >> $LOG
$PY scripts/icai2026_experiments.py eval --configs H0 --maps train --seeds $S \
  --tag icai_action_log --log-actions >> $LOG 2>&1

echo "== $(date -u +%FT%TZ) APF sensitivity (center/surface x d0 4,6,8,12)" >> $LOG
$PY scripts/icai2026_experiments.py apf-sensitivity --maps train \
  --tag icai_apf_sensitivity >> $LOG 2>&1

echo "ALL_CHEAP_EVALS_DONE $(date -u +%FT%TZ)" >> $LOG
