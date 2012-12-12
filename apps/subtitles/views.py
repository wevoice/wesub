# -*- coding: utf-8 -*-
# Amara, universalsubtitles.org
#
# Copyright (C) 2012 Participatory Culture Foundation
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
from videos.models import Video
from subtitles.models import SubtitleLanguage

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

def edit_subtitles(request, video_id, language_code, task_id=None):
    # FIXME permissions the motherf
    video = get_object_or_404(Video, video_id=video_id)
    # FIXME: validate language code
    try:
        language = video.newsubtitlelanguage_set.get(language_code=language_code)
    except SubtitleLanguage.DoesNotExist:
        language = SubtitleLanguage(video=video,language_code=language_code )
    if not language.can_writelock(request.browser_id):
        return render_to_response("subtitles/subtitle-editor-locked.html")
    language.writelock(request.user, request.browser_id, save=True)
    return render_to_response("subtitles/subtitle-editor.html", {
        'video': video,
        'language': language
    }, context_instance=RequestContext(request))

