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

from __future__ import absolute_import
import re

from django.contrib.auth.hashers import make_password
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
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
    is_partner = serializers.BooleanField(required=False, read_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'full_name', 'first_name', 'last_name', 'biography',
            'homepage', 'avatar', 'languages', 'num_videos', 'resource_uri',
            'created_by', 'is_partner',
        )

    default_error_messages = {
        'invalid-username': 'Invalid Username: {username}',
    }

    valid_username_re = re.compile(r'[\w\-@\.\+]+$')
    def validate_username(self, username):
        if not self.valid_username_re.match(username):
            self.fail('invalid-username',
                      username=username.encode('ascii', 'replace'))
        return username

    def to_representation(self, user):
        data = super(UserSerializer, self).to_representation(user)
        if hasattr(self, 'login_token'):
            data['auto_login_url'] = reverse(
                "auth:token-login", args=(self.login_token.token,),
                request=self.context['request'])
        return data

class PasswordField(serializers.CharField):
    def to_internal_value(self, password):
        return make_password(password)

class UserCreateSerializer(UserSerializer):
    username = serializers.CharField(max_length=30)
    password = PasswordField(required=False, write_only=True)
    api_key = serializers.CharField(source='api_key.key', read_only=True)
    create_login_token = serializers.BooleanField(write_only=True,
                                                  required=False)
    find_unique_username = serializers.BooleanField(write_only=True,
                                                    required=False)

    default_error_messages = {
        'username-not-unique': 'Username not unique: {username}',
        'username-too-long': 'Username too long: {username}',
    }

    def __init__(self, *args, **kwargs):
        super(UserCreateSerializer, self).__init__(*args, **kwargs)
        if self.context['request'].user.is_partner:
            self.fields['is_partner'].read_only = False

    def validate(self, data):
        if data.get('find_unique_username'):
            # if we need to find a unique username, then we should stricter
            # limit on the username length
            if len(data['username']) > 24:
                self.fail('username-too-long', username=data['username'])
        return data

    def create(self, validated_data):
        find_unique_username = validated_data.pop('find_unique_username',
                                                  False)
        create_login_token = validated_data.pop('create_login_token', False)
        try:
            if find_unique_username:
                user = User.objects.create_with_unique_username(
                    created_by=self.context['request'].user, **validated_data)
            else:
                user = User.objects.create(
                    created_by=self.context['request'].user, **validated_data)
        except IntegrityError, e:
            self.fail('username-not-unique',
                      username=validated_data['username'])
        user.ensure_api_key_created()
        if create_login_token:
            self.login_token = LoginToken.objects.for_user(user)
        return user

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'email', 'api_key', 'password', 'create_login_token',
            'find_unique_username',
        )

class UserUpdateSerializer(UserSerializer):
    username = serializers.CharField(read_only=True)
    password = PasswordField(required=False, write_only=True)
    api_key = serializers.CharField(source='api_key.key', read_only=True)

    def update(self, user, validated_data):
        if user != self.context['request'].user:
            raise PermissionDenied()
        return super(UserSerializer, self).update(user, validated_data)

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + (
            'email', 'api_key', 'password',
        )

class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    """
    API endpoint for user data.

    # Fetching #

    ## `GET /api/users/[username]/`

    ### Fields:

    - **username:** username
    - **first_name:** First name
    - **last_name:** Last name
    - **homepage:** Homepage URL
    - **biography:** Bio text
    - **num_videos:** Number of videos followed by the user
    - **languages:** List of languages the user speaks
    - **avatar:** URL to the user's avatar image
    - **resource_uri:** User API URI
    - **full_name:** Full name of the user.

    ### Notes:

    - Many of these fields will be blank if the user hasn't set them from
    their profile page

    - The ``full_name`` field is not used in the amara interface and there is
    no requirement that it needs to be first_name + last_name.  This field is
    for API consumers that want to create users to match their internal users
    and use the full names internally instead of first + last.

    # Creating/Updating #

    ## `POST /api/users/`

    ### Fields:

    - **username:** username.  30 chars or fewer alphanumeric chars, @, _ and
      are accepted.
    - **email:** A valid email address
    - **password:** any number of chars, all chars allowed.
    - **first_name:** Any chars, max 30 chars. Optional.
    - **last_name:** Any chars, max 30 chars. Optional.
    - **create_login_token:** *optional*, if sent the response will also
      include a url that when visited will login the created user.  Use this to
      allow users to login without explicitly setting their passwords.  This URL
      expires in 2 hours
    - **find_unique_username:** *optional*, if username is taken, we will find
      a similar, unused, username for the new user.  If passed, make sure you
      check the username returned since it might not be the same one that you
      passed in.  If set, usernames can only be a maximum of 24 characters to
      make room for potential extra characters.
    - **username:** username
    - **first_name:** First name
    - **last_name:** Last name
    - **homepage:** Homepage URL
    - **biography:** Bio text
    - **num_videos:** Number of videos created by the user
    - **languages:** List of languages the user speaks
    - **avatar:** URL to the user's avatar image
    - **resource_uri:** User API URI
    - **email:** User's email
    - **api_key:** User API Key
    - **full_name:** Full name

    **Note:** This response includes the ``email`` and ``api_key``, which
    aren't included in the normal GET response.  If clients wish to make
    requests on behalf of this newly created user through the api, they must
    hold on to this key.

    ## `PUT /api/users/[username]`

    Use PUT to update your account.

    - ``username`` must match the username of the auth credentials sent.
    - PUT inputs the same fields as POST, except `username`,
    `create_login_token`, and `find_unique_username`.
    """

    queryset = User.objects.all().select_related('created_by')
    lookup_field = 'username'
    lookup_value_regex = r'[\w\-@\.\+\s]+'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        elif self.request.method == 'POST':
            return UserCreateSerializer
        elif self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        else:
            raise ValueError("Invalid request method: {}".format(
                self.request.method))
