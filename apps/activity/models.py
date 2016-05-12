# Amara, universalsubtitles.org
#
# Copyright (C) 2016 Participatory Culture Foundation
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

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from auth.models import CustomUser as User
from codefield import CodeField, Code
from comments.models import Comment
from teams.models import Team
from teams.permissions_const import (ROLE_OWNER, ROLE_ADMIN, ROLE_MANAGER,
                                     ROLE_CONTRIBUTOR, ROLE_NAMES)
from utils import dates
from utils import translation
from utils.text import fmt
from videos.models import Video

# Couple of models that we use to track extra info related to activity records
class VideoDeletion(models.Model):
    url = models.URLField(max_length=512, blank=True)
    title = models.CharField(max_length=2048, blank=True)

class URLEdit(models.Model):
    old_url = models.URLField(max_length=512, blank=True)
    new_url = models.URLField(max_length=512, blank=True)

class ActivityType(Code):
    # Model that the related_obj_id field points to
    related_model = None
    # Is this type still in active use?
    active = True

    def get_message(self, record):
        """Get the message to display in activity logs."""
        raise NotImplementedError()

    def format_message(self, record, msg, **data):
        return msg % ActivityMessageDict(record, data)

class ActivityMessageDict(object):
    """Helper class to format our messages.

    It has knows how to fetch data for several standard keys that we use in
    our messages.
    """
    def __init__(self, record, data):
        self.record = record
        self.data = data

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        elif key == 'language_url':
            return self.record.get_language_url()
        elif key == 'language':
            return self.record.get_language_code_display()
        elif key == 'video_url':
            return self.record.get_video_url()
        elif key == 'video':
            return self.record.get_video_title()
        elif key == 'team':
            return self.record.team
        else:
            # Like the fmt() function, display something in the message rather
            # than raise an exception
            return key

class VideoAdded(ActivityType):
    slug = 'video-added'
    label = _('Video Added')

    def get_message(self, record):
        return _('Video added to amara')

class VideoTitleChanged(ActivityType):
    slug = 'video-title-changed'
    label = _('Video Title Changed')
    # The subtitle version history tells the story better
    active = False

    def get_message(self, record):
        return _('Videos title was changed')

class CommentAdded(ActivityType):
    slug = 'comment-added'
    label = _('Comment added')
    related_model = Comment

    def get_message(self, record):
        if record.language_code:
            return self.format_message(record,
                _(u'Commented on <a href="%(language_url)s">%(language)s '
                  'subtitles</a> for <a href="%(video_url)s">%(video)s</a>'))
        else:
            return self.format_message(record,
                _(u'Commented on <a href="%(video_url)s">%(video)s</a>'))

class VersionAdded(ActivityType):
    slug = 'version-added'
    label = _('Version added')

    def get_message(self, record):
        return self.format_message(record,
            _(u'Edited <a href="%(language_url)s">%(language)s '
              'subtitles</a> for <a href="%(video_url)s">%(video)s</a>'))

class VideoURLAdded(ActivityType):
    slug = 'video-url-added'
    label = _('Video URL added')
    related_model = URLEdit

    def get_message(self, record):
        url_edit = self.get_related_obj()
        return self.format_message(record,
            _(u'Added new URL for <a href="%(video_url)s">%(video)s</a>'))

class TranslationAdded(ActivityType):
    slug = 'translation-added'
    label = _('Translation URL added')
    # Not tracked since around the DMR changes. We haven't had a new instance
    # of this since 2013
    active = False

    def get_message(self, record):
        return _('Added a translation')

class SubtitleRequestCreated(ActivityType):
    slug = 'subtitle-request-created'
    label = _('Subtitle request created')
    # I'm not sure exactly what this was supposed to be used for.  We have 0
    # instances of this in the database
    active = False

    def get_message(self, record):
        return _('Subtitle request created')

class VersionApproved(ActivityType):
    slug = 'version-approved'
    label = _('Version approved')

    def get_message(self, record):
        return self.format_message(record,
            _('Approved <a href="%(language_url)s">%(language)s</a> subtitles'
              ' for <a href="%(video_url)s">%(video)s</a>'))

class MemberJoined(ActivityType):
    slug = 'member-joined'
    label = _('Member Joined')

    # For the related_obj_id field, we store an integer code for the role.
    # Map member role values to those codes
    role_to_code = {
        ROLE_OWNER: 1,
        ROLE_ADMIN: 2,
        ROLE_MANAGER: 3,
        ROLE_CONTRIBUTOR: 4,
    }
    code_to_role = { v: k for (k, v) in role_to_code.items() }

    def get_message(self, record):
        return self.format_message(record,
            _("Joined the %(team)s team as a %(role)s"),
            role=self.get_role_name(record.related_obj_id))

    def get_related_obj(self, related_obj_id):
        try:
            return self.code_to_role[related_obj_id]
        except KeyError:
            return None

    def get_role_name(self, related_obj_id):
        role = self.get_related_obj(related_obj_id)
        return ROLE_NAMES.get(role, _('Unknown role'))

class VersionRejected(ActivityType):
    slug = 'version-rejected'
    label = _('Version Rejected')

    def get_message(self, record):
        return self.format_message(record,
            _('Rejected <a href="%(language_url)s">%(language)s</a> subtitles'
              ' for <a href="%(video_url)s">%(video)s</a>'))

class MemberLeft(ActivityType):
    slug = 'member-left'
    label = _('Member Left')

    def get_message(self, record):
        return self.format_message(record, _("Left the %(team)s team"))

