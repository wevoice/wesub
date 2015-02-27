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

import json
import urllib
import urlparse

from django.conf import settings
from django.test import TestCase
from nose.tools import *
import mock
import jwt

from utils.test_utils import *
from externalsites import google

class TestRequestTokenURL(TestCase):
    def test_online_access(self):
        redirect_uri = 'http://example.com/my-callback'
        state = {'foo': 'bar', 'baz': 3}

        correct_params = {
            "client_id": settings.YOUTUBE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "openid scope1 scope2",
            "state": json.dumps(state),
            "response_type": "code",
            "openid.realm": 'http://example.com/',
            "access_type": "online",
            "approval_prompt": "force",
        }
        token_url = urlparse.urlparse(google.request_token_url(
            redirect_uri, "online", state, ['scope1', 'scope2']
        ))
        assert_equal(token_url.scheme, 'https')
        assert_equal(token_url.netloc, 'accounts.google.com')
        assert_equal(token_url.path, '/o/oauth2/auth')
        assert_equal(urlparse.parse_qs(token_url.query), {
            "client_id": [settings.YOUTUBE_CLIENT_ID],
            "redirect_uri": [redirect_uri],
            "scope": ["openid scope1 scope2"],
            "state": [json.dumps(state)],
            "response_type": ["code"],
            "access_type": ["online"],
            "openid.realm": ['http://example.com/'],
        })

    def test_offline_access(self):
        redirect_uri = 'http://example.com/my-callback'
        state = {'foo': 'bar', 'baz': 3}
        token_url = urlparse.urlparse(google.request_token_url(
            redirect_uri, "offline", state, ['scope1', 'scope2']
        ))
        assert_equal(token_url.scheme, 'https')
        assert_equal(token_url.netloc, 'accounts.google.com')
        assert_equal(token_url.path, '/o/oauth2/auth')
        assert_equal(urlparse.parse_qs(token_url.query), {
            "client_id": [settings.YOUTUBE_CLIENT_ID],
            "redirect_uri": [redirect_uri],
            "scope": ["openid scope1 scope2"],
            "state": [json.dumps(state)],
            "response_type": ["code"],
            "openid.realm": ['http://example.com/'],
            "access_type": ["offline"],
            # I think approval_prompt is required when access_type==offline
            "approval_prompt": ["force"],
        })

class OauthTokenMocker(RequestsMocker):
    redirect_uri = 'http://example.com/my-callback'
    access_token = 'test-access_token'
    openid_id = 'test-openid-id'
    sub = '12345'

    def expect_token_request(self, response_data=None, status_code=200,
                             refresh_token=None):
        if response_data is None:
            response_data = {
                'access_token': self.access_token,
                'id_token': jwt.encode({
                    'openid_id': self.openid_id,
                    'sub': self.sub,
                }, 'test-secret'),
            }
            if refresh_token:
                response_data['refresh_token'] = refresh_token
        self.expect_request(
            'post', "https://accounts.google.com/o/oauth2/token",
            data={
                'client_id': settings.YOUTUBE_CLIENT_ID,
                'client_secret': settings.YOUTUBE_CLIENT_SECRET,
                'code': 'test-authorization-code',
                'grant_type': 'authorization_code',
                'redirect_uri': self.redirect_uri,
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            },
            status_code=status_code,
            body=json.dumps(response_data),
        )

class OAuthCallbackTest(TestCase):
    test_state = {'foo': 'test-state'}

    def make_mock_callback_request(self):
        return mock.Mock(GET={
            'code': 'test-authorization-code',
            'state': json.dumps(self.test_state)
        })

    def test_callback(self):
        mocker = OauthTokenMocker()
        mocker.expect_token_request()
        with mocker:
            auth_info = google.handle_callback(
                self.make_mock_callback_request(),
                mocker.redirect_uri)
        self.assertEqual(auth_info.access_token, mocker.access_token)
        self.assertEqual(auth_info.refresh_token, None)
        self.assertEqual(auth_info.openid_id, mocker.openid_id)
        self.assertEqual(auth_info.sub, mocker.sub)
        self.assertEqual(auth_info.state, self.test_state)

    def test_callback_for_offline_access(self):
        mocker = OauthTokenMocker()
        mocker.expect_token_request(refresh_token='test-refresh-token')
        with mocker:
            auth_info = google.handle_callback(
                self.make_mock_callback_request(),
                mocker.redirect_uri)
        self.assertEqual(auth_info.refresh_token, 'test-refresh-token')

    def test_callback_error(self):
        mocker = OauthTokenMocker()
        mocker.expect_token_request(response_data={'error': 'test-error' })
        with mocker:
            with assert_raises(google.OAuthError):
                google.handle_callback(
                    self.make_mock_callback_request(),
                    mocker.redirect_uri)

    def test_callback_status_code_error(self):
        mocker = OauthTokenMocker()
        mocker.expect_token_request(status_code=400)
        with mocker:
            with assert_raises(google.OAuthError):
                google.handle_callback(
                    self.make_mock_callback_request(),
                    mocker.redirect_uri)

class AccessTokenTest(TestCase):
    def test_get_new_access_token(self):
        mocker = RequestsMocker()
        mocker.expect_request(
            'post', "https://accounts.google.com/o/oauth2/token", data={
                'client_id': settings.YOUTUBE_CLIENT_ID,
                'client_secret': settings.YOUTUBE_CLIENT_SECRET,
                'grant_type': 'refresh_token',
                'refresh_token': 'test-refresh-token',
            }, headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }, body=json.dumps({
                'access_token': 'test-access-token',
            }),
        )
        google.get_new_access_token.run_original_for_test()
        with mocker:
            access_token = google.get_new_access_token(
                'test-refresh-token')
        self.assertEqual(access_token, 'test-access-token')

    def test_get_new_access_token_error(self):
        mocker = RequestsMocker()
        mocker.expect_request(
            'post', "https://accounts.google.com/o/oauth2/token", data={
                'client_id': settings.YOUTUBE_CLIENT_ID,
                'client_secret': settings.YOUTUBE_CLIENT_SECRET,
                'grant_type': 'refresh_token',
                'refresh_token': 'test-refresh-token',
            }, headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }, body=json.dumps({
                'error': 'test-error',
            }),
        )
        google.get_new_access_token.run_original_for_test()
        with mocker:
            self.assertRaises(google.OAuthError,
                              google.get_new_access_token,
                              'test-refresh-token')

    def test_revoke_auth_token(self):
        mocker = RequestsMocker()
        mocker.expect_request(
            'get', 'https://accounts.google.com/o/oauth2/revoke',
            params={'token': 'test-token'})
        google.revoke_auth_token.run_original_for_test()
        with mocker:
            google.revoke_auth_token('test-token')
