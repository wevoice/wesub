from datetime import datetime, timedelta, date
import itertools

from django.test import TestCase

from apps.auth.models import CustomUser as User
from apps.teams.models import (
    Team, BillingRecord, BillingReport, Workflow, TeamVideo
)
from apps.subtitles.models import SubtitleLanguage, SubtitleVersion
from apps.subtitles.pipeline import add_subtitles
from apps.teams.permissions_const import (ROLE_CONTRIBUTOR, ROLE_MANAGER,
                                          ROLE_ADMIN)
from apps.teams.models import BillingRecord, Task
from apps.videos.models import Video
from apps.videos.tasks import video_changed_tasks
from apps.videos.types.youtube import FROM_YOUTUBE_MARKER
from apps.videos.tests.data import (
    make_subtitle_lines, make_subtitle_language, get_video, get_user,
    make_subtitle_version
)
from utils import test_factories
from utils import test_utils

import mock

class OldTypeBillingTest(TestCase):
    # FIXME: should move this away from using fixtures
    fixtures = [
        "staging_users.json",
        "staging_teams.json"
    ]

    def setUp(self):
        self.video = get_video()
        self.team = Team.objects.all()[0]
        TeamVideo.objects.get_or_create(video=self.video, team=self.team,
                                        added_by=get_user())

    def process_report(self, report):
        # don't really save the report, since that would try to upload the csv
        # file to S3
        with mock.patch.object(report, 'save') as mock_save:
            report.process()
            self.assertEquals(mock_save.call_count, 1)
        return report.csv_file.read()

    def test_approved(self):

        self.assertEquals(0, Workflow.objects.count())

        self.team.workflow_enabled = True
        self.team.save()

        Workflow.objects.create(team=self.team, approve_allowed=20)

        self.assertEquals(1, Workflow.objects.count())
        self.assertTrue(self.team.get_workflow().approve_enabled)

        english = make_subtitle_language(self.video, 'en')
        spanish = make_subtitle_language(self.video, 'es')

        for i in range(1, 10):
            add_subtitles(self.video, english.language_code,[],
                          created=datetime(2012, 1, i, 0, 0, 0),
                          visibility='private',
            )


        # make two versions public to be sure we're selecting the very first one
        v1_en = SubtitleVersion.objects.get(subtitle_language=english, version_number=3)
        v2_en = SubtitleVersion.objects.get(subtitle_language=english, version_number=6)

        v1_en.publish()
        v1_en.save()
        v2_en.publish()
        v2_en.save()

        b = BillingReport.objects.create( start_date=date(2012, 1, 1),
                                          end_date=date(2012, 1, 2))
        b.teams.add(self.team)

        past_date = self.team.created - timedelta(days=5)
        make_subtitle_version(spanish, created=past_date, note=FROM_YOUTUBE_MARKER)


        langs = self.video.newsubtitlelanguage_set.all()
        self.assertEqual(len(langs) , 2)
        created, imported, _ = b._get_lang_data(langs,
                                                datetime(2012, 1, 1, 13, 30, 0),
                                                self.team )

        self.assertEqual(len(created) , 1)

        v = created[0][1]
        self.assertEquals(v.version_number, 3)
        self.assertEqual(v.subtitle_language , english)


    def test_get_imported(self):

        team = Team.objects.all()[0]
        video = Video.objects.all()[0]

        team_created = team.created

        b = BillingReport.objects.create( start_date=date(2012, 1, 1),
                                          end_date=date(2012, 1, 2))
        b.teams.add(team)

        SubtitleLanguage.objects.all().delete()

        sl_en = SubtitleLanguage.objects.create(video=video, language_code='en')
        sl_cs = SubtitleLanguage.objects.create(video=video, language_code='cs')
        sl_fr = SubtitleLanguage.objects.create(video=video, language_code='fr')
        sl_es = SubtitleLanguage.objects.create(video=video, language_code='es')
        SubtitleLanguage.objects.create(video=video, language_code='ru')

        before_team_created = team_created - timedelta(days=10)
        after_team_created = team_created + timedelta(days=10)

        # Imported
        add_subtitles(video, 'fr', [], created=before_team_created, note=FROM_YOUTUBE_MARKER)
        # Created
        add_subtitles(video, 'fr', [], created=after_team_created)
        add_subtitles(video, 'en', [], created=before_team_created, note=FROM_YOUTUBE_MARKER)
        # Imported
        add_subtitles(video, 'es', [], created=before_team_created)
        # Imported
        add_subtitles(video, 'cs', [], created=after_team_created, note=FROM_YOUTUBE_MARKER)

        # Done with setup, let's test things

        languages = SubtitleLanguage.objects.all()
        imported, crowd_created = b._separate_languages(languages)

        self.assertEquals(len(imported), 3)
        imported_pks = [i.pk for i in imported]
        self.assertTrue(sl_fr.pk in imported_pks)
        self.assertTrue(sl_es.pk in imported_pks)
        self.assertTrue(sl_cs.pk in imported_pks)

    def test_record_insertion(self):
        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.primary_audio_language_code = 'en'
        video.user = user
        video.save()

        now = datetime.now()

        sv = add_subtitles(video, 'en', make_subtitle_lines(4), complete=True,
                          author=user, created=now)
        sl = sv.subtitle_language

        video_changed_tasks(video.pk, sv.pk)

        self.assertEquals(1, BillingRecord.objects.all().count())

        br = BillingRecord.objects.all()[0]

        self.assertEquals(br.video.pk, video.pk)
        self.assertEquals(br.team.pk, video.get_team_video().team.pk)
        self.assertEquals(br.created, now)
        self.assertEquals(br.is_original, sl.is_primary_audio_language())
        self.assertEquals(br.user.pk, user.pk)
        self.assertEquals(br.new_subtitle_language.pk, sl.pk)

        team = video.get_team_video().team
        start = datetime(2013, 1, 1, 0, 0)
        end = datetime.now() + timedelta(days=1)

        csv_data = BillingRecord.objects.csv_report_for_team(team, start, end)

        self.assertEquals(2, len(csv_data))
        self.assertEquals(10, len(csv_data[1]))

        # 2
        sv = add_subtitles(video, 'en', make_subtitle_lines(4), author=user, created=now)
        sl = sv.subtitle_language
                          
        video_changed_tasks(video.pk, sv.pk)

        # A new one shouldn't be created for the same language
        self.assertEquals(1, BillingRecord.objects.all().count())

    def test_update_language_complete(self):
        """
        https://unisubs.sifterapp.com/issues/2225
        Create a version not synced.
        Then later
        """
        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.save()

        first_version = add_subtitles(video, 'en', make_subtitle_lines(4,  is_synced=False), complete=False, author=user)

        # create a transla
        video_changed_tasks(video.pk, first_version.pk)
        self.assertEquals(0, BillingRecord.objects.all().count())
        second_version = add_subtitles(video, 'en', make_subtitle_lines(4), complete=True, author=user)
        video_changed_tasks(video.pk, second_version.pk)

        self.assertEquals(1, BillingRecord.objects.all().count())


    def test_update_source_language(self):
        """
        https://unisubs.sifterapp.com/issues/2225
        Create a version not synced.
        Create a translation.
        Then later finish the original one
        """
        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.save()

        original_version = add_subtitles(
            video, 'en', make_subtitle_lines(4, is_synced=False),
            complete=False, author=user )
        original_lang = original_version.subtitle_language

        video_changed_tasks(video.pk, original_version.pk)
        self.assertEquals(0, BillingRecord.objects.all().count())

        translation_version = add_subtitles(
            video, 'pt', make_subtitle_lines(4, is_synced=False),
                author=user, parents=[original_version])
        translation_language = translation_version.subtitle_language
        # no billing for this one, because it isn't synced!
        self.assertEquals(0, BillingRecord.objects.all().count())


        # now sync them
        original_version = add_subtitles(
            video, 'en', make_subtitle_lines(4, is_synced=True),
                complete=True, author=user)
        original_lang = original_version.subtitle_language
        video_changed_tasks(video.pk, original_version.pk)
        bl_original = BillingRecord.objects.filter(new_subtitle_language=original_lang)
        self.assertEquals(1, bl_original.count())

        translation_version = add_subtitles(
            video, 'pt', make_subtitle_lines(5),
            author=user, parents=[original_version], complete=True)
        video_changed_tasks(video.pk, translation_version.pk)
        bl_translation = BillingRecord.objects.filter(new_subtitle_language=translation_language)
        self.assertEquals(1, bl_translation.count())


    def test_two_languages(self):
        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.save()

        sv_en = add_subtitles(video, 'en', make_subtitle_lines(4), author=user, complete=True)
        video_changed_tasks(video.pk, sv_en.pk)

        sv_cs = add_subtitles(video, 'cs', make_subtitle_lines(4), complete=True, author=user)
        video_changed_tasks(video.pk, sv_cs.pk)

        self.assertEquals(2, BillingRecord.objects.all().count())

    def test_incomplete_language(self):
        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.save()

        sv_en = add_subtitles(video, 'en', make_subtitle_lines(4), complete=False)

        video_changed_tasks(video.pk, sv_en.pk)

        self.assertEquals(0, BillingRecord.objects.all().count())

    def test_original_language(self):
        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.primary_audio_language_code = ''
        video.save()

        sv_en = add_subtitles(video, 'en', make_subtitle_lines(4), complete=True)
        video_changed_tasks(video.pk, sv_en.pk)

        self.assertEquals(1, BillingRecord.objects.all().count())

        br = BillingRecord.objects.all()[0]
        self.assertFalse(br.is_original)

    def test_non_ascii_text(self):
        non_ascii_text = u'abcd\xe9'

        user = test_factories.create_user(username=non_ascii_text)
        test_factories.create_team_member(self.team, user)

        self.video.title = non_ascii_text
        self.video.save()

        sv = add_subtitles(self.video, 'en', make_subtitle_lines(4), 
                           title=non_ascii_text,
                           author=user,
                           description=non_ascii_text,
                           complete=True)
        video_changed_tasks(self.video.pk, sv.pk)

        report = BillingReport.objects.create(
            start_date=sv.created - timedelta(days=1),
            end_date=sv.created + timedelta(days=1),
            type=BillingReport.TYPE_NEW,
        )
        report.teams.add(self.team)
        self.process_report(report)

