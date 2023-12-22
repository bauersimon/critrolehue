VENV := $(if $(IS_CI),,venv/bin/)

install: install-python install-apt install-venv
.PHONY: install

install-python:
	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt update && sudo apt install python3.11 python3.11-venv -y
.PHONY: install-python

install-apt:
	sudo apt update && sudo apt install ffmpeg -y
.PHONY: install-apt

install-venv: uninstall
	python3.11 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
.PHONY: install-venv

format:
	$(VENV)autopep8 --in-place --recursive extractor/
	$(VENV)autopep8 --in-place --recursive tests/
	$(VENV)isort extractor/
	$(VENV)isort tests/
	$(VENV)ruff --fix --fix-only -e extractor/
	$(VENV)ruff --fix --fix-only -e tests/
.PHONY: format

lint:
	$(VENV)ruff extractor/
	$(VENV)ruff tests/
	$(VENV)pyright extractor/
	$(VENV)pyright tests/
.PHONY: lint

test: clean
	$(VENV)coverage run -m unittest discover
	$(VENV)coverage combine
	$(VENV)coverage report
	$(VENV)coverage html
	$(VENV)coverage xml
	@if [ -z "$(IS_CI)" ]; then xdg-open htmlcov/index.html &> /dev/null; fi
.PHONY: test

clean:
	find -name "__pycache__" -exec rm -rv {} +
	rm -rf .coverage .ruff_cache htmlcov coverage.xml
.PHONY: clean

uninstall:
	rm -rf venv
.PHONY: uninstall