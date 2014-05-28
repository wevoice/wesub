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

"""utils.factories.py -- Factoryboy factories for testing
"""

from __future__ import absolute_import

import datetime
import hashlib

from django.contrib.auth.hashers import make_password
from django.template.defaultfilters import slugify
import factory
from factory.django import DjangoModelFactory

import accountlinker.models
import auth.models
import externalsites.models
import subtitles.models
import teams.models
import videos.models
from subtitles import pipeline

class VideoURLFactory(DjangoModelFactory):
    FACTORY_FOR = videos.models.VideoUrl

    url = factory.Sequence(
        lambda n: 'http://example.com/videos/video-{0}'.format(n))
    type = videos.models.VIDEO_TYPE_HTML5

class VideoFactory(DjangoModelFactory):
    FACTORY_FOR = videos.models.Video

    title = factory.Sequence(lambda n: 'Test Video {0}'.format(n))
    duration = 100
    allow_community_edits = False

    video_url = factory.RelatedFactory(VideoURLFactory, 'video', primary=True)

class KalturaVideoFactory(VideoFactory):
    FACTORY_HIDDEN_ARGS = ('name',)

    video_url__type = 'K'
    name = 'video'

    @factory.lazy_attribute
    def video_url__url(self):
        # generate a video with a kaltura-style URL
        entry_id = '1_' + hashlib.md5(self.name).hexdigest()[:8]
        return ('http://cdnbakmi.kaltura.com'
                '/p/1492321/sp/149232100/serveFlavor/entryId/'
                '%s/flavorId/1_dqgopb2z/name/%s.mp4') % (entry_id,
                                                         self.name)

class BrightcoveVideoFactory(VideoFactory):
    # generate a video with a brightcove-style URL
    FACTORY_HIDDEN_ARGS = ('brightcove_id', 'player_id')

    player_id = '1234'
    video_url__type = 'C'

    @factory.lazy_attribute
    def video_url__url(self):
        return 'http://bcove.me/services/link/bcpid%s/bctid%s' % (
            self.player_id, self.brightcove_id)

class UserFactory(DjangoModelFactory):
    FACTORY_FOR = auth.models.CustomUser

    username = factory.Sequence(lambda n: 'test_user_{0}'.format(n))
    email = factory.LazyAttribute(lambda u: '%s@example.com' % u.username)
    first_name = 'TestUser'
    last_name = factory.Sequence(lambda n: 'Number {0}'.format(n))
    notify_by_email = True
    valid_email = True
    password = 'password'

    @classmethod
    def _generate(cls, create, attrs):
        """Override the default _generate() to disable the post-save signal."""
        if 'password' in attrs:
            attrs['password'] = make_password(attrs['password'])
        return super(UserFactory, cls)._generate(create, attrs)

    @factory.post_generation
    def languages(self, create, extracted, **kwargs):
        if extracted:
            assert create
            for language_code in extracted:
                auth.models.UserLanguage.objects.create(
                    user=self, language=language_code)

class TeamFactory(DjangoModelFactory):
    FACTORY_FOR = teams.models.Team

    name = factory.Sequence(lambda n: 'Team %s' % n)
    slug = factory.LazyAttribute(lambda t: slugify(t.name))
    membership_policy = teams.models.Team.OPEN

    @classmethod
    def _generate(cls, create, attrs):
        team = super(TeamFactory, cls)._generate(create, attrs)
        if create:
            # this forces the default project to be created
            team.default_project
        return team

class WorkflowFactory(DjangoModelFactory):
    FACTORY_FOR = teams.models.Workflow
    review_allowed = 30 # admin must review
    approve_allowed = 20 # admin must approve

class TeamMemberFactory(DjangoModelFactory):
    FACTORY_FOR = teams.models.TeamMember

    role = teams.models.TeamMember.ROLE_OWNER
    user = factory.SubFactory(UserFactory)
    team = factory.SubFactory(TeamFactory)

class TeamVideoFactory(DjangoModelFactory):
    FACTORY_FOR = teams.models.TeamVideo

    team = factory.SubFactory(TeamFactory)
    video = factory.SubFactory(VideoFactory)

    @classmethod
    def _generate(cls, create, attrs):
        tv = super(TeamVideoFactory, cls)._generate(create, attrs)
        tv.video.user = tv.added_by
        return tv

    @factory.lazy_attribute
    def added_by(tv):
        member = TeamMemberFactory.create(team=tv.team)
        return member.user

