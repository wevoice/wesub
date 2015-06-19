# -*- coding: utf-8 -*-
import time

from rest_framework.test import APILiveServerTestCase, APIClient
from videos.models import *
from utils.factories import *
from webdriver_testing import data_helpers
from webdriver_testing.data_factories import TeamLangPrefFactory
from subtitles import pipeline
from webdriver_testing.webdriver_base import WebdriverTestCase

class TestCaseActivity(APILiveServerTestCase, WebdriverTestCase):
    """TestSuite for teams tasks api  """
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseActivity, cls).setUpClass()
        cls.client = APIClient
        cls.data_utils = data_helpers.DataHelpers()
        cls.staff = UserFactory(is_staff=True)
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

        time.sleep(2)
        cls.time = int(time.time())
        time.sleep(2)
        #complete french translate tasks
        pipeline.add_subtitles(cls.video, 'fr', SubtitleSetFactory(),
                               committer=cls.member, author=cls.member, complete=True)
        cls.data_utils.complete_review_task(cls.tv, 20, cls.manager)
        cls.data_utils.complete_approve_task(cls.tv, 20, cls.manager)
       
        #german lang translate needs approve 
        pipeline.add_subtitles(cls.video, 'de', SubtitleSetFactory(),
                               committer=cls.member, author=cls.member, complete=True)
        cls.data_utils.complete_review_task(cls.tv, 20, cls.manager)

        #reject spanish subs in review
        pipeline.add_subtitles(cls.video, 'es', SubtitleSetFactory(),
                               committer=cls.member, author=cls.member, complete=True)
        cls.data_utils.complete_review_task(cls.tv, 30, cls.manager)

        #reject pt-br subs in approve
        pipeline.add_subtitles(cls.video, 'pt-br', SubtitleSetFactory(),
                               committer=cls.member, author=cls.member, complete=True)
        cls.data_utils.complete_review_task(cls.tv, 20, cls.manager)
        cls.data_utils.complete_approve_task(cls.tv, 30, cls.manager)

        #add some non-team videos with subs
        cls.user = UserFactory()
        langs = ['en', 'fr', 'de', 'it', 'pt-br']
        for lc in langs:
            cls.vid = VideoFactory(primary_audio_language_code=lc) 
            pipeline.add_subtitles(cls.vid, lc, SubtitleSetFactory(),
                                   complete=True, committer=cls.user, author=cls.user)
            pipeline.add_subtitles(cls.vid, 'en', SubtitleSetFactory(),
                                   committer=cls.user, author=cls.user)

    def _get (self, url='/api/activity/', user=None):
        self.client.force_authenticate(user)
        response = self.client.get(url)
        response.render()
        r = (json.loads(response.content))
        return r


    def test_list_activity(self):
        """List off user's activity. 

        """
        r = self._get(user=self.user)
        self.assertEqual(10, r['meta']['total_count'])

    def test_sub_language(self):
        url = '/api/activity/?type=4'
        r = self._get(url=url, user=self.user)
        self.assertEqual('pt-br', r['objects'][1]['language'])
        self.assertIn('pt-br', r['objects'][1]['language_url'])


    def test_video_query(self):
        """Query user activity for a video 

        """
        url = '/api/activity/?video=%s' % self.vid.video_id
        r = self._get(url=url, user=self.user)
        self.assertEqual(2, r['meta']['total_count'])


    def test_type_query(self):
        """query user activity by type

        """
        url = '/api/activity/?type=4'
        r = self._get(url=url, user=self.user)
        self.logger.info(r)
        self.assertEqual(10, r['meta']['total_count'])


    def test_lang_query(self):
        """query activity by language

        """
        url = '/api/activity/?language=en'
        r = self._get(url=url, user=self.user)
        self.logger.info(r)
        self.assertEqual(6, r['meta']['total_count'])


    def test_team_lang_query(self):
        """query activity by language

        """
        url = '/api/activity/?language=en&team=%s' % self.team.slug
        r = self._get(url=url, user=self.member)
        self.logger.info(r)
        self.assertEqual(7, r['meta']['total_count'])

        url = '/api/activity/?language=pt-br&team=%s' % self.team.slug
        r = self._get(url=url, user=self.member)
        self.logger.info(r)
        self.assertEqual(3, r['meta']['total_count'])
    
    def test_rejected_query(self):
        """query team task reject version

        """
        url = '/api/activity/?team=%s&type=10' % self.team.slug
        r = self._get(url=url, user=self.admin)
        self.logger.info(r)
        self.assertEqual(1, r['meta']['total_count'])


    def test_decline_query(self):
        """query team task decline version

        """
        url = '/api/activity/?team=%s&type=14&lang=es' % self.team.slug
        r = self._get(url=url, user=self.admin)
        self.logger.info(r)
        self.assertEqual(1, r['meta']['total_count'])


    def test_accepted_query(self):
        """query team task accept version activity

        """
        url = '/api/activity/?team=%s&type=13' % self.team.slug
        r = self._get(url=url, user=self.admin)
        self.logger.info(r)
        self.assertEqual(4, r['meta']['total_count'])


    def test_approve_query(self):
        """query team task approve activity

        """
        url = '/api/activity/?team=%s&type=8' % self.team.slug
        r = self._get(url=url, user=self.admin)
        self.logger.info(r)
        self.assertEqual(2, r['meta']['total_count'])

    def test_approve_lang_query(self):
        """query team task approve french version

        """
        url = '/api/activity/?team=%s&type=8&language=fr' % self.team.slug
        r = self._get(url=url, user=self.admin)
        self.logger.info(r)
        self.assertEqual(1, r['meta']['total_count'])

    def test_time_query(self):
        """query in time range """
        url = '/api/activity/?team={0}&before={1}'.format(self.team.slug, self.time)
        r = self._get(url=url, user=self.admin)
        self.assertEqual(7, r['meta']['total_count'])

        url = '/api/activity/?team={0}&after={1}'.format(self.team.slug, self.time)
        r = self._get(url=url, user=self.admin)
        self.assertEqual(15, r['meta']['total_count'])
