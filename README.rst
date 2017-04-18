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

Once installed, this package provides a command line tool::

    $ python -m ingestors.cli <PATH TO YOUR FILE>

This tool will print the JSON formatted results.

.. code-block:: console

    $ python -m ingestors.cli tests/fixtures/image.svg
    {
      "authors": [],
      "checksum": "a0233ebbf9d64a0adf1ddf13be248cd48c2ad69f",
      "content": "Testing ingestors 1..2..3..",
      "file_size": 15969,
      "mime_type": "image/svg+xml",
      "order": 0,
      "title": "image.svg"
    }

There's also a simple API you can use.
For more help, please see the `usage <specs.html>`_.


.. code-block:: python

    import io
    import ingestors

    with io.open('myfile.txt', 'rb') as fio:
        ingestor, data, children_data = ingestors.ingest(fio, file_path)

        print ingestor, data, children_data

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
