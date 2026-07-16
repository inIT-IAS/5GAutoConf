VENV_DIR := .venv

ifeq ($(OS),Windows_NT)
	PYTHON_BIN := python
	PYTHON := $(VENV_DIR)/Scripts/python.exe
	SPHINX_APIDOC := $(VENV_DIR)/Scripts/sphinx-apidoc.exe
	SPHINX_BUILD := $(VENV_DIR)/Scripts/sphinx-build.exe
	PIP := $(VENV_DIR)/Scripts/pip.exe
	READMECOV := $(VENV_DIR)/Scripts/readme-cov.exe
	REMOVE := powershell -Command "Remove-Item -Recurse -Force -ErrorAction Ignore"
	GENERATED := '*.generated.*'
else
	PYTHON_BIN := python3
	PYTHON := $(VENV_DIR)/bin/python3
	SPHINX_APIDOC := $(VENV_DIR)/bin/sphinx-apidoc
	SPHINX_BUILD := $(VENV_DIR)/bin/sphinx-build
	PIP := $(VENV_DIR)/bin/pip3
	READMECOV := $(VENV_DIR)/bin/readme-cov
	REMOVE := rm -rf
	GENERATED := *.generated.*
endif

.PHONY: run synth build install docs test test-slow clean

run:
	$(PYTHON) run.py -f 78 -b 40 -r 30 -d TDD -c 3780 -s b210 -l info

synth:
	$(PYTHON) run.py -f 78 -b 40 -c 3780 -s b210 -l info n=1.000293 r-cell=1900 ue-speed=27.78 tau-d=15.00 x=1 y=0 subframe-number=9 starting-symbol=0 n-slot-ra=2 n-t-ra-slot=1 n-dur-ra=12

debug:
	$(PYTHON) run.py -f 78 -b 40 -r 30 -d TDD -c 3780 -s b210 -l debug

build:
	$(PYTHON) -m build

install:
	$(PYTHON_BIN) -m venv $(VENV_DIR)
	$(PIP) install ".[dev,dist]"
	$(PYTHON) -m compileall .
	$(PYTHON) -m scripts.build_long_guard_time_prach_pusch_combination_tables
	$(PYTHON) -m scripts.build_prach_ssb_collision_free_tables
	$(PYTHON) -m scripts.build_tau_d_max_rtd_max_table

docs:
	$(SPHINX_APIDOC) -f -o docs/api . docs site test.py
	$(SPHINX_BUILD) -b html --keep-going docs docs/_build

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
	-$(REMOVE) "docs/api"
	-$(REMOVE) "docs/_build"
	-$(REMOVE) "docs/__pycache__"