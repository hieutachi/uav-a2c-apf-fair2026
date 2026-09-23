.PHONY: help verify validate smoke ledger analysis figures test gate all

PY ?= python
export MPLBACKEND=Agg
export PYTHONIOENCODING=utf-8

help:
	@echo "Targets: verify validate smoke ledger analysis figures test gate all"

verify:            ## check the python environment / package versions
	bash scripts/verify_environment.sh

validate:          ## checksum-validate raw artifacts against the manifest
	$(PY) scripts/validate_artifacts.py

smoke:             ## one-command smoke test (tiny synthetic reproduction)
	$(PY) scripts/run_smoke_test.py

ledger:            ## rebuild the canonical rollout ledger from immutable raw data
	$(PY) scripts/build_ledger.py

analysis:          ## reproduce all tables/statistics from the frozen ledger
	$(PY) scripts/reproduce_analysis.py

figures:           ## regenerate figures/tables from the ledger
	$(PY) scripts/reproduce_figures.py

test:              ## run unit + gate tests
	$(PY) -m pytest tests -q

gate: validate analysis test   ## full release gate

all: verify validate ledger analysis figures test
