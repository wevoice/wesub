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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from __future__ import absolute_import

from django.core.urlresolvers import reverse

from utils import test_factories
from teams.models import TeamVideo
from videos.tests.feeds import FeedImportTest

class TeamAddVideosTest(FeedImportTest):
    def test_video_feed_submit(self):
        team = test_factories.create_team()
        user = test_factories.create_team_member(team).user
        self.client.login(username=user.username, password='password')
        feed_url = u'http://example.com/feed'
        url = reverse('teams:add_videos', kwargs={'slug':team.slug})
        data = { 'feed_url': feed_url, }

        response = self.client.post(url, data)

        self.assertEqual(team.videos.count(), 2)
        for video in team.videos.all():
            self.assertEquals(video.user, user)
            self.assertEquals(video.get_team_video().added_by, user)
