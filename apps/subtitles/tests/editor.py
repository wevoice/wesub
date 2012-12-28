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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

import datetime
from django.core.urlresolvers import  reverse
from django.test import TestCase

from auth.models import CustomUser
from subtitles.tests.utils import (
    make_video
)

class EditorViewTest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.get_or_create(username='admin')[0]
        self.user.set_password('admin')
        self.user.save()

    def _login(self, user=None):
        user = user or self.user
        self.client.login(username=user.username, password='admin')

    def test_login_required(self):
        video = make_video()
        url = reverse("subtitles:subtitle-editor", args=(video.video_id,'en'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # redirect from the login_required decorator does not include
        # the locale name, but the reverse we use does ;)
        login_url = "/".join(reverse("auth:login").split("/")[2:])
        self.assertIn(login_url, response['location'])
        self._login()
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_valid_language_requured(self):
        video = make_video()
        self._login()
        url = reverse("subtitles:subtitle-editor", args=(video.video_id,'xxxxx'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 500)
