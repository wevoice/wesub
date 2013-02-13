# -*- coding: utf-8 -*-
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

"""Basic sanity tests to make sure the subtitle models aren't completely broken."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from babelsubs.storage import SubtitleSet

from apps.auth.models import CustomUser as User
from apps.subtitles.forms import SubtitlesUploadForm
from apps.subtitles.tests.utils import (
    make_video, make_sl, make_subtitle_set, refresh
)

class SubtitleUploadFormTest(TestCase):

    def setUp(self):
        self.video = make_video()
        self.en = make_sl(self.video, 'en')
        self.fr = make_sl(self.video, 'fr')
        self.de = make_sl(self.video, 'de')
        self.user = User.objects.get_or_create(username='admin')

    def test_verify_no_translation_conflict(self):
        # we'll have baseline subs in English and German.
        # At first we have a French from german, then
        # we try to upload French from English, should fail
        en_version = self.en.add_version(subtitles=make_subtitle_set('en'))
        de_version = self.de.add_version(subtitles=make_subtitle_set('ge'))
        fr_version = self.fr.add_version(subtitles=make_subtitle_set('fr'), parents=[de_version])

        self.fr = refresh(self.fr)
        self.assertEqual(self.fr.subtitleversion_set.count(), 1)
        self.assertEqual(self.fr.get_translation_source_language_code(), 'de')
        f = SubtitlesUploadForm(self.user, self.video)
        self.assertRaises(ValidationError, f._verify_no_translation_conflict, self.fr, 'en')