class DateMaker(object):
    """Get dates to use for billing events."""
    def __init__(self):
        self.current_date = self.start_date()

    def next_date(self):
        self.current_date += timedelta(days=1)
        return self.current_date

    def date_before_start(self):
        return self.start_date() - timedelta(days=1)

    def start_date(self):
        return datetime(2012, 1, 1, 0, 0, 0)

    def end_date(self):
        return self.current_date + timedelta(days=1)

def get_report_data(report_rows):
    """Get report data in an easy to test way.

    Converts each row into a dict, with the keys being the keys from the
    header row.

    Converts the list of rows into a dict mapping (video_id, language_code) to
    a row.
    """
    header_row = report_rows[0]
    rv = {}
    for row in report_rows[1:]:
        row_data = dict((header, value)
                        for (header, value)
                        in zip(header_row, row))
        video_id = row_data['Video ID']
        language_code = row_data['Language']
        assert (video_id, language_code) not in rv, \
                "Duplicate video_id/language in row: (%s, %s)" % (
                    video_id, language_code)
        rv[video_id, language_code] = row_data
    return rv

class NewTypeBillingTest(TestCase):
    def setUp(self):
        self.team = test_factories.create_team()

    def add_subtitles(self, video, *args, **kwargs):
        version = add_subtitles(video, *args, **kwargs)
        BillingRecord.objects.insert_record(version)
        return version

    def get_report_data(self, team, start_date, end_date):
        """Get report data in an easy to test way.
        """
        report = BillingReport.objects.create(start_date=start_date,
                                              end_date=end_date,
                                              type=BillingReport.TYPE_NEW)
        report.teams.add(team)
        return get_report_data(report.generate_rows())

    def test_language_number(self):
        date_maker = DateMaker()
        user = test_factories.create_team_member(self.team).user

        video = test_factories.create_video(primary_audio_language_code='en')
        test_factories.create_team_video(self.team, user, video)
        self.add_subtitles(video, 'en', make_subtitle_lines(4),
                           created=date_maker.next_date(),
                           complete=True)
        self.add_subtitles(video, 'fr', make_subtitle_lines(4),
                           created=date_maker.next_date(),
                           complete=True)
        self.add_subtitles(video, 'de', make_subtitle_lines(4),
                           created=date_maker.next_date(),
                           complete=True)

        video2 = test_factories.create_video(primary_audio_language_code='en')
        test_factories.create_team_video(self.team, user, video2)
        # the english version was added before the date range of the report.
        # It should still bump the language number though.
        self.add_subtitles(video2, 'en', make_subtitle_lines(4),
                           created=date_maker.date_before_start(),
                           complete=True)
        self.add_subtitles(video2, 'fr', make_subtitle_lines(4),
                           created=date_maker.next_date(),
                           complete=True)

        data = self.get_report_data(self.team,
                                    date_maker.start_date(),
                                    date_maker.end_date())
        self.assertEquals(len(data), 4)
        self.assertEquals(data[video.video_id, 'en']['Language number'], 1)
        self.assertEquals(data[video.video_id, 'fr']['Language number'], 2)
        self.assertEquals(data[video.video_id, 'de']['Language number'], 3)
        self.assertEquals(data[video2.video_id, 'fr']['Language number'], 2)

    def test_missing_records(self):
        date_maker = DateMaker()
        user = test_factories.create_team_member(self.team).user

        video = test_factories.create_video(primary_audio_language_code='en')
        test_factories.create_team_video(self.team, user, video)
        # For en and de, we call pipeline.add_subtitles directly, so there's
        # no BillingRecord in the sytem.  This simulates the languages that
        # were completed before BillingRecords were around.
        add_subtitles(video, 'en', make_subtitle_lines(4),
                           created=date_maker.next_date(),
                           complete=True)
        add_subtitles(video, 'de', make_subtitle_lines(4),
                           created=date_maker.next_date(),
                           complete=True)
        # pt-br has a uncompleted subtitle language.  We should not list that
        # language in the report
        add_subtitles(video, 'pt-br', make_subtitle_lines(4),
                           created=date_maker.next_date(),
                           complete=False)
        self.add_subtitles(video, 'fr', make_subtitle_lines(4),
                           created=date_maker.next_date(),
                           complete=True)
        self.add_subtitles(video, 'es', make_subtitle_lines(4),
                           created=date_maker.next_date(),
                           complete=True)
        data = self.get_report_data(self.team,
                                    date_maker.start_date(),
                                    date_maker.end_date())
        self.assertEquals(len(data), 4)
        self.assertEquals(data[video.video_id, 'en']['Language number'], 0)
        self.assertEquals(data[video.video_id, 'de']['Language number'], 0)
        self.assertEquals(data[video.video_id, 'fr']['Language number'], 1)
        self.assertEquals(data[video.video_id, 'es']['Language number'], 2)
        self.assertEquals(data[video.video_id, 'en']['Minutes'], 0)
        self.assertEquals(data[video.video_id, 'de']['Minutes'], 0)

