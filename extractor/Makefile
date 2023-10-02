.PHONY: clean format install install-env install-system test uninstall

install: install-system install-env

install-system:
	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt update && sudo apt install ffmpeg python3.11 python3.11-venv -y

install-env:
	python3.11 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

format:
	venv/bin/autopep8 --in-place --recursive extractor/
	venv/bin/autopep8 --in-place --recursive tests/
	venv/bin/isort extractor/
	venv/bin/isort tests/

test:
	. venv/bin/activate && python -m unittest discover

clean:
	find -name "__pycache__" -exec rm -rv {} +

uninstall:
	rm -rf venv