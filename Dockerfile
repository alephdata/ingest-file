FROM alephdata/platform:2.0.5

RUN apt-get -qq -y update \
    && apt-get -qq -y upgrade \
    && apt-get -qq -y install libreoffice

COPY . /ingestors
WORKDIR /ingestors
RUN pip install -e /ingestors[dev]