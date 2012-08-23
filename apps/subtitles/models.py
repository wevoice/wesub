# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.html.

"""Django models represention subtitles."""

import datetime
import itertools

from django.conf import settings
from django.db import models
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _

from apps.auth.models import CustomUser as User
from apps.videos.models import Video
from libs.dxfpy import SubtitleSet


ALL_LANGUAGES = sorted([(val, _(name)) for val, name in settings.ALL_LANGUAGES],
                       key=lambda v: v[1])


# Utility functions -----------------------------------------------------------
def mapcat(fn, iterable):
    """Mapcatenate.

    Map the given function over the given iterable.  Each mapping should result
    in an interable itself.  Concatenate these results.

    E.g.:

        foo = lambda i: [i, i+1]
        mapcatenate(foo, [20, 200, 2000])
        [20, 21, 200, 201, 2000, 2001]

    """
    return itertools.chain.from_iterable(itertools.imap(fn, iterable))


# Lineage functions -----------------------------------------------------------
def lineage_to_json(lineage):
    return json.dumps(lineage)

def json_to_lineage(json_lineage):
    return json.loads(json_lineage)

def get_lineage(parents):
    """Return a lineage map for a version that has the given parents."""
    lineage = {}

    # The new version's lineage should be the result of merging the parents'
    # lineages, taking the later version whenever there's a conflict, and adding
    # the parent versions themselves to the map.
    for parent in parents:
        l, v = parent.language_code, parent.version_number

        if l not in lineage or lineage[l] < v:
            lineage[l] = v

        for l, v in parent.lineage.items():
            if l not in lineage or lineage[l] < v:
                lineage[l] = v

    return lineage


# SubtitleLanguages -----------------------------------------------------------
class SubtitleLanguageManager(models.Manager):
    def _needing_initial_signoff(self, unofficial_signoffs_required,
                                 official_signoffs_required):
        """Return a QS of SLs that need an initial signoff."""

        qs = self.get_query_set().filter(
            unofficial_signoff_count=0,
            official_signoff_count=0)

        return qs

    def _needing_unofficial_signoff(self, unofficial_signoffs_required,
                                    official_signoffs_required):
        """Return a QS of SLs that need an unofficial signoff."""

        qs = self.get_query_set().filter(
            unofficial_signoff_count__gt=0,
            unofficial_signoff_count__lt=unofficial_signoffs_required)

        # actual_un_count = unofficial_signoff_count + greatest(0, official_signoff_count - official_signoffs_required)
        # (unofficial_count > 0)

        # qs.extra(where=['unofficial_signoff_count < %d' % (unofficial_signoffs_required)])

        return qs

    def _needing_official_signoff(self, unofficial_signoffs_required,
                                  official_signoffs_required):
        """Return a QS of SLs that need an official signoff."""

        qs = self.get_query_set().filter(
            unofficial_signoff_count__gte=unofficial_signoffs_required,
            official_signoff_count__lt=official_signoffs_required)

        return qs

