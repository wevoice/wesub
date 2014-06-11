# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
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
from urllib import quote_plus
import urlparse

from django.db import models
from django.db.models import query
from django.utils.translation import ugettext_lazy as _
import babelsubs
# because of our insane circular imports we need to import haystack right here
# or else things blow up
import haystack

from auth.models import CustomUser as User
from externalsites import syncing
from externalsites.exceptions import SyncingError
from subtitles.models import SubtitleLanguage, SubtitleVersion
from teams.models import Team
from utils import youtube
from videos.models import VideoUrl, VideoFeed
import videos.models

def now():
    # define now as a function so it can be patched in the unittests
    return datetime.datetime.now()

class ExternalAccountManager(models.Manager):
    def create(self, team=None, user=None, **kwargs):
        if team is not None and user is not None:
            raise ValueError("team and user can't both be specified")
        if team is not None:
            kwargs['type'] = ExternalAccount.TYPE_TEAM
            kwargs['owner_id'] = team.id
        elif user is not None:
            kwargs['type'] = ExternalAccount.TYPE_USER
            kwargs['owner_id'] = user.id

        return super(ExternalAccountManager, self).create(**kwargs)

    def for_owner(self, owner):
        if isinstance(owner, Team):
            type_ = ExternalAccount.TYPE_TEAM
        elif isinstance(owner, User):
            type_ = ExternalAccount.TYPE_USER
        else:
            raise TypeError("Invalid owner type: %r" % owner)
        return self.filter(type=type_, owner_id=owner.id)

    def for_video_url(self, video_url):
        """Filter accounts by a VideoUrl

        By default this is a no-op, but subclasses like YouTubeAccount
        override it.
        """
        return self

    def lookup(self, video, video_url):
        qs = self.for_video_url(video_url)

        team_video = video.get_team_video()
        if team_video is not None:
            return qs.get(type=ExternalAccount.TYPE_TEAM,
                          owner_id=team_video.team_id)
        else:
            return qs.get(type=ExternalAccount.TYPE_USER,
                          owner_id=video.user_id)

class ExternalAccount(models.Model):
    account_type = NotImplemented
    video_url_type = NotImplemented

    TYPE_USER = 'U'
    TYPE_TEAM = 'T'
    TYPE_CHOICES = (
        (TYPE_USER, _('User')),
        (TYPE_TEAM, _('Team')),
    )

    type = models.CharField(max_length=1,choices=TYPE_CHOICES)
    owner_id = models.IntegerField()

    objects = ExternalAccountManager()

    @property
    def team(self):
        if self.type == ExternalAccount.TYPE_TEAM:
            return Team.objects.get(id=self.owner_id)
        else:
            return None

    @property
    def user(self):
        if self.type == ExternalAccount.TYPE_USER:
            return User.objects.get(id=self.owner_id)
        else:
            return None

    def is_for_video_url(self, video_url):
        return video_url.type == self.video_url_type

    def update_subtitles(self, video_url, language):
        version = language.get_public_tip()
        if version is None or self.should_skip_syncing():
            return
        sync_history_values = {
            'account': self,
            'video_url': video_url,
            'language': language,
            'action': SyncHistory.ACTION_UPDATE_SUBTITLES,
            'version': version,
        }

        try:
            self.do_update_subtitles(video_url, language, version)
        except StandardError, e:
            SyncHistory.objects.create_for_error(e, **sync_history_values)
        else:
            SyncHistory.objects.create_for_success(**sync_history_values)
            SyncedSubtitleVersion.objects.set_synced_version(
                self, video_url, language, version)

    def delete_subtitles(self, video_url, language):
        sync_history_values = {
            'account': self,
            'language': language,
            'video_url': video_url,
            'action': SyncHistory.ACTION_DELETE_SUBTITLES,
        }
        if self.should_skip_syncing():
            return

        try:
            self.do_delete_subtitles(video_url, language)
        except StandardError, e:
            SyncHistory.objects.create_for_error(e, **sync_history_values)
        else:
            SyncHistory.objects.create_for_success(**sync_history_values)
            SyncedSubtitleVersion.objects.unset_synced_version(
                self, video_url, language)

    def do_update_subtitles(self, video_url, language, version):
        """Do the work needed to update subititles.

        Subclasses must implement this method.
        """
        raise NotImplementedError()

    def do_delete_subtitles(self, video_url, language):
        """Do the work needed to delete subtitles

        Subclasses must implement this method.
        """
        raise NotImplementedError()

    def should_skip_syncing(self):
        """Return True if we should not sync subtitles.

        Subclasses may optionally override this method.
        """
        return False

    class Meta:
        abstract = True
        unique_together = [
            ('type', 'owner_id')
        ]

