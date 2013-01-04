from django.test import TestCase

from auth.models import CustomUser as User
from apps.teams.models import Team, TeamVideo, TeamMember
from apps.teams.tests.teamstestsutils import  create_team, create_member
from apps.videos.models import Video, SubtitleLanguage

class AutoCreateTest(TestCase):

    def setUp(self):
        self.team = create_team(review_setting=10, approve_setting=10,
            autocreate_subtitle=True, autocreate_translate=True)
        self.video = Video.get_or_create_for_url('http://www.example.com/test.mp4')[0]
        self.member = create_member(self.team, role=TeamMember.ROLE_ADMIN)

    def test_no_audio_language(self):
       tv = TeamVideo(team=self.team, video=self.video, added_by=self.member.user)
       tv.save()
       tasks = tv.task_set.all()
       self.assertEqual(tasks.count() , 1)
       transcribe_task = tasks.filter(type=10, language='')
       self.assertEqual(transcribe_task.count(), 1)

    def test_audio_language(self):
        # create the original language for this video
        sl = SubtitleLanguage.objects.create(video=self.video, language='en', is_original=True)
        tv = TeamVideo(team=self.team, video=self.video, added_by=self.member.user)
        tv.save()
        tasks = tv.task_set.all()
        self.assertEqual(tasks.count() , 1)
        transcribe_task = tasks.filter(type=10, language='en')
        self.assertEqual(transcribe_task.count(), 1)
