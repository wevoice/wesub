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

"""externalsites.signalhandlers -- Signal handler functions."""

from django.dispatch import receiver
from django.db.models.signals import post_save

from externalsites import tasks
from externalsites.models import KalturaAccount, lookup_accounts
from subtitles.models import SubtitleLanguage, SubtitleVersion
from videos.models import Video
import subtitles.signals

@receiver(subtitles.signals.public_tip_changed)
def on_public_tip_changed(signal, sender, version, **kwargs):
    if not isinstance(sender, SubtitleLanguage):
        raise ValueError("sender must be a SubtitleLanguage: %s" % sender)
    if not isinstance(version, SubtitleVersion):
        raise ValueError("version has wrong type: %s" % version)
    language = sender
    for account, video_url in lookup_accounts(language.video):
        tasks.update_subtitles.delay(account.account_type, account.id,
                                     video_url.id, language.id, version.id)

@receiver(subtitles.signals.language_deleted)
def on_language_deleted(signal, sender, **kwargs):
    if not isinstance(sender, SubtitleLanguage):
        raise ValueError("sender must be a SubtitleLanguage: %s" % sender)
    language = sender
    for account, video_url in lookup_accounts(language.video):
        tasks.delete_subtitles.delay(account.account_type, account.id,
                                     video_url.id, language.id)

@receiver(post_save, sender=KalturaAccount)
def on_account_save(signal, sender, instance, **kwargs):
    tasks.update_all_subtitles.delay(instance.account_type, instance.id)