class VersionReviewed(ActivityType):
    slug = 'version-reviewed'
    label = _('Version Reviewed')
    # Probably related to tasks, but never used.  There are 0 instances in our
    # production database
    active = False

    def get_message(self, record):
        return self.format_message(record,
            _('Reviewed <a href="%(language_url)s">%(language)s</a> subtitles'
              ' for <a href="%(video_url)s">%(video)s</a>'))

class VersionAccepted(ActivityType):
    slug = 'version-accepted'
    label = _('Version Accepted')

    def get_message(self, record):
        return self.format_message(record,
            _('Accepted <a href="%(language_url)s">%(language)s</a> subtitles'
              ' for <a href="%(video_url)s">%(video)s</a>'))

class VersionDeclined(ActivityType):
    slug = 'version-declined'
    label = _('Version Declined')

    def get_message(self, record):
        return self.format_message(record,
            _('Declined <a href="%(language_url)s">%(language)s</a> subtitles'
              ' for <a href="%(video_url)s">%(video)s</a>'))

class VideoDeleted(ActivityType):
    slug = 'video-deleted'
    label = _('Video deleted')
    related_model = VideoDeletion

    def get_message(self, record):
        deletion = record.get_related_obj()
        return self.format_message(record, _('Deleted a video: %(title)s'),
                                   title=deletion.title)

class VideoURLEdited(ActivityType):
    slug = 'video-url-edited'
    label = _('Video URL edited')
    related_model = URLEdit

    def get_message(self, record):
        url_edit = record.get_related_obj()
        msg = _('Changed primary url from '
                '<a href="%(old_url)s">%(old_url)s</a> to '
                '<a href="%(new_url)s">%(new_url)s</a>')
        return self.format_message(record, msg, old_url=url_edit.old_url,
                                   new_url=url_edit.new_url)

class VideoURLDeleted(ActivityType):
    slug = 'video-url-deleted'
    label = _('Video URL deleted')
    related_model = URLEdit

    def get_message(self, record):
        url_edit = record.get_related_obj()
        msg = _('Deleted url <a href="%(url)s">%(url)s</a>')
        return self.format_message(record, msg, url=url_edit.old_url)

activity_choices = [
    VideoAdded, VideoTitleChanged, CommentAdded, VersionAdded, VideoURLAdded,
    TranslationAdded, SubtitleRequestCreated, VersionApproved, MemberJoined,
    VersionRejected, MemberLeft, VersionReviewed, VersionAccepted,
    VersionDeclined, VideoDeleted, VideoURLEdited, VideoURLDeleted,
]

class ActivityRecord(models.Model):
    type = CodeField(choices=activity_choices)
    # User activity stream for this record.  Almost always this is the user
    # who performed the action, the exceptions are things like the
    # member-joined record when an admin manually adds a user to a team.
    user = models.ForeignKey(User, blank=True, null=True,
                             related_name='activity')
    # Video activity stream for this record.  This will be NULL for non-video
    # records, like team member join/leave.
    video = models.ForeignKey(Video, blank=True, null=True,
                              related_name='activity')
    # Language code of the video.  We denormalize this field because we use it
    # as a filter and we want to avoid a join in that case
    video_language_code = models.CharField(max_length=16, blank=True,
                                           default='',
                                           choices=translation.ALL_LANGUAGE_CHOICES)
    # Team activity stream for this record.  If a video moves from team to
    # team, we will make a copy of the video activity and have record in each
    # team.  You can use the copied_from field to determine which was the
    # original record.
    team = models.ForeignKey(Team, blank=True, null=True,
                             related_name='activity')
    # Language related to the activity for things like version-added.
    language_code = models.CharField(max_length=16, blank=True, default='',
                                     choices=translation.ALL_LANGUAGE_CHOICES)
    # This works like a generic foreign key.  Depending on the type field, it
    # will reference a different model
    related_obj_id = models.IntegerField(blank=True, null=True)
    created = models.DateTimeField(default=dates.now, db_index=True)
    # When a video moves from team to team, we create copies of each record.
    # The original gets moved to the new team and the copy stays with the old
    # team.
    copied_from = models.ForeignKey('self', blank=True, null=True)

    class Meta:
        # If we were using a newer version of django we would have this:
        #index_together = [
            ## Team activity stream.  There's often lots of activity per-team,
            ## so we add some extra indexes here
            #('team', 'created'),
            #('team', 'type', 'created'),
            #('team', 'language_code', 'created'),
            #('team', 'video_language_code', 'created'),
            ## Video activity stream
            #('video', 'copied_from', 'created')
            ## User activity stream
            #('user', 'copied_from', 'created')
        #]
        # Instead, these are handled by the setup_indexes code and a south
        # migration
        pass

    def __unicode__(self):
        return u'ActivityRecord: {}'.format(self.type)

    def get_language_code_display(self):
        if self.language_code:
            return translation.get_language_label(self.language_code)
        else:
            return ''

    def get_video_url(self):
        if self.video:
            return self.video.get_absolute_url()
        else:
            return ''

    def get_language_url(self):
        if self.video and self.language_code:
            return self.video.get_language_url(self.language_code)
        else:
            return ''

    def get_video_title(self):
        if self.video:
            return self.video.title_display()
        else:
            return ''

    def get_message(self):
        return self.type_obj.get_message(self)

    def get_related_obj(self):
        if not hasattr(self, '_related_obj_cache'):
            self._related_obj_cache = self._get_related_obj()
        return self._related_obj_cache

    def _get_related_obj(self):
        ModelClass = self.type_obj.related_model
        if ModelClass is None or self.related_obj_id is None:
            return None
        else:
            return ModelClass.objects.get(id=self.related_obj_id)
