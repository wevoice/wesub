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
Team Resource
^^^^^^^^^^^^^

Get a list of teams
+++++++++++++++++++

.. http:get:: /api2/partners/teams/

    :>json name: Name of the team
    :>json slug: Machine name for the team slug (used in URLs)
    :>json description: Team description
    :>json is_visible: Should this team's videos be publicly visible?
    :>json membership_policy: See below for possible values
    :>json video_policy: See below for possible values

Get a list of teams
+++++++++++++++++++
.. http:get:: /api2/partners/teams/[team-slug]/

    Returns one entry from the team list resource data.

Updating a team
+++++++++++++++

.. http:put:: /api2/partners/teams/[team-slug]:

    :<json name: (required) Name of the team
    :<json slug: (required) Manchine name for the team (used in URLs)
    :<json description: Team description
    :<json is_visible: Should this team be publicly visible?
    :<json membership_policy: See below for possible values
    :<json video_policy: See below for possible values

Policy values
+++++++++++++

Membership policy:

* ``Open``
* ``Application``
* ``Invitation by any team member``
* ``Invitation by manager``
* ``Invitation by admin``

Video policy:

* ``Any team member``
* ``Managers and admins``
* ``Admins only``

Team Member Resource
^^^^^^^^^^^^^^^^^^^^

Get info on a team member
+++++++++++++++++++++++++

.. http:get:: /api2/partners/teams/[team-slug]/members/[username]

    :<json username: username
    :<json role: One of: ``owner``, ``admin``, ``manager``, or ``contributor``

Litsing all team members
++++++++++++++++++++++++

.. http:get:: /api2/partners/teams/[team-slug]/members/

    Returns a list of team member data.  Each item is the same as above.

Add a new member to a team
++++++++++++++++++++++++++

.. http:post:: /api2/partners/teams/[team-slug]/members/

    :>json username: username of the user to add
    :>json role: One of: ``owner``, ``admin``, ``manager``, or ``contributor``


Change a team member's role
+++++++++++++++++++++++++++

.. http:put:: /api2/partners/teams/[team-slug]/members/[username]/

    :>json role: One of: ``owner``, ``admin``, ``manager``, or ``contributor``

Removing a user from a team
+++++++++++++++++++++++++++

.. http:delete:: /api2/partners/teams/[team-slug]/members/[username]/

Safe Team Member Resource
^^^^^^^^^^^^^^^^^^^^^^^^^

This resource behaves the same as the normal Team Member resource except with
couple differences for the POST action to add members

* An invitation is sent to the user to join the team instead of simply adding
  them
* If no user exists with the username, and an ``email`` field is included in
  the POST data, we will create a user and send an email to the email account.