class SubtitleLanguage(models.Model):
    """SubtitleLanguages are the equivalent of a 'branch' in a VCS.

    These exist mostly to coordiante access to a language amongst users.  Most
    of the actual data for the subtitles is stored in the version themselves.

    """
    video = models.ForeignKey(Video, related_name='newsubtitlelanguage_set')
    language_code = models.CharField(max_length=16, choices=ALL_LANGUAGES)

    # TODO: Remove followers?
    followers = models.ManyToManyField(User, blank=True,
                                       related_name='followed_newlanguages')

    # TODO: Remove followers?
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

    # Denormalized signoff/collaborator count fields.
    # These are stored here for speed of retrieval and filtering.  They are
    # updated in the update_signoff_counts() method, which is called from the
    # Collaborator .save() method.
    unofficial_signoff_count = models.PositiveIntegerField(default=0)
    official_signoff_count = models.PositiveIntegerField(default=0)
    pending_signoff_count = models.PositiveIntegerField(default=0)
    pending_signoff_unexpired_count = models.PositiveIntegerField(default=0)
    pending_signoff_expired_count = models.PositiveIntegerField(default=0)

    objects = SubtitleLanguageManager()

    class Meta:
        unique_together = [('video', 'language_code')]


    def __unicode__(self):
        return 'SubtitleLanguage %s / %s / %s' % (
            (self.id or '(unsaved)'), self.video.video_id,
            self.get_language_code_display()
        )


    def save(self, *args, **kwargs):
        creating = not self.pk

        if creating and not self.created:
            self.created = datetime.datetime.now()

        return super(SubtitleLanguage, self).save(*args, **kwargs)


    def get_tip(self):
        """Return the tipmost version of this language (if any)."""

        versions = self.subtitleversion_set.order_by('-version_number')[:1]

        if versions:
            return versions[0]
        else:
            return None


    def add_version(self, *args, **kwargs):
        """Add a SubtitleVersion to the tip of this language.

        You probably don't need this.  You probably want
        apps.subtitles.pipeline.add_subtitles instead.

        Does not check any writelocking -- that's up to the pipeline.

        """
        kwargs['subtitle_language'] = self
        kwargs['language_code'] = self.language_code
        kwargs['video'] = self.video

        tip = self.get_tip()

        version_number = ((tip.version_number + 1) if tip else 1)
        kwargs['version_number'] = version_number

        parents = kwargs.pop('parents', [])

        if tip:
            parents.append(tip)

        kwargs['lineage'] = get_lineage(parents)

        sv = SubtitleVersion(*args, **kwargs)
        sv.save()

        if parents:
            for p in parents:
                sv.parents.add(p)

        return sv

    def update_signoff_counts(self):
        """Update the denormalized signoff count fields and save."""

        cs = self.collaborator_set.all()

        self.official_signoff_count = len(
            [c for c in cs if c.signoff and c.signoff_is_official])

        self.unofficial_signoff_count = len(
            [c for c in cs if c.signoff and (not c.signoff_is_official)])

        self.pending_signoff_count = len(
            [c for c in cs if (not c.signoff)])

        self.pending_signoff_expired_count = len(
            [c for c in cs if (not c.signoff) and c.expired])

        self.pending_signoff_unexpired_count = len(
            [c for c in cs if (not c.signoff) and (not c.expired)])

        self.save()


