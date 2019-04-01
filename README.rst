|Build Status| |Coveralls Status| |Updates|

Spiders
=======

Scrapy based spiders that crawl for job listings.

Scrapes `Tvinna <http://www.tvinna.is/>`__, `Morgunblaðið <http://www.mbl.is/atvinna/>`__, `Vísir <https://job.visir.is/>`__ and `Alfreð <https://alfred.is/>`__ for job postings.

This project relies upon the `multiplechoice/sqlalchemy-mappings` project to maintain the correct database structures.

Running
-------

The project uses Pyenv to control the virtualenv, which is installed with the following command:

.. code-block:: bash

    $ pyenv virtualenv 3.7.2 spiders-3.7.2

Once this is done the requirements can be installed with Pip in the usual manner.

Testing
-------

Tests are invoked with pytest:

.. code-block:: bash

    $ pytest --disable-pytest-warnings --doctest-modules --doctest-report ndiff jobs

.. |Build Status| image:: https://travis-ci.org/multiplechoice/spiders.svg?branch=master
  :target: https://travis-ci.org/multiplechoice/spiders
.. |Coveralls Status| image:: https://coveralls.io/repos/github/multiplechoice/spiders/badge.svg?branch=master
  :target: https://coveralls.io/github/multiplechoice/spiders?branch=master
.. |Updates| image:: https://pyup.io/repos/github/multiplechoice/spiders/shield.svg
  :target: https://pyup.io/repos/github/multiplechoice/spiders/
  :alt: Updates
