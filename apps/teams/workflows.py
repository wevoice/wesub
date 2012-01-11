# Universal Subtitles, universalsubtitles.org
#
# Copyright (C) 2011 Participatory Culture Foundation
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

from apps.teams.models import Task


def _handle_subtitle(subtitle_version):
    """Handle when a user completes a set of subtitles."""

    tasks = Task.objects.incomplete_subtitle().filter(
                team_video__video=subtitle_version.language.video)

    for task in tasks:
        task.complete()

def _handle_translate(subtitle_version):
    """Handle when a user completes a translation of a set of subtitles."""

    tasks = Task.objects.incomplete_translate().filter(
                team_video__video=subtitle_version.language.video)

    for task in tasks:
        task.complete()

def handle_subtitles_completed(subtitle_version):
    """Perform any necessary actions for when a user finishes a set of subtitles.

    This function does a lot of checking so it's safe to call each time a set of
    subtitles is completed.

    """

    if subtitle_version.language.is_original or subtitle_version.language.is_forked:
        return _handle_subtitle(subtitle_version)
    else:
        return _handle_translate(subtitle_version)


def handle_review_completed(subtitle_version):
    tasks = Task.objects.incomplete_review().filter(
                team_video__video=subtitle_version.language.video)

    for task in tasks:
        task.complete()

def handle_approve_completed(subtitle_version):
    tasks = Task.objects.incomplete_approve().filter(
                team_video__video=subtitle_version.language.video)

    for task in tasks:
        task.complete()
