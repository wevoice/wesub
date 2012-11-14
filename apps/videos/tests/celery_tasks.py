# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
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

import datetime

from babelsubs.storage import SubtitleSet
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import TestCase

from apps.auth.models import CustomUser as User
from apps.comments.forms import CommentForm
from apps.comments.models import Comment
from apps.messages.models import Message
from apps.videos.models import Video
from apps.subtitles.models import (
    SubtitleLanguage, SubtitleVersion
)
from apps.subtitles import pipeline

from apps.videos.tasks import video_changed_tasks, send_change_title_email, _send_notification
from apps.videos.tests import utils


class TestCeleryTasks(TestCase):
    fixtures = ['test.json', 'subtitle_fixtures.json']

    def setUp(self):
        self.user = User.objects.get(pk=2)
        self.video = Video.objects.all()[:1].get()
        self.language = self.video.subtitle_language()
        self.language.language_code = 'en'
        self.language.save()
        self.latest_version = self.language.get_tip()

        self.latest_version.author.notify_by_email = True
        self.latest_version.author.is_active = True
        self.latest_version.author.save()

        self.video.followers.clear()
        self.language.followers.add(self.latest_version.author)
        self.video.followers.add(self.latest_version.author)

    def test_send_change_title_email(self):
        user = User.objects.all()[2]

        old_title = self.video.title
        new_title = u'New title'
        self.video.title = new_title
        self.video.save()

        result = send_change_title_email.delay(self.video.id, user.id,
                                               old_title, new_title)
        if result.failed():
            self.fail(result.traceback)
        self.assertEqual(len(mail.outbox), 1)

        mail.outbox = []
        result = send_change_title_email.delay(self.video.id, None, old_title,
                                               new_title)
        if result.failed():
            self.fail(result.traceback)
        self.assertEqual(len(mail.outbox), 1)

    def test_notification_sending(self):
        """
        Make the system send updates only on the object being followed
        (language vs. video).

        The following is taken directly from the ticket
        -----------------------------------------------

        1. Followers of a video (submitter + anyone who chose to follow the
            video) should:

            * Be listed as followers for each language of this video
            * Get notifications about any changes made to the video or any of
                the related languages.
            * Get notifications about any comments left on the video or any of
                the related videos.

        2. Followers of a language (followers of language +
            transcriber(s)/translator(s) + editor(s) + anyone who chose to
            follow the language) should:

            * Get notifications about any changes made to the subtitles in
                this language, but not in any other language for the same video.
            * Get notifications about comments made on the subtitles in this
                language, but not in any other language for the video, nor on
                the video as a whole entity.
        """

        # Video is submitted by self.user (pk 2, admin@mail.net)
        # The submitter is automatically added to followers via the
        # ``Video.get_or_create_for_url`` method.  Here we do that by hand.
        self.assertEquals(0, Message.objects.count())
        self.assertEquals(0, Comment.objects.count())
        self.video.user = self.user
        self.video.user.notify_by_email = True
        self.video.user.notify_by_message = False
        self.video.user.save()
        self.video.followers.add(self.user)
        self.video.save()

        # Create a user that only follows the language
        user_language_only = User.objects.create(username='languageonly',
                email='dude@gmail.com', notify_by_email=True,
                notify_by_message=True)

        user_language2_only = User.objects.create(username='languageonly2',
                email='dude2@gmail.com', notify_by_email=True,
                notify_by_message=True)

        # Create a user that will make the edits
        user_edit_maker = User.objects.create(username='editmaker',
                email='maker@gmail.com', notify_by_email=True,
                notify_by_message=True)

        self.language.followers.clear()
        self.language.followers.add(user_language_only)
        latest_version = self.language.get_tip()
        latest_version.title = 'Old title'
        latest_version.description = 'Old description'
        latest_version.save()

        # Create another language
        lan2 = SubtitleLanguage.objects.create(video=self.video, language_code='ru')
        lan2.followers.add(user_language2_only)
        self.assertEquals(4, SubtitleLanguage.objects.count())

        subtitles = self.language.get_tip().get_subtitles()
        subtitles.append_subtitle(1500, 3000, 'new text')
        version = pipeline.add_subtitles(self.video, self.language.language_code, 
                                         subtitles, author=user_edit_maker,
                                         title="New title", description="New description")

        # Clear the box because the above generates some emails
        mail.outbox = []

        # Kick it off
        video_changed_tasks(version.video.id, version.id)

        # --------------------------------------------------------------------

        # How many emails should we have?
        # * The submitter
        # * All video followers who want emails
        # * All followers of the language being changed
        # * Minus the change author
        #
        # In our case that is: languageonly, adam, admin
        people = set(self.video.followers.filter(notify_by_email=True))
        people.update(self.language.followers.filter(notify_by_email=True))

        number = len(list(people)) - 1  # for the editor
        self.assertEqual(len(mail.outbox), number)

        email = mail.outbox[0]
        tos = [item for sublist in mail.outbox for item in sublist.to]

        self.assertTrue('New description' in email.body)
        self.assertTrue('Old description' in email.body)
        self.assertTrue('New title' in email.body)
        self.assertTrue('Old title' in email.body)

        # Make sure that all followers of the video got notified
        # Excluding the author of the new version
        excludes = list(User.objects.filter(email__in=[version.author.email]).all())
        self.assertEquals(1, len(excludes))
        followers = self.video.notification_list(excludes)
        self.assertTrue(excludes[0].notify_by_email and
                excludes[0].notify_by_message)
        self.assertTrue(followers.filter(pk=self.video.user.pk).exists())

        for follower in followers:
            self.assertTrue(follower.email in tos)

        self.assertTrue(self.user.notify_by_email)
        self.assertTrue(self.user.email in tos)

        # Refresh objects
        self.user = User.objects.get(pk=self.user.pk)
        self.video = Video.objects.get(pk=self.video.pk)

        # Messages sent?
        self.assertFalse(self.video.user.notify_by_message)
        self.assertFalse(User.objects.get(pk=self.video.user.pk).notify_by_message)
        followers = self.video.followers.filter(
                notify_by_message=True).exclude(pk__in=[e.pk for e in excludes])

        self.assertEquals(followers.count(), 1)
        self.assertNotEquals(followers[0].pk, self.user.pk)

        self.assertEquals(followers.count(), Message.objects.count())
        for follower in followers:
            self.assertTrue(Message.objects.filter(user=follower).exists())

        language_follower_email = None
        for email in mail.outbox:
            if user_language_only.email in email.to:
                language_follower_email = email
                break

        self.assertFalse(language_follower_email is None)

        # --------------------------------------------------------------------
        # Now test comment notifications

        Message.objects.all().delete()
        mail.outbox = []

        # Video comment first
        form =  CommentForm(self.video, {
            'content': 'Text',
            'object_pk': self.video.pk,
            'content_type': ContentType.objects.get_for_model(self.video).pk
            })
        form.save(self.user, commit=True)

        self.assertEquals(1, Comment.objects.count())
        self.assertEqual(len(mail.outbox), 1)

        emails = []
        for e in mail.outbox:
            for a in e.to:
                emails.append(a)

        followers = self.video.followers.filter(notify_by_email=True)
        self.assertEquals(emails.sort(), [f.email for f in followers].sort())

        followers = self.video.followers.filter(notify_by_email=False)
        for follower in followers:
            self.assertFalse(follower.email in emails)

        followers = self.video.followers.filter(notify_by_message=True)
        self.assertEquals(followers.count(), Message.objects.count())
        for message in Message.objects.all():
            self.assertTrue(isinstance(message.object, Video))
            self.assertTrue(message.user in list(followers))

        # And now test comments on languages
        Message.objects.all().delete()
        mail.outbox = []

        form =  CommentForm(self.language, {
            'content': 'Text',
            'object_pk': self.language.pk,
            'content_type': ContentType.objects.get_for_model(self.language).pk
            })

        form.save(self.user, commit=True)

        self.assertEquals(Message.objects.count(),
                self.language.followers.filter(notify_by_message=True).count())

        followers = self.language.followers.filter(notify_by_message=True)

        # The author of the comment shouldn't get a message
        self.assertFalse(Message.objects.filter(user=self.user).exists())

        lan2 = SubtitleLanguage.objects.get(pk=lan2.pk)
        lan2_followers = lan2.followers.all()

        for message in Message.objects.all():
            self.assertTrue(isinstance(message.object,
                SubtitleLanguage))
            self.assertTrue(message.user in list(followers))
            self.assertFalse(message.user in list(lan2_followers))


