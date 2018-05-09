FROM alephdata/platform:2.0.5

RUN apt-get -qq -y update \
    && apt-get -qq -y upgrade \
    && apt-get -qq -y install libreoffice python3-pip

COPY . /ingestors
WORKDIR /ingestors
RUN pip3 install nose
RUN pip3 install -e /ingestors[dev]
# force install flanker from github
RUN pip3 install -U git+https://github.com/mailgun/flanker.git@ce552940497d10a167aa5ee25c0ef8a89f3e080f#egg=flanker