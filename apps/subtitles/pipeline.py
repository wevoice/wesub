# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

"""The subtitle creation pipeline.

To understand why this module/idea is necessary you need to understand the pain
that not having it causes.

In the beginning was videos.models.SubtitleVersion.  When you needed to update
some subtitles for a video, you created a new SubtitleVersion and saved it in
the standard Django manner.  This is simple, but things quickly spiraled out of
control.

First, there are a number of special things you may or may not need to do when
adding a new version.  You need to check that the user actually has permission
to add it.  It probably needs to trigger reindexing (if it's public).  It may
need to interact with tasks.  There are many little things like this.

Second, there are a number of places where we need to add versions.  Obviously
the subtitling dialog needs to create them, as do the Review/Approve dialog.  So
does the "rollback" functionality.  The "upload a subtitle file" process create
versions.

If you try to stick with a simple Django model creation for all the places
versions are created, you need to perform all the fiddly little checks in all
those places.  This quickly becomes painful and unmanageable.

And so we come to the subtitle pipeline.  Its purpose is to encapsulate the
process of adding subtitles to keep all the painful complexity in one place.  In
a nutshell:

                                subtitles go in
                                       ||
                         (pipeline handles everything)
                                       ||
                                       \/
                           SubtitleVersion comes out

"""

from django.db import transaction

from apps.subtitles.models import SubtitleLanguage, SubtitleVersion


def _strip_nones(d):
    """Strip all entries in a dictionary that have a value of None."""

    items = d.items()
    for k, v in items:
        if v == None:
            d.pop(k)


# Private Implementation ------------------------------------------------------
def _get_version(video, v):
    """Get the appropriate SV belonging to the given video.

    Works with SubtitleVersions, ids, and (language_code, version_number) pairs.

    """
    if isinstance(v, SubtitleVersion):
        if v.video_id != video.id:
            raise SubtitleVersion.DoesNotExist(
                "That SubtitleVersion does not belong to this Video!")
        else:
            return v
    elif isinstance(v, int):
        return SubtitleVersion.objects.get(video=video, id=v)
    elif isinstance(v, tuple) or isinstance(v, list):
        language_code, version_number = v
        return SubtitleVersion.objects.get(video=video,
                                           language_code=language_code,
                                           version_number=version_number)
    else:
        raise ValueError("Cannot look up version from %s" % type(v))

def _get_language(video, language_code):
    """Return appropriate SubtitleLanguage and a needs_save boolean.

    If a SubtitleLanguage for this video/language does not exist, an unsaved one
    will be created and returned.  It's up to the caller to save it if
    necessary.

    """
    try:
        sl = SubtitleLanguage.objects.get(video=video,
                                          language_code=language_code)
        language_needs_save = False
    except SubtitleLanguage.DoesNotExist:
        sl = SubtitleLanguage(video=video, language_code=language_code)
        language_needs_save = True

    return sl, language_needs_save

def _add_subtitles(video, language_code, subtitles, title, description, author,
                   visibility, visibility_override, parents,
                   rollback_of_version_number):
    """Add subtitles in the language to the video.  Really.

    This function is the meat of the subtitle pipeline.  The user-facing
    add_subtitles and unsafe_add_subtitles are thin wrappers around this.

    """
    sl, language_needs_save = _get_language(video, language_code)

    if language_needs_save:
        sl.save()

    data = {'title': title, 'description': description, 'author': author,
            'visibility': visibility, 'visibility_override': visibility_override,
            'parents': [_get_version(video, p) for p in (parents or [])],
            'rollback_of_version_number': rollback_of_version_number}
    _strip_nones(data)

    version = sl.add_version(subtitles=subtitles, **data)

    return version

