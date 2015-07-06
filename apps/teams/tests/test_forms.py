# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
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

from __future__ import absolute_import

from django.test import TestCase
from nose.tools import *

from teams import forms
from teams.permissions import *
from utils.factories import *
from utils.test_utils import patch_for_test, reload_obj

class EditMemberFormTest(TestCase):
    @patch_for_test('teams.permissions.get_edit_member_permissions')
    def setUp(self, mock_permission_check):
        self.mock_permission_check = mock_permission_check
        self.mock_permission_check.return_value = EDIT_MEMBER_ALL_PERMITTED
        self.team = TeamFactory()
        self.member = TeamMemberFactory(team=self.team)
        self.contributor = TeamMemberFactory(team=self.team,
                                             role=ROLE_CONTRIBUTOR)
        self.manager = TeamMemberFactory(team=self.team,
                                         role=ROLE_MANAGER)
        self.admin = TeamMemberFactory(team=self.team,
                                       role=ROLE_ADMIN)
        self.owner = TeamMemberFactory(team=self.team,
                                       role=ROLE_OWNER)

    def make_form(self, data=None):
        return forms.EditMembershipForm(self.member, data=data)

    def check_choices(self, form, member_choices, role_choices):
        assert_equal(
            [c[0] for c in form.fields['member'].choices],
            [m.id for m in member_choices]
        )
        assert_equal(
            [c[0] for c in form.fields['role'].choices],
            role_choices
        )
        assert_items_equal(form.editable_member_ids,
                           [m.id for m in member_choices])


    def test_all_permitted(self):
        form = self.make_form()
        self.check_choices(
            form,
            [ self.contributor, self.manager, self.admin, self.owner, ],
            [ ROLE_CONTRIBUTOR, ROLE_MANAGER, ROLE_ADMIN, ],
        )

        assert_true('remove' in form.fields)

    def test_cant_edit_admin(self):
        self.mock_permission_check.return_value = EDIT_MEMBER_CANT_EDIT_ADMIN
        form = self.make_form()
        self.check_choices(
            form,
            [ self.contributor, self.manager, ],
            [ ROLE_CONTRIBUTOR, ROLE_MANAGER, ],
        )
        assert_true('remove' in form.fields)

    def test_not_pemitted(self):
        self.mock_permission_check.return_value = EDIT_MEMBER_NOT_PERMITTED
        form = self.make_form()
        self.check_choices(form, [], [])
        assert_false('remove' in form.fields)

    def test_update_role(self):
        form = self.make_form(data={
            'member': self.contributor.id,
            'role': ROLE_MANAGER,
        })
        assert_true(form.is_valid())
        form.save()
        assert_equal(reload_obj(self.contributor).role, ROLE_MANAGER)

    def test_remove(self):
        form = self.make_form(data={
            'member': self.contributor.id,
            'role': ROLE_MANAGER,
            'remove': 1,
        })
        assert_true(form.is_valid())
        form.save()
        assert_false(
            TeamMember.objects.filter(id=self.contributor.id).exists()
        )
