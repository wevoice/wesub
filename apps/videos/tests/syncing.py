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

from django.core.urlresolvers import reverse
from django.test import TestCase

from apps.auth.models import CustomUser as User
from subtitles.models import SubtitleVersion, SubtitleLanguage 
from videos.models import Video

class TimingChangeTest(TestCase):
    '''
    This group of test is to make sure that timmiing is not being
    rounded ever
    '''

    def setUp(self):
        original_video , created = Video.get_or_create_for_url("http://www.example.com/original.mp4")
        self.to_upload_video= Video.get_or_create_for_url("http://www.example.com/to_uplaod.mp4")[0]
        self.original_video = original_video
        language = SubtitleLanguage.objects.create(video=original_video, language='en', is_original=True, is_forked=True)
        version = SubtitleVersion.objects.create(
            language=language,
            version_no=0,
            datetime_started=datetime.now(),
            is_forked = language.is_forked
        )

        for x in xrange(5):
            s= Subtitle.objects.create(
                version = version,
                subtitle_id=x,
                subtitle_order=x,
                subtitle_text="Sub %s" % x,
                start_time =  x * 1033,
                end_time = (x * 1033)+ 888
        )

        self.user = User.objects.get_or_create(username='admin')[0]
        self.user.set_password('admin')
        self.user.save()

    def _download_subs(self, format, video, unsynced=False):
        url = reverse("widget:download_" + format)
        res = self.client.get(url, {
            'video_id': video.video_id,
            'lang_pk': video.subtitle_language("en").pk
        })
        self.assertEqual(res.status_code, 200)
        parser =  ParserList[format](res.content.decode('utf-8'))
        self.assertEqual(len(parser), 5)
        subs = [x for x in parser]
       
        for i,item in enumerate(subs):
            if unsynced:
                self.assertEqual(item['start_time'], None)
                self.assertEqual(item['end_time'], None)
            else:
                self.assertEqual(item['start_time'], i * 1033)
                self.assertEqual(item['end_time'], (i * 1033) + 888)
        return subs

    def _download_then_upload(self,format, unsynced=False):
        subs = self._download_subs(format, self.original_video, unsynced=unsynced)
        cleaned_subs = []
        for s in subs:
            cleaned_subs.append({
                'text': markup_to_html(s['subtitle_text']),
                'start': s['start_time'],
                'end': s['end_time'],
                'id': None,
            })


        as_string  = unicode(GenerateSubtitlesHandler[format](
            cleaned_subs, self.to_upload_video,
            sl=SubtitleLanguage(language='en', video=self.to_upload_video)
        ))
        # file uploads need an actual file handler, StringIO won't do it, dammit
        file_path = "/tmp/sample-upload.%s" % format
        fd = open(file_path, 'w')
        fd.write(as_string.encode('utf-8'))
        fd.close()
        fd = open(file_path)
        data = {
            'language': 'en',
            'video_language': 'en',
            'video': self.to_upload_video.pk,
            'draft': fd,
            'is_complete': True
            }
        self.client.login(username='admin', password='admin')
        response = self.client.post(reverse('videos:upload_subtitles'), data)
        # this is an ajax upload, the result gets serialized inside a text area,
        # if successfull will have the video id on the the 'next' json content
        self.assertIn('/videos/%s/en' % self.to_upload_video.video_id, response.content)
        subtitles = self.to_upload_video.subtitle_language("en").version().subtitle_set.all()
        self.assertEqual(len(subtitles), 5)
        for i,item in enumerate(subtitles):
            if unsynced:
                self.assertEqual(item.start_time, None)
                self.assertEqual(item.end_time, None)
            else:
                self.assertEqual(item.start_time, i * 1033)
                self.assertEqual(item.end_time, (i * 1033) + 888)

    def test_dowload_then_upload_srt(self):
        # this is a 'round trip' test
        # we store subs directly into the db, with known timming
        # we then dowload the subs in each format
        # upload them through the upload
        # then check the new subs timming against the original ones
        self._download_then_upload('srt')

    def test_dowload_then_upload_dfxp(self):
        # this is a 'round trip' test
        # we store subs directly into the db, with known timming
        # we then dowload the subs in each format
        # upload them through the upload
        # then check the new subs timming against the original ones
        self._download_then_upload('dfxp')

    def test_dowload_then_upload_ssa(self):
        # this is a 'round trip' test
        # we store subs directly into the db, with known timming
        # we then dowload the subs in each format
        # upload them through the upload
        # then check the new subs timming against the original ones
        self._download_then_upload('ssa')

    def test_dowload_then_upload_ttml(self):
        # this is a 'round trip' test
        # we store subs directly into the db, with known timming
        # we then dowload the subs in each format
        # upload them through the upload
        # then check the new subs timming against the original ones
        self._download_then_upload('ttml')

    def test_dowload_then_upload_sbv(self):
        # this is a 'round trip' test
        # we store subs directly into the db, with known timming
        # we then dowload the subs in each format
        # upload them through the upload
        # then check the new subs timming against the original ones
        self._download_then_upload('sbv')


    def test_unsynced_srt(self):
        Subtitle.objects.filter(version__language__video=self.original_video).update(start_time=None, end_time=None)
        self._download_then_upload('srt', unsynced=True)

    def test_unsynced_dfxp(self):
        Subtitle.objects.filter(version__language__video=self.original_video).update(start_time=None, end_time=None)
        self._download_then_upload('dfxp', unsynced=True)

    def test_unsynced_sbv(self):
        Subtitle.objects.filter(version__language__video=self.original_video).update(start_time=None, end_time=None)
        self._download_then_upload('sbv', unsynced=True)

    def test_unsynced_ssa(self):
        Subtitle.objects.filter(version__language__video=self.original_video).update(start_time=None, end_time=None)
        self._download_then_upload('ssa', unsynced=True)
