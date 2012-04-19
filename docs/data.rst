Data representation
===================

This document describes how data is stored in the database.  A lot of the
following items are interconnected so be sure to read the whole document.

.. warning:: This is a work in progress.

Videos
------

The video model contains the usual meta such as the *ID*, *title* and
*description*.

A video can be *claimed* by a team.  This means that the original owner loses
his or her privileges associated with the ownership of the video.  Teams are
created via the Django admin and only trusted users can have teams created for
them.  Connecting videos with teams is done via the ``TeamVideo`` model.

Languages
~~~~~~~~~

A subtitle language is attached to a video object.

There is a notion of a preferred language.  A team can choose which languages
are important to them and request that those be translated first.

.. seealso:: :doc:`List of supported languages </languages>`.

Versions
~~~~~~~~

Versions are 0-indexed.

A subtitle version is attached to subtitle language.  This means that each
language maintains its versions independently of others.

Version visibility is determined by its owner.  If a video is owned by a single
user (i.e. not a team), all versions for that video are public.  However, if
it's owned by a team, only team members can see all versions.

Teams
-----

A team has a number of different roles.

.. seealso:: :doc:`Roles and permissions </permissions>`

Tasks
~~~~~

Once a video is added, transcription and translation tasks can be assigned to
team members.
