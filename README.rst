Ingestors extract useful information in a structured standard format.

Ingestors is free software under MIT license.

.. image:: https://img.shields.io/travis/alephdata/ingestors.svg
   :target: https://travis-ci.org/alephdata/ingestors
   :alt: Build Status

.. image:: https://readthedocs.org/projects/ingestors/badge/?version=latest
   :target: https://ingestors.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

Supported file types:

* Plain text
* Images
* Web pages
* PDF files

Other features:

* Extendable and composable using classes and mixins.
* Serializable results object with basic metadata support.
* Throughly tested using local and external set of fixtures.
* Lightweight worker-style support for logging, failures and callbacks.

============
Installation
============

To install Ingestors, use `pip` or add it to your project dependencies.

.. code-block:: console

    $ pip install ingestors

To install all system dependencies, use::

    $ pip install ingestors[full]

If you don't have `pip` installed, this `Python installation guide`_ can guide
you through the process.

.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


Documentation
-------------

The documentation for Ingestors is available at
`ingestors.readthedocs.io <http://ingestors.readthedocs.io/>`_.

Feel free to edit the source files in the ``docs`` folder and send pull
requests for improvements.

To build the documentation, please install the dependencies first and run
``make docs``::

  $ pip install -r requirements_dev.txt
  $ make docs


Now you can browse the documentation locally at
``http://localhost:8000/docs/_build/html/``::

  $ make docs-web
