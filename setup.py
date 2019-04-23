#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='ingestors',
    version='0.13.0',
    description="Ingestors extract useful information in a structured standard format.",  # noqa
    author="Organized Crime and Corruption Reporting Project",
    author_email='data@occrp.org',
    url='https://github.com/alephdata/ingestors',
    packages=find_packages(exclude=['tests']),
    package_dir={'ingestors': 'ingestors'},
    include_package_data=True,
    install_requires=[
        'click >= 7.0',
        'banal >= 0.4.2',
        'normality >= 1.0.0',
        'servicelayer >= 1.0.0',
        'pantomime >= 0.3.3',
        'requests[security] >= 2.21.0',
        'xlrd >= 1.2.0',
        'openpyxl >= 2.5.14',
        'followthemoney >= 1.3.0',
        'odfpy >= 1.3.5',
        'cchardet >= 2.1.1',
        'lxml >= 4.2.1',
        'pillow >= 5.1.0',
        'olefile >= 0.44',
        'python-magic >= 0.4.12',
        'pypdf2 >= 1.26.0',
        'rarfile >= 3.0',
        'flanker >= 0.9.0',
        'ply >= 3.10',
        'imapclient >= 1.0.2',
        'dbf >= 0.96.8',
        'pdflib >= 0.1.5',
        'pymediainfo >= 2.3.0',
        'balkhash >= 0.3.3',
    ],
    extras_require={
        'dev': [
            'bumpversion>=0.5.3',
            'wheel>=0.29.0',
            'flake8>=2.6.0',
            'nose',
            'coverage>=4.1'
        ],
        'tesseract': [
            'tesserocr >= 2.2.2',
        ],
        'google': [
            'google-cloud-vision',
        ]
    },
    license="MIT",
    zip_safe=False,
    keywords='ingestors',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=[],
    entry_points={
        'ingestors': [
            'ignore = ingestors.ignore:IgnoreIngestor',
            'html = ingestors.documents.html:HTMLIngestor',
            'xml = ingestors.documents.xml:XMLIngestor',
            'plain = ingestors.documents.plain:PlainTextIngestor',
            'office = ingestors.documents.office:DocumentIngestor',
            'opendoc = ingestors.documents.opendoc:OpenDocumentIngestor',
            'ooxml = ingestors.documents.ooxml:OfficeOpenXMLIngestor',
            'djvu = ingestors.documents.djvu:DjVuIngestor',
            'pdf = ingestors.documents.pdf:PDFIngestor',
            'rar = ingestors.packages.rar:RARIngestor',
            'zip = ingestors.packages.zip:ZipIngestor',
            'tar = ingestors.packages.tar:TarIngestor',
            '7z = ingestors.packages:SevenZipIngestor',
            'gz = ingestors.packages:GzipIngestor',
            'bz2 = ingestors.packages:BZ2Ingestor',
            'pst = ingestors.email.outlookpst:OutlookPSTIngestor',
            'olm = ingestors.email.olm:OutlookOLMArchiveIngestor',
            'opfmsg = ingestors.email.olm:OutlookOLMMessageIngestor',
            'olemsg = ingestors.email.outlookmsg:OutlookMsgIngestor',
            'msg = ingestors.email.msg:RFC822Ingestor',
            'csv = ingestors.tabular.csv:CSVIngestor',
            'access = ingestors.tabular.access:AccessIngestor',
            'sqlite = ingestors.tabular.sqlite:SQLiteIngestor',
            'xls = ingestors.tabular.xls:ExcelIngestor',
            'xlsx = ingestors.tabular.xlsx:ExcelXMLIngestor',
            'ods = ingestors.tabular.ods:OpenOfficeSpreadsheetIngestor',
            'mbox = ingestors.email.mbox:MboxFileIngestor',
            'dbf = ingestors.tabular.dbf:DBFIngestor',
            'image = ingestors.media.image:ImageIngestor',
            'tiff = ingestors.media.tiff:TIFFIngestor',
            'svg = ingestors.media.svg:SVGIngestor',
            'audio = ingestors.media.audio:AudioIngestor',
            'video = ingestors.media.video:VideoIngestor'
        ],
        'console_scripts': [
            'ingestors = ingestors.cli:cli'
        ],
    }
)
