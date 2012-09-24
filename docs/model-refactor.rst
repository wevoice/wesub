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

The ``is_original`` field on a ``SubtitleLanguage`` had two separate
meanings that should never have been shoehorned into the same field

* Is this language "standalone" (i.e.: "not a translation", or "was transcribed
  directly from the video")?
* Is this language the language that the people in the video are speaking?

Clearly these can be at odds.

Refactor
~~~~~~~~

The "is this language the language the people in the video are speaking" bit of
information has been moved to the ``Video`` model, as the field
``primary_audio_language_code``.

``primary_audio_language_code`` is a character field containing language codes
as strings, like ``"en"`` or ``pt-br``.

For the other meaning, see the next section of fields.

Porting
~~~~~~~

We may previously have tried to see if this language was the one spoken in the
video by checking ``is_original``::

    if sublanguage.is_original:
        pass

In the new model you can do that by comparing language codes::

    if sublanguage.language_code == sublanguage.video.primary_audio_language_code:
        pass

And now it's clear what you're actually checking.

This may be worth turning into a convenience function at some point so we can be
more concise::

    if sublanguage.is_primary_audio_language():
        pass

is_original, is_forked, is_dependent, standard_language
-------------------------------------------------------

These four fields are intertwined in horrible ways.

In the previous data model, a ``SubtitleLanguage`` could either stand on its
own, or be "dependent" on another language (the "translation" idea).

``is_original`` is a field that was used to specify that this language was
"transcribed directly from the video".  See the previous section for more
information.

``standard_language`` is the field that recorded what the "source" language for
a translation was.

``is_forked`` was added as a way to make previously-dependent languages
standalone.  There are a number of reasons why that was needed, none are
important here.

``is_dependent`` was a convenience method that tried to guess if the language
was standalone or dependent on another one.

Let's look at an example.  Suppose someone created a language A by transcribing
straight from the video::

    _   is_original  is_dependent   standard_language   is_forked
    A   True         False          None                False

Now someone comes alone and creates language Q by translating A::

    _   is_original  is_dependent   standard_language   is_forked
    A   True         False          None                False
    Q   False        True           A                   False

Someone else creates another translation of A, call it R::

    _   is_original  is_dependent   standard_language   is_forked
    A   True         False          None                False
    Q   False        True           A                   False
    R   False        True           A                   False

Someone else creates a translation of R (note: that's a translation of
a translation)::

    _   is_original  is_dependent   standard_language   is_forked
    A   True         False          None                False
    Q   False        True           A                   False
    R   False        True           A                   False
    S   False        True           R                   False

Now someone comes along and "forks" Q.  This can happen for a number of reasons,
but the result is that Q becomes standalone (but *not* original!)::

    _   is_original  is_dependent   standard_language   is_forked
    A   True         False          None                False
    Q   False        False          A                   True
    R   False        True           A                   False
    S   False        True           R                   False

Refactor
~~~~~~~~

First, the "which language are the people in the video speaking" concept is
covered in the previous section.

The new data model does not have a concept of "standalone" versus "dependent"
languages.  It *does* have the concept of "translated from", and it's less
restrictive than the previous model.

All ``SubtitleVersion`` objects now track their parentage.  So if Q1 was
translated from A1, Q1's parent set will be ``{A1}``.  If ``Q2`` uses ``B1`` as
a source/reference, Q2's parent set will be ``{Q1, B1}``::

    .
       Q2
       |\
       | \
       |  \
       Q1 |
       |  |
      /   |
     |    |
    A1    B1

Since parentage is now tracked at the ``SubtitleVersion`` level, we need a way
to mimic the old behavior at the ``SubtitleLanguage`` level.  The lineage map is
the solution.

``SubtitleVersion`` objects now have an ``.lineage`` property.  Internally it's
stored as a blob of JSON, but you can access it easily as a Python object
through the ``version.lineage`` property.

The lineage is a dict containing a mapping of language codes (the keys) to
version numbers (the values).  Each time you create a new version using another
language as a reference, that new version's lineage map will be updated.
Entried are *never* removed, only added or updated!

Let's look at another example::

    .
       Q3  
       |\  
       | \ 
       |  B2
       |  |
       |  |
       Q2 |
       |\ |
       | \|
       |  |
       Q1 |
       |  |
      /   |
     |    |
    A1    B1

    Q1 {A: 1}
    Q2 {A: 1, B: 2}
    Q2 {A: 1, B: 3}

Currently there is no way to translate a language from 2 or more sources, so at
most the lineage maps for all existing data will have one key, value pair.

Porting
~~~~~~~

To determine if a particular ``SubtitleLanguage`` is "translated from another
language" you can examine the lineage map of its latest version (aka the "tip"
version)::

    tip_version = subtitlelang.get_tip()

    lineage = tip_version.lineage
    source_codes = lineage.keys()

    if not source_codes:
        print "%s is a standalone language" % subtitlelang
    else:
        sibling_languages = subtitlelang.video.newsubtitlelanguage_set
        source_language = sibling_languages.get(language_code=source_codes[0])

        print "%s is a translation of %s" % (subtitlelang, source_language)


