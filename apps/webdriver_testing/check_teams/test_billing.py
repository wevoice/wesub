# -*- coding: utf-8 -*-
import os
import datetime
import csv
from collections import defaultdict
import time


from apps.webdriver_testing.webdriver_base import WebdriverTestCase
from apps.webdriver_testing.data_factories import TeamMemberFactory
from apps.webdriver_testing.data_factories import TeamVideoFactory

from apps.webdriver_testing.data_factories import UserFactory
from apps.webdriver_testing.data_factories import VideoUrlFactory
from apps.webdriver_testing.data_factories import BillingFactory
from apps.webdriver_testing import data_helpers
from apps.webdriver_testing.pages.site_pages import billing_page 

class TestCaseBilling(WebdriverTestCase):
    NEW_BROWSER_PER_TEST_CASE = False

    @classmethod
    def setUpClass(cls):
        super(TestCaseBilling, cls).setUpClass()
        cls.data_utils = data_helpers.DataHelpers()
        cls.billing_pg = billing_page.BillingPage(cls)
        cls.terri = UserFactory.create(username='Terri', 
                                       is_staff=True, is_superuser=True)
        cls.user = UserFactory.create()
        cls.team = TeamMemberFactory.create(user = cls.user).team
        cls.subs_data_dir = os.path.join(os.getcwd(), 'apps', 
            'webdriver_testing', 'subtitle_data')
        cls.video, cls.tv = cls._create_tv_with_original_subs(cls.user, cls.team)
        cls._upload_sv_translation(cls.video, cls.user, complete=True)

        cls.bill_dict = cls.create_team_bill()
        cls.billing_pg.open_billing_page()
        cls.billing_pg.log_in(cls.terri.username, 'password')


    @classmethod
    def create_team_bill(cls):
        report = BillingFactory( start_date=(datetime.date.today() - 
                                            datetime.timedelta(1)),
                                end_date=datetime.datetime.now(),
                                )
        report.teams=[cls.team]
        report.save()
        report.process()
        cls.bill = 'user-data/%s' % report.csv_file
        bill_dict = cls._bill_dict(cls.bill)
        return bill_dict


    @classmethod
    def _create_tv_with_original_subs(cls, user, team, complete=True):
        member_creds = dict(username=user.username, password='password')
        sub_file = os.path.join(cls.subs_data_dir, 'Timed_text.en.srt')
        video = VideoUrlFactory().video
        tv = TeamVideoFactory.create(
            team=team, 
            video=video, 
            added_by=user)
        data = {'language_code': 'en',
                'video': video.pk,
                'primary_audio_language_code': 'en',
                'draft': open(sub_file),
                'is_complete': complete,
                'complete': int(complete),
                }
        cls.data_utils.upload_subs(video, data, member_creds)
        return video, tv

    @classmethod
    def _upload_sv_translation(cls, video, user, complete=False):
        member_creds = dict(username=user.username, password='password')

        data = {'language_code': 'sv',
                'video': video.pk,
                'from_language_code': 'en',
                'draft': open('apps/webdriver_testing/subtitle_data/'
                              'Timed_text.sv.dfxp'),
                'is_complete': complete,
                'complete': int(complete),}
        cls.data_utils.upload_subs(video, data=data, user=member_creds)

    @classmethod
    def _bill_dict(cls, bill_file):
        team_bill = defaultdict(dict)
        with open(bill_file, 'rb') as fp:
            reader = csv.DictReader(fp, dialect='excel')
            for rowdict in reader:
                video_id = rowdict.pop("Video ID")
                lang = rowdict.pop("Language")
                cls.logger.info(lang)
                team_bill[video_id][lang] = rowdict 
        return dict(team_bill)
        

    def test_complete(self):
        """Complete team videos are billed.

        """

        self.assertEqual('3.0', 
                         self.bill_dict[self.video.video_id]['en']['Minutes'])


    def test_incomplete(self):
        """Incomplete languages have no billing record. """
        video, tv = self._create_tv_with_original_subs(self.user, self.team)
        inc_video, inc_tv = self._create_tv_with_original_subs(self.user, 
                                                               self.team, 
                                                               complete=False)

        report = BillingFactory(start_date=(datetime.date.today() - 
                                            datetime.timedelta(1)),
                                end_date=datetime.datetime.now(),
                                )
        report.teams=[self.team]
        report.save()

        report.process()
        bill = 'user-data/%s' % report.csv_file
        bill_dict = self._bill_dict(bill)
        self.assertNotIn(inc_video.video_id, bill_dict.keys())

    def test_primary_audio_language(self):
        """Primary audio lang true / false included in Original field.

        """
        self.logger.info(self.bill_dict)
        self.assertEqual('True',
                         self.bill_dict[self.video.video_id]['en']['Original'])
        self.assertEqual('False',
                         self.bill_dict[self.video.video_id]['sv']['Original'])


    def test_translation__complete(self):
        """Billing record added for complete translations

        """
        self.assertIn('sv', self.bill_dict[self.video.video_id].keys())

    def test_translation__incomplete(self):
        """Incomplete languages have -1 minutes.

        """
        video, tv = self._create_tv_with_original_subs(self.user, self.team)
        self._upload_sv_translation(video, self.user, complete=False)

        report = BillingFactory(start_date=(datetime.date.today() - 
                                            datetime.timedelta(1)),
                                end_date=datetime.datetime.now(),
                                )
        report.teams=[self.team]
        report.save()
        report.process()
        bill = 'user-data/%s' % report.csv_file
        bill_dict = self._bill_dict(bill)
        sv_bill = bill_dict[video.video_id]['sv']

        self.logger.info(sv_bill)
        self.assertEqual('-1', sv_bill['Minutes'])


    def test_minutes(self):
        """Minutes from last synced sub rounded up to whole minute.

        """
        self.assertEqual('3.0', 
                         self.bill_dict[self.video.video_id]['en']['Minutes'])


    def test_source(self):
        """Source of subs is listed in data (youtube, upload, api...)

        """
        self.assertEqual('upload', 
                         self.bill_dict[self.video.video_id]['en']['Source'])

    def test_user(self):
        """User credit with subtitles is listed in the record.

        """
        testuser = TeamMemberFactory.create().user
        video, tv = self._create_tv_with_original_subs(self.user, self.team)
        self._upload_sv_translation(video, testuser, complete=True)
        report = BillingFactory(start_date=(datetime.date.today() - 
                                            datetime.timedelta(1)),
                                end_date=datetime.datetime.now(),
                                )
        report.teams=[self.team]
        report.save()
        report.process()
        bill = 'user-data/%s' % report.csv_file
        bill_dict = self._bill_dict(bill)
        self.assertEqual(self.user.username, bill_dict[video.video_id]['en']['User'])
        self.assertEqual(testuser.username, bill_dict[video.video_id]['sv']['User'])


    def test_team(self):
        """Team is listed in the record.

        """
        self.assertEqual(self.team.slug, 
                         self.bill_dict[self.video.video_id]['en']['Team'])
    
    def test_created(self):
        """Data subtitles completed is listed in the record.

        """
        en = self.video.subtitle_language('en').get_tip(full=True)
        self.assertEqual(en.created.strftime("%Y-%m-%d %H:%M:%S"), 
                         self.bill_dict[self.video.video_id]['en']['Created'])

    def test_video(self):
        """Video id is listed in the record.

        """
        self.assertIn(self.video.video_id, self.bill_dict.keys())


    def test_new_billing_fields(self):
        video, tv = self._create_tv_with_original_subs(self.user, self.team)
        report = BillingFactory(start_date=(datetime.date.today() - 
                                            datetime.timedelta(1)),
                                end_date=datetime.datetime.now(),
                                )
        report.teams=[self.team]
        report.save()
        report.process()
        bill = csv.DictReader(open('user-data/%s' %report.csv_file))
        expected_fields = ['Video Title', 'Video ID', 'Language', 'Minutes', 
                           'Original', 'Language number', 'Team', 'Created', 'Source', 'User']
        self.assertEqual(expected_fields, bill.fieldnames)


    def test_old_billing_fields(self):
        video, tv = self._create_tv_with_original_subs(self.user, self.team)
        report = BillingFactory(type=1,
                                start_date=(datetime.date.today() - 
                                            datetime.timedelta(1)),
                                end_date=datetime.datetime.now(),
                                )
        report.teams=[self.team]
        report.save()
        report.process()
        bill = csv.DictReader(open('user-data/%s' %report.csv_file))
        expected_fields = ['Video title', 'Video URL', 'Video language',
                           'Source', 'Billable minutes', 'Version created',
                           'Language number', 'Team']
        self.assertEqual(expected_fields, bill.fieldnames)

 
    def test_download__new_model(self):
        """Data range of records downloaded to a csv file for a team.

        """
        for x in range(3):
            video, tv = self._create_tv_with_original_subs(self.user, self.team)

        self.billing_pg.open_billing_page()
        self.billing_pg.log_in(self.terri.username, 'password')
        self.billing_pg.open_billing_page()
        start = (datetime.date.today() - datetime.timedelta(7))
        end =  (datetime.date.today() + datetime.timedelta(2))
        self.logger.info(start.strftime("%Y-%m-%d"))

        self.billing_pg.submit_billing_parameters(self.team.name,
                                                  start.strftime("%Y-%m-%d"),
                                                  end.strftime("%Y-%m-%d"),
                                                  'New model')
        report_dl = self.billing_pg.check_latest_report_url()
        self.logger.info(report_dl)
        new_headers = 'Video Title,Video ID,Language,Minutes,Original,Language number,Team,Created,Source,User' 
        self.assertEqual(6, len(report_dl))
        self.assertEqual(new_headers, report_dl[0])

    def test_download__multi_team_new(self):
        """Create a report for several teams.

        """

        team2_user = UserFactory.create()
        team2 = TeamMemberFactory.create(user = team2_user).team
        video2, tv2 = self._create_tv_with_original_subs(team2_user, team2)
        self._upload_sv_translation(video2, team2_user, complete=True)


        for x in range(3):
            self._create_tv_with_original_subs(team2_user, team2)

        self.billing_pg.open_billing_page()
        self.billing_pg.log_in(self.terri.username, 'password')
        self.billing_pg.open_billing_page()
        start = (datetime.date.today() - datetime.timedelta(7))
        end =  (datetime.date.today() + datetime.timedelta(2))
        self.logger.info(start.strftime("%Y-%m-%d"))
        team_names = ','.join([self.team.name, team2.name])
        self.billing_pg.submit_billing_parameters(team_names,
                                                  start.strftime("%Y-%m-%d"),
                                                  end.strftime("%Y-%m-%d"),
                                                  'New model')
        report_dl = self.billing_pg.check_latest_report_url()
        self.logger.info(report_dl)
        new_headers = 'Video Title,Video ID,Language,Minutes,Original,Language number,Team,Created,Source,User' 
        self.assertEqual(8, len(report_dl))
        self.assertEqual(new_headers, report_dl[0])

    def test_download__old_model(self):
        """Data range of records downloaded to a csv file for a team.

        """
        for x in range(3):
            video, tv = self._create_tv_with_original_subs(self.user, self.team)

        self.billing_pg.open_billing_page()
        self.billing_pg.log_in(self.terri.username, 'password')
        self.billing_pg.open_billing_page()
        start = (datetime.date.today() - datetime.timedelta(7))
        end =  (datetime.date.today() + datetime.timedelta(2))
        self.logger.info(start.strftime("%Y-%m-%d"))

        self.billing_pg.submit_billing_parameters(self.team.name,
                                                  start.strftime("%Y-%m-%d"),
                                                  end.strftime("%Y-%m-%d"),
                                                  'Old model')
        report_dl = self.billing_pg.check_latest_report_url()
        self.logger.info(report_dl)
        old_headers = ('Video title,Video URL,Video language,Source,Billable minutes,'
                       'Version created,Language number,Team')
        self.assertEqual(6, len(report_dl))
        self.assertEqual(old_headers, report_dl[0])


    def test_download__multi_team_old(self):
        """Create a report for several teams.

        """

        team2_user = UserFactory.create()
        team2 = TeamMemberFactory.create(user = team2_user).team
        video2, tv2 = self._create_tv_with_original_subs(team2_user, team2)
        self._upload_sv_translation(video2, team2_user, complete=True)


        for x in range(3):
            self._create_tv_with_original_subs(team2_user, team2)

        self.billing_pg.open_billing_page()
        self.billing_pg.log_in(self.terri.username, 'password')
        self.billing_pg.open_billing_page()
        start = (datetime.date.today() - datetime.timedelta(7))
        end =  (datetime.date.today() + datetime.timedelta(2))
        team_names = ','.join([self.team.name, team2.name])
        self.billing_pg.submit_billing_parameters(team_names,
                                                  start.strftime("%Y-%m-%d"),
                                                  end.strftime("%Y-%m-%d"),
                                                  'Old model')
        report_dl = self.billing_pg.check_latest_report_url()
        self.logger.info(report_dl)
        self.assertEqual(8, len(report_dl))

    def tearDown(self):
        self.browser.get_screenshot_as_file("MYTMP/%s.png" % self.id())

