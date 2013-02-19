Subtitle Storage
================

This document describes the format for storing subtitles in the new data model,
which is not in use yet!  If you're reading this, make sure you know what you're
doing!

``SubtitleVersion`` objects store their subtitles as a blob of JSON in the
database.  You should use the ``subtitle`` property to get and set this as
a Python object for convenience.

Main Structure
--------------

Subtitles are stored as a list::

    [subtitle, subtitle, ...]

This list should be in order.  This is up to you to manage when creating/editing
it.

.. note:: TODO: Use bisection to find subtitles fast once the Python community
          stops bikeshedding and adds the key= argument to the bisection
          functions.

Subtitle Structure
------------------

A single subtitle, as a Python object, looks like this::

    { 'start_ms': 4506,
      'end_ms': 7800,
      'content': "Today we're going to look at some cat pictures.",
      'meta': {
        'starts_paragraph': True,
      },
    }

``start_ms`` and ``end_ms`` are the starting and ending times of the subtitle,
in milliseconds.  Do not try to use sub-millisecond precision.  No one needs
that, and it will make comparing the floats for equality more complicated.

``content`` is the actual text of the subtitle.  This is encoded in our
internal, Markdown-like format.

The ``meta`` dictionary may contain other fields with information about this
subtitle.  It may or may not contain a given key, so you'll want to always use
``subtitle['meta'].get('foo')``.

Currently the following metadata can be found in some subtitles:

``starts_paragraph`` is pretty self explanatory.  If it's not in the ``meta``
dict assume it's ``False``.
