===================
Data Model Refactor
===================

Some useful information about the data model refactor.

.. contents::

Naming Things
=============

Right now our code is a hodgepodge of names, nicknames, abbreviated names, etc.
Part of the goal of this refactor should be to clean up this mess.

I propose two guide for naming things: one for "public" names like methods,
functions, classes, etc.  This should be more strict so you don't have to try to
remember "is that method called ``get_recent_lang`` or
``get_recent_language``?".  The other is for "private" names like local
variables -- names which are never used outside of the screen's-worth of code
they're used in.

Public Names
------------

Public names should be unambiguous, and there should be one way to name them.

  ``language``
    This word means "a ``SubtitleLanguage`` object".  So a method called
    ``get_recent_language`` should return a ``SubtitleLanguage``.

  ``language_code``
    This word means "a string representing a language code", like ``"fr-ca"``.
    So a method called ``get_recent_language_code`` should return one of these
    strings.

  ``version``
    This word means "a ``SubtitleVersion`` object".  So a method called
    ``get_recent_version`` should return a ``SubtitleVersion``.

  ``version_number``
    This word means "an integer representing a version number", like ``10``.


Private Names
-------------

Private names can be more flexible (because you can always just look up to
refresh your memory) and shorter.

  ``language``, ``lang``, ``subtitle_language``, ``sublang``, ``sl``
    A ``SubtitleLanguage`` object.

  ``language_code``, ``lang_code``, ``lc``, ``lcode``
    A string representing a language code, like ``"pt-br"``.

  ``version``, ``ver``, ``subtitle_version``, ``sv``
    A ``SubtitleVersion`` object.

  ``version_number``, ``vnum``, ``vn``
    A version number (integer).

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
    Q2 {A: 1, B: 1}
    Q3 {A: 1, B: 2}

Currently there is no way to translate a language from 2 or more sources, so at
most the lineage maps for all existing data will have one key, value pair.

``is_forked`` is staying put, but only temporarily.  Once we implement the new
UI we can remove it forever.

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

This has been implemented on
``subtitles.SubtitleLanguage.get_translation_source_language`` and
``subtitles.SubtitleLanguage.get_translation_source_language_code``.

If you're going to be adding a new SubtitleLanguage as a translation of another
one, you should create its versions with the appropriate parents.

For example, if a user wants to add a new translation of A, called B, you
would::

    pipeline.add_version(..., parents=[B])

You can do that every time or just the first time, it doesn't really matter::

    .
        B2        B2
       /|         |
      / B1        B1
     / /         /
     |/         /
     |         |
    A1        A1

In both of these, B2 will have the same lineage.  I think the first option makes
more sense though, because you're "using" A1 as a reference both times.

has_version, had_version
------------------------

These two confusing ``SubtitleLanguage`` fields had the following meanings in
the old data model:

  ``has_version``
    Is there more than one version, and does the latest version have more than
    0 subtitles?

  ``had_version``
    Is there more than one version, and did some previous version have more than
    0 subtitles?

These were used for things like "get all the languages for this video that have
some subtitles in their latest version, which we'll display on the video page".

Refactor
~~~~~~~~

We're no longer explicitely storing these fields on the ``SubtitleLanguage``
model.  Doing so has historically proven to be excruciatingly error-prone.
Instead there are two pieces of information that should cover all these use
cases.

First, SubtitleVersion objects now have a ``subtitle_count`` attribute.  This
*is* denormalized from the subtitles themselves, but this is okay because
``SubtitleVersion`` objects are immutable except for a single flag.

**Aside:** If ``SubtitleVersion`` objects ever become mutable we are going to
hate our lives.  ``SubtitleVersion`` objects are immutable.  They must be.  Do
not mute them.  This is a core principle of this whole model -- woe be unto
whomever breaks that principle.

Now that versions have the subtitle counts in a queryable field, it's possible
to write manager methods that use this to figure out the ``has_version``,
``had_version`` information.

To see which languages have (or do not have) a version with 1 or more subtitles
anywhere in their history (this is what ``had_version`` tried to track), use:

* ``SubtitleLanguage.objects.having_nonempty_versions()``
* ``SubtitleLanguage.objects.not_having_nonempty_versions()``

To find languages whose *latest* version has (or does not have) 1 or more
subtitles (this is what ``has_version`` tried to track), use:

* ``SubtitleLanguage.objects.having_nonempty_tip()``
* ``SubtitleLanguage.objects.not_having_nonempty_tip()``

**These methods contain dark and evil black magic!**  Their guts are ugly, but
they are very fast and do not require us to denormalize the data any further.

They also return normal querysets that can be further filtered, excluded, etc,
which means that the magic shouldn't affect you unless you go poking around
inside them.

