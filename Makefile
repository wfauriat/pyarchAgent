PYTHON = /opt/venvs/pyDS/bin/python

.PHONY: help ollama_backend anthropic_backend

help:
	@echo "====help===="
	@echo "make ollama_backend"
	@echo "make anthropic_backend"
	@echo "============"

ollama_backend:
	$(PYTHON) -m src.ollama_backend

anthropic_backend:
	$(PYTHON) -m src.anthropic_backend