# SubtitleVersions ------------------------------------------------------------
class SubtitleVersionManager(models.Manager):
    def public(self):
        """Return a queryset of all publicly-visible versions."""
        return (self.get_query_set()
                    .exclude(visibility='private', visibility_override='')
                    .exclude(visibility_override='private'))

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
    parents = models.ManyToManyField('self', symmetrical=False, blank=True)

    video = models.ForeignKey(Video)
    subtitle_language = models.ForeignKey(SubtitleLanguage)
    language_code = models.CharField(max_length=16, choices=ALL_LANGUAGES)

    visibility = models.CharField(max_length=10,
                                  choices=(('public', 'public'),
                                           ('private', 'private')),
                                  default='public')

    # Visibility override can be used by team admins to force a specific type of
    # visibility for a version.  If set, it takes precedence over, but does not
    # affect, the main visibility field.
    visibility_override = models.CharField(max_length=10, blank=True,
                                           choices=(('public', 'public'),
                                                    ('private', 'private')),
                                           default='')

    version_number = models.PositiveIntegerField(default=1)

    author = models.ForeignKey(User, default=User.get_anonymous,
                               related_name='newsubtitleversion_set')

    title = models.CharField(max_length=2048, blank=True)
    description = models.TextField(blank=True)

    created = models.DateTimeField(editable=False)

    # Subtitles are stored in a text blob, serialized as base64'ed zipped XML
    # (oh the joys of Django).  Use the subtitles property to get and set them.
    # You shouldn't be touching this field.
    serialized_subtitles = models.TextField(blank=True)

    # Lineage is stored as a blob of JSON to save on DB rows.  You shouldn't
    # need to touch this field yourself, use the lineage property.
    serialized_lineage = models.TextField(blank=True)

    objects = SubtitleVersionManager()

    def get_subtitles(self):
        """Return the SubtitleSet for this version.

        A SubtitleSet will always be returned.  It may be empty if there are no
        subtitles.

        """
        # We cache the parsed subs for speed.
        if self._subtitles == None:
            if self.serialized_subtitles == '':
                self._subtitles = SubtitleSet()
            else:
                self._subtitles = SubtitleSet.from_blob(
                                      self.serialized_subtitles)

        return self._subtitles

    def set_subtitles(self, subtitles):
        """Set the SubtitleSet for this version.

        You have a few options here:

        * Passing None will set the subtitles to an empty set.
        * Passing a SubtitleSet will set the subtitles to that set.
        * Passing a vanilla list (or any iterable) will create a SubtitleSet
          from that and set the subtitles to it.

        """
        if subtitles == None:
            subtitles = SubtitleSet()
        else:
            if not isinstance(subtitles, SubtitleSet):
                subtitles = SubtitleSet.from_list(subtitles)

            self.serialized_subtitles = subtitles.to_blob()

        # We cache the parsed subs for speed.
        self._subtitles = subtitles


    def get_lineage(self):
        # We cache the parsed lineage for speed.
        if self._lineage == None:
            if self.serialized_lineage:
                self._lineage = json_to_lineage(self.serialized_lineage)
            else:
                self._lineage = {}

        return self._lineage

    def set_lineage(self, lineage):
        self.serialized_lineage = lineage_to_json(lineage)
        self._lineage = lineage

    lineage = property(get_lineage, set_lineage)

    class Meta:
        unique_together = [('video', 'language_code', 'version_number')]


    def __init__(self, *args, **kwargs):
        subtitles = kwargs.pop('subtitles', None)
        lineage = kwargs.pop('lineage', None)

        super(SubtitleVersion, self).__init__(*args, **kwargs)

        self._subtitles = None
        if subtitles != None:
            self.set_subtitles(subtitles)

        self._lineage = None
        if lineage != None:
            self.lineage = lineage

    def __unicode__(self):
        return u'SubtitleVersion %s / %s / %s v%s' % (
            (self.id or '(unsaved)'), self.video.video_id,
            self.get_language_code_display(), self.version_number
        )


    def save(self, *args, **kwargs):
        creating = not self.pk

        if creating and not self.created:
            self.created = datetime.datetime.now()

        # Sanity checking of the denormalized data.
        assert self.language_code == self.subtitle_language.language_code, \
               "Version language code does not match Language language code!"

        assert self.video_id == self.subtitle_language.video_id, \
               "Version video does not match Language video!"

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


# Collaborators ---------------------------------------------------------------
class CollaboratorManager(models.Manager):
    def get_for(self, subtitle_language):
        return self.get_query_set().filter(subtitle_language=subtitle_language)

    def get_all_signoffs_for(self, subtitle_language):
        return self.get_for(subtitle_language).filter(signoff=True)

    def get_peer_signoffs_for(self, subtitle_language):
        return (self.get_all_signoffs_for(subtitle_language)
                    .filter(signoff_is_official=False))

    def get_official_signoffs_for(self, subtitle_language):
        return (self.get_all_signoffs_for(subtitle_language)
                    .filter(signoff_is_official=True))

    def get_unsignedoff_for(self, subtitle_language, include_expired=False):
        qs = self.get_for(subtitle_language).filter(signoff=False)

        if not include_expired:
            qs = qs.exclude(expired=True)

        return qs

class Collaborator(models.Model):
    """Collaborator models represent a user working on a specific language."""

    user = models.ForeignKey(User)
    subtitle_language = models.ForeignKey(SubtitleLanguage)

    signoff = models.BooleanField(default=False)
    signoff_is_official = models.BooleanField(default=False)
    expired = models.BooleanField(default=False)

    expiration_start = models.DateTimeField(editable=False)

    created = models.DateTimeField(editable=False)

    objects = CollaboratorManager()

    class Meta:
        unique_together = (('user', 'subtitle_language'),)


    def save(self, *args, **kwargs):
        creating = not self.pk

        if creating and not self.created:
            self.created = datetime.datetime.now()

        if creating and not self.expiration_start:
            self.expiration_start = self.created

        result = super(Collaborator, self).save(*args, **kwargs)

        # Update the denormalized signoff count fields for SubtitleLanguages.
        # This has to be done after we've saved this Collaborator so the changes
        # will take effect.
        self.subtitle_language.update_signoff_counts()

        return result