class ApprovalTypeBillingTest(TestCase):
    @test_utils.patch_for_test('teams.models.Task.now')
    def setUp(self, mock_now):
        self.date_maker = DateMaker()
        mock_now.side_effect = self.date_maker.next_date
        self.setup_team()
        self.setup_users()
        self.setup_videos()

    def setup_team(self):
        self.team = test_factories.create_team(workflow_enabled=True)
        test_factories.create_workflow(
            self.team,
            review_allowed=20, # manager must review
            approve_allowed=20, # admin must approve
        )

    def setup_users(self):
        # make a bunch of users to subtitle/review the work
        subtitlers = [test_factories.create_user() for i in xrange(3)]
        reviewers = [test_factories.create_user() for i in xrange(2)]
        for u in subtitlers:
            test_factories.create_team_member(user=u, team=self.team,
                                              role=ROLE_CONTRIBUTOR)
        for u in reviewers:
            test_factories.create_team_member(user=u, team=self.team,
                                              role=ROLE_MANAGER)
        self.subtitler_iter = itertools.cycle(subtitlers)
        self.reviewer_iter = itertools.cycle(reviewers)

        self.admin = test_factories.create_team_member(team=self.team,
                                                       role=ROLE_ADMIN).user

    def setup_videos(self):
        # make a bunch of languages that have moved through the review process
        self.subtitlers = {}
        self.reviewers = {}
        self.approved_languages = []
        self.approval_dates = {}
        self.translations = set()

        v1 = test_factories.create_team_video(self.team).video
        v2 = test_factories.create_team_video(self.team).video
        v3 = test_factories.create_team_video(self.team).video
        languages = [
            (v1, 'en'),
            (v1, 'fr'),
            (v1, 'de'),
            (v1, 'pt-br'),
            (v2, 'en'),
            (v2, 'es'),
            (v2, 'fr'),
            (v2, 'de'),
            (v2, 'pt-br'),
            (v3, 'en'),
            (v3, 'de'),
        ]
        self.videos = {
            v1.video_id: v1,
            v2.video_id: v2,
            v3.video_id: v3,
        }

        for i, (video, language_code) in enumerate(languages):
            video_id = video.video_id
            subtitler = self.subtitler_iter.next()
            reviewer = self.reviewer_iter.next()
            if i % 3 == 0:
                task_type = 'Translate'
                self.translations.add((video_id, language_code))
            else:
                task_type = 'Subtitle'
            review_task = test_factories.make_review_task(
                video.get_team_video(), language_code, subtitler, task_type)
            approve_task = review_task.complete_approved(reviewer)
            self.assertEquals(approve_task.type, Task.TYPE_IDS['Approve'])
            self.subtitlers[video_id, language_code] = subtitler
            self.reviewers[video_id, language_code] = reviewer
            if i < 6:
                # for some of those videos, approve them
                approve_task.complete_approved(self.admin)
                self.approved_languages.append(
                    video.subtitle_language(language_code))
                self.approval_dates[video_id, language_code] = \
                        self.date_maker.current_date
            if 6 <= i < 8:
                # for some of those videos, send them back to review, then
                # review again and approve the final result
                # for some of those videos, approve them
                review_task2 = approve_task.complete_rejected(self.admin)
                approve_task2 = review_task2.complete_approved(reviewer)
                approve_task2.complete_approved(self.admin)
                self.approved_languages.append(
                    video.subtitle_language(language_code))
                self.approval_dates[video_id, language_code] = \
                        self.date_maker.current_date

    def get_report_data(self, start_date, end_date):
        """Get report data in an easy to test way.
        """
        report = BillingReport.objects.create(
            start_date=start_date, end_date=end_date,
            type=BillingReport.TYPE_APPROVAL)
        report.teams.add(self.team)
        return get_report_data(report.generate_rows())

    def check_report_rows(self, report_data):
        # check that we got the right number of rows
        self.assertEquals(len(report_data), len(self.approved_languages))
        # check video ids and language codes
        self.assertEquals(set(report_data.keys()),
                          set((lang.video.video_id, lang.language_code)
                              for lang in self.approved_languages))

    def check_approver(self, report_data):
        for (video_id, language_code), row in report_data.items():
            subtitler = self.subtitlers[video_id, language_code]
            reviewer = self.reviewers[video_id, language_code]
            self.assertEquals(row['Approver'], unicode(self.admin))

    def check_language_columns(self, report_data):
        for (video_id, language_code), row in report_data.items():
            lang = self.videos[video_id].subtitle_language(language_code)
            self.assertEquals(row['Original'],
                              lang.is_primary_audio_language())
            if (video_id, language_code) in self.translations:
                self.assertEquals(row['Translation?'], True)
            else:
                self.assertEquals(row['Translation?'], False)

    def test_report(self):
        report_data = self.get_report_data(self.date_maker.start_date(),
                                    self.date_maker.end_date())
        self.check_report_rows(report_data)
        self.check_approver(report_data)
        self.check_language_columns(report_data)
