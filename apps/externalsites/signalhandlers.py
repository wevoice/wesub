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
from externalsites.models import KalturaAccount, accounts_for_video
from subtitles.models import SubtitleLanguage
from videos.models import Video
import subtitles.signals

@receiver(subtitles.signals.public_tip_changed)
def on_public_tip_changed(signal, sender, version, **kwargs):
    language = sender
    for account in accounts_for_video(language.video):
        tasks.update_subtitles(account.account_type, account.id, language.id,
                               version.id)

@receiver(subtitles.signals.language_deleted)
def on_language_deleted(signal, sender, **kwargs):
    language = sender
    for account in accounts_for_video(language.video):
        tasks.delete_subtitles(account.account_type, account.id, language.id)

@receiver(post_save, sender=KalturaAccount)
def on_account_save(signal, sender, instance, **kwargs):
    tasks.update_all_subtitles(instance.account_type, instance.id)
