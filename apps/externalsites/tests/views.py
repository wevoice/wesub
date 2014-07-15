# Amara, universalsubtitles.org
#
# Copyright (C) 2014 Participatory Culture Foundation
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
from django.core.urlresolvers import reverse

from externalsites.views import settings_page_redirect_url
from utils.factories import *

class SettingsPageRedirectUrlTest(TestCase):
    def test_normal_redirect(self):
        team = TeamFactory()
        data = {}
        correct_url = reverse('teams:settings_externalsites',
                              kwargs={ 'slug': team.slug })
        self.assertEquals(
            settings_page_redirect_url(team, data),
            correct_url)

    def test_add_youtube_account_redirect(self):
        team = TeamFactory()
        data = {'add-youtube-account': 1}
        correct_url = "%s?team_slug=%s" % (
            reverse('externalsites:youtube-add-account'),
            team.slug)
        self.assertEquals(
            settings_page_redirect_url(team, data),
            correct_url)
