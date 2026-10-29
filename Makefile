# Rebuild the Mundelein study: make results, make paper, or make all.
# REPS sets the replicate count, e.g. `make results REPS=5` for a quick smoke test.

VENV   := .venv
PYTHON := $(VENV)/bin/python
REPS   ?= 60

.PHONY: all results paper test clean help

help:
	@echo "make venv      create .venv and install pinned requirements"
	@echo "make results   run the experiments (CSV tables and PDF figures); REPS=$(REPS)"
	@echo "make paper     build paper/paper.pdf with latexmk"
	@echo "make test      run the simulator verification tests"
	@echo "make all       results, then paper"
	@echo "make clean     remove LaTeX build files"

all: results paper

$(VENV)/.installed: requirements.txt
	python3 -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt
	touch $@

venv: $(VENV)/.installed

results: $(VENV)/.installed
	cd model && ../$(PYTHON) run_experiments.py $(REPS)

test: $(VENV)/.installed
	$(PYTHON) -m unittest discover -s tests -v

paper:
	cd paper && latexmk -pdf -interaction=nonstopmode paper.tex

clean:
	cd paper && latexmk -c