class TestVideoChangedEmailNotification(TestCase):
    def setUp(self):
        self.user_1 = User.objects.create(username='user_1')
        self.user_2 = User.objects.create(username='user_2')

        self.video = video = Video.get_or_create_for_url("http://www.example.com/video.mp4")[0]
        video.primary_audio_language_code = 'en'
        video.user = self.user_1
        video.save()
        mail.outbox = []
        self.original_language = SubtitleLanguage.objects.create(video=video, language_code='en')
        subs = SubtitleSet.from_list('en',[
            (1000, 2000, "1"),
            (2000, 3000, "2"),
            (3000, 4000, "3"),
        ])
        self.original_language.add_version(subtitles=subs)

    def test_no_version_no_breakage(self):
        initial_count= len(mail.outbox)
        res = _send_notification(1000)
        self.assertEqual(res, False)
        self.assertEqual(len(mail.outbox), initial_count)

    def test_email_diff_not_for_private(self):
        # make sure we never send email for private versions
        initial_count= len(mail.outbox)
        version = self.original_language.get_tip()
        version.visibility = 'private'
        version.save()

        self.assertTrue(version.is_private())
        res = _send_notification(version.pk)
        self.assertEqual(res, False)
        self.assertEqual(len(mail.outbox), initial_count )

    def test_email_diff_notification_wont_fire_without_changes(self):
        initial_count= len(mail.outbox)
        # version is indentical to previous one
        old_version = self.original_language.get_tip()
        new_version = self.original_language.add_version(subtitles=old_version.get_subtitles())
        # no notifications should be sent
        res = _send_notification(new_version.pk)
        self.assertEqual(res, None)
        self.assertEqual(len(mail.outbox), initial_count )

    def test_email_diff_subtitles(self):
        initial_count= len(mail.outbox)
        # version is indentical to previous one
        old_version = self.original_language.get_tip()
        new_version = self.original_language.add_version(subtitles=old_version.get_subtitles())
        res = _send_notification(new_version.pk)
        self.assertEqual(res, None)
        self.assertEqual(len(mail.outbox), initial_count )

