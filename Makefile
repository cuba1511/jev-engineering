.PHONY: install cli api check

PYTHON := .venv/bin/python
PIP := $(PYTHON) -m pip

install:
	python3 -m venv .venv
	$(PIP) install -r requirements.txt

cli:
	$(PYTHON) -m app.cli

api:
	$(PYTHON) -m uvicorn app.api.main:app --reload

check:
	$(PYTHON) -m compileall app
