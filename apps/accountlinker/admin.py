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
from models import ThirdPartyAccount, YoutubeSyncRule
from auth.models import CustomUser as User
from teams.models import Team


class TeamMemberInline(admin.TabularInline):
    model = Team.third_party_accounts.through


class UserMemberInline(admin.TabularInline):
    model = User.third_party_accounts.through


class ThirdPartyAccountAdmin(admin.ModelAdmin):
    list_display = ('type', 'full_name', 'username',)
    search_fields = ('full_name', 'username',)
    inlines = [UserMemberInline, TeamMemberInline]


admin.site.register(ThirdPartyAccount, ThirdPartyAccountAdmin)
admin.site.register(YoutubeSyncRule)
