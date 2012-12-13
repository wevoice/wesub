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
import json

from videos.models import Video
from subtitles.models import SubtitleLanguage, SubtitleVersion

from django.db.models import Count
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

def _version_data(version):
    '''
    Creates a dict with version info, suitable for encoding
    into json and bootstrapping the editor.
    '''
    return {
        'number': version.version_number,
        'subtitlesXML': version.get_subtitles().to_xml(),
        'title': version.title,
        'description': version.description,
    }

def _language_data(language, editing_version, translated_from_version):
    '''
    Creates a dict with language info, suitable for encoding
    into json and bootstrapping the editor. Includes
    the version data for the version being edited and the
    original translation source, if any.
    '''
    versions_data = []
    for version_number in range(1, language.num_versions +1):
        version_data = {'number':version_number}
        if editing_version and editing_version.version_number == version_number and \
            editing_version.subtitle_language == language:
            version_data.update(_version_data(editing_version))
        elif translated_from_version and translated_from_version.version_number == version_number and \
            translated_from_version.subtitle_language == language:
            version_data.update(_version_data(translated_from_version))

        versions_data.append(version_data)
    return {
        'translatedFrom': translated_from_version and {
            'language_code': translated_from_version.subtitle_language.language_code,
            'version_number': translated_from_version.version_number,
        },
        'editingLanguage': language == editing_version.subtitle_language,
        'code': language.language_code,
        'name': language.get_language_code_display(),
        'pk': language.pk,
        'numVersions': language.num_versions,
        'versions': versions_data,
    }

def subtitle_editor(request, video_id, language_code, task_id=None):
    '''
    Renders the subtitle-editor page, with all data neeeded for the UI
    as a json object on the html document.
    If the language does not exist, it will create one and lock it.
    Also decides what source version should be shown initially (if
    it is a translation).
    '''
    # FIXME: permissions
    video = get_object_or_404(Video, video_id=video_id)
    # FIXME: validate language code
    try:
        editing_language = video.newsubtitlelanguage_set.get(language_code=language_code)
    except SubtitleLanguage.DoesNotExist:
        editing_language = SubtitleLanguage(video=video,language_code=language_code )
    if not editing_language.can_writelock(request.browser_id):
        return render_to_response("subtitles/subtitle-editor-locked.html")
    editing_language.writelock(request.user, request.browser_id, save=True)
    # if this language is a traslation, show both
    editing_version = editing_language.get_tip(public=False)
    translated_from_version = None
    lineage = editing_version and editing_version.get_lineage()
    if editing_version and lineage:
        translated_from_version = SubtitleVersion.objects.get(
            subtitle_language__language_code=lineage.keys()[0], version_number=lineage.values()[0])
    languages = video.newsubtitlelanguage_set.having_nonempty_versions().annotate(
        num_versions=Count('subtitleversion'))
    editor_data = {
        'video': {
            'id': video.video_id,
            'videoURL': video.get_video_url()
        },
        'languages': [_language_data(lang, editing_version, translated_from_version) for lang in languages],
    }
    return render_to_response("subtitles/subtitle-editor.html", {
        'video': video,
        'language': editing_language,
        'other_languages': languages,
        'version': editing_version,
        'editor_data': json.dumps(editor_data, indent=4)
    }, context_instance=RequestContext(request))

