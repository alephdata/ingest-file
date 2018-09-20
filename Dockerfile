FROM ubuntu:18.04
ENV DEBIAN_FRONTEND noninteractive

# Enable non-free archive for `unrar`.
# RUN echo "deb http://http.us.debian.org/debian stretch non-free" >/etc/apt/sources.list.d/nonfree.list
RUN apt-get -qq -y update \
    && apt-get -q -y install build-essential locales ca-certificates \
        # python deps (mostly to install their dependencies)
        python3-pip python3-dev python3-pil \
        # libraries
        libxslt1-dev libpq-dev libldap2-dev libsasl2-dev \
        zlib1g-dev libicu-dev libxml2-dev \
        # package tools
        unrar p7zip-full  \
        # audio & video metadata
        libmediainfo-dev \
        # image processing, djvu
        imagemagick-common imagemagick mdbtools djvulibre-bin \
        libtiff5-dev libjpeg-dev libfreetype6-dev libwebp-dev \
        # tesseract
        libtesseract-dev tesseract-ocr-eng libleptonica-dev \
        # pdf processing toolkit
        poppler-utils poppler-data pst-utils \
        # document processing
        libreoffice \
        # libpff build tools
        git autoconf automake autopoint libtool pkg-config \
    && apt-get -qq -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set up the locale and make sure the system uses unicode for the file system.
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# en_GB.ISO-8859-15 ISO-8859-15/en_GB.ISO-8859-15 ISO-8859-15/' /etc/locale.gen && \
    locale-gen
ENV LANG='en_US.UTF-8' \
    LANGUAGE='en_US:en' \
    LC_ALL='en_US.UTF-8'

RUN pip3 install -q --upgrade pip setuptools six wheel
RUN curl -SL "https://github.com/sunu/libpff/archive/master.tar.gz" | tar -xz -C /tmp/ && cd /tmp/libpff-master \
    && ./synclibs.sh && ./autogen.sh && ./configure --enable-python \
    && cd /tmp/libpff-master && python3 setup.py install
RUN pip3 install -q banal>=0.3.4 \
                   normality>=0.5.11 \
                   celestial>=0.2.3 \
                   urllib3>=1.21 \
                   requests>=2.18.4 \
                   xlrd>=1.1.0 \
                   pyicu>=2.0.3 \
                   openpyxl>=2.5.3 \
                   odfpy>=1.3.5 \
                   cchardet>=2.1.1 \
                   lxml>=4.2.1 \
                   pillow>=5.1.0 \
                   olefile>=0.44 \
                   tesserocr>=2.2.2 \
                   python-magic>=0.4.12 \
                   pypdf2>=1.26.0 \
                   rarfile>=3.0 \
                   flanker>=0.9.0 \
                   ply==3.10 \
                   imapclient>=1.0.2 \
                   dbf>=0.96.8 \
                   pdflib>=0.1.5 \
                   pymediainfo>=2.3.0 \
                   nose

COPY . /ingestors
WORKDIR /ingestors
RUN pip3 install -e /ingestors[dev]