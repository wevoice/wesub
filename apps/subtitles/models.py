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
import datetime
import itertools

from django.conf import settings
from django.db import models, transaction
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _

from apps.auth.models import CustomUser as User
from apps.videos.models import Video


ALL_LANGUAGES = [(val, _(name))for val, name in settings.ALL_LANGUAGES]


def mapcat(fn, iterable):
    """Mapcatenate.

    Map the given function over the given iterable.  Each mapping should result
    in an interable itself.  Concatenate these results.

    E.g.:

        def foo(i):
            return [i, i+1]

        mapcatenate(foo, [20, 200, 2000])
        [20, 21, 200, 201, 2000, 2001]

    """
    return itertools.chain.from_iterable(itertools.imap(fn, iterable))


def subtitles_to_json(subtitles):
    return json.dumps(subtitles)

def json_to_subtitles(json_subtitles):
    return json.loads(json_subtitles)


class SubtitleLanguage(models.Model):
    """SubtitleLanguages are the equivalent of a 'branch' in a VCS.

    These exist mostly to coordiante access to a language amongst users.  Most
    of the actual data for the subtitles is stored in the version themselves.

    """
    video = models.ForeignKey(Video, related_name='newsubtitlelanguage_set')
    language_code = models.CharField(max_length=16, choices=ALL_LANGUAGES)

    followers = models.ManyToManyField(User, blank=True,
                                       related_name='followed_newlanguages')
    collaborators = models.ManyToManyField(User, blank=True,
                                           related_name='collab_newlanguages')

    writelock_time = models.DateTimeField(null=True, blank=True,
                                          editable=False)
    writelock_owner = models.ForeignKey(User, null=True, blank=True,
                                        editable=False,
                                        related_name='writelocked_newlanguages')
    writelock_session_key = models.CharField(max_length=255, blank=True,
                                             editable=False)

    created = models.DateTimeField(editable=False)

    class Meta:
        unique_together = [('video', 'language_code')]


    def __unicode__(self):
        return 'SubtitleLanguage %d / %s / %s' % (
            self.id, self.video.video_id, self.get_language_code_display())


    def save(self, *args, **kwargs):
        creating = not self.pk

        if creating:
            self.created = datetime.datetime.now()

        return super(SubtitleLanguage, self).save(*args, **kwargs)


    def add_version(self, *args, **kwargs):
        """Add a SubtitleVersion to the tip of this language.

        Does not check any writelocking -- you need to do that yourself.

        It will run its reads/writes in a transaction, so the results should be
        fairly sane.

        """
        with transaction.commit_on_success():
            kwargs['subtitle_language'] = self
            kwargs['language_code'] = self.language_code
            kwargs['video'] = self.video

            last_version = list(
                self.subtitleversion_set.order_by('-version_number')[:1])
            last_version = last_version[0] if last_version else None

            version_number = ((last_version.version_number + 1)
                              if last_version else 1)
            kwargs['version_number'] = version_number

            parents = kwargs.pop('parents', None)

            sv = SubtitleVersion(*args, **kwargs)
            sv.save()

            if last_version:
                sv.parents.add(last_version)

            if parents:
                for p in parents:
                    sv.parents.add(p)

        return sv

class SubtitleVersion(models.Model):
    """SubtitleVersions are the equivalent of a 'changeset' in a VCS.

    They are designed with a few key principles in mind.

    First, SubtitleVersions should be mostly immutable.  Once written they
    should never be changed, unless a team needs to publish or unpublish them.
    Any other changes should simply create a new version.

    Second, SubtitleVersions are self-contained.  There's a little bit of
    denormalization going on with the video and language_code fields, but this
    makes it much easier for a SubtitleVersion to stand on its own and will
    improve performance overall.

    Because they're (mostly) immutable, the denormalization is less of an issue
    than it would be otherwise.

    You should only create new SubtitleVersions through the `add_version` method
    of SubtitleLanguage instances.  This will ensure consistency and handle
    updating the parentage and version numbers correctly.

    """
    parents = models.ManyToManyField('self', symmetrical=False)

    video = models.ForeignKey(Video)
    subtitle_language = models.ForeignKey(SubtitleLanguage)
    language_code = models.CharField(max_length=16, choices=ALL_LANGUAGES)

    visibility = models.CharField(max_length=10,
                                  choices=(('public', 'public'),
                                           ('private', 'private')),
                                  default='public')

    version_number = models.PositiveIntegerField(default=0)

    author = models.ForeignKey(User, default=User.get_anonymous,
                               related_name='newsubtitleversion_set')

    title = models.CharField(max_length=2048, blank=True)
    description = models.TextField(blank=True)

    created = models.DateTimeField(editable=False)

    # Subtitles are stored in a text blob, serialized as JSON.  Use the
    # subtitles property to get and set them.  You shouldn't be touching this
    # field.
    serialized_subtitles = models.TextField(blank=True)

    def get_subtitles(self):
        # We cache the parsed subs for speed.
        if not self._subtitles:
            self._subtitles = json_to_subtitles(self.serialized_subtitles)

        return self._subtitles

    def set_subtitles(self, subtitles):
        self.serialized_subtitles = subtitles_to_json(subtitles)
        self._subtitles = subtitles

    subtitles = property(get_subtitles, set_subtitles)

    class Meta:
        unique_together = [('video', 'language_code', 'version_number')]


    def __init__(self, *args, **kwargs):
        subtitles = kwargs.pop('subtitles', None)

        super(SubtitleVersion, self).__init__(*args, **kwargs)

        self._subtitles = None
        if subtitles:
            self.subtitles = subtitles

    def __unicode__(self):
        return u'SubtitleVersion %d / %s / %s v%d' % (
            self.id, self.video.video_id, self.get_language_code_display(),
            self.version_number
        )


    def save(self, *args, **kwargs):
        creating = not self.pk

        if creating:
            self.created = datetime.datetime.now()

        return super(SubtitleVersion, self).save(*args, **kwargs)


    def get_ancestors(self):
        """Return all ancestors of this version.  WARNING: MAY EAT YOUR DB!

        Returning all ancestors of a version is very database-intensive, because
        we need to walk each relation.  It will make roughly l^b database calls,
        where l is the length of a branch of history and b is the "branchiness".

        You probably don't need this.  You probably want to use the lineage
        instead.  This is mostly here for sanity tests.

        """
        def _ancestors(version):
            return [version] + list(mapcat(_ancestors, version.parents.all()))

        return set(mapcat(_ancestors, self.parents.all()))

