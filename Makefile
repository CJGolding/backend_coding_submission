SHELL := /bin/bash

.PHONY: init requirements test lint clean

init:
	rm -rf .venv
	python3 -m venv .venv && \
	source .venv/bin/activate 

requirements:
	source .venv/bin/activate && \
	pip install -r requirements.txt 

test:
	source .venv/bin/activate && \
	coverage run --omit '.venv/*' -m pytest --junitxml=./test-results/test-results.xml -v tests/ && \
	coverage report -m

lint:
	source .venv/bin/activate && \
	pip install pylint && \
	pylint --fail-under=8 ./src

clean:
	rm -rf .venv/ && \
	rm -f .coverage && \
	rm -rf test-results/

run: 
	source .venv/bin/activate && \
	python3 src/main.py