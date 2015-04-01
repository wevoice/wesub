# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.html.

"""
Users Resource
^^^^^^^^^^^^^^

Fetching user data
++++++++++++++++++

.. http:get:: /api/users/[username]/

    :>json username: username
    :>json first_name: First name
    :>json last_name: Last name
    :>json homepage: Homepage URL
    :>json biography: Bio text
    :>json num_videos: Number of videos followed by the user
    :>json languages: List of languages the user speaks
    :>json avatar: URL to the user's avatar image
    :>json resource_uri: User API URI
    :>json full_name: Full name of the user.

.. note::

    Many of these fields will be blank if the user hasn't set them from their
    profile page

.. note::

    The ``full_name`` field is not used in the amara interface and there is no
    requirement that it needs to be first_name + last_name.  This field is for
    API consumers that want to create users to match their internal users and
    use the full names internally instead of first + last.

Creating Users
++++++++++++++

.. http:post:: /api/users/

    :<json username: username.  30 chars or fewer
        alphanumeric chars, @, _ and - are accepted.
    :<json email: A valid email address
    :<json password: any number of chars, all chars allowed.
    :<json first_name: Any chars, max 30 chars. Optional.
    :<json last_name: Any chars, max 30 chars. Optional.
    :<json create_login_token: *optional*, if sent the response will also
        include a url that when visited will login the created user.  Use this
        to allow users to login without explicitly setting their passwords.
        This URL expires in 2 hours
    :>json username: username
    :>json first_name: First name
    :>json last_name: Last name
    :>json homepage: Homepage URL
    :>json biography: Bio text
    :>json num_videos: Number of videos created by the user
    :>json languages: List of languages the user speaks
    :>json avatar: URL to the user's avatar image
    :>json resource_uri: User API URI
    :>json email: User's email
    :>json api_key: User API Key
    :>json full_name: Full name

.. note::

    This response includes the ``email`` and ``api_key``, which aren't
    included in the normal GET response.  If clients wish to make requests on
    behalf of this newly created user through the api, they must hold on to
    this key.

Updating Your Account
+++++++++++++++++++++

.. http:put:: /api/users/[username]

Use PUT to update your user account.  ``username`` must match the username of
the auth credentials sent.  PUT inputs the same fields as POST, with the
exception of username.
"""

from __future__ import absolute_import
import re

from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from rest_framework import mixins
from rest_framework import serializers
from rest_framework import viewsets
from rest_framework.reverse import reverse

from auth.models import CustomUser as User, LoginToken

class UserSerializer(serializers.ModelSerializer):
    num_videos = serializers.IntegerField(source='videos.count',
                                          read_only=True)
    languages = serializers.ListField(
        child=serializers.CharField(),
        source='get_languages', read_only=True)
    resource_uri = serializers.HyperlinkedIdentityField(
        view_name='api:users-detail', lookup_field='username')
    created_by = serializers.CharField(source='created_by.username',
                                       read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'full_name', 'first_name', 'last_name', 'biography',
            'homepage', 'avatar', 'languages', 'num_videos', 'resource_uri',
            'created_by',
        )

class UserWriteSerializer(UserSerializer):
    api_key = serializers.CharField(source='api_key.key', read_only=True)
    create_login_token = serializers.BooleanField(write_only=True,
                                                  required=False)

    default_error_messages = {
        'invalid-username': 'Invalid Username: {username}',
    }

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields['username'].read_only = True

    valid_username_re = re.compile(r'[\w\-@\.\+]+$')
    def validate_username(self, username):
        if not self.valid_username_re.match(username):
            self.fail('invalid-username',
                      username=username.encode('ascii', 'replace'))
        return username

    def create(self, validated_data):
        user = User(created_by=self.context['request'].user)
        user = self._update(user, validated_data)
        user.ensure_api_key_created()
        return user

    def update(self, user, validated_data):
        if user != self.context['request'].user:
            raise PermissionDenied()
        return self._update(user, validated_data)

    def _update(self, user, validated_data):
        for key, value in validated_data.items():
            if key == 'password':
                user.set_password(value)
            else:
                setattr(user, key, value)
        user.save()
        if 'create_login_token' in validated_data:
            self.login_token = LoginToken.objects.for_user(user)
        return user

    def to_representation(self, user):
        data = super(UserWriteSerializer, self).to_representation(user)
        if hasattr(self, 'login_token'):
            data['auto_login_url'] = reverse(
                "auth:token-login", args=(self.login_token.token,),
                request=self.context['request'])
        return data

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'email', 'api_key', 'password', 'create_login_token',
        )
        extra_kwargs = {
            'password': { 'required': False, 'write_only':True },
        }

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):

    queryset = User.objects.all().select_related('created_by')
    lookup_field = 'username'
    lookup_value_regex = r'[\w\-@\.\+]+'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        elif self.request.method in ('POST', 'PUT', 'PATCH'):
            return UserWriteSerializer
        else:
            raise ValueError("Invalid request method: {}".format(
                self.request.method))
