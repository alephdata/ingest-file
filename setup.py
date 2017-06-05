#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    name='ingestors',
    version='0.2.0',
    description="""
    Ingestors extract useful informationin a structured standard format.
    """.strip(),
    long_description=readme + '\n\n' + history,
    author="Stas Sușcov",
    author_email='stas+ingestors@nerd.ro',
    url='https://github.com/alephdata/ingestors',
    packages=find_packages(exclude=['tests']),
    package_dir={'ingestors': 'ingestors'},
    include_package_data=True,
    install_requires=[
        'normality>=0.4.0',
        'urllib3>=1.21',
        'subprocess32==3.2.7',
        'messytables==0.15.2',
        'unicodecsv==0.14.1',
        'lxml==3.7.3',
        'pillow==4.0.0',
        'tesserwrap==0.1.6',
        'python-magic==0.4.12',
        'pycountry>=17.5',
        'rarfile==3.0'
    ],
    license="MIT",
    zip_safe=False,
    keywords='ingestors',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=[],
    entry_points={
        'ingestors': [
            'html = ingestors.documents.html:HTMLIngestor',
            'plain = ingestors.documents.plain:PlainTextIngestor',
            'office = ingestors.documents.office:DocumentIngestor',
            'image = ingestors.documents.image:ImageIngestor',
            'djvu = ingestors.documents.djvu:DjVuIngestor',
            'pdf = ingestors.documents.pdf:PDFIngestor',
            'rar = ingestors.packages:RARIngestor',
            'zip = ingestors.packages:ZipIngestor',
            'tar = ingestors.packages:TarIngestor',
            '7z = ingestors.packages:SevenZipIngestor',
            'gz = ingestors.packages:GzipIngestor',
            'bz2 = ingestors.packages:BZ2Ingestor'
        ]
    }
)
