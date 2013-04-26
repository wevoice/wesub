# -*- coding: utf-8 -*-
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

from django.db import IntegrityError
from django.test import TestCase

from apps.auth.models import CustomUser as User
from apps.subtitles.models import Collaborator
from apps.subtitles.tests.utils import make_video, make_sl, refresh


class TestCollaborator(TestCase):
    def setUp(self):
        self.video = make_video()
        self.sl = make_sl(self.video, 'en')


    def test_create_collaborators(self):
        users = User.objects.all()

        u1 = users[0]
        u2 = users[1]

        c1 = Collaborator(subtitle_language=self.sl, user=u1)
        c2 = Collaborator(subtitle_language=self.sl, user=u2)

        c1.save()
        c2.save()

        # Make sure basic defaults are correct.
        self.assertEqual(c1.user_id, u1.id)
        self.assertEqual(c1.subtitle_language.language_code, 'en')
        self.assertEqual(c1.signoff, False)
        self.assertEqual(c1.signoff_is_official, False)
        self.assertEqual(c1.expired, False)

        self.assertEqual(c2.user_id, u2.id)
        self.assertEqual(c2.subtitle_language.language_code, 'en')
        self.assertEqual(c2.signoff, False)
        self.assertEqual(c2.signoff_is_official, False)
        self.assertEqual(c2.expired, False)

        # Make sure both objects got created properly, and get_for finds them.
        cs = Collaborator.objects.get_for(self.sl)
        self.assertEqual(cs.count(), 2)

        # Make sure we can't create two Collaborators for the same
        # language/video combination.
        self.assertRaises(IntegrityError,
                          lambda: Collaborator(subtitle_language=self.sl,
                                               user=u1).save())

    def test_signoff_retrieval(self):
        users = User.objects.all()

        u1 = users[0]
        u2 = users[1]

        c1 = Collaborator(subtitle_language=self.sl, user=u1)
        c2 = Collaborator(subtitle_language=self.sl, user=u2)

        c1.save()
        c2.save()

        cs = Collaborator.objects
        sl = self.sl

        # collab signoff is_official expired
        # 1
        # 2
        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 2)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 0)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 0)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 0)

        # collab signoff is_official expired
        # 1      ✔
        # 2
        c1.signoff = True
        c1.save()

        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 1)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 1)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 1)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 0)

        # collab signoff is_official
        # 1      ✔
        # 2      ✔
        c2.signoff = True
        c2.save()

        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 0)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 2)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 2)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 0)

        # collab signoff is_official expired
        # 1      ✔       ✔
        # 2      ✔
        c1.signoff_is_official = True
        c1.save()

        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 0)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 2)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 1)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 1)

        # collab signoff is_official expired
        # 1      ✔       ✔
        # 2      ✔       ✔
        c2.signoff_is_official = True
        c2.save()

        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 0)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 2)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 0)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 2)

        # collab signoff is_official expired
        # 1
        # 2
        c1.signoff = False
        c1.signoff_is_official = False
        c1.save()

        c2.signoff = False
        c2.signoff_is_official = False
        c2.save()

        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl, include_expired=True).count(), 2)

        # collab signoff is_official expired
        # 1                          ✔
        # 2
        c1.expired = True
        c1.save()

        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 1)
        self.assertEqual(cs.get_unsignedoff_for(sl, include_expired=True).count(), 2)

        # collab signoff is_official expired
        # 1                          ✔
        # 2                          ✔
        c2.expired = True
        c2.save()

        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 0)
        self.assertEqual(cs.get_unsignedoff_for(sl, include_expired=True).count(), 2)

        # collab signoff is_official expired
        # 1      ✔       ✔           ✔
        # 2      ✔                   ✔
        c1.signoff = True
        c1.signoff_is_official = True
        c1.save()

        c2.signoff = True
        c2.signoff_is_official = False
        c2.save()

        self.assertEqual(cs.get_for(sl).count(), 2)
        self.assertEqual(cs.get_unsignedoff_for(sl).count(), 0)
        self.assertEqual(cs.get_all_signoffs_for(sl).count(), 2)
        self.assertEqual(cs.get_peer_signoffs_for(sl).count(), 1)
        self.assertEqual(cs.get_official_signoffs_for(sl).count(), 1)


