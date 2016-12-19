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
from django.db import transaction
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from auth.models import CustomUser as User
from codefield import CodeField, Code
from comments.models import Comment
from mysqltweaks import query
from teams.models import Team
from teams.permissions import can_view_activity
from teams.permissions_const import (ROLE_OWNER, ROLE_ADMIN, ROLE_MANAGER,
                                     ROLE_CONTRIBUTOR, ROLE_NAMES)
from utils import dates
from utils import translation
from utils.text import fmt
from videos.models import Video

# Track progress on migrating the old activity records
class ActivityMigrationProgress(models.Model):
    last_migrated_id = models.IntegerField()

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

    def get_message(self, record, user):
        """Get the message to display in activity logs."""
        raise NotImplementedError()

    def format_message(self, record, msg, **data):
        return msg % ActivityMessageDict(record, data)

    def get_related_obj(self, related_obj_id):
        ModelClass = self.related_model
        if ModelClass is None or related_obj_id is None:
            return None
        else:
            return (ModelClass.objects.all()
                    .select_related()
                    .get(id=related_obj_id))

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

    def get_message(self, record, user):
        return self.format_message(
            record,
            _('added a video: <a href="%(video_url)s">%(video)s</a>'))

class VideoTitleChanged(ActivityType):
    slug = 'video-title-changed'
    label = _('Video Title Changed')
    # The subtitle version history tells the story better
    active = False

    def get_message(self, record, user):
        return _('edited a video title')

class CommentAdded(ActivityType):
    slug = 'comment-added'
    label = _('Comment added')
    related_model = Comment

    def get_message(self, record, user):
        if record.language_code:
            return self.format_message(record,
                _(u'commented on <a href="%(language_url)s">%(language)s '
                  'subtitles</a> for <a href="%(video_url)s">%(video)s</a>'))
        else:
            return self.format_message(record,
                _(u'commented on <a href="%(video_url)s">%(video)s</a>'))

class VersionAdded(ActivityType):
    slug = 'version-added'
    label = _('Version added')

    def get_message(self, record, user):
        return self.format_message(record,
            _(u'edited <a href="%(language_url)s">%(language)s '
              'subtitles</a> for <a href="%(video_url)s">%(video)s</a>'))

class VideoURLAdded(ActivityType):
    slug = 'video-url-added'
    label = _('Video URL added')
    related_model = URLEdit

    def get_message(self, record, user):
        url_edit = record.get_related_obj()
        return self.format_message(record,
            _(u'added new URL for <a href="%(video_url)s">%(video)s</a>'))

class TranslationAdded(ActivityType):
    slug = 'translation-added'
    label = _('Translation URL added')
    # Not tracked since around the DMR changes. We haven't had a new instance
    # of this since 2013
    active = False

    def get_message(self, record, user):
        return _('added a translation')

class SubtitleRequestCreated(ActivityType):
    slug = 'subtitle-request-created'
    label = _('Subtitle request created')
    # I'm not sure exactly what this was supposed to be used for.  We have 0
    # instances of this in the database
    active = False

    def get_message(self, record, user):
        return _('created a subtitle request')

