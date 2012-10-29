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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

import datetime

from django.core.cache import cache

from apps.teams.models import Team, TeamMember, TeamVideo, Workflow
from apps.videos.models import Video, SubtitleLanguage, SubtitleVersion
from apps.videos.tests.videos import WebUseTest
from apps.videos.types.youtube import YoutubeVideoType


class TestFollowingVideos(WebUseTest):
    fixtures = ['test.json', 'subtitle_fixtures.json']

    def setUp(self):
        self._make_objects()
        self.vt = YoutubeVideoType
        self.data = [{
            'url': 'http://www.youtube.com/watch#!v=UOtJUmiUZ08&feature=featured&videos=Qf8YDn9mbGs',
            'video_id': 'UOtJUmiUZ08'
        },{
            'url': 'http://www.youtube.com/v/6Z5msRdai-Q',
            'video_id': '6Z5msRdai-Q'
        },{
            'url': 'http://www.youtube.com/watch?v=woobL2yAxD4',
            'video_id': 'woobL2yAxD4'
        },{
            'url': 'http://www.youtube.com/watch?v=woobL2yAxD4&amp;playnext=1&amp;videos=9ikUhlPnCT0&amp;feature=featured',
            'video_id': 'woobL2yAxD4'
        }]
        self.shorter_url = "http://youtu.be/HaAVZ2yXDBo"
        cache.clear()

    def test_create_video(self):
        """
        When a video is created, the submitter should follow that video.
        """
        self._login()
        video, created = Video.get_or_create_for_url(
                video_url="http://example.com/123.mp4", user=self.user)

        self.assertTrue(video.followers.filter(pk=self.user.pk).exists())

    def test_create_edit_subs(self):
        """
        Trascriber, translator should follow language, not video.
        """
        self._login()

        youtube_url = 'http://www.youtube.com/watch?v=XDhJ8lVGbl8'
        video, created = Video.get_or_create_for_url(youtube_url)
        self.assertEquals(2, SubtitleLanguage.objects.count())
        SubtitleVersion.objects.all().delete()

        # Create a transcription

        language = SubtitleLanguage.objects.get(language='en')
        language.is_original = True
        language.save()
        self.assertFalse(language.followers.filter(pk=self.user.pk).exists())

        version = SubtitleVersion(language=language, user=self.user,
                datetime_started=datetime.now(), version_no=0,
                is_forked=False)
        version.save()

        # Trascription author follows language, not video
        self.assertTrue(version.is_transcription)
        self.assertFalse(video.followers.filter(pk=self.user.pk).exists())
        self.assertTrue(language.followers.filter(pk=self.user.pk).exists())

        # Create a translation
        czech = SubtitleLanguage.objects.create(language='ru', is_original=False,
                video=video)
        self.assertEquals(3, SubtitleLanguage.objects.count())

        version = SubtitleVersion(language=czech, user=self.user,
                datetime_started=datetime.now(), version_no=0,
                is_forked=False)
        version.save()

        # Translation creator follows language, not video
        self.assertTrue(version.is_translation)
        self.assertFalse(video.followers.filter(pk=self.user.pk).exists())
        self.assertTrue(czech.followers.filter(pk=self.user.pk).exists())

        # Now editing --------------------------------------------------------

        self.assertNotEquals(language.pk, czech.pk)
        video.followers.clear()
        language.followers.clear()
        czech.followers.clear()

        version = SubtitleVersion(language=language, user=self.user,
                datetime_started=datetime.now(), version_no=1,
                is_forked=False)
        version.save()

        self.assertFalse(video.followers.filter(pk=self.user.pk).exists())
        self.assertTrue(language.followers.filter(pk=self.user.pk).exists())

        version = SubtitleVersion(language=czech, user=self.user,
                datetime_started=datetime.now(), version_no=1,
                is_forked=False)
        version.save()

        self.assertFalse(video.followers.filter(pk=self.user.pk).exists())
        self.assertTrue(czech.followers.filter(pk=self.user.pk).exists())

    def test_review_subs(self):
        """
        When you review a set of subtitles, you should follow that language.
        """
        self._login()
        youtube_url = 'http://www.youtube.com/watch?v=XDhJ8lVGbl8'

        vt = self.vt(youtube_url)
        video, created = Video.get_or_create_for_url(youtube_url)

        lang = vt.get_subtitled_languages()[0]

        language = SubtitleLanguage.objects.get(language='en')
        version = SubtitleVersion(language=language,
                datetime_started=datetime.now(), version_no=10)
        version.save()

        team, created = Team.objects.get_or_create(name='name', slug='slug')
        TeamMember.objects.create(team=team, user=self.user,
                role=TeamMember.ROLE_OWNER)
        team_video, _= TeamVideo.objects.get_or_create(team=team, video=video,
                added_by=self.user)
        Workflow.objects.create(team=team, team_video=team_video,
                review_allowed=30
                )

        sl = video.subtitle_language(lang['lang_code'])
        self.assertEquals(1, sl.followers.count())
        latest = video.latest_version(language_code='en')
        latest.set_reviewed_by(self.user)
        latest.save()

        self.assertEquals(2, sl.followers.count())

    def test_approve_not(self):
        """
        When you approve subtitles, you should *not* follow anything.
        """
        self._login()
        youtube_url = 'http://www.youtube.com/watch?v=XDhJ8lVGbl8'

        vt = self.vt(youtube_url)
        video, created = Video.get_or_create_for_url(youtube_url)

        lang = vt.get_subtitled_languages()[0]

        language = SubtitleLanguage.objects.get(language='en')
        version = SubtitleVersion(language=language,
                datetime_started=datetime.now(), version_no=10)
        version.save()

        team, created = Team.objects.get_or_create(name='name', slug='slug')
        TeamMember.objects.create(team=team, user=self.user,
                role=TeamMember.ROLE_OWNER)
        team_video, _= TeamVideo.objects.get_or_create(team=team, video=video,
                added_by=self.user)
        Workflow.objects.create(team=team, team_video=team_video,
                review_allowed=30
                )

        sl = video.subtitle_language(lang['lang_code'])
        self.assertEquals(1, sl.followers.count())
        latest = video.latest_version(language_code='en')
        latest.set_approved_by(self.user)
        latest.save()

        self.assertEquals(1, sl.followers.count())

