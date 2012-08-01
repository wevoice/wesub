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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.


from django.contrib import admin
from apps.subtitles.models import get_lineage, SubtitleLanguage, SubtitleVersion



class SubtitleLanguageAdmin(admin.ModelAdmin):
    list_display = ['video_title', 'language_code', 'version_count', 'tip',
                    'created']
    list_filter = ['created', 'language_code']
    search_fields = ['video__title', 'video__video_id', 'language_code']
    raw_id_fields = ['video', 'followers', 'collaborators']

    def video_title(self, sl):
        return sl.video.title_display()
    video_title.short_description = 'video'

    def version_count(self, sl):
        return sl.subtitleversion_set.count()
    version_count.short_description = 'number of versions'

    def tip(self, sl):
        ver = sl.get_tip()
        return ver.version_number if ver else None
    tip.short_description = 'tip version'


class SubtitleVersionAdmin(admin.ModelAdmin):
    list_display = ['video_title', 'id', 'language', 'version_num',
                    'visibility', 'parent_ids', 'created']
    raw_id_fields = ['video', 'subtitle_language', 'parents', 'author']
    list_filter = ['created', 'visibility', 'language_code']
    search_fields = ['video__video_id', 'video__title', 'title',
                     'language_code', 'description']

    def version_num(self, sv):
        return '#' + str(sv.version_number)
    version_num.short_description = 'version #'

    def video_title(self, sv):
        return sv.video.title_display()
    video_title.short_description = 'video'

    def language(self, sv):
        return sv.subtitle_language.get_language_code_display()

    def parent_ids(self, sv):
        pids = map(str, sv.parents.values_list('id', flat=True))
        return ', '.join(pids) if pids else None

    # Hack to generate lineages properly when modifying versions in the admin
    # interface.  Maybe we should just disallow this entirely once the version
    # models are hooked up everywhere else?
    def response_change(self, request, obj):
        response = super(SubtitleVersionAdmin, self).response_change(request, obj)
        obj.lineage = get_lineage(obj.parents.all())
        obj.save()
        return response

    def response_add(self, request, obj, *args, **kwargs):
        response = super(SubtitleVersionAdmin, self).response_add(request, obj)
        obj.lineage = get_lineage(obj.parents.all())
        obj.save()
        return response


admin.site.register(SubtitleLanguage, SubtitleLanguageAdmin)
admin.site.register(SubtitleVersion, SubtitleVersionAdmin)
