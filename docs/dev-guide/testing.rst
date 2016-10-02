Testing
=======

The Amara project uses the `Nose <http://nose.readthedocs.org/en/latest/>`_
testing framework.

.. _running-tests:

Running tests
-------------

You should always run your tests inside the Vagrant VM because the test suite
depends on a running Solr instance.

To run all unittests:

::

    $ dev test

To run tests for a specific Django app:

::

    $ dev test videos

To run a specific test class:

::

    $ dev test videos.tests:ViewsTest


To run a specific test case within a test class:

::

    $ dev test videos.tests:ViewsTest.test_index

