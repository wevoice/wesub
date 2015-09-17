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

from django import forms

from utils.text import fmt

class TeamMemberInput(forms.CharField):
    """Input to select team members.  """

    def set_team(self, team):
        """Set the team to find members for.

        This must be called during form initialization
        """
        self.team = team

    def clean(self, value):
        try:
            team = self.team
        except AttributeError:
            raise AssertionError("team not set")

        try:
            members_qs = team.members.all().select_related('user')
            return members_qs.get(user__username=value)
        except TeamMember.DoesNotExist:
            raise forms.ValidationError(fmt(
                _(u'%(username)s is not a member of the team'),
                username=value))
