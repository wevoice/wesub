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

from django.test import TestCase

from apps.videos import metadata_manager
from apps.videos.models import Video
from apps.videos.tests.videos import create_langs_and_versions


class TestMetadataManager(TestCase):
    fixtures = ['staging_users.json', 'staging_videos.json']

    def test_language_count(self):
        video = Video.objects.all()[0]
        create_langs_and_versions(video, ['en'])
        metadata_manager.update_metadata(video.pk)
        video = Video.objects.all()[0]
        self.assertEqual(video.languages_count, 1)

