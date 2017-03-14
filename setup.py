#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'chardet==2.3.0'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='ingestors',
    version='0.1.0',
    description="""
    Ingestors extract useful informationin a structured standard format.
    """.strip(),
    long_description=readme + '\n\n' + history,
    author="Stas Sușcov",
    author_email='stas+ingestors@nerd.ro',
    url='https://github.com/alephdata/ingestors',
    packages=['ingestors'],
    package_dir={'ingestors': 'ingestors'},
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
