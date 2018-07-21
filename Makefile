DOCKER=docker run -v $(PWD)/dist:/ingestors/dist -ti alephdata/ingestors

build:
	# docker pull alephdata/ingestors
	docker build --cache-from alephdata/ingestors -t alephdata/ingestors .

shell:
	$(DOCKER) bash

lint: ## check style with flake8
	$(DOCKER) flake8 ingestors tests

test: ## run tests quickly with the default Python
	$(DOCKER) nosetests --with-coverage --cover-package=ingestors

dist: ## builds source and wheel package
	$(DOCKER) python setup.py sdist bdist_wheel

clean: 
	rm -fr dist/
