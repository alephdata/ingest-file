IMAGE=alephdata/ingest-file
COMPOSE=docker-compose
DOCKER=$(COMPOSE) run --rm ingest-file
TAG=latest

.PHONY: build push

all: build shell

pull:
	$(COMPOSE) pull --include-deps --ignore-pull-failures

build:
	$(COMPOSE) build --pull

push:
	docker push $(IMAGE):$(TAG)

services:
	$(COMPOSE) up -d --remove-orphans postgres convert-document redis

shell: services
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
