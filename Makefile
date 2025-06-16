INGEST=ghcr.io/openaleph/ingest-file
COMPOSE=docker compose
DOCKER=$(COMPOSE) run --rm ingest-file

.PHONY: build

all: build shell

build:
	$(COMPOSE) build --no-rm --parallel

services:
	$(COMPOSE) up -d --remove-orphans postgres redis

shell: services
	$(DOCKER) /bin/bash

lint:
	ruff check .

format:
	black .

format-check:
	black --check .

test: build services
	PYTHONDEVMODE=1 PYTHONTRACEMALLOC=1 $(DOCKER) pytest --cov=ingestors --cov-report html --cov-report term

restart: build
	$(COMPOSE) up --force-recreate --no-deps --detach ingest-file

tail:
	$(COMPOSE) logs -f

stop:
	$(COMPOSE) down --remove-orphans

clean:
	rm -rf dist build
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -type d -name __pycache__ -exec rm -r {} \+

dev:
	python3 -m pip install --upgrade pip
	python3 -m pip install -q -r requirements-dev.txt
