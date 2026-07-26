.PHONY: install lint format run test

ENV_NAME := techscout

install:
	conda env create -f environment.yml || conda env update -f environment.yml --prune

lint:
	flake8 techscout tests

format:
	black techscout tests

run:
	python -m techscout.main

test:
	pytest -v