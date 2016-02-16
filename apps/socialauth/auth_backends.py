from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from socialauth.models import OpenidProfile as UserAssociation, AuthMeta

import random

class CustomUserBackend(ModelBackend):

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

class OpenIdBackend:
    def authenticate(self, openid_key, request, provider, email=None):
        try:
            assoc = UserAssociation.objects.get(openid_key = openid_key)
            user = User.objects.get(pk=assoc.user.pk)
            if user.is_active:
                return user
            else:
                return
        except (UserAssociation.DoesNotExist, User.DoesNotExist):
            #fetch if openid provider provides any simple registration fields
            nickname = None
            if request.openid and request.openid.sreg:
                if email is None:
                    email = request.openid.sreg.get('email')
                nickname = request.openid.sreg.get('nickname')
            elif request.openid and request.openid.ax:
                if email is None:
                    email = request.openid.ax.get('email')
                nickname = request.openid.ax.get('nickname')
            if nickname is None :
                nickname =  ''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(10)])
            if email is None:
                valid_username = False
                email =  '%s@%s.%s.com'%(nickname, provider, settings.SITE_NAME)
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
            assoc.user = user
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

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk = user_id)
            return user
        except User.DoesNotExist:
            return None

