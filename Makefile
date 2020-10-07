IMAGE=alephdata/ingest-file
COMPOSE=docker-compose
DOCKER=$(COMPOSE) run --rm ingest-file
TAG=latest

.PHONY: build push

all: build shell

pull:
	$(COMPOSE) pull --include-deps --ignore-pull-failures

build:
	$(COMPOSE) build

push:
	docker push $(IMAGE):$(TAG)

services:
	$(COMPOSE) up -d --remove-orphans postgres convert-document redis

shell: services
	$(DOCKER) /bin/bash

test:
	$(DOCKER) nosetests --with-coverage --cover-package=ingestors

restart:
	$(COMPOSE) build ingest-file convert-document
	$(COMPOSE) up --force-recreate --no-deps --detach convert-document ingest-file

tail:
	$(COMPOSE) logs -f

stop:
	$(COMPOSE) down --remove-orphans

clean:
	rm -rf dist build .eggs ui/build
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -type d -name __pycache__ -exec rm -r {} \+
	find ui/src -name '*.css' -exec rm -f {} +

dev: 
	pip install -q bump2version babel jinja2
