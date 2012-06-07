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

from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from apps.auth.models import CustomUser as User
from apps.thirdpartyaccounts.models import FacebookAccount, TwitterAccount
from socialauth.lib import oauthtwitter
from socialauth.lib.facebook import get_user_info, get_facebook_signature


TWITTER_CONSUMER_KEY = getattr(settings, 'TWITTER_CONSUMER_KEY', '')
TWITTER_CONSUMER_SECRET = getattr(settings, 'TWITTER_CONSUMER_SECRET', '')
FACEBOOK_API_KEY = getattr(settings, 'FACEBOOK_API_KEY', '')
FACEBOOK_API_SECRET = getattr(settings, 'FACEBOOK_API_SECRET', '')
FACEBOOK_REST_SERVER = getattr(settings, 'FACEBOOK_REST_SERVER',
                               'http://api.facebook.com/restserver.php')


class TwitterAuthBackend(object):
    def _get_existing_user(self, data):
        try:
            tpa = TwitterAccount.objects.get(username=data.screen_name)
            return User.objects.get(pk=tpa.user_id)
        except (TwitterAccount.DoesNotExist, User.DoesNotExist):
            return None

    def _find_available_username(self, data):
        username = data.screen_name

        name_count = User.objects.filter(username__startswith=username).count()
        if name_count:
            username = '%s%d' % (username, name_count + 1)

        return username

    def _get_first_last_name(self, data):
        name_data = data.name.split()

        try:
            first_name, last_name = name_data[0], ' '.join(name_data[1:])
        except:
            first_name, last_name = data.screen_name, ''

        return first_name, last_name

    def _create_user(self, access_token, data):
        username = self._find_available_username(data)

        twitter_username = data.screen_name
        first_name, last_name = self._get_first_last_name(data)
        avatar = data.profile_image_url

        email = '%s@twitteruser.%s.com' % (twitter_username, settings.SITE_NAME)

        user = User(username=username, email=email, first_name=first_name,
                    last_name=last_name)
        temp_password = User.objects.make_random_password(length=24)
        user.set_password(temp_password)
        user.save()

        TwitterAccount.objects.create(user=user, username=twitter_username,
                                      access_token=access_token.key,
                                      avatar=avatar)

        return user


    def authenticate(self, access_token):
        twitter = oauthtwitter.OAuthApi(TWITTER_CONSUMER_KEY,
                                        TWITTER_CONSUMER_SECRET,
                                        access_token)
        try:
            userinfo = twitter.GetUserInfo()
        except:
            # If we cannot get the user information, user cannot be authenticated
            raise

        user = self._get_existing_user(userinfo)
        if not user:
            user = self._create_user(access_token, userinfo)

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None


class FacebookAuthBackend(object):
    def _get_existing_user(self, data):
        try:
            tpa = FacebookAccount.objects.get(uid=data['uid'])
            return User.objects.get(pk=tpa.user_id)
        except (FacebookAccount.DoesNotExist, User.DoesNotExist):
            return None

    def _find_available_username(self, data):
        username = data.get('first_name', 'FACEBOOK_USER')

        name_count = User.objects.filter(username__istartswith=username).count()
        if name_count:
            username = '%s%d' % (username, name_count + 1)

        return username

    def _create_user(self, data):
        username = self._find_available_username(data)

        first_name = data.get('first_name')
        last_name = data.get('last_name')
        facebook_uid = data.get('uid')
        avatar = data.get('pic_small')

        email = '%s@facebookuser.%s.com' % (first_name, settings.SITE_NAME)

        user = User(username=username, email=email, first_name=first_name,
                    last_name=last_name)
        temp_password = User.objects.make_random_password(length=24)
        user.set_password(temp_password)
        user.save()

        FacebookAccount.objects.create(uid=facebook_uid, user=user,
                                       avatar=avatar)

        return user


    def authenticate(self, cookies):
        if FACEBOOK_API_KEY in cookies:
            signature_hash = get_facebook_signature(FACEBOOK_API_KEY,
                                                    FACEBOOK_API_SECRET,
                                                    cookies,
                                                    True)

            hash_matches = (signature_hash == cookies[FACEBOOK_API_KEY])

            expiration = datetime.datetime.fromtimestamp(
                    float(cookies[FACEBOOK_API_KEY + '_expires']))
            not_expired = (expiration > datetime.datetime.now())

            if hash_matches and not_expired:
                user_info_response = get_user_info(FACEBOOK_API_KEY,
                                                   FACEBOOK_API_SECRET,
                                                   cookies)
                data = user_info_response[0]

                user = self._get_existing_user(data)
                if not user:
                    user = self._create_user(data)
                return user
            else:
                return None


        else:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except:
            return None