def _rollback_to(video, language_code, version_number, rollback_author):
    target = SubtitleVersion.objects.get(video=video,
                                         language_code=language_code,
                                         version_number=version_number)

    # The new version is mostly a copy of the target.
    data = {
        'video': target.video,
        'language_code': target.language_code,
        'subtitles': target.get_subtitles(),
        'title': target.title,
        'description': target.description,
        'visibility_override': None,
    }

    # If any version in the history is public, then rollbacks should also result
    # in public versions.
    existing_versions = target.sibling_set.all()
    data['visibility'] = ('public'
                          if any(v.is_public() for v in existing_versions)
                          else 'private')

    # The author of the rollback is distinct from the target's author.
    data['author'] = rollback_author

    # The new version is always simply a child of the current tip.
    data['parents'] = None

    # Finally, rollback versions have a special attribute to track them.
    data['rollback_of_version_number'] = version_number

    return _add_subtitles(**data)


# Public API ------------------------------------------------------------------
def unsafe_add_subtitles(video, language_code, subtitles,
                         title=None, description=None, author=None,
                         visibility=None, visibility_override=None,
                         parents=None):
    """Add subtitles in the language to the video without a transaction.

    You probably want to use add_subtitles instead, but if you're already inside
    a transaction that will rollback on exceptions you can use this instead of
    dealing with nested transactions.

    For more information see the docstring for add_subtitles.  Aside from the
    transaction handling this function works exactly the same way.

    """
    return _add_subtitles(video, language_code, subtitles, title, description,
                          author, visibility, visibility_override, parents,
                          None)

def add_subtitles(video, language_code, subtitles,
                  title=None, description=None, author=None,
                  visibility=None, visibility_override=None,
                  parents=None):
    """Add subtitles in the language to the video.  It all starts here.

    This function is your main entry point to the subtitle pipeline.

    It runs in a transaction, so while it may fail the DB should be left in
    a consistent state.

    If you already have a transaction running you can use unsafe_add_subtitles
    to avoid dealing with nested transactions.

    You need to check writelocking yourself.  For now.  This may change in the
    future.

    Subtitles can be given as a SubtitleSet, or a list of
    (from_ms, to_ms, content) tuples, or a string containing a hunk of DXFP XML.

    Title and description should be strings, or can be omitted to set them to
    ''.  If you want them to be set to the same thing as the previous version
    you need to pass it yourself.

    Author can be given as a CustomUser object.  If omitted the author will be
    marked as anonymous.

    Visibility and visibility_override can be given as the strings 'public' or
    'private', or omitted to use the defaults ('public' and '' respectively).

    Parents can be given as an iterable of parent identifiers.  These can be
    SubtitleVersion objects, or integers representing primary keys of
    SubtitleVersions, or tuples of (language_code, version_number).  Note that
    the previous version of the language (if any) will always be marked as
    a parent.

    """
    with transaction.commit_on_success():
        return _add_subtitles(video, language_code, subtitles, title,
                              description, author, visibility,
                              visibility_override, parents, None)


def unsafe_rollback_to(video, language_code, version_number,
                       rollback_author=None):
    """Rollback to the given video/language/version without a transaction.

    You probably want to use rollback_to instead, but if you're already inside
    a transaction that will rollback on exceptions you can use this instead of
    dealing with nested transactions.

    For more information see the docstring for rollback_to.  Aside from the
    transaction handling this function works exactly the same way.

    """
    return _rollback_to(video, language_code, version_number, rollback_author)

def rollback_to(video, language_code, version_number,
                rollback_author=None):
    """Rollback to the given video/language/version.

    A rollback creates a new version at the tip of the branch, identical to the
    target version except for a few items:

    * The parent is simply the current tip, regardless of the target's parents.
    * The author of the rollback is distinct from the target's author.
    * The new version will be public if ANY version in the history is public,
      or private otherwise.

    If the target version does not exist, a SubtitleVersion.DoesNotExist
    exception will be raised.

    This function runs in a transaction, so while it may fail the DB should be
    left in a consistent state.

    If you already have a transaction running you can use unsafe_rollback_to
    to avoid dealing with nested transactions.

    """
    with transaction.commit_on_success():
        return _rollback_to(video, language_code, version_number,
                            rollback_author)

