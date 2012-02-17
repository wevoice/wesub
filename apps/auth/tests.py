# Universal Subtitles, universalsubtitles.org
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
from datetime import datetime, timedelta
from urlparse import urlparse

from django.core.urlresolvers import reverse
from django.core import mail
from django.test import TestCase
from auth.models import CustomUser as User
from auth.models import LoginToken
from videos.models import Video

class TestModels(TestCase):
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]

    def setUp(self):
        self.video = Video.objects.exclude(subtitlelanguage=None)[:1].get()
        self.video.followers = []
        self.sl = self.video.subtitlelanguage_set.all()[:1].get()
        self.sl.followers = []

        self.ovideo = Video.objects.exclude(subtitlelanguage=None).exclude(pk=self.video.pk)[:1].get()
        self.ovideo.followers = []
        self.osl = self.ovideo.subtitlelanguage_set.all()[:1].get()
        self.osl.followers = []

        self.user = User.objects.all()[:1].get()

    def test_videos_updating_1(self):
        self.assertEqual(self.video.followers.count(), 0)
        self.assertEqual(self.ovideo.followers.count(), 0)
        self.assertEqual(self.user.videos.count(), 0)

        self.video.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id])

        self.ovideo.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id, self.ovideo.id])

        self.video.followers.remove(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.ovideo.id])

        self.ovideo.followers = []
        self.assertEqual(self.user.videos.count(), 0)

        self.user.followed_videos.add(self.video)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id])

        self.user.followed_videos.add(self.ovideo)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id, self.ovideo.id])

        self.user.followed_videos.remove(self.video)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.ovideo.id])

        self.user.followed_videos = []
        self.assertEqual(self.user.videos.count(), 0)

    def test_videos_updating_2(self):
        self.assertEqual(self.video.followers.count(), 0)
        self.assertEqual(self.ovideo.followers.count(), 0)
        self.assertEqual(self.user.videos.count(), 0)

        self.video.followers.add(self.user)
        self.ovideo.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id, self.ovideo.id])

        self.sl.followers.add(self.user)
        self.video.followers.remove(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id, self.ovideo.id])

        self.sl.followers.remove(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.ovideo.id])

        self.ovideo.followers = []
        self.assertEqual(self.user.videos.count(), 0)

        self.sl.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id])

        self.video.followers.add(self.user)
        self.sl.followers.remove(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.video.id])

        self.video.followers.remove(self.user)
        self.assertEqual(self.user.videos.count(), 0)

    def test_videos_updating_3(self):
        self.assertEqual(self.sl.followers.count(), 0)
        self.assertEqual(self.osl.followers.count(), 0)
        self.assertEqual(self.user.videos.count(), 0)

        self.sl.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.sl.video.id])

        self.osl.followers.add(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.sl.video.id, self.osl.video.id])

        self.sl.followers.remove(self.user)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.osl.video.id])

        self.osl.followers = []
        self.assertEqual(self.user.videos.count(), 0)

        self.user.followed_languages.add(self.sl)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.sl.video.id])

        self.user.followed_languages.add(self.osl)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.sl.video.id, self.osl.video.id])

        self.user.followed_languages.remove(self.sl)
        self.assertEqual(list(self.user.videos.values_list('id', flat=True)), [self.osl.video.id])

        self.user.followed_languages = []
        self.assertEqual(self.user.videos.count(), 0)


class UserCreationTest(TestCase):
    def test_notfications(self):
        self.assertEqual(len(mail.outbox), 0)
        user = User(email='la@example.com', username='someone')
        user.set_password("secret")
        user.save()
        self.assertEqual(len(mail.outbox), 1)

class BaseTokenTest(TestCase):
    fixtures = ["staging_users.json", "staging_videos.json", "staging_teams.json"]

    def setUp(self):
        self.user = User.objects.all()[0]

class LoginTokenModelTest(BaseTokenTest):
    def test_creation(self):
       lt1 = LoginToken.objects.for_user(self.user)
       lt2 = LoginToken.objects.for_user(self.user, updates=False)
       self.assertEqual(lt1.token, lt2.token)
       self.assertEqual(len(lt1.token), 40)
       # assesrt updates does what it says
       lt3 = LoginToken.objects.for_user(self.user, updates=True)
       self.assertNotEqual(lt3.token, lt2.token)
       self.assertEqual(len(lt3.token), 40)

    def test_expire(self):

       lt1 = LoginToken.objects.for_user(self.user)
       self.assertFalse(lt1.is_expired)
       self.assertFalse(LoginToken.objects.get_expired().filter(pk=lt1.pk).exists())
       older_date = datetime.now() - timedelta(minutes=1) - LoginToken.EXPIRES_IN
       lt1.created = older_date
       lt1.save()
       self.assertTrue(lt1.is_expired)
       self.assertTrue(LoginToken.objects.get_expired().filter(pk=lt1.pk).exists())


class LoginTokenViewsTest(BaseTokenTest):
    def test_valid_login(self):
       lt1 = LoginToken.objects.for_user(self.user)
       redirect_url = '/en/videos/watch'
       url = reverse("auth:token-login", args=(lt1.token,)) + "?next=%s" % redirect_url
       response = self.client.get(url)
       self.assertEqual(response.status_code, 302)
       location = response._headers['location'][1]
       redirect_path = urlparse(location).path
       self.assertEqual(redirect_path, redirect_url)

    def test_invalid_login(self):
       lt1 = LoginToken.objects.for_user(self.user)
       redirect_url = '/en/videos/watch'
       url = reverse("auth:token-login", args=(lt1.token,)) + "?next=%s" % redirect_url
       lt1.delete()
       response = self.client.get(url)
       self.assertEqual(response.status_code, 403)

    def test_staff_is_offlimit(self):
       lt1 = LoginToken.objects.for_user(self.user)
       self.user.is_staff  = True
       self.user.save()
       redirect_url = '/en/videos/watch'
       url = reverse("auth:token-login", args=(lt1.token,)) + "?next=%s" % redirect_url
       response = self.client.get(url)
       self.assertEqual(response.status_code, 403)

    def test_superuser_is_offlimit(self):
       lt1 = LoginToken.objects.for_user(self.user)
       self.user.is_superuser  = True
       self.user.save()
       redirect_url = '/en/videos/watch'
       url = reverse("auth:token-login", args=(lt1.token,)) + "?next=%s" % redirect_url
       response = self.client.get(url)
       self.assertEqual(response.status_code, 403)