class TestSubtitleLanguageCollaboratorInteractions(TestCase):
    def setUp(self):
        self.video = make_video()

        self.sl = make_sl(self.video, 'en')

        users = User.objects.all()

        u1 = users[0]
        u2 = users[1]
        u3 = users[2]

        self.c1 = Collaborator(subtitle_language=self.sl, user=u1)
        self.c2 = Collaborator(subtitle_language=self.sl, user=u2)
        self.c3 = Collaborator(subtitle_language=self.sl, user=u3)

        self.c1.save()
        self.c2.save()
        self.c3.save()


    def test_signoff_counts(self):
        """Test the various types of signoff counting.

        Does not test expiration at all.

        """
        sl = self.sl

        # collab signoff official
        # 1
        # 2
        # 3
        sl = refresh(sl)

        self.assertEqual(sl.unofficial_signoff_count, 0)
        self.assertEqual(sl.official_signoff_count, 0)
        self.assertEqual(sl.pending_signoff_count, 3)

        # collab signoff official
        # 1      ✔
        # 2
        # 3
        self.c1.signoff = True
        self.c1.save()

        sl = refresh(sl)

        self.assertEqual(sl.unofficial_signoff_count, 1)
        self.assertEqual(sl.official_signoff_count, 0)
        self.assertEqual(sl.pending_signoff_count, 2)

        # collab signoff official
        # 1      ✔       ✔
        # 2
        # 3
        self.c1.signoff_is_official = True
        self.c1.save()

        sl = refresh(sl)

        self.assertEqual(sl.unofficial_signoff_count, 0)
        self.assertEqual(sl.official_signoff_count, 1)
        self.assertEqual(sl.pending_signoff_count, 2)

        # collab signoff official
        # 1      ✔       ✔
        # 2      ✔
        # 3      ✔
        self.c2.signoff = True
        self.c2.save()
        self.c3.signoff = True
        self.c3.save()

        sl = refresh(sl)

        self.assertEqual(sl.unofficial_signoff_count, 2)
        self.assertEqual(sl.official_signoff_count, 1)
        self.assertEqual(sl.pending_signoff_count, 0)

    def test_pending_expiration_counts(self):
        """Tests the effects of collaborator expiration on signoff counts."""

        sl = self.sl

        # collab signoff expired
        # 1
        # 2
        # 3
        sl = refresh(sl)

        self.assertEqual(sl.pending_signoff_count, 3)
        self.assertEqual(sl.pending_signoff_expired_count, 0)
        self.assertEqual(sl.pending_signoff_unexpired_count, 3)

        # collab signoff expired
        # 1              ✔
        # 2
        # 3
        self.c1.expired = True
        self.c1.save()

        sl = refresh(sl)

        self.assertEqual(sl.pending_signoff_count, 3)
        self.assertEqual(sl.pending_signoff_expired_count, 1)
        self.assertEqual(sl.pending_signoff_unexpired_count, 2)

        # collab signoff expired
        # 1              ✔
        # 2              ✔
        # 3              ✔
        self.c2.expired = True
        self.c2.save()
        self.c3.expired = True
        self.c3.save()

        sl = refresh(sl)

        self.assertEqual(sl.pending_signoff_count, 3)
        self.assertEqual(sl.pending_signoff_expired_count, 3)
        self.assertEqual(sl.pending_signoff_unexpired_count, 0)

        # collab signoff expired
        # 1              ✔
        # 2      ✔       ✔
        # 3              ✔
        self.c2.signoff = True
        self.c2.save()

        sl = refresh(sl)

        self.assertEqual(sl.pending_signoff_count, 2)
        self.assertEqual(sl.pending_signoff_expired_count, 2)
        self.assertEqual(sl.pending_signoff_unexpired_count, 0)

        self.assertEqual(sl.unofficial_signoff_count, 1)