class VersionApproved(ActivityType):
    slug = 'version-approved'
    label = _('Version approved')

    def get_message(self, record, user):
        return self.format_message(record,
            _('approved <a href="%(language_url)s">%(language)s</a> subtitles'
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

    def get_message(self, record, user):
        return self.format_message(record,
            _("joined the %(team)s team as a %(role)s"),
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

    def get_message(self, record, user):
        return self.format_message(record,
            _('rejected <a href="%(language_url)s">%(language)s</a> subtitles'
              ' for <a href="%(video_url)s">%(video)s</a>'))

class MemberLeft(ActivityType):
    slug = 'member-left'
    label = _('Member Left')

    def get_message(self, record, user):
        return self.format_message(record, _("left the %(team)s team"))

class VersionReviewed(ActivityType):
    slug = 'version-reviewed'
    label = _('Version Reviewed')
    # Probably related to tasks, but never used.  There are 0 instances in our
    # production database
    active = False

    def get_message(self, record, user):
        return self.format_message(record,
            _('reviewed <a href="%(language_url)s">%(language)s</a> subtitles'
              ' for <a href="%(video_url)s">%(video)s</a>'))

class VersionAccepted(ActivityType):
    slug = 'version-accepted'
    label = _('Version Accepted')

    def get_message(self, record, user):
        return self.format_message(record,
            _('accepted <a href="%(language_url)s">%(language)s</a> subtitles'
              ' for <a href="%(video_url)s">%(video)s</a>'))

class VersionDeclined(ActivityType):
    slug = 'version-declined'
    label = _('Version Declined')

    def get_message(self, record, user):
        return self.format_message(record,
            _('declined <a href="%(language_url)s">%(language)s</a> subtitles'
              ' for <a href="%(video_url)s">%(video)s</a>'))

class VideoDeleted(ActivityType):
    slug = 'video-deleted'
    label = _('Video deleted')
    related_model = VideoDeletion

    def get_message(self, record, user):
        deletion = record.get_related_obj()
        return self.format_message(record, _('deleted a video: %(title)s'),
                                   title=deletion.title)

class VideoURLEdited(ActivityType):
    slug = 'video-url-edited'
    label = _('Video URL edited')
    related_model = URLEdit

    def get_message(self, record, user):
        url_edit = record.get_related_obj()
        msg = _('changed primary url from '
                '<a href="%(old_url)s">%(old_url)s</a> to '
                '<a href="%(new_url)s">%(new_url)s</a>')
        return self.format_message(record, msg, old_url=url_edit.old_url,
                                   new_url=url_edit.new_url)

class VideoURLDeleted(ActivityType):
    slug = 'video-url-deleted'
    label = _('Video URL deleted')
    related_model = URLEdit

    def get_message(self, record, user):
        url_edit = record.get_related_obj()
        msg = _('deleted url <a href="%(url)s">%(url)s</a>')
        return self.format_message(record, msg, url=url_edit.old_url)

class VideoMovedToTeam(ActivityType):
    slug = 'video-moved-to-team'
    label = _('Video moved to team')
    related_model = Team

    def get_message(self, record, user):
        team = record.get_related_obj()
        if team is None:
            msg = _('moved <a href="%(video_url)s">%(video)s</a> to %(to_team)s')
            from_team_name = None
            from_team_url = None
        elif can_view_activity(team, user):
            msg = _('moved <a href="%(video_url)s">%(video)s</a> to %(to_team)s from <a href="%(from_team_url)s">%(from_team_name)s</a>')
            from_team_name = team.name
            from_team_url = reverse('teams:dashboard', args=(team.slug,))
        else:
            msg = _('moved <a href="%(video_url)s">%(video)s</a> to %(to_team)s from another team')
            from_team_name = None
            from_team_url = None
        return self.format_message(record, msg, from_team_name=from_team_name, from_team_url=from_team_url, to_team=record.team.name)

class VideoMovedFromTeam(ActivityType):
    slug = 'video-moved-from-team'
    label = _('Video moved from team')
    related_model = Team

    def get_message(self, record, user):
        team = record.get_related_obj()
        if team is None:
            msg = _('removed <a href="%(video_url)s">%(video)s</a> from %(from_team)s')
            to_team_name = None
            to_team_url = None
        elif can_view_activity(team, user):
            msg = _('moved <a href="%(video_url)s">%(video)s</a> from %(from_team)s to <a href="%(to_team_url)s">%(to_team_name)s</a>')
            to_team_name = team.name
            to_team_url = reverse('teams:dashboard', args=(team.slug,))
        else:
            msg = _('moved <a href="%(video_url)s">%(video)s</a> from %(from_team)s to another team')
            to_team_name = None
            to_team_url = None
        return self.format_message(record, msg, from_team=record.team.name, to_team_name=to_team_name, to_team_url=to_team_url)

activity_choices = [
    VideoAdded, VideoTitleChanged, CommentAdded, VersionAdded, VideoURLAdded,
    TranslationAdded, SubtitleRequestCreated, VersionApproved, MemberJoined,
    VersionRejected, MemberLeft, VersionReviewed, VersionAccepted,
    VersionDeclined, VideoDeleted, VideoURLEdited, VideoURLDeleted,
    VideoMovedToTeam, VideoMovedFromTeam,
]

class ActivityQueryset(query.QuerySet):
    def original(self):
        # For some reason, using copied_from__isnull=True results in an extra
        # join.  So we need a custom WHERE clause
        return self.extra(where=[
            'activity_activityrecord.copied_from_id IS NULL',
        ])

    # Split team activity into "team activity" and "team video activity".
    # This is a holdover from the old activity system.  It would be nice to
    # remove this, see #2559.
    TEAM_ACTIVITY_TYPES = ['member-left', 'member-joined']
    def team_activity(self):
        return self.filter(type__in=self.TEAM_ACTIVITY_TYPES)

    def team_video_activity(self):
        return self.exclude(type__in=self.TEAM_ACTIVITY_TYPES)

    def viewable_by_user(self, user):
        if user.is_superuser:
            return self
        q = Q(team__isnull=True) | Q(team__is_visible=True)
        if user.is_authenticated():
            q |= Q(team__in=user.teams.all())

        return self.filter(q)

class ActivityManager(models.Manager):
    use_for_related_fields = True

    def get_query_set(self):
        return ActivityQueryset(self.model, using=self._db)

    def original(self):
        return self.get_query_set().original()

    def for_video(self, video, team=None):
        qs = self.filter(video=video).original()
        if team is None:
            return qs.filter(private_to_team=False)
        else:
            return qs.filter(team=team)

    def for_api_user(self, user):
        # Used for the default API listing.  It would be nice to simplify this
        # see #2557
        return (self
                .filter(Q(user=user) | Q(team__in=user.teams.all()))
                .original()
                .distinct())

    def for_user(self, user):
        return (self.filter(user=user).original()
                .force_index('user_copied_created'))

    def for_team(self, team):
        return self.filter(team=team)

    def create(self, type, **attrs):
        return super(ActivityManager, self).create(type=type, **attrs)

    def create_for_video(self, type, video, team=None, **attrs):
        team_video = video.get_team_video()
        if team is None:
            team_id = team_video.team_id if team_video else None
        else:
            team_id = team.id
        return self.create(
            type=type, video=video, team_id=team_id,
            video_language_code=video.primary_audio_language_code, **attrs)

    def create_for_video_added(self, video):
        return self.create_for_video('video-added', video,
                                     user=video.user, created=video.created)

    def create_for_comment(self, video, comment, language_code=''):
        return self.create_for_video(
            'comment-added', video, user=comment.user,
            created=comment.submit_date, related_obj_id=comment.id,
            language_code=language_code)

    def create_for_subtitle_version(self, version):
        return self.create_for_video(
            'version-added', version.video,
            language_code=version.language_code, user=version.author,
            created=version.created)

    def create_for_video_url_added(self, video_url):
        with transaction.commit_on_success():
            url_edit = URLEdit.objects.create(new_url=video_url.url)
            return self.create_for_video('video-url-added', video_url.video,
                                         user=video_url.added_by,
                                         created=video_url.created,
                                         related_obj_id=url_edit.id)

    def create_for_version_approved(self, version, user):
        return self.create_for_video('version-approved', version.video,
                                     user=user,
                                     language_code=version.language_code,
                                     created=dates.now())

    def create_for_version_accepted(self, version, user):
        return self.create_for_video('version-accepted', version.video,
                                     user=user,
                                     language_code=version.language_code,
                                     created=dates.now())

    def create_for_version_rejected(self, version, user):
        return self.create_for_video('version-rejected', version.video,
                                     user=user,
                                     language_code=version.language_code,
                                     created=dates.now())

    def create_for_version_declined(self, version, user):
        return self.create_for_video('version-declined', version.video,
                                     user=user,
                                     language_code=version.language_code,
                                     created=dates.now())

    def create_for_new_member(self, member):
        role_code = MemberJoined.role_to_code[member.role]
        return self.create('member-joined', team=member.team,
                           user=member.user, created=member.created,
                           related_obj_id=role_code)

    def create_for_member_deleted(self, member):
        return self.create('member-left', team=member.team,
                           user=member.user, created=dates.now())

    def create_for_video_deleted(self, video, user):
        with transaction.commit_on_success():
            team_video = video.get_team_video()
            team_id = team_video.team_id if team_video else None
            url = video.get_video_url()
            video_deletion = VideoDeletion.objects.create(
                title=video.title_display(),
                url=url if url is not None else '')
            return self.create('video-deleted', user=user,
                               created=dates.now(), team_id=team_id,
                               related_obj_id=video_deletion.id)

    def create_for_video_url_made_primary(self, video_url, old_url, user):
        with transaction.commit_on_success():
            url_edit = URLEdit.objects.create(old_url=old_url.url,
                                              new_url=video_url.url)
            return self.create_for_video('video-url-edited', video_url.video,
                                         user=user, created=dates.now(),
                                         related_obj_id=url_edit.id)

    def create_for_video_url_deleted(self, video_url, user):
        with transaction.commit_on_success():
            url_edit = URLEdit.objects.create(old_url=video_url.url)
            return self.create_for_video('video-url-deleted', video_url.video,
                                         user=user, created=dates.now(),
                                         related_obj_id=url_edit.id)

    def create_for_video_moved(self, video, user, from_team=None, to_team=None):
        with transaction.commit_on_success():
            if from_team is not None:
                if to_team is not None:
                    to_team_id = to_team.id
                else:
                    to_team_id = None
                self.create_for_video('video-moved-from-team', video,
                                      user=user, created=dates.now(),
                                      related_obj_id=to_team_id,
                                      team=from_team,
                                      private_to_team=True)
            if to_team is not None:
                if from_team is not None:
                    from_team_id = from_team.id
                else:
                    from_team_id = None
                self.create_for_video('video-moved-to-team', video,
                                      user=user, created=dates.now(),
                                      related_obj_id=from_team_id,
                                      team=to_team,
                                      private_to_team=True)

    def move_video_records_to_team(self, video, team):
        for record in self.filter(video=video, copied_from=None,
                                  private_to_team=False):
            record.move_to_team(team)

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
    copied_from = models.ForeignKey('self', blank=True, null=True,
                                    related_name='copies')
    # Make a record private to a team.  This does 2 things: disable the
    # copying behavior above and not include it in the default video listing.
    private_to_team = models.BooleanField(default=False, blank=True)

    objects = ActivityManager()

    class Meta:
        ordering = ['-created']
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

    def __unicode__(self):
        return u'ActivityRecord: {}'.format(self.type)

    @classmethod
    def active_type_choices(cls):
        code_list = cls._meta.get_field('type').code_list
        return [ (code.slug, code.label) for code in code_list if code.active ]

    def move_to_team(self, new_team):
        with transaction.commit_on_success():
            # Make a copy of the record for our current team
            if self.team is not None:
                self.make_copy()
            # Move to the new team
            self.team = new_team
            self.save()
            # Delete any old copies on the new team
            if new_team is not None:
                ActivityRecord.objects.filter(copied_from=self,
                                              team_id=new_team.id).delete()

    def make_copy(self):
        copy = ActivityRecord(copied_from=self)
        fields = ['type', 'user_id', 'team_id', 'video_id', 'language_code',
                  'related_obj_id', 'created', ]
        for name in fields:
            setattr(copy, name, getattr(self, name))
        copy.save()
        return copy

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

    def get_message(self, user=None):
        return self.type_obj.get_message(self, user)

    def get_related_obj(self):
        if not hasattr(self, '_related_obj_cache'):
            self._related_obj_cache = self.type_obj.get_related_obj(
                self.related_obj_id)
        return self._related_obj_cache
