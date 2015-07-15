# -*- coding: utf-8 -*-
from rest_framework.test import APILiveServerTestCase, APIClient
from django.core import mail

from caching.tests.utils import assert_invalidates_model_cache
from videos.models import *
from utils.factories import *
from webdriver_testing import data_helpers
from webdriver_testing.data_factories import TeamLangPrefFactory
from subtitles import pipeline
from webdriver_testing.webdriver_base import WebdriverTestCase

class TestCaseTasks(APILiveServerTestCase, WebdriverTestCase):
    """TestSuite for teams tasks api  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseTasks, cls).setUpClass()
        cls.client = APIClient
        cls.data_utils = data_helpers.DataHelpers()
        cls.admin = UserFactory()
        cls.manager = UserFactory()
        cls.member = UserFactory()
        cls.team = TeamFactory(admin=cls.admin,
                               manager=cls.manager,
                               member=cls.member,
                               workflow_enabled=True
                              )
        WorkflowFactory.create(
            team = cls.team,
            review_allowed = 10,
            approve_allowed = 20,
            autocreate_subtitle = True,
            autocreate_translate = True)
        lang_list = ['en', 'ru', 'pt-br', 'fr', 'de', 'es']
        for language in lang_list:
            TeamLangPrefFactory.create(
                team = cls.team,
                language_code = language,
                preferred = True)
        cls.video = VideoFactory(primary_audio_language_code="en")
        cls.tv = TeamVideoFactory(team=cls.team, video=cls.video)

        #complete transcribe task
        #add 1 draft version of subtitles
        pipeline.add_subtitles(cls.video, 'en', SubtitleSetFactory(),
                               committer=cls.member, author=cls.member, complete=False)
        #add a final version of subtitles
        pipeline.add_subtitles(cls.video, 'en', SubtitleSetFactory(),
                               committer=cls.member, author=cls.member, complete=True)
        cls.data_utils.complete_review_task(cls.tv, 20, cls.manager)
        cls.data_utils.complete_approve_task(cls.tv, 20, cls.manager)
        #complete french translate tasks
        pipeline.add_subtitles(cls.video, 'fr', SubtitleSetFactory(),
                               committer=cls.member, author=cls.member, complete=True)
        cls.data_utils.complete_review_task(cls.tv, 20, cls.manager)
        cls.data_utils.complete_approve_task(cls.tv, 20, cls.manager)
       
        #german lang translate needs approve 
        pipeline.add_subtitles(cls.video, 'de', SubtitleSetFactory(),
                               committer=cls.member, author=cls.member, complete=True)
        cls.data_utils.complete_review_task(cls.tv, 20, cls.manager)

    def _get (self, url='/api/teams/', user=None):
        self.client.force_authenticate(user)
        response = self.client.get(url)
        response.render()
        r = (json.loads(response.content))
        return r

    def _post(self, url='/api/teams/', data=None, user=None):
        self.client.force_authenticate(user)
        response = self.client.post(url, data)
        response.render()
        r = (json.loads(response.content))
        return r

    def _put(self, url='/api/teams/', data=None, user=None):
        self.client.force_authenticate(user)
        response = self.client.put(url, data)
        response.render()
        r = (json.loads(response.content))
        return r

    def _delete(self, url='/api/teams/', user=None):
        self.client.force_authenticate(user)
        response = self.client.delete(url)
        try:
            response.render()
            r = (json.loads(response.content))
            return r
        except:
            return response.status_code


    def test_list_transcribe(self):
        """List off the existing tasks. 

        """
        video = VideoFactory(primary_audio_language_code="it")
        tv = TeamVideoFactory(team=self.team, video=video)
        url = '/api/teams/%s/tasks/?type=Subtitle' % self.team.slug
        r = self._get(url=url, user=self.member)
        self.assertEqual(2, len(r['objects']))

    def test_completed_transcribe(self):
        """List off the existing completed tasks filtered by type. 
        """
        url = '/api/teams/%s/tasks/?completed&type=Subtitle' % self.team.slug
        r = self._get(url=url, user=self.member)
        self.assertEqual(1, len(r['objects']))

    def test_list_open_translate(self):
        """List off the existing open tasks of a type. 

        GET /api2/partners/teams/[team-slug]/tasks/
        """
        url = '/api/teams/%s/tasks/?open&type=Translate' % self.team.slug
        r = self._get(url=url, user=self.member)
        self.assertEqual(3, len(r['objects']))


    def test_query_video_id(self):
        """Query for tasks of a video_id. 

        GET /api2/partners/teams/[team-slug]/tasks/
        """
        url = '/api/teams/{0}/tasks/?video_id={1}'.format(
            self.team.slug, self.video.video_id)
        r = self._get(url=url, user=self.member)
        self.assertEqual(12, len(r['objects']))

    def test_query_video_id_type(self):
        """Query for tasks of a video_id and type. 
        """
        url = '/api/teams/{0}/tasks/?video_id={1}&type=Approve'.format(
            self.team.slug, self.video.video_id)
        r = self._get(url=url, user=self.member)
        self.assertEqual(3, len(r['objects']))


    def test_query_video_id_lang(self):
        """Query for tasks of a video_id. 
        """
        url = '/api/teams/{0}/tasks/?video_id={1}&language=de'.format(
            self.team.slug, self.video.video_id)

        r = self._get(url=url, user=self.member)
        self.logger.info(r)
        self.assertEqual(3, len(r['objects']))

    def test_query_completed_videoid_lang(self):
        """Query for tasks of a video_id. 
        """
        url = '/api/teams/{0}/tasks/?video_id={1}&language=de&completed'.format(
            self.team.slug, self.video.video_id)
        r = self._get(url=url, user=self.member)
        self.logger.info(r)
        self.assertEqual(2, len(r['objects']))


    def test_query_assignee(self):
        """Query for tasks by assignee.
       
        """
        url = '/api/teams/%s/tasks/?assignee=%s' % (
                self.team.slug, self.member.username)
        r = self._get(url=url, user=self.member)
        self.assertEqual(3, len(r['objects']))

 
    def test_task_detail(self):
        """Get the details of a task.
        """
        url = '/api/teams/%s/tasks/1/' % self.team.slug
        r = self._get(url=url, user=self.member)
        self.logger.info(r)
        self.assertEqual(r['complete'], True) 
        self.assertEqual(r['type'], 'Subtitle') 
        self.assertEqual(r['language'], 'en') 
        self.assertEqual(r['video_id'], self.video.video_id) 

    def test_create_update_delete(self):
        """Create a new task for a video.

        """

        team = TeamFactory(admin=self.admin,
                           manager=self.manager,
                           member=self.member,
                           workflow_enabled=True, 
                           task_assign_policy = 30
                              )
        WorkflowFactory.create(
            team = team,
            review_allowed = 10,
            approve_allowed = 20,
            autocreate_subtitle = True,
            autocreate_translate = False )


        #Add a video with original lang 'it', and publish
        video = VideoFactory(primary_audio_language_code="it")
        tv = TeamVideoFactory(team=team, video=video)
        pipeline.add_subtitles(video, 'it', SubtitleSetFactory(),
                               committer=self.admin, author=self.member, complete=True)
        url = '/api/videos/%s/languages/en/subtitles/actions/' % video.video_id
        r = self._post(url=url, data={'action': 'approve'}, user=self.manager)
        r = self._post(url=url, data={'action': 'approve'}, user=self.admin)

        #Create a translate task
        url = '/api/teams/%s/tasks/' % team.slug
        data = {"type": "Translate",
                "video_id": video.video_id,
                "language": "es-mx"
                }
        #team member can not create task via api.
        r = self._post(url=url, data=data, user=self.member)
        self.assertEqual(r, {u'detail': u'Permission denied'})
        r = self._post(url=url, data=data, user=self.admin)
        url = '/api/teams/{0}/tasks/{1}/'.format(team.slug, r['id'])
        data = {'assignee': self.member.username}

        #update task assignee (must be admin)
        r = self._put(url=url, data=data, user=self.manager)
        self.assertEqual(r, {u'detail': u'Permission denied'})
        r = self._put(url=url, data=data, user=self.admin)
        self.logger.info(r)
        self.assertEqual(r['assignee'], self.member.username)

        #delete the task (must be admin)
        r = self._delete(url=url, user=self.member)
        self.assertEqual(r, {u'detail': u'Permission denied'})
        r = self._delete(url=url, user=self.admin)
        self.assertEqual(r, 204)

    def test_fetch_public_subtitles(self):
        """Return public subtitles of a moderated video.

        For videos under moderation only the latest published version is returned. 
        """
        user = UserFactory()
        url = '/api/videos/{0}/languages/en/'.format(
                   self.video.video_id)

        r = self._get(url=url, user=user)
        self.logger.info(r)
        self.assertEqual(1, len(r['versions']))
        self.assertEqual(2, r['versions'][0]['version_no'])

    def test_fetch_draft_subtitles(self):
        """Fetch nothing if moderated and no version has been accepted in review.
        """
        user = UserFactory()
        url = '/api/videos/{0}/languages/de/?format=srt'.format(self.video.video_id)
        r = self._get(url=url, user=user)
        self.logger.info(r)
        self.assertEqual(r, {u'detail': u'Not found'})

