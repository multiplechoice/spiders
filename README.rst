|Build Status| |Coveralls Status| |Updates|

Spiders
=======

Scrapy based spiders that crawl for job listings.

Scrapes `Tvinna <http://www.tvinna.is/>`__, `Morgunblaðið <http://www.mbl.is/atvinna/>`__, `Job.is <https://atvinna.frettabladid.is/>`__ and `Alfreð <https://alfred.is/>`__ for job postings.

This project relies upon the ``multiplechoice/sqlalchemy-mappings`` project to maintain the correct database structures.

Developing
----------

Development is done in Python using the Scrapy_ library. Scrapy is used to download and then parse the target websites.
We use the selectors within Scrapy to extract spcific XPath or CSS elements containing the relevant advertisement 
information. Generally job adverts contain most of the following elements (internal variable names are in brackets):
 * the company recruiting (*company*)
 * the position being advertised (*title*)
 * the date of posting (*posted*)
 * the deadline for applications (*deadline*)
 * a descriptive text (*description*)
 * an image showing a formatted advert (*images* and *file_urls*)

In addition we extract the URL to the specific advert. These may rot overtime but are useful to store.

Extracting Images from Adverts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some advertisements include both a descriptive text and an image. The images are often the same as might be found in
a print version of the advert in a newspaper or magazine. We can extract and save these images for display later.

The images are extracted by setting the *file_urls* variable within the scraped job object (*items.JobsItem*). The object
stores the parsed elements from the advertisement and is what is persisted to the database.

By adding a URL to the *file_urls* attribute the *pipelines.ImageDownloader* class is invoked that will save the given 
URLs to the specified backend.

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

    $ pytest --disable-pytest-warnings --doctest-modules --doctest-report ndiff jobs tests

Deploying
---------

Deployments are handled using Serverless_ deployments. To install the ``sls`` tool you need to use ``npm``:

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
The AWS Lambdas are then deployed using the ``sls`` tool:

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
.. _Scrapy: https://scrapy.org/
