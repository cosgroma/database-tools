========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - |github-actions| |codecov|
    * - package
      - |version| |wheel| |supported-versions| |supported-implementations| |commits-since|

.. |github-actions| image:: https://github.com/cosgroma/database-tools/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/cosgroma/database-tools/actions

.. |codecov| image:: https://codecov.io/gh/cosgroma/database-tools/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://app.codecov.io/github/cosgroma/database-tools

.. |version| image:: https://img.shields.io/pypi/v/databasetools.svg
    :alt: PyPI Package latest release
    :target: https://pypi.org/project/databasetools

.. |wheel| image:: https://img.shields.io/pypi/wheel/databasetools.svg
    :alt: PyPI Wheel
    :target: https://pypi.org/project/databasetools

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/databasetools.svg
    :alt: Supported versions
    :target: https://pypi.org/project/databasetools

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/databasetools.svg
    :alt: Supported implementations
    :target: https://pypi.org/project/databasetools

.. |commits-since| image:: https://img.shields.io/github/commits-since/cosgroma/database-tools/v0.0.0.svg
    :alt: Commits since latest release
    :target: https://github.com/cosgroma/database-tools/compare/v0.0.0...main



.. end-badges

Document Database tools and helpers.

* Free software: GNU Lesser General Public License v3 or later (LGPLv3+)

Installation
============

::

    pip install databasetools

You can also install the in-development version with::

    pip install https://github.com/cosgroma/database-tools/archive/main.zip


Documentation
=============


To use the project:

.. code-block:: python

    import databasetools
    databasetools.compute(...)



Development
===========

To run all the tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
