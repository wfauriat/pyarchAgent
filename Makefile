PYTHON = /opt/venvs/pyDS/bin/python

.PHONY: help ollama_backend anthropic_backend test

help:
	@echo "====help===="
	@echo "make ollama_backend"
	@echo "make anthropic_backend"
	@echo "make test"	
	@echo "============"

ollama_backend:
	$(PYTHON) -m agentAPI.ollama_backend

anthropic_backend:
	$(PYTHON) -m agentAPI.anthropic_backend

test:
	$(PYTHON) -m pytest -v