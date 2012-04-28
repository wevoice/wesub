Deployment Guide
================

To deploy Amara to the various environments we use Fabric.

Many deployments can be done with a very simple set of Fabric tasks, but read
through each of the following sections to see if you need to worry about them.

Specifying an Environment
-------------------------

Whenever you're running deployment tasks you need to specify the environment.
You'll need to do this every time you run the ``fab`` command.  For example::

    fab dev:sjl ...
    fab staging:nicksergeant ...

There is a separate task for each environment (``dev``, ``staging`` and,
``prod``).  You need to specify your username as an argument to the task as in
the example above.

Fabric Output and Logging
-------------------------

Deployment Steps
----------------

There are several steps/components to our deployment process.  You won't always
need to run all of them (many deployments will only need the main deployment
step) but you should read through them all.

Maintenance Pages
~~~~~~~~~~~~~~~~~

When deploying to production you should make sure to display the "Universal
Subtitles is currently down for maintenance" page so users won't see
a partially-deployed version of the site while the deployment is happening.

For deployments to dev or staging we don't usually bother putting up the page.
Few enough people use those environments that it's not worth the extra effort.
If you really want to, though, you can.

To put up the maintenance page you can use the ``add_disabled`` task.  You can
then do whatever you need to do to actually deploy the site, then take down the
maintenance page using ``remove_disabled``::

    fab staging:sjl add_disabled
    fab staging:sjl ...
    fab staging:sjl remove_disabled

New Python Requirements
~~~~~~~~~~~~~~~~~~~~~~~

If new requirements have been added to ``requirements.txt`` you'll need to run
this task to ``pip install`` them::

    fab <environment> update_environment

If no new requirements were added you can skip this step.

New Django Apps
~~~~~~~~~~~~~~~

If new Django applications were created or added (*including third-party ones!*)
you'll need to sync them into the database::

    fab <environment> syncdb

If no new apps were created or added you can skip this step.

Database Migrations
~~~~~~~~~~~~~~~~~~~

If any new database migrations have been added (including any from new third
party apps, see above) you'll need to run them::

    fab <environment> migrate

For some migrations (especially ones having to do with Subtitle and
SubtitleVersion tables) this can take a long time and runs the risk of your SSH
connection failing, so they are run in a screen session to be safe.

If you've converted an app to South, you'll need to fake the migration (this is
extremely rare for us to do though)::

    fab <environment> migrate_fake:<app_name> # if we converted an app to south, pretty rare

.. note:: TODO: Talk about the logging

Code Deployment
~~~~~~~~~~~~~~~

The main deployment step, and the one that you'll always need to do is
``update``::

    fab <environment> update

This will actually update the Django code, as well as rebuild/package/upload the
static media files.

.. note:: TODO: talk about update_static and update_web

Solr Reindexing
~~~~~~~~~~~~~~~

If any of the Solr schemas have changed you'll need to update the schema and
kick off a reindexing::

    fab <environment> update_solr_schema

This will take a **long** time (on the order of a few hours).  The Fabric task
will start the reindexing process in a screen session and immediately detach.
The dev mailing list will get an email when it finishes.

.. note:: TODO: Talk about the logging

Review/Conclusion
-----------------

For a full deployment the process would look like this::

    fab <environment> add_disabled
    fab <environment> update_environment
    fab <environment> syncdb
    fab <environment> migrate_fake:<app_name> # if we converted an app to south, pretty rare
    fab <environment> migrate
    fab <environment> update
    fab <environment> remove_disabled
    fab <environment> update_solr_schema

However, most deployments won't need all of these.  In fact you can usually get
away with a simple::

    fab staging:sjl update

if you're deploying to dev or staging.

.. note: TODO: talk about switch_branch ?
