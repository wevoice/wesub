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

from django.shortcuts import redirect, render

from teams.views import settings_page
from externalsites import forms

class AccountFormHandler(object):
    """Handles a single form for the settings tab

    On the settings tab we show several forms for different accounts.
    AccountFormHandler handles the logic for a single form.
    """
    def __init__(self, form_name, form_class):
        self.form_name = form_name
        self.form_class = form_class
        self.should_redirect = False

    def handle_post(self, post_data, context):
        pass

    def handle_get(self, post_data, context):
        pass

@settings_page
def team_settings_tab(request, team):
    form_classes = [
        forms.KalturaAccountForm,
    ]
    posted_form = None

    if request.method == 'POST':
        for FormClass in form_classes:
            if FormClass.should_process_data(request.POST):
                posted_form = FormClass(team, request.POST)
                if 'remove' in request.POST and posted_form.allow_remove:
                    posted_form.delete_account()
                    return redirect('teams:settings_externalsites',
                                    slug=team.slug)
                if posted_form.is_valid():
                    posted_form.save()
                    return redirect('teams:settings_externalsites',
                                    slug=team.slug)
    all_forms = []
    for FormClass in form_classes:
        if posted_form is not None and isinstance(posted_form, FormClass):
            all_forms.append(posted_form)
        else:
            all_forms.append(FormClass(team))

    return render(request, 'externalsites/team-settings-tab.html', {
        'team': team,
        'forms': all_forms,
    })