class KalturaAccount(ExternalAccount):
    account_type = 'K'
    video_url_type = videos.models.VIDEO_TYPE_KALTURA

    partner_id = models.CharField(max_length=100,
                                  verbose_name=_('Partner ID'))
    secret = models.CharField(
        max_length=100, verbose_name=_('Secret'),
        help_text=_('Administrator secret found in Settings -> '
                    'Integration on your Kaltura control panel'))

    class Meta:
        verbose_name = _('Kaltura account')

    def __unicode__(self):
        return "Kaltura: %s" % (self.partner_id)

    def do_update_subtitles(self, video_url, language, tip):
        kaltura_id = video_url.get_video_type().kaltura_id()
        subtitles = tip.get_subtitles()
        sub_data = babelsubs.to(subtitles, 'srt')

        syncing.kaltura.update_subtitles(self.partner_id, self.secret,
                                         kaltura_id, language.language_code,
                                         sub_data)

    def do_delete_subtitles(self, video_url, language):
        kaltura_id = video_url.get_video_type().kaltura_id()
        syncing.kaltura.delete_subtitles(self.partner_id, self.secret,
                                         kaltura_id, language.language_code)

class BrightcoveAccount(ExternalAccount):
    account_type = 'B'
    video_url_type = videos.models.VIDEO_TYPE_BRIGHTCOVE

    publisher_id = models.CharField(max_length=100,
                                    verbose_name=_('Publisher ID'))
    write_token = models.CharField(max_length=100)
    import_feed = models.OneToOneField(VideoFeed, null=True,
                                       on_delete=models.SET_NULL)

    def __unicode__(self):
        return "Brightcove: %s" % (self.publisher_id)

    def do_update_subtitles(self, video_url, language, tip):
        video_id = video_url.get_video_type().brightcove_id
        syncing.brightcove.update_subtitles(self.write_token, video_id,
                                            language.video)

    def do_delete_subtitles(self, video_url, language):
        video_id = video_url.get_video_type().brightcove_id
        if language.video.get_merged_dfxp() is not None:
            # There are other languaguages still, we need to update the
            # subtitles by merging those language's DFXP
            syncing.brightcove.update_subtitles(self.write_token, video_id,
                                                language.video)
        else:
            # No languages left, delete the subtitles
            syncing.brightcove.delete_subtitles(self.write_token, video_id)

    def should_skip_syncing(self):
        return self.write_token == ''

    def feed_url(self, player_id, tags):
        url_start = ('http://link.brightcove.com'
                    '/services/mrss/player%s/%s') % (
                        player_id, self.publisher_id)
        if tags is not None:
            return '%s/tags/%s' % (url_start,
                                   '/'.join(quote_plus(t) for t in tags))
        else:
            return url_start + "/new"

    def make_feed(self, player_id, tags=None):
        """Create a feed for this account.

        :returns: True if the feed was changed
        """
        feed_url = self.feed_url(player_id, tags)
        if self.import_feed:
            if feed_url != self.import_feed.url:
                self.import_feed.url = feed_url
                self.import_feed.save()
                return True
        else:
            self.import_feed = VideoFeed.objects.create(
                url=self.feed_url(player_id, tags),
                team=self.team)
            self.save()
            return True
        return False

    def remove_feed(self):
        if self.import_feed:
            self.import_feed.delete();
            self.import_feed = None
            self.save()

    def feed_info(self):
        if self.import_feed is None:
            return None
        path_parts = urlparse.urlparse(self.import_feed.url).path.split("/")
        for part in path_parts:
            if part.startswith("player"):
                player_id = part[len("player"):]
                break
        else:
            raise ValueError("Unable to parse feed URL")

        try:
            i = path_parts.index('tags')
        except ValueError:
            tags = None
        else:
            tags = tuple(path_parts[i+1:])
        return player_id, tags


