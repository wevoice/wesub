from datetime import datetime, timedelta, date

from django.test import TestCase

from apps.auth.models import CustomUser as User
from apps.teams.models import Team, BillingRecord, BillingReport, Workflow
from apps.videos.models import SubtitleLanguage, SubtitleVersion, Video
from apps.videos.tasks import video_changed_tasks
from apps.videos.types.youtube import FROM_YOUTUBE_MARKER

from utils.test_utils import add_subs

class BillingTest(TestCase):
    fixtures = [
        "staging_users.json",
        "staging_videos.json",
        "staging_teams.json"
    ]

    def test_approved(self):
        from apps.teams.moderation_const import APPROVED

        self.assertEquals(0, Workflow.objects.count())

        team = Team.objects.all()[0]
        team.workflow_enabled = True
        team.save()

        Workflow.objects.create(team=team, approve_allowed=20)

        self.assertEquals(1, Workflow.objects.count())
        self.assertTrue(team.get_workflow().approve_enabled)

        language = SubtitleLanguage.objects.all()[0]

        for i in range(1, 10):
            SubtitleVersion.objects.create(language=language,
                                           datetime_started=datetime(2012, 1, i, 0, 0, 0),
                                           version_no=i)

        v1 = SubtitleVersion.objects.get(language=language, version_no=3)
        v2 = SubtitleVersion.objects.get(language=language, version_no=6)

        v1.moderation_status = APPROVED
        v1.save()
        v2.moderation_status = APPROVED
        v2.save()

        b = BillingReport.objects.create(team=team,
                                         start_date=date(2012, 1, 1), end_date=date(2012, 1, 2))

        langs = language.video.subtitlelanguage_set.all()
        c = langs[0]
        d = team.created - timedelta(days=5)
        SubtitleVersion.objects.create(language=c, version_no=0,
                                       note=FROM_YOUTUBE_MARKER,
                                       datetime_started=d)

        self.assertTrue(len(langs) > 0)
        created, imported, _ = b._get_lang_data(langs, datetime(2012, 1, 1, 13, 30, 0))

        self.assertTrue(len(created) > 0)

        v = created[0][1]
        self.assertEquals(v.version_no, 3)

        team.workflow_enabled = False
        team.save()

        created, imported, _ = b._get_lang_data(langs, datetime(2012, 1, 1, 13, 30, 0))
        self.assertEquals(1, len(created))
        v = created[0][1]
        self.assertEquals(v.version_no, 9)

    def test_get_imported(self):

        team = Team.objects.all()[0]
        video = Video.objects.all()[0]

        team_created = team.created

        b = BillingReport.objects.create(team=team,
                                         start_date=date(2012, 1, 1), end_date=date(2012, 1, 2))

        SubtitleLanguage.objects.all().delete()

        sl_en = SubtitleLanguage.objects.create(video=video, language='en')
        sl_cs = SubtitleLanguage.objects.create(video=video, language='cs')
        sl_fr = SubtitleLanguage.objects.create(video=video, language='fr')
        sl_es = SubtitleLanguage.objects.create(video=video, language='es')
        SubtitleLanguage.objects.create(video=video, language='ru')

        before_team_created = team_created - timedelta(days=10)
        after_team_created = team_created + timedelta(days=10)

        # Imported
        SubtitleVersion.objects.create(language=sl_fr,
                                       datetime_started=before_team_created, note=FROM_YOUTUBE_MARKER,
                                       version_no=0)

        # Created
        SubtitleVersion.objects.create(language=sl_fr,
                                       datetime_started=after_team_created,
                                       version_no=1)

        SubtitleVersion.objects.create(language=sl_en,
                                       datetime_started=before_team_created, note=FROM_YOUTUBE_MARKER,
                                       version_no=0)

        # Imported
        SubtitleVersion.objects.create(language=sl_es,
                                       datetime_started=before_team_created,
                                       version_no=0)

        # Imported
        SubtitleVersion.objects.create(language=sl_cs,
                                       datetime_started=after_team_created, note=FROM_YOUTUBE_MARKER,
                                       version_no=0)

        # Done with setup, let's test things

        languages = SubtitleLanguage.objects.all()
        imported, crowd_created = b._separate_languages(languages)

        self.assertEquals(len(imported), 3)
        imported_pks = [i.pk for i in imported]
        self.assertTrue(sl_fr.pk in imported_pks)
        self.assertTrue(sl_es.pk in imported_pks)
        self.assertTrue(sl_cs.pk in imported_pks)

    def test_record_insertion(self):

        BillingRecord.objects.all().delete()

        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.save()

        now = datetime.now()

        sl, sv = add_subs(video, 'en', 4, language_is_complete=True,
                          user=user, datetime_started=now)

        video_changed_tasks(video.pk, sv.pk)

        self.assertEquals(1, BillingRecord.objects.all().count())

        br = BillingRecord.objects.all()[0]

        self.assertEquals(br.video.pk, video.pk)
        self.assertEquals(br.team.pk, video.get_team_video().team.pk)
        self.assertEquals(br.created, now)
        self.assertEquals(br.is_original, sl.is_original)
        self.assertEquals(br.user.pk, user.pk)
        self.assertEquals(br.subtitle_language.pk, sl.pk)

        team = video.get_team_video().team
        start = datetime(2013, 1, 1, 0, 0)
        end = datetime(2013, 5, 1, 0, 0, 0)

        csv_data = BillingRecord.objects.csv_report_for_team(team, start, end)

        self.assertEquals(2, len(csv_data))
        self.assertEquals(8, len(csv_data[1]))

        # 2
        sl, sv = add_subs(video, 'en', 4, user=user, datetime_started=now,
                          language_is_original=False )
        video_changed_tasks(video.pk, sv.pk)

        # A new one shouldn't be created for the same language
        self.assertEquals(1, BillingRecord.objects.all().count())

    def test_update_language_complete(self):
        """
        https://unisubs.sifterapp.com/issues/2225
        Create a version not synced.
        Then later
        """
        BillingRecord.objects.all().delete()

        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.save()

        sl, first_version = add_subs(video, 'en', 4, is_synced=False, language_is_complete=False, user=user)

        # create a transla
        video_changed_tasks(video.pk, first_version.pk)
        self.assertEquals(0, BillingRecord.objects.all().count())
        sl, second_version = add_subs(video, 'en', 4, is_synced=True, language_is_complete=True, user=user)
        video_changed_tasks(video.pk, second_version.pk)

        self.assertEquals(1, BillingRecord.objects.all().count())


    def test_update_source_language(self):
        """
        https://unisubs.sifterapp.com/issues/2225
        Create a version not synced.
        Create a translation.
        Then later finish the original one
        """
        BillingRecord.objects.all().delete()

        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.save()

        original_lang, original_version = add_subs( video, 'en', 4,
            is_synced=False, language_is_complete=False, user=user )

        video_changed_tasks(video.pk, original_version.pk)
        self.assertEquals(0, BillingRecord.objects.all().count())

        translation_language, translation_version = add_subs(video, 'pt', 4,
                is_synced=False, user=user, translated_from='en')
        # no billing for this one, because it isn't synced!
        self.assertEquals(0, BillingRecord.objects.all().count())


        # now sync the original language
        original_lang, original_version = add_subs(video, 'en', 4,
                is_synced=True, language_is_complete=True, user=user)
        video_changed_tasks(video.pk, original_version.pk)

        # now that the original version is synced we should bill for both
        bl_original = BillingRecord.objects.filter(subtitle_language=original_lang)
        bl_translation = BillingRecord.objects.filter(subtitle_language=translation_language)
        self.assertEquals(1, bl_original.count())
        self.assertEquals(1, bl_translation.count())


    def test_two_languages(self):
        from apps.teams.models import BillingRecord
        from apps.videos.tasks import video_changed_tasks

        BillingRecord.objects.all().delete()

        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.save()

        sl_en , sv_en = add_subs(video, 'en', 4, user=user, language_is_complete=True)
        video_changed_tasks(video.pk, sv_en.pk)

        sl_cs, sv_cs = add_subs(video, 'cs', 4, language_is_complete=True, user=user)
        video_changed_tasks(video.pk, sv_cs.pk)

        self.assertEquals(2, BillingRecord.objects.all().count())

    def test_incomplete_language(self):
        from apps.teams.models import BillingRecord
        from apps.videos.tasks import video_changed_tasks

        BillingRecord.objects.all().delete()

        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.save()

        sl_en, sv_en = add_subs(video, 'en', 4, language_is_complete=False)

        video_changed_tasks(video.pk, sv_en.pk)

        self.assertEquals(0, BillingRecord.objects.all().count())

    def test_original_language(self):
        from apps.teams.models import BillingRecord
        from apps.videos.tasks import video_changed_tasks

        BillingRecord.objects.all().delete()

        user = User.objects.all()[0]

        video = Video.objects.filter(teamvideo__isnull=False)[0]
        video.user = user
        video.save()

        sl_en, sv_en = add_subs(video, 'en', 4, language_is_complete=True, language_is_original=False)
        video_changed_tasks(video.pk, sv_en.pk)

        self.assertEquals(1, BillingRecord.objects.all().count())

        br = BillingRecord.objects.all()[0]
        self.assertFalse(br.is_original)
