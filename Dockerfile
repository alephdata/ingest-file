FROM alephdata/platform:2.1.0

RUN apt-get -qq -y update \
    && apt-get -qq -y install libreoffice

COPY . /ingestors
WORKDIR /ingestors
RUN pip install nose
RUN pip install -e /ingestors[dev]
# force install flanker from github
RUN pip install -U git+https://github.com/mailgun/flanker.git@ce552940497d10a167aa5ee25c0ef8a89f3e080f#egg=flanker