"""

from __future__ import absolute_import
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework import viewsets

from api.pagination import AmaraPaginationMixin
from auth.models import CustomUser as User
from teams.models import Team, TeamMember
import teams.permissions as team_permissions

class MappedChoiceField(serializers.ChoiceField):
    """Choice field that maps internal values to choices."""

    default_error_messages = {
        'unknown-choice': "Unknown choice: {choice}",
    }

    def __init__(self, choices, *args, **kwargs):
        self.map = dict((value, choice) for value, choice in choices)
        self.rmap = dict((choice, value) for value, choice in choices)
        super(MappedChoiceField, self).__init__(self.rmap.keys(), *args,
                                                **kwargs)

    def to_internal_value(self, choice):
        try:
            return self.rmap[choice]
        except KeyError:
            self.fail('unknown-choice', choice=choice)

    def to_representation(self, value):
        return self.map[value]

class TeamSerializer(serializers.ModelSerializer):
    # Handle mapping internal values for membership/video policy to the values
    # we use in the api (currently the english display name)
    MEMBERSHIP_POLICY_CHOICES = (
        (Team.OPEN, u'Open'),
        (Team.APPLICATION, u'Application'),
        (Team.INVITATION_BY_ALL, u'Invitation by any team member'),
        (Team.INVITATION_BY_MANAGER, u'Invitation by manager'),
        (Team.INVITATION_BY_ADMIN, u'Invitation by admin'),
    )
    VIDEO_POLICY_CHOICES = (
        (Team.VP_MEMBER, u'Any team member'),
        (Team.VP_MANAGER, u'Managers and admins'),
        (Team.VP_ADMIN, u'Admins only'),
    )
    membership_policy = MappedChoiceField(
        MEMBERSHIP_POLICY_CHOICES, required=False,
        default=Team._meta.get_field('membership_policy').get_default())
    video_policy = MappedChoiceField(
        VIDEO_POLICY_CHOICES, required=False,
        default=Team._meta.get_field('video_policy').get_default())

    class Meta:
        model = Team
        fields = ('name', 'slug', 'description', 'is_visible',
                  'membership_policy', 'video_policy')

class TeamUpdateSerializer(TeamSerializer):
    name = serializers.CharField(required=False)
    slug = serializers.SlugField(required=False)

class TeamViewSet(AmaraPaginationMixin, viewsets.ModelViewSet):
    lookup_field = 'slug'
    paginate_by = 20

    def get_queryset(self):
        return Team.objects.for_user(self.request.user)

    def get_serializer_class(self):
        if 'slug' in self.kwargs:
            return TeamUpdateSerializer
        else:
            return TeamSerializer

    def perform_create(self, serializer):
        if not team_permissions.can_create_team(self.request.user):
            raise PermissionDenied()
        serializer.save()

    def perform_update(self, serializer):
        if not team_permissions.can_change_team_settings(serializer.instance,
                                                         self.request.user):
            raise PermissionDenied()
        serializer.save()

    def perform_destroy(self, instance):
        if not team_permissions.can_delete_team(instance, self.request.user):
            raise PermissionDenied()
        instance.delete()

class TeamMemberSerializer(serializers.Serializer):
    default_error_messages = {
        'user-does-not-exist': "User does not exist: {username}",
        'user-already-member': "User is already a team member",
    }

    ROLE_CHOICES = (
         TeamMember.ROLE_OWNER,
         TeamMember.ROLE_ADMIN,
         TeamMember.ROLE_MANAGER,
         TeamMember.ROLE_CONTRIBUTOR,
    )

    username = serializers.CharField(source='user.username')
    role = serializers.ChoiceField(ROLE_CHOICES)

    def validate_username(self, username):
        try:
            self.user = User.objects.get(username=username)
            return username
        except User.DoesNotExist:
            self.fail('user-does-not-exist', username=username)

    def create(self, validated_data):
        try:
            return self.context['team'].members.create(
                user=self.user,
                role=validated_data['role'],
            )
        except IntegrityError:
            self.fail('user-already-member')

class TeamMemberUpdateSerializer(TeamMemberSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    def update(self, instance, validated_data):
        instance.role = validated_data['role']
        instance.save()
        return instance

class TeamMemberViewSet(viewsets.ModelViewSet):
    lookup_field = 'username'

    def initial(self, request, *args, **kwargs):
        super(TeamMemberViewSet, self).initial(request, *args, **kwargs)
        self.team = get_object_or_404(Team, slug=kwargs['team_slug'])

    def get_serializer_class(self):
        if 'username' in self.kwargs:
            return TeamMemberUpdateSerializer
        else:
            return TeamMemberSerializer

    def get_serializer_context(self):
        return {
            'team': self.team,
        }

    def get_queryset(self):
        if not self.team.user_is_member(self.request.user):
            raise PermissionDenied()
        return self.team.members.all()

    def get_object(self):
        if not self.team.user_is_member(self.request.user):
            raise PermissionDenied()
        member = get_object_or_404(self.team.members,
                                   user__username=self.kwargs['username'])
        return member

    def perform_create(self, serializer):
        if not team_permissions.can_add_member(self.team, self.request.user):
            raise PermissionDenied()
        serializer.save()

    def perform_update(self, serializer):
        if not team_permissions.can_assign_role(
            self.team, self.request.user, serializer.validated_data['role'],
            serializer.instance.user):
            raise PermissionDenied()
        serializer.save()

    def perform_destroy(self, member):
        if not team_permissions.can_remove_member(self.team,
                                                  self.request.user):
            raise PermissionDenied()
        if member.role == TeamMember.ROLE_OWNER:
            raise serializers.ValidationError("Can't remove team owner")
        member.delete()
