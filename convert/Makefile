IMAGE=ghcr.io/alephdata/convert-document:latest

build:
	docker build -t $(IMAGE) .

push:
	docker push $(IMAGE)

shell: build
	docker run -ti -v $(PWD):/convert -p 3000:3000 $(IMAGE) bash

run: build
	docker run -p 3000:3000 --tmpfs /tmp --rm -ti $(IMAGE)

test:
	rm out.pdf
	curl -o out.pdf -F format=pdf -F 'file=@fixtures/agreement.docx' http://localhost:3000/convert
