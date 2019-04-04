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

Invoking Scrapy Spiders
^^^^^^^^^^^^^^^^^^^^^^^

Spiders can be run locally by invoking Scrapy, or by running the AWS Lambda handler:

.. code-block:: bash

    $ scrapy crawl tvinna
    2019-04-04 10:35:00 [scrapy.utils.log] INFO: Scrapy 1.6.0 started (bot: jobs)
    ...
    $ python lambda.py
    2019-04-04 10:35:24 [scrapy.utils.log] INFO: Scrapy 1.6.0 started (bot: jobs)
    ...


Testing
-------

Tests are invoked with pytest:

.. code-block:: bash

    $ pytest --disable-pytest-warnings --doctest-modules --doctest-report ndiff jobs

Deploying
---------

Deployments are handled using Serverless_ deployments. To install the `sls` tool you need to use `npm`:

.. code-block:: bash

    $ npm install -g serverless
    /usr/local/bin/serverless -> /usr/local/lib/node_modules/serverless/bin/serverless
    /usr/local/bin/slss -> /usr/local/lib/node_modules/serverless/bin/serverless
    /usr/local/bin/sls -> /usr/local/lib/node_modules/serverless/bin/serverless
    $ sls create --template aws-python3 --name spiders --path spiders
    Serverless: Generating boilerplate...
    ...
    $ npm install --save serverless-python-requirements
    ...

The above commands install the command line tool, creates a template, and installs the Python requirements extension.
The AWS Lambdas are then deployed using the `sls` tool:

.. code-block:: bash

    $ sls deploy --region eu-central-1


.. |Build Status| image:: https://travis-ci.org/multiplechoice/spiders.svg?branch=master
  :target: https://travis-ci.org/multiplechoice/spiders
.. |Coveralls Status| image:: https://coveralls.io/repos/github/multiplechoice/spiders/badge.svg?branch=master
  :target: https://coveralls.io/github/multiplechoice/spiders?branch=master
.. |Updates| image:: https://pyup.io/repos/github/multiplechoice/spiders/shield.svg
  :target: https://pyup.io/repos/github/multiplechoice/spiders/
  :alt: Updates
.. _Serverless: https://serverless.com/