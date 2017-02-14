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
import logging
import random

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User as AuthUser

from auth.models import CustomUser as User
from socialauth.models import OpenidProfile as UserAssociation, AuthMeta

logger = logging.getLogger(__name__)

class CustomUserBackend(ModelBackend):
    supports_object_permissions = False
    supports_anonymous_user = False

    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(username=username, is_active=True)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class OpenIdBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False


    @staticmethod
    def pre_authenticate(openid_key, request, provider):
        try:
            assoc = OpenIdBackend._lookup_association(openid_key, request, provider)
            return (True, '')
        except UserAssociation.DoesNotExist:
            email = None
            if request.openid and request.openid.sreg:
                email = request.openid.sreg.get('email')
            elif request.openid and request.openid.ax:
                if provider in ('Google', 'Yahoo'):
                    key = 'http://axschema.org/contact/email'
                    email = request.openid.ax.get(key)[-1]
                else:
                    try:
                        email = request.openid.ax.get('email')
                    except KeyError:
                        pass
            return (False, email)

    def authenticate(self, openid_key, request, provider, email=None):
        try:
            assoc = OpenIdBackend._lookup_association(openid_key, request, provider)
            if assoc.user.is_active:
                return assoc.user
            else:
                return
        except UserAssociation.DoesNotExist:
            #fetch if openid provider provides any simple registration fields
            nickname = None
            if request.openid and request.openid.sreg:
                if email is None:
                    email = request.openid.sreg.get('email')
                nickname = request.openid.sreg.get('nickname')
            elif request.openid and request.openid.ax:
                if provider in ('Google', 'Yahoo'):
                    key = 'http://axschema.org/contact/email'
                    if email is None:
                        email = request.openid.ax.get(key)[-1]
                else:
                    try:
                        if email is None:
                            email = request.openid.ax.get('email')
                    except KeyError:
                        pass

                    try:
                        nickname = request.openid.ax.get('nickname')
                    except KeyError:
                        pass

            if nickname is None :
                if email:
                    nickname = email.split('@')[0]
                else:
                    nickname =  ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(10)])
            if email is None:
                valid_username = False
                email =  None #'%s@example.openid.com'%(nickname)
            else:
                valid_username = True
            existing_users = User.objects.filter(username=nickname).count()
            if existing_users > 0:
                index = 0
                username = '%s%s'%(nickname, index)
                while existing_users > 0:
                    username = '%s%s'%(nickname, index)
                    existing_users = User.objects.filter(username=username).count()
                    index += 1
                user = User.objects.create_user(username, email)
            else:
                user = User.objects.create_user(nickname, email)
            user.save()

            #create openid association
            assoc = UserAssociation()
            assoc.openid_key = openid_key
            assoc.user = user#AuthUser.objects.get(pk=user.pk)
            if email:
                assoc.email = email
            if nickname:
                assoc.nickname = nickname
            if valid_username:
                assoc.is_username_valid = True
            assoc.save()

            #Create AuthMeta
            auth_meta = AuthMeta(user = user, provider = provider)
            auth_meta.save()
            return user

    @staticmethod
    def _lookup_association(openid_key, request, provider):
        if provider == 'Google':
            return OpenIdBackend._lookup_gmail_assocation(openid_key, request,
                                                 provider)
        else:
            return UserAssociation.objects.get(openid_key = openid_key)

    @staticmethod
    def _lookup_gmail_assocation(openid_key, request, provider):
        email = request.openid.ax.get('http://axschema.org/contact/email')[-1]
        try:
            rv = UserAssociation.objects.filter(email=email)[0]
        except IndexError:
            raise UserAssociation.DoesNotExist()
        if rv.openid_key != openid_key:
            logger.error("Gmail OpenID key different for user", extra={
                'email': email,
                'original OpenID key': rv.openid_key,
                'new OpenID key': openid_key,
            })
        return rv

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk = user_id)
            return user
        except User.DoesNotExist:
            return None

