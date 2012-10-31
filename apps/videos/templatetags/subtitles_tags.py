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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

from django import template
from django.core.urlresolvers import reverse
from django.template.defaultfilters import linebreaks

from apps.subtitles.forms import SubtitlesUploadForm
from apps.videos import format_time
from apps.videos.forms import CreateVideoUrlForm
from utils.unisubsmarkup import markup_to_html


register = template.Library()


@register.inclusion_tag('videos/_upload_subtitles.html', takes_context=True)
def upload_subtitles(context, video):
    context['video'] = video
    initial = {}

    current_language = context.get('language')
    if current_language:
        initial['language_code'] = current_language.language_code

    primary_language = video.get_primary_audio_subtitle_language()
    if primary_language:
        initial['primary_audio_language_code'] = primary_language.language_code

    context['form'] = SubtitlesUploadForm(context['user'], video,
                                          initial=initial)

    return context

@register.simple_tag
def complete_color(language):
    if not language.subtitles_complete:
        return 'eighty'
    else:
        return 'full'

@register.inclusion_tag('videos/_video_url_panel.html', takes_context=True)
def video_url_panel(context):
    video = context['video']
    context['form'] = CreateVideoUrlForm(context['user'], initial={'video': video.pk})
    context['video_urls'] = video.videourl_set.all()
    return context

@register.simple_tag
def video_url_count(video):
    return video.videourl_set.count()


@register.simple_tag
def language_url(request, lang):
    """Return the absolute url for that subtitle language.

    Takens into consideration whether the video is private or public.  Also
    handles the language-without-language that should be going away soon.

    """
    lc = lang.language_code or 'unknown'
    return reverse('videos:translation_history',
                   args=[lang.video.video_id, lc, lang.pk])

@register.filter
def format_sub_time(t):
    return '' if t < 0 else format_time(t)

@register.filter
def display_subtitle(text):
    """
    Transforms our internal markup to html friendly diplay:
    use the default subtitle formatiing tags (i, b, u)
    and replace \n with <br>
    """
    txt = linebreaks(markup_to_html(text))
    return txt