Porting
~~~~~~~

Let's say you need to get a list of all the languages for a particular video
where the latest version has at least one subtitle.  Previously::

    SubtitleLanguage.objects.filter(video=video, has_version=True)

Now::

    SubtitleLanguage.objects.having_nonempty_versions().filter(video=video)

Subtitle Parsing / Generation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We moved everything related to various subtitles formats to the external project babelsubs.

Porting Parsing
~~~~~~~~~~~~~~~

First, find out the parser you need::

    from babelsubs.parsers.base import discover
    try:
        parser = discover(format)
    except KeyError:
        pass # format not found

Once you have a parser, feed it the input string and call to_internal::

    try:
        subtitles = parser(input_string, language='en').to_internal()
    except SubtitleParserError as e:
        pass # subs do not conform to format, see e.original_error for more details


This will give you a SubtitleSet, a wrapper around the internal storage mechanism we're using (dfxp).
See https://github.com/pculture/babelsubs/blob/master/babelsubs/storage.py#L117

The subtitle set is what subtitleversion.set_subtitles expect. The shorter form for this is::

    from babelsubs import SubtitleParserError
    from babelsubs.parsers.base import discover
    try:
        parser = discover(format)
        subtitles = parser(input_string, language='en').to_internal()
    except KeyError:
        pass # format not found
    except SubtitleParserError as e:
        pass # subs do not conform to format, see e.original_error for more details

Those are the two places where it can fail, on fiding a suitable parser, and parsing the actual subs.

Porting Generation
~~~~~~~~~~~~~~~~~~

Get the SubtitleSet for the SubtitleVersion you want to generate, then::

     from babelsubs.generators import discover

     subtitle_set = sub_version.get_subtitles()
     try:
          generator = discover(format)
          serialized_subs = unicode(generator(subtitle_set))
     except KeyError:
          pass # no generator for this format found

Migration Plan
==============

Migrating the data to the new data model is going to be tricky, because we can't
bring the site down completely for a few days to do it.  There are going to be
three main steps to the migration.

Initial Schema Migration
------------------------

The first step will be to run migrations that do not conflict with the current
operation of the site.  This will include:

* The migrations that add the new subtitles app and all of its models.
* The migrations that add the syncing fields (``needs_sync`` and
  ``new_subtitle_*``) to the old models.

*TODO*: We may need to reorder migrations on the dev branch first, which is
going to be a painful mess.  But otherwise bad things will happen in step three.
sjl will probably be in charge of this.

We'll also need to cherry-pick over the code that updates ``needs_sync`` in the
old models.

After this step is complete nothing should have changed except for the extra
fields and tables.

Background Data Migration
-------------------------

The next step is to migrate ``SubtitleLanguage`` and ``SubtitleVersion`` objects
into the new data model.

The ``apps/subtitles/tern.py`` script handles this.  It's a command line script
with various options, use ``tern.py --help`` to see the full usage syntax.

Tern will look in the database and choose a ``SubtitleLanguage`` or
``SubtitleVersion`` that needs to be ported and create/update the corresponding
new model.  It uses the ``needs_sync`` and ``new_subtitle_*`` fields to track
this.  It chooses ``SubtitleLanguage`` objects to port in a random order (except
that bases are always chosen before translations).  It should handle filling in
the ``parent`` fields and such correctly.

Tern should be able to be run in the background without any problems.  It
migrates one language at a time, and doesn't touch the old one except to mark
``needs_sync`` as ``False``.  It should also be safe to run multiple times on
the same language, in case it has changed.

*TODO*: Determine where the Tern data will be logged, and who'll be in charge of
reviewing it for any errors (probably sjl).

*TODO*: Determine all the places where ``needs_sync`` needs to be set back to
``True`` when some data changes.  I've already got the ``save()`` methods doing
this which should cover most of the cases, but if we ever use something like
``.update()`` for ``SubtitleLanguage`` or ``SubtitleVersion`` models then we'll
need to manually set this field.

Final Schema Migration
----------------------

After Tern has finished migrating all the old models into the new ones, it's
time for the final migration.  We should bring the site down at this point to
ensure that no data sneaks by us.

Once the site is down, we'll run Tern one more time to catch any stray data that
got in after the last run.

Taking a DB snapshot at this point is probably a good idea.

Then we'll merge over all the new DMR code, and run all remaining migrations.
These should be (comparatively) fast.

*TODO*: Review what the remaining migrations are to make sure they'll actually
be fast.

Finally, we switch the site back on and the DMR is live!  We should refrain from
deleting the old data for a while, just in case we need to refer to it to
restore something.

