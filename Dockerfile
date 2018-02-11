FROM alephdata/platform:2.0.0

COPY . /ingestors
WORKDIR /ingestors
RUN pip install -e /ingestors[dev]