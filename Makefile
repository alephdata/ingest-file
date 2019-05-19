DOCKER=docker-compose run --rm shell 
IMAGE=alephdata/ingest-file:latest

build:
	docker build -t $(IMAGE) .

push:
	docker push $(IMAGE)

shell:
	$(DOCKER) bash

lint: ## check style with flake8
	$(DOCKER) flake8 ingestors tests

test: build ## run tests quickly with the default Python
	$(DOCKER) nosetests --with-coverage --cover-package=ingestors

dist: ## builds source and wheel package
	$(DOCKER) python3 setup.py sdist bdist_wheel

clean:
	rm -fr dist/

.PHONY: dist build test shell clean