from __future__ import absolute_import

from django.test import TestCase

from auth.models import CustomUser as User
from teams.models import Team, TeamMember
from teams.forms import CreateTeamForm

class BaseMembershipTests(TestCase):
    def setUp(self):
        self.auth = dict(username='admin', password='admin')
        self.user = User.objects.all()[0]

class MembershipTests(BaseMembershipTests):
    def _login(self):
        self.client.login(**self.auth)

    def test_new_team_has_owner(self):
        f = CreateTeamForm(
            self.user,
            dict(
            name="arthur",
            slug="arthur",
            membership_policy=1,
            video_policy=1,
        ))
        t = f.save(self.user)
        self.assertEqual(
            t.members.get(user=self.user).role,
            TeamMember.ROLE_OWNER,
            "New teams should always be created by their owner")
