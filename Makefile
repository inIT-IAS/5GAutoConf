VENV_DIR := .venv

ifeq ($(OS),Windows_NT)
	PYTHON_BIN := python
	PYTHON := $(VENV_DIR)/Scripts/python.exe
	PIP := $(VENV_DIR)/Scripts/pip.exe
	READMECOV := $(VENV_DIR)/Scripts/readme-cov.exe
	REMOVE := powershell -Command "Remove-Item -Recurse -Force -ErrorAction Ignore"
	GENERATED := '*.generated.*'
else
	PYTHON_BIN := python3
	PYTHON := $(VENV_DIR)/bin/python3
	PIP := $(VENV_DIR)/bin/pip3
	READMECOV := $(VENV_DIR)/bin/readme-cov
	REMOVE := rm -rf
	GENERATED := *.generated.*
endif

.PHONY: run build install test test-slow clean

run:
	$(PYTHON) run.py -f 78 -b 40 -r 30 -d TDD -c 3780 -s b210 -l info

debug:
	$(PYTHON) run.py -f 78 -b 40 -r 30 -d TDD -c 3780 -s b210 -l debug

build:
	$(PYTHON) -m build

install:
	$(PYTHON_BIN) -m venv $(VENV_DIR)
	$(PIP) install .[dev,dist]
	$(PYTHON) -m compileall .
	$(PYTHON) -m scripts.build_long_guard_time_prach_pusch_combination_tables
	$(PYTHON) -m scripts.build_prach_ssb_collision_free_tables
	$(PYTHON) -m scripts.build_tau_d_max_rtd_max_table

test:
	$(PYTHON) -m coverage run --omit '$(VENV_DIR)/*,*/ts_dicts.py' -m pytest test.py -v -m "not slow"
	$(PYTHON) -m coverage report -m

test-slow:
	$(PYTHON) -m coverage run --omit '$(VENV_DIR)/*,*/ts_dicts.py' -m pytest test.py -v
	$(PYTHON) -m coverage report -m
	$(READMECOV)

clean:
	-$(REMOVE) __pycache__
	-$(REMOVE) "build"
	-$(REMOVE) "configurator/__pycache__"
	-$(REMOVE) "dist"
	-$(REMOVE) $(GENERATED)
	-$(REMOVE) "5GAutoConf.egg-info"
	-$(REMOVE) "scripts/__pycache__"
	-$(REMOVE) "tables"
	-$(REMOVE) "plots"
	-$(REMOVE) $(VENV_DIR)
	-$(REMOVE) ".pytest_cache"
	-$(REMOVE) "gnbautoconf.egg-info"
	-$(REMOVE) ".coverage"