class YouTubeAccountManager(ExternalAccountManager):
    def for_video_url(self, video_url):
        if video_url.owner_username:
            return self.filter(channel_id=video_url.owner_username)
        else:
            return self.none()

class YouTubeAccount(ExternalAccount):
    """YouTube account to sync to.

    Note that we can have multiple youtube accounts for a user/team.  We use
    the username attribute to lookup a specific account for a video.
    """
    account_type = 'Y'
    video_url_type = videos.models.VIDEO_TYPE_YOUTUBE

    channel_id = models.CharField(max_length=255, db_index=True)
    username = models.CharField(max_length=255)
    oauth_refresh_token = models.CharField(max_length=255)

    objects = YouTubeAccountManager()

    class Meta:
        unique_together = [
            ('type', 'owner_id', 'channel_id'),
        ]

    def __unicode__(self):
        return "YouTube: %s" % (self.username)

    def do_update_subtitles(self, video_url, language, version):
        """Do the work needed to update subititles.

        Subclasses must implement this method.
        """
        access_token = youtube.get_new_access_token(self.oauth_refresh_token)
        syncing.youtube.update_subtitles(video_url.videoid, access_token,
                                         version)
                                         
    def do_delete_subtitles(self, video_url, language):
        access_token = youtube.get_new_access_token(self.oauth_refresh_token)
        syncing.youtube.delete_subtitles(video_url.videoid, access_token,
                                         language.language_code)

account_models = [
    KalturaAccount,
    BrightcoveAccount,
    YouTubeAccount,
]
_account_type_to_model = dict(
    (model.account_type, model) for model in account_models
)
_video_type_to_account_model = dict(
    (model.video_url_type, model) for model in account_models
)
_account_type_choices = [
    (model.account_type, model._meta.verbose_name)
    for model in account_models
]

def get_account(account_type, account_id):
    AccountModel = _account_type_to_model[account_type]
    return AccountModel.objects.get(id=account_id)

def lookup_accounts(video):
    """Lookup an external accounts for a given video.

    This function examines the team associated with the video and the set of
    VideoURLs to determine external accounts that we should sync with.

    :returns: list of (account, video_url) tuples
    """
    team_video = video.get_team_video()
    rv = []
    for video_url in video.get_video_urls():
        account = lookup_account(video, video_url)
        if account is not None:
            rv.append((account, video_url))
    return rv

def lookup_account(video, video_url):
    AccountModel = _video_type_to_account_model.get(video_url.type)
    if AccountModel is None:
        return None
    try:
        return AccountModel.objects.lookup(video, video_url)
    except AccountModel.DoesNotExist:
        return None

def can_sync_videourl(video_url):
    return video_url.type in _video_type_to_account_model


class SyncedSubtitleVersionManager(models.Manager):
    def set_synced_version(self, account, video_url, language, version):
        """Set the synced version for a given account/language."""
        lookup_values = {
            'account_type': account.account_type,
            'account_id': account.id,
            'video_url': video_url,
            'language': language,
        }
        try:
            synced_version = self.get(**lookup_values)
        except SyncedSubtitleVersion.DoesNotExist:
            synced_version = SyncedSubtitleVersion(**lookup_values)
        synced_version.version = version
        synced_version.save()

    def unset_synced_version(self, account, video_url, language):
        """Set the synced version for a given account/language."""
        self.filter(account_type=account.account_type,
                    account_id=account.id,
                    video_url=video_url,
                    language=language).delete()