class ProjectFactory(DjangoModelFactory):
    FACTORY_FOR = teams.models.Project

    team = factory.SubFactory(TeamFactory)
    name = factory.Sequence(lambda n: 'Project %s' % n)


class TaskFactory(DjangoModelFactory):
    FACTORY_FOR = teams.models.Task
    type = teams.models.Task.TYPE_IDS['Subtitle']

    @classmethod
    def create_review(cls, team_video, language_code, user, **kwargs):
        """Create a task, then move it to the review stage

        assumptions:
            - there are no Tasks or SubtitleVersions for this video+language
            - review is enabled for the team
        """
        sub_data = kwargs.pop('sub_data', None)
        if 'type' in kwargs and isinstance(kwargs['type'], basestring):
            kwargs['type'] = teams.models.Task.TYPE_IDS[kwargs['type']]
        team = team_video.team
        task = cls.create(team=team, team_video=team_video, assignee=None,
                          language=language_code, **kwargs)
        version = pipeline.add_subtitles(team_video.video, language_code,
                                         sub_data, complete=False,
                                         visibility='private')
        task.assignee = user
        task.new_subtitle_version = version
        return task.complete()

    @classmethod
    def create_approve(cls, team_video, language_code, user, **kwargs):
        """Create a task, then move it to the approval stage

        assumptions:
            - there are no Tasks or SubtitleVersions for this video+language
            - approve is enabled for the team
        """
        task = cls.create_review(team_video, language_code, user)
        if task.type == teams.models.Task.TYPE_IDS['Approve']:
            # review isn't enabled, but approve is.  Just return the task
            # early
            return task

        task.assignee = user
        task.approved = teams.models.Task.APPROVED_IDS['Approved']
        return task.complete()

class ThirdPartyAccountFactory(DjangoModelFactory):
    FACTORY_FOR = accountlinker.models.ThirdPartyAccount
    FACTORY_HIDDEN_ARGS = ('video_url',)

    oauth_access_token = '123'
    oauth_refresh_token = ''

    username = factory.LazyAttribute(lambda tpa: tpa.video_url.owner_username)
    type = factory.LazyAttribute(lambda tpa: tpa.video_url.type)

class SubtitleLanguageFactory(DjangoModelFactory):
    FACTORY_FOR = subtitles.models.SubtitleLanguage

class OldSubtitleLanguageFactory(DjangoModelFactory):
    FACTORY_FOR = videos.models.SubtitleLanguage

    is_original = True
    language = 'en'
    created = datetime.datetime(2000, 1, 1)

class OldSubtitleVersionFactory(DjangoModelFactory):
    FACTORY_FOR = videos.models.SubtitleVersion

    title = 'Title'
    description = 'Description'
    datetime_started = datetime.datetime(2000, 1, 1)

class BrightcoveAccountFactory(DjangoModelFactory):
    FACTORY_FOR = externalsites.models.BrightcoveAccount

    team = factory.SubFactory(TeamFactory)
    publisher_id = 'publisher'
    write_token = 'write-token'

def bulk_subs(sub_data):
    """Create a bunch of videos/languages/versions

    sub_data is a dict of dicts containing the data to create the objects
    with:

    * sub_data maps video titles to language data
    * language data map language codes to a list of version data
    * version data is a dict containing kwargs to pass to
    pipeline.create_subtitles().

    returns a tuple of dicts:
    * a dict that maps video titles to videos
    * a dict that maps (title, language_code) to languages
    * a dict that maps (title, language_code, version_number) to versions
    """
    videos = {}
    langs = {}
    versions = {}
    for video_title, language_data in sub_data.items():
        video = VideoFactory(title=video_title)
        videos[video_title] = video
        for language_code, version_data in language_data.items():
            lang = SubtitleLanguageFactory(video=video,
                                           language_code=language_code)
            langs[video_title, language_code] = lang
            for kwargs in version_data:
                v = pipeline.add_subtitles(video, language_code, None,
                                           **kwargs)
                versions[video_title, language_code, v.version_number] = v
    return videos, langs, versions

__all__ = ['bulk_subs']
__all__.extend(name for name in globals() if 'Factory' in name)
