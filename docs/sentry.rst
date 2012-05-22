Sentry
======

This document describes how you can run the Sentry server inside Vagrant.
Amara uses the latest sentry server and the raven client.  Django exceptions
are logged.  Regular Django logging goes to sentry as well.

1.  Log in to your vagrant VM
2.  Make sure all Python requirements are up-to-date
3.  ``$ ./dev-sentry.sh``
4.  Create a user for yourself
5.  Open http://unisubs.example.com:9000
6.  Log in to the console 
7.  Navigate the menus and find your server's DSN string
8.  Open ``dev_settings.py`` and paste your string to ``SENTRY_DSN``.  Change
    the host to ``localhost``.
9.  Turn ``DEBUG`` off.
10. Start your development server
11. Profit

.. note:: If you have been using Vagrant to develop Amara for a while, you will
    have to halt your VM and start it again to properly forward your ports.
    The sentry server runs on port 9000 and has to be opened up to the host
    machine.

You may have to add the following to your local settings

.. code-block:: python

    SENTRY_DSN = "your local dsn"
    SENTRY_DEBUG = False
    MIDDLEWARE_CLASSES = (
        'raven.contrib.django.middleware.SentryResponseErrorIdMiddleware',
        'raven.contrib.django.middleware.Sentry404CatchMiddleware',
        ) + MIDDLEWARE_CLASSES

Resources
---------

You might find these helpful when playing with Sentry:

* `Sentry docs <http://sentry.readthedocs.org/en/latest/index.html>`_
* `Sentry source <https://github.com/dcramer/sentry>`_
* `Raven docs <http://raven.readthedocs.org/en/latest/index.html>`_
* `Raven source <https://github.com/dcramer/raven>`_
