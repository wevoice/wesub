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

from django.contrib import admin
from django import forms
from models import ThirdPartyAccount, YoutubeSyncRule


class ThirdPartyAccountAdminForm(forms.ModelForm):

    users = forms.fields.CharField(
            help_text="List of users that have this account (changing this field does nothing)")
    teams = forms.fields.CharField(
            help_text="List of teams that have this account (changing this field does nothing)")

    def __init__(self, *args, **kwargs):
        super(ThirdPartyAccountAdminForm, self).__init__(*args, **kwargs)

        users = self.instance.users.all()
        users = ", ".join([u.username for u in users])

        teams = self.instance.teams.all()
        teams = ", ".join([u.slug for u in teams])

        self.fields['users'].initial = users
        self.fields['teams'].initial = teams

        self.fields['users'].widget.attrs['readonly'] = True
        self.fields['teams'].widget.attrs['readonly'] = True

    class Meta:
        model = ThirdPartyAccount


class ThirdPartyAccountAdmin(admin.ModelAdmin):
    list_display = ('type', 'full_name', 'username',)
    search_fields = ('full_name', 'username',)
    form = ThirdPartyAccountAdminForm


admin.site.register(ThirdPartyAccount, ThirdPartyAccountAdmin)
admin.site.register(YoutubeSyncRule)
