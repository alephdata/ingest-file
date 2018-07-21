FROM python:3.6-stretch
ENV DEBIAN_FRONTEND noninteractive

# Enable non-free archive for `unrar`.
RUN echo "deb http://http.us.debian.org/debian stretch non-free" >/etc/apt/sources.list.d/nonfree.list
RUN apt-get -q -y update \
    && apt-get -q -y install build-essential apt-utils locales \
        # python deps (mostly to install their dependencies)
        python3-pip python3-dev python3-pil libboost-python-dev \
        # libraries
        libxslt1-dev libgsf-1-dev zlib1g-dev libicu-dev libxml2-dev \
        # package tools
        unrar p7zip-full  \
        # image processing, djvu
        imagemagick-common imagemagick mdbtools djvulibre-bin \
        libtiff5-dev libjpeg-dev libfreetype6-dev libwebp-dev liblcms2-dev \
        # document processing
        libreoffice \
        # tesseract
        libtesseract-dev tesseract-ocr-eng libleptonica-dev \
        # pdf processing toolkit
        poppler-utils poppler-data \
        # audio & video metadata
        libmediainfo-dev \
    && apt-get -qq -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# New version of the PST file extractor
RUN ln -s /usr/bin/python /usr/bin/python3.6.6
RUN mkdir /tmp/libpst \
    && wget -qO- http://www.five-ten-sg.com/libpst/packages/libpst-0.6.71.tar.gz | tar xz -C /tmp/libpst --strip-components=1 \
    && cd /tmp/libpst \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/libpst

# Set up the locale and make sure the system uses unicode for the file system.
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# en_GB.ISO-8859-15 ISO-8859-15/en_GB.ISO-8859-15 ISO-8859-15/' /etc/locale.gen && \
    locale-gen
ENV LANG='en_US.UTF-8' \
    LANGUAGE='en_US:en' \
    LC_ALL='en_US.UTF-8'

RUN pip install -q --upgrade pip setuptools six wheel
RUN pip install -q banal>=0.3.4 \
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
RUN pip install -e /ingestors[dev]