class SyncedSubtitleVersion(models.Model):
    """Stores the subtitle version that is currently synced to an external
    account.
    """

    account_type = models.CharField(max_length=1,
                                    choices=_account_type_choices)
    account_id = models.PositiveIntegerField()
    video_url = models.ForeignKey(VideoUrl)
    language = models.ForeignKey(SubtitleLanguage, db_index=True)
    version = models.ForeignKey(SubtitleVersion)

    class Meta:
        unique_together = (
            ('account_type', 'account_id', 'video_url', 'language'),
        )

    def __unicode__(self):
        return "SyncedSubtitleVersion: %s %s -> %s (%s)" % (
            self.language.video.video_id,
            self.language.language_code,
            self.version.version_number,
            self.get_account())

    objects = SyncedSubtitleVersionManager()

    def get_account(self):
        return get_account(self.account_type, self.account_id)

class SyncHistoryManager(models.Manager):
    def get_for_language(self, language):
        return self.filter(language=language).order_by('-id')

    def create_for_success(self, **kwargs):
        # for SyncingError, we just use the message directly, since it
        # describes a known failure point, for other errors we convert the
        # object to a string
        return self.create(result=SyncHistory.RESULT_SUCCESS, **kwargs)

    def create_for_error(self, e, **kwargs):
        # for SyncingError, we just use the message directly, since it
        # describes a known failure point, for other errors we convert the
        # object to a string
        if isinstance(e, SyncingError):
            details = e.msg
        else:
            details = str(e)
        return self.create(result=SyncHistory.RESULT_ERROR, details=details,
                           **kwargs)

    def create(self, *args, **kwargs):
        if 'datetime' not in kwargs:
            kwargs['datetime'] = now()
        if 'account' in kwargs:
            account = kwargs.pop('account')
            kwargs['account_id'] = account.id
            kwargs['account_type'] = account.account_type
        return models.Manager.create(self, *args, **kwargs)

class SyncHistory(models.Model):
    """History of all subtitle sync attempts."""

    ACTION_UPDATE_SUBTITLES = 'U'
    ACTION_DELETE_SUBTITLES = 'D'
    ACTION_CHOICES = (
        (ACTION_UPDATE_SUBTITLES, 'Update Subtitles'),
        (ACTION_DELETE_SUBTITLES, 'Delete Subtitles'),
    )

    RESULT_SUCCESS = 'S'
    RESULT_ERROR = 'E'

    RESULT_CHOICES = (
        (RESULT_SUCCESS, _('Success')),
        (RESULT_ERROR, _('Error')),
    )

    account_type = models.CharField(max_length=1,
                                    choices=_account_type_choices)
    account_id = models.PositiveIntegerField()
    video_url = models.ForeignKey(VideoUrl)
    language = models.ForeignKey(SubtitleLanguage, db_index=True)
    action = models.CharField(max_length=1, choices=ACTION_CHOICES)
    datetime = models.DateTimeField()
    version = models.ForeignKey(SubtitleVersion, null=True, blank=True)
    result = models.CharField(max_length=1, choices=RESULT_CHOICES)
    details = models.CharField(max_length=255, blank=True, default='')

    objects = SyncHistoryManager()

    class Meta:
        verbose_name = verbose_name_plural = _('Sync history')

    def __unicode__(self):
        return "SyncHistory: %s - %s for %s (%s)" % (
            self.datetime.date(),
            self.get_action_display(),
            self.get_account(),
            self.get_result_display())

    def get_account(self):
        return get_account(self.account_type, self.account_id)

