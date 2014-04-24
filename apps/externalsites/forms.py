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

from django import forms
from django.core import validators
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from externalsites import models

class AccountForm(forms.ModelForm):
    """Base class for forms on the teams tab.

    We show multiples forms on that tab.  This class helps provide a generic
    interface so that the view code doesn't need to special case each form
    """

    label = NotImplemented

    def __init__(self, team, data=None):
        account = self.get_account(team)
        self.allow_remove = (account is not None)
        self.team = team
        forms.ModelForm.__init__(self, data, instance=account)

    @classmethod
    def form_name(cls):
        return str(cls)

    def get_account(self, team):
        ModelClass = self._meta.model
        try:
            return ModelClass.objects.filter(team=team).get()
        except ModelClass.DoesNotExist:
            return None

    @classmethod
    def should_process_data(self, data):
        return data.get('form-name') == self.form_name()

    def save(self, commit=True):
        account = forms.ModelForm.save(self, commit=False)
        account.team = self.team
        if commit:
            account.save()
        return account

    def delete_account(self):
        self.instance.delete()

class KalturaAccountForm(AccountForm):
    label = _("Kaltura")

    class Meta:
        model = models.KalturaAccount
        fields = ['partner_id', 'secret']

    def clean_partner_id(self):
        partner_id = self.cleaned_data['partner_id']
        if partner_id is not None:
            try:
                int(partner_id)
            except ValueError:
                raise forms.ValidationError(
                    _('Partner ID must contain only numbers'))
        return self.cleaned_data['partner_id']

class BrightcoveAccountForm(AccountForm):
    label = _("Brightcove")

    FEED_ALL_NEW = 'N'
    FEED_WITH_TAGS = 'T'
    FEED_CHOICES = (
        (FEED_ALL_NEW, ugettext_lazy('All new videos')),
        (FEED_WITH_TAGS, ugettext_lazy('Videos with tags:')),
    )

    publisher_id = forms.IntegerField()
    feed_enabled = forms.BooleanField(required=False)
    player_id = forms.CharField(required=False)
    feed_type = forms.ChoiceField(choices=FEED_CHOICES,
                                  initial=FEED_ALL_NEW)
    feed_tags = forms.CharField(required=False)

    class Meta:
        model = models.BrightcoveAccount
        fields = ['publisher_id', 'write_token' ]

    def clean(self):
        if self.cleaned_data['feed_enabled']:
            if not self.cleaned_data['player_id']:
                self._errors['player_id'] = [
                    forms.ValidationError(
                        _('Must specify a player id to import from a feed'))
                ]
            if (self.cleaned_data['feed_type'] == self.FEED_WITH_TAGS and
                not self.cleaned_data['feed_tags']):
                self._errors['feed_tags'] = [
                    forms.ValidationError(_('Must specify tags to import'))
                ]
        return self.cleaned_data

    def save(self, commit=True):
        account = AccountForm.save(self, commit)
        if self.cleaned_data['feed_enabled']:
            if self.cleaned_data['feed_type'] == self.FEED_ALL_NEW:
                account.make_feed(self.cleaned_data['player_id'])
            elif self.cleaned_data['feed_type'] == self.FEED_WITH_TAGS:
                account.make_feed(self.cleaned_data['player_id'],
                                  self.cleaned_data['feed_tags'].split())
        else:
            account.remove_feed()
        return account
