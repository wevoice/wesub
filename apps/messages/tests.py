# -*- coding: utf-8 -*-
# Universal Subtitles, universalsubtitles.org
#
# Copyright (C) 2010 Participatory Culture Foundation
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

from django.test import TestCase
from apps.auth.models import CustomUser as User
from apps.auth.models import EmailConfirmation
from django.core import mail

from apps.messages.models import Message
from apps.messages import tasks as notifier
from teams.models import Team, TeamMember, Application
from videos.models import Action
from utils import send_templated_email

class MessageTest(TestCase):

    def setUp(self):
        self.author = User.objects.all()[:1].get()
        self.subject = "Let's talk"
        self.body = "Will you please help me out with Portuguese trans?"
        self.user = User.objects.exclude(pk=self.author.pk)[:1].get()

    def _create_message(self, to_user):
        self.message = Message(user=to_user,
                           author=self.author,
                           subject=self.subject,
                          content=self.body)
        self.message.save()

    def _send_email(self, to_user):
        send_templated_email(to_user, "test email", "messages/email/email_confirmed.html", {})

    def test_send_email_to_allowed_user(self):
        self.user.notify_by_email = True
        self.user.save()
        assert self.user.is_active and self.user.email
        
        self._send_email(self.user)
        self.assertEqual(len(mail.outbox), 1)

    def test_send_email_to_optout_user(self):
        self.user.notify_by_email = False
        self.user.save()
        assert self.user.is_active and self.user.email
                
        self._send_email(self.user)
        self.assertEquals(len(mail.outbox), 0)

    def test_message_to_optout_user(self):
        self.user.notify_by_message = False
        self.user.notify_by_email = False
        self.user.save()
        self._send_email(self.user)
        self._create_message(self.user)
        self.assertEquals(len(mail.outbox), 0)
        self.assertEquals(Message.objects.unread().filter(user=self.user).count(), 0)
        self.assertEquals(Message.objects.filter(user=self.user).count(), 1)
        
    def test_member_join(self):
        def _get_counts(member):
            email_to = "%s <%s>" %(member.user.username, member.user.email) 
            return Message.objects.filter(user=member.user).count() , \
                len([x for x in mail.outbox if email_to in x.recipients()])
            
        
        team , created= Team.objects.get_or_create(name='test', slug='test')
        
        # creates dummy users:
        for x in xrange(0,5):
            user, member = User.objects.get_or_create(
                username="test%s" % x,
                email = "test%s@example.com" % x,
            )
            tm = TeamMember(team=team, user=user)
            if x == 0:
                tm.role = TeamMember.ROLE_OWNER
                owner = tm
            elif x == 1:
                tm.role = TeamMember.ROLE_ADMIN
                admin = tm
            elif x == 2:
                tm.role = TeamMember.ROLE_MANAGER
                manager = tm
            elif x == 3:
                tm.role = TeamMember.ROLE_CONTRIBUTOR
                contributor = tm
            if x < 4:
                # don't save the last role until we have counts
                tm.save()
            else:
                tm.role= TeamMember.ROLE_CONTRIBUTOR
            
        # now make sure we count previsou messages
        owner_messge_count_1, owner_email_count_1 = _get_counts(owner)
        admin_messge_count_1, admin_email_count_1 = _get_counts(admin)
        manager_messge_count_1, manager_email_count_1 = _get_counts(manager)
        contributor_messge_count_1, contributor_email_count_1 = _get_counts(contributor)
        # save the last team member and check that each group has appropriate counts 
        tm.save()
        # owner and admins should receive email + message
        owner_messge_count_2, owner_email_count_2 = _get_counts(owner)
        self.assertEqual(owner_messge_count_1 + 1, owner_messge_count_2)
        self.assertEqual(owner_email_count_1 + 1, owner_email_count_2)
        admin_messge_count_2, admin_email_count_2 = _get_counts(admin)
        self.assertEqual(admin_messge_count_1 + 1, admin_messge_count_2)
        self.assertEqual(admin_email_count_1 + 1, admin_email_count_2)
        # manager shoud not
        manager_messge_count_2, manager_email_count_2 = _get_counts(manager)
        self.assertEqual(manager_messge_count_1 , manager_messge_count_2)
        self.assertEqual(manager_email_count_1 , manager_email_count_2)
        # contributor shoud not
        contributor_messge_count_2, contributor_email_count_2 = _get_counts(contributor)
        self.assertEqual(contributor_messge_count_1 , contributor_messge_count_2)
        self.assertEqual(contributor_email_count_1 , contributor_email_count_2)


        # now, this has to show up on everybody activitis fed
        action = Action.objects.get(team=team, user=tm.user, action_type=Action.MEMBER_JOINED)
        self.assertTrue(Action.objects.for_user(tm.user).filter(pk=action.pk).exists())
        self.assertTrue(Action.objects.for_user(owner.user).filter(pk=action.pk).exists())
        self.assertTrue(Action.objects.for_user(manager.user).filter(pk=action.pk).exists())
        self.assertTrue(Action.objects.for_user(contributor.user).filter(pk=action.pk).exists())
        self.assertTrue(Action.objects.for_user(admin.user).filter(pk=action.pk).exists())
        
    def test_member_leave(self):
        def _get_counts(member):
            email_to = "%s <%s>" %(member.user.username, member.user.email) 
            return Message.objects.filter(user=member.user).count() , \
                len([x for x in mail.outbox if email_to in x.recipients()])
            
        
        team , created= Team.objects.get_or_create(name='test', slug='test')
        
        # creates dummy users:
        for x in xrange(0,5):
            user, member = User.objects.get_or_create(
                username="test%s" % x,
                email = "test%s@example.com" % x,
                notify_by_email = True,
            )
            tm = TeamMember(team=team, user=user)
            if x == 0:
                tm.role = TeamMember.ROLE_OWNER
                owner = tm
            elif x == 1:
                tm.role = TeamMember.ROLE_ADMIN
                admin = tm
            elif x == 2:
                tm.role = TeamMember.ROLE_MANAGER
                manager = tm
            elif x == 3:
                tm.role = TeamMember.ROLE_CONTRIBUTOR
                contributor = tm
            if x < 4:
                # don't save the last role until we have counts
                tm.save()
            else:
                tm.role= TeamMember.ROLE_CONTRIBUTOR
            
        tm.save()
        # now make sure we count previsou messages
        owner_messge_count_1, owner_email_count_1 = _get_counts(owner)
        admin_messge_count_1, admin_email_count_1 = _get_counts(admin)
        manager_messge_count_1, manager_email_count_1 = _get_counts(manager)
        contributor_messge_count_1, contributor_email_count_1 = _get_counts(contributor)

        # now delete and check numers
        
        tm_user = tm.user
        tm_user_pk = tm.user.pk
        team_pk = tm.team.pk
        tm.delete()
        notifier.team_member_leave(team_pk, tm_user_pk)
        # save the last team member and check that each group has appropriate counts 
        # owner and admins should receive email + message
        owner_messge_count_2, owner_email_count_2 = _get_counts(owner)
        self.assertEqual(owner_messge_count_1 + 1, owner_messge_count_2)
        self.assertEqual(owner_email_count_1 + 1, owner_email_count_2)
        admin_messge_count_2, admin_email_count_2 = _get_counts(admin)
        self.assertEqual(admin_messge_count_1 + 1, admin_messge_count_2)
        self.assertEqual(admin_email_count_1 + 1, admin_email_count_2)
        # manager shoud not
        manager_messge_count_2, manager_email_count_2 = _get_counts(manager)
        self.assertEqual(manager_messge_count_1 , manager_messge_count_2)
        self.assertEqual(manager_email_count_1 , manager_email_count_2)
        # contributor shoud not
        contributor_messge_count_2, contributor_email_count_2 = _get_counts(contributor)
        self.assertEqual(contributor_messge_count_1 , contributor_messge_count_2)
        self.assertEqual(contributor_email_count_1 , contributor_email_count_2)


        # now, this has to show up on everybody activitis fed
        action = Action.objects.get(team=team, user=tm_user, action_type=Action.MEMBER_LEFT)
        self.assertTrue(Action.objects.for_user(tm.user).filter(pk=action.pk).exists())
        self.assertTrue(Action.objects.for_user(owner.user).filter(pk=action.pk).exists())
        self.assertTrue(Action.objects.for_user(manager.user).filter(pk=action.pk).exists())
        self.assertTrue(Action.objects.for_user(contributor.user).filter(pk=action.pk).exists())
        self.assertTrue(Action.objects.for_user(admin.user).filter(pk=action.pk).exists())
        
    def test_application_new(self):
        def _get_counts(member):
            email_to = "%s <%s>" %(member.user.username, member.user.email) 
            return Message.objects.filter(user=member.user).count() , \
                len([x for x in mail.outbox if email_to in x.recipients()])
            
        
        team , created= Team.objects.get_or_create(name='test', slug='test')
        applying_user = User.objects.all()[0]
        # creates dummy users:
        for x in xrange(0,4):
            user, member = User.objects.get_or_create(
                username="test%s" % x,
                email = "test%s@example.com" % x,
                notify_by_email = True,
            )
            tm = TeamMember(team=team, user=user)
            if x == 0:
                tm.role = TeamMember.ROLE_OWNER
                owner = tm
            elif x == 1:
                tm.role = TeamMember.ROLE_ADMIN
                admin = tm
            elif x == 2:
                tm.role = TeamMember.ROLE_MANAGER
                manager = tm
            elif x == 3:
                tm.role = TeamMember.ROLE_CONTRIBUTOR
                contributor = tm
            tm.save()
            
        # now make sure we count previsou messages
        owner_messge_count_1, owner_email_count_1 = _get_counts(owner)
        admin_messge_count_1, admin_email_count_1 = _get_counts(admin)
        manager_messge_count_1, manager_email_count_1 = _get_counts(manager)
        contributor_messge_count_1, contributor_email_count_1 = _get_counts(contributor)

        # now delete and check numers
        Application.objects.create(team=team,user=applying_user)
        # owner and admins should receive email + message
        owner_messge_count_2, owner_email_count_2 = _get_counts(owner)
        print [x.subject for x in Message.objects.filter(user=owner.user)]
        self.assertEqual(owner_messge_count_1 + 1, owner_messge_count_2)
        self.assertEqual(owner_email_count_1 + 1, owner_email_count_2)
        admin_messge_count_2, admin_email_count_2 = _get_counts(admin)
        self.assertEqual(admin_messge_count_1 + 1, admin_messge_count_2)
        self.assertEqual(admin_email_count_1 + 1, admin_email_count_2)
        # manager shoud not
        manager_messge_count_2, manager_email_count_2 = _get_counts(manager)
        self.assertEqual(manager_messge_count_1 , manager_messge_count_2)
        self.assertEqual(manager_email_count_1 , manager_email_count_2)
        # contributor shoud not
        contributor_messge_count_2, contributor_email_count_2 = _get_counts(contributor)
        self.assertEqual(contributor_messge_count_1 , contributor_messge_count_2)
        self.assertEqual(contributor_email_count_1 , contributor_email_count_2)


    def test_account_verified(self):
       user = User.objects.filter(
           notify_by_email=True, email__isnull=False)[0]
       c = EmailConfirmation.objects.send_confirmation(user)
       num_emails = len(mail.outbox)
       num_messages = Message.objects.filter(user=user).count()
       EmailConfirmation.objects.confirm_email(c.confirmation_key)
       self.assertEqual(num_emails +1, len(mail.outbox))
       self.assertEqual(num_messages +1,
                        Message.objects.filter(user=user).count())
