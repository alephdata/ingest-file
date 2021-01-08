INGEST=ghcr.io/alephdata/ingest-file
CONVERT=ghcr.io/alephdata/convert-document
COMPOSE=docker-compose
DOCKER=$(COMPOSE) run --rm ingest-file

.PHONY: build

all: build shell

build:
	$(COMPOSE) build --no-rm --parallel

pull-cache:
	-docker pull -q $(INGEST):cache
	-docker pull -q $(CONVERT):cache

cached-build: pull-cache
	docker build --cache-from $(INGEST):cache -t $(INGEST) .
	docker build --cache-from $(CONVERT):cache -t $(CONVERT) convert

fresh-cache:
	docker build --pull --no-cache -t $(INGEST):cache .
    docker build --pull --no-cache -t $(CONVERT):cache convert

services:
	$(COMPOSE) up -d --remove-orphans postgres redis

shell: services
	$(COMPOSE) up -d --remove-orphans convert-document
	$(DOCKER) /bin/bash

test: services
	$(DOCKER) nosetests --with-coverage --cover-package=ingestors

restart: build
	$(COMPOSE) up --force-recreate --no-deps --detach convert-document ingest-file

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
	pip install -q bump2version
