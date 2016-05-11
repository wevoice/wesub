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

from django.test import TestCase

from activity.models import ActivityRecord
from comments.models import Comment
from subtitles import pipeline
from teams.permissions_const import *
from utils import dates
from utils.factories import *
from utils.test_utils import *
import teams.signals
import videos.signals

def clear_activity():
    ActivityRecord.objects.all().delete()

class ActivityCreationTest(TestCase):
    def check_save_doesnt_create_new_record(self, instance):
        pre_count = ActivityRecord.objects.count()
        instance.save()
        assert_equal(ActivityRecord.objects.count(), pre_count)

    def test_video_added(self):
        video = VideoFactory()
        clear_activity()
        videos.signals.video_added.send(
            sender=video,
            video_url=video.get_primary_videourl_obj())
        record = ActivityRecord.objects.get(type='video-added')
        assert_equals(record.video, video)
        assert_equals(record.user, video.user)
        assert_equals(record.created, video.created)

    def test_comment_added(self):
        video = VideoFactory()
        user = UserFactory()
        comment = Comment.objects.create(content_object=video, user=user,
                                         content='Foo')
        record = ActivityRecord.objects.get(type='comment-added')
        assert_equals(record.video, video)
        assert_equals(record.user, user)
        assert_equals(record.created, comment.submit_date)
        assert_equals(record.get_related_obj(), comment)
        assert_equals(record.language_code, '')

    def test_comment_added_to_subtitles(self):
        version = pipeline.add_subtitles(VideoFactory(), 'en',
                                         SubtitleSetFactory())
        language = version.subtitle_language
        user = UserFactory()
        comment = Comment.objects.create(content_object=language, user=user,
                                         content='Foo')
        record = ActivityRecord.objects.get(type='comment-added')
        assert_equals(record.video, language.video)
        assert_equals(record.user, user)
        assert_equals(record.created, comment.submit_date)
        assert_equals(record.get_related_obj(), comment)
        assert_equals(record.language_code, 'en')

    def test_version_added(self):
        version = pipeline.add_subtitles(VideoFactory(), 'en',
                                         SubtitleSetFactory())
        record = ActivityRecord.objects.get(type='version-added')
        assert_equal(record.user, version.author)
        assert_equal(record.video, version.video)
        assert_equal(record.language_code, version.language_code)
        assert_equal(record.created, version.created)
        self.check_save_doesnt_create_new_record(version)

    def test_video_url_added(self):
        video = VideoFactory()
        video_url = VideoURLFactory(video=video)
        clear_activity()
        videos.signals.video_url_added.send(sender=video_url, video=video,
                                            new_video=False)
        record = ActivityRecord.objects.get(type='video-url-added')
        assert_equal(record.user, video_url.added_by)
        assert_equal(record.video, video)
        assert_equal(record.language_code, '')
        assert_equal(record.created, video_url.created)
        # We don't currently use it, but we store the new URL in the related
        # object
        url_edit = record.get_related_obj()
        assert_equal(url_edit.new_url, video_url.url)

    def test_video_url_added_with_new_video(self):
        # In this case, we shouldn't create an video-url-added record, since
        # we already created the video-added record
        video = VideoFactory()
        video_url = VideoURLFactory(video=video)
        clear_activity()
        videos.signals.video_url_added.send(sender=video_url, video=video,
                                            new_video=True)
        assert_false(
            ActivityRecord.objects.filter(type='video-url-added').exists())

    def test_member_joined(self):
        member = TeamMemberFactory(role=ROLE_MANAGER)
        record = ActivityRecord.objects.get(type='member-joined')
        assert_equal(record.user, member.user)
        assert_equal(record.video, None)
        assert_equal(record.team, member.team)
        assert_equal(record.language_code, '')
        assert_equal(record.created, member.created)
        assert_equal(record.get_related_obj(), ROLE_MANAGER)
        # After deleting the team member, get_related_obj() should still work
        member.delete()
        assert_equal(reload_obj(record).get_related_obj(), ROLE_MANAGER)

    def test_member_left(self):
        member = TeamMemberFactory()
        now = dates.now.current
        teams.signals.member_leave.send(sender=member)
        record = ActivityRecord.objects.get(type='member-left')
        assert_equal(record.user, member.user)
        assert_equal(record.video, None)
        assert_equal(record.team, member.team)
        assert_equal(record.language_code, '')
        assert_equal(record.created, now)

class ActivityVideoLanguageTest(TestCase):
    def test_initial_video_language(self):
        video = VideoFactory(primary_audio_language_code='en')
        record = ActivityRecord.objects.create_for_video_added(video)
        assert_equal(record.video_language_code, 'en')

    def test_video_language_changed(self):
        video = VideoFactory(primary_audio_language_code='en')
        record = ActivityRecord.objects.create_for_video_added(video)
        video.primary_audio_language_code = 'fr'
        videos.signals.language_changed.send(
            sender=video, old_primary_audio_language_code='en')
        assert_equal(reload_obj(record).video_language_code, 'fr')

class TeamVideoActivityTest(TestCase):
    # These tests test video activity and teams.  Our general system for
    # handling this is:
    #  - When a video moves to a team, we make a copy of it for the team it
    #  left.
    #  - We set the team field on the original record to the new team
    #  - The copy on the old team the copied_from field set
    def check_copies(self, record, current_team, old_teams):
        assert_equal(reload_obj(record).team, current_team)
        qs = ActivityRecord.objects.filter(copied_from=record)
        assert_items_equal([a.team for a in qs], old_teams)

    def test_team_video_activity(self):
        # Test activity on a team video
        team = TeamFactory()
        video = TeamVideoFactory(team=team).video
        clear_activity()
        record = ActivityRecord.objects.create_for_video_added(video)
        self.check_copies(record, team, [])

    def test_add_to_team(self):
        # Test adding a non-team video to a team
        video = VideoFactory()
        clear_activity()
        record = ActivityRecord.objects.create_for_video_added(video)
        team = TeamFactory()
        TeamVideoFactory(team=team, video=video)
        self.check_copies(record, team, [])
        
    def move_to_team(self):
        # same thing if we move from 1 team to another
        video = VideoFactory()
        team_video = TeamVideoFactory(video=video)
        first_team = team_video.team
        clear_activity()
        record = ActivityRecord.objects.create_for_video_added(video)
        second_team = TeamFactory()
        team_video.move_to(second_team)
        self.check_copies(record, second_team, [first_team])

    def test_move_back(self):
        # Test moving a video back to a team it was already in before
        video = VideoFactory()
        team_video = TeamVideoFactory(video=video)
        first_team = team_video.team
        clear_activity()
        record = ActivityRecord.objects.create_for_video_added(video)
        second_team = TeamFactory()
        team_video.move_to(second_team)
        team_video.move_to(first_team)
        self.check_copies(record, first_team, [second_team])

    def test_move_back_to_public(self):
        # Test a team video being deleted, putting the video pack in the
        # public area
        video = VideoFactory()
        team_video = TeamVideoFactory(video=video)
        first_team = team_video.team
        clear_activity()
        record = ActivityRecord.objects.create_for_video_added(video)
        team_video.delete()
        self.check_copies(record, None, [first_team])
