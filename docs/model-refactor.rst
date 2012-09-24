=========================
Data model refactor notes
=========================

Some useful information about the data model refactor.

.. contents::

Porting Guide
=============

Here is a list of fields you'll probably encounter while refactoring things to
fit the new data model and how to deal with them.

is_original
-----------

Previously
~~~~~~~~~~

The ``is_original`` field on a ``SubtitleLanguage`` specified
whether that language was the "original" or "primary audio language" of its
video.

After Refactoring
~~~~~~~~~~~~~~~~~

This information has been moved to the ``Video`` model,
as the field ``primary_audio_language_code``.

``primary_audio_language_code`` is a character field containing language codes
as strings, like ``"en"`` or ``pt-br``.

Porting
~~~~~~~

In a lot of places we may check to see if a language is the original one for its
video::

    if sublanguage.is_original:
        pass

In the new model you can do that by comparing language codes::

    if sublanguage.language_code == sublanguage.video.primary_audio_language_code:
        pass

This may be worth turning into a convenience function at some point so we can be
mroe concise::

    if sublanguage.is_primary_audio_language():
        pass

