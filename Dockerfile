FROM alephdata/platform:2.0.1

COPY . /ingestors
WORKDIR /ingestors
RUN pip install -e /ingestors[dev]