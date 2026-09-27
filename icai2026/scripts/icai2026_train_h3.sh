#!/usr/bin/env bash
# ICAI-FAI 2026: train H3 (geometry-aware A2C, no APF) — 4 maps x 5 seeds x 5M steps.
# 6 concurrent jobs, 4 OpenMP threads each (24 of 32 logical cores).
set -u
cd "$(dirname "$0")/.." || exit 1
PY="/c/Users/N4G/AppData/Local/Programs/Python/Python313/python.exe"
export OMP_NUM_THREADS=4
mkdir -p results/icai2026/logs
for m in map-random-01 map-corridor-01 map-barrier-01 map-mixed-01; do
  for s in 101 211 307 401 503; do
    echo "$PY scripts/icai2026_experiments.py train-h3 --map $m --seed $s --steps 5000000"
  done
done > results/icai2026/logs/h3_jobs.txt
xargs -P 6 -I{} sh -c '{} >> results/icai2026/logs/h3_train.log 2>&1' \
  < results/icai2026/logs/h3_jobs.txt
echo "ALL_H3_TRAINING_DONE $(date -u +%FT%TZ)" >> results/icai2026/logs/h3_train.log
