Backwards incompatible changes in 1.4
=====================================

This page mirrors the *Backwards incompatible changes* section in the `Django
1.4 release notes`_.  Please refer to it when you make changes to this page.
The goal of this document is to spot any places where upgrading to Django 1.4
might break our app.

SECRET_KEY setting is required
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No issues.  The ``SECRET_KEY`` is already populated.

django.contrib.admin
~~~~~~~~~~~~~~~~~~~~

Supported browsers for the admin
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No issues.  Obviously, nobody who uses our admin interface still uses IE6.

Removed admin icons
~~~~~~~~~~~~~~~~~~~

CSS class names in admin forms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compatibility with old signed data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

django.contrib.flatpages
~~~~~~~~~~~~~~~~~~~~~~~~

Serialization of :class:`~datetime.datetime` and :class:`~datetime.time`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``supports_timezone`` changed to ``False`` for SQLite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``MySQLdb``-specific exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Database connection's thread-locality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`COMMENTS_BANNED_USERS_GROUP` setting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

`IGNORABLE_404_STARTS` and `IGNORABLE_404_ENDS` settings
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CSRF protection extended to PUT and DELETE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Password reset view now accepts ``subject_template_name``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``django.core.template_loaders``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``django.db.models.fields.URLField.verify_exists``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``django.core.files.storage.Storage.open``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

YAML deserializer now uses ``yaml.safe_load``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Session cookies now have the ``httponly`` flag by default
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``urlize`` filter no longer escapes every URL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``assertTemplateUsed`` and ``assertTemplateNotUsed`` as context manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Database connections after running the test suite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Output of ``manage.py help <help>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``extends`` template tag
~~~~~~~~~~~~~~~~~~~~~~~~

Loading some incomplete fixtures no longer works
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Development Server Multithreading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Attributes disabled in markdown when safe mode set
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

FormMixin get_initial returns an instance-specific dictionary
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




.. _Django 1.4 release notes: https://docs.djangoproject.com/en/dev/releases/1.4/#backwards-incompatible-changes-in-1-4
