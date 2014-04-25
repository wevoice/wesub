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
import videos.tasks

class AccountForm(forms.ModelForm):
    """Base class for forms on the teams tab.

    We show multiples forms on that tab.  This class helps provide a generic
    interface so that the view code doesn't need to special case each form
    """

    enabled = forms.BooleanField(required=False)

    def __init__(self, team, data=None, **kwargs):
        self.team = team
        forms.ModelForm.__init__(self, data, **kwargs)

    @classmethod
    def get_account(cls, team):
        ModelClass = cls._meta.model
        try:
            return ModelClass.objects.filter(team=team).get()
        except ModelClass.DoesNotExist:
            return None

    def delete_account(self):
        if self.instance.id is not None:
            self.instance.delete()

    def save(self):
        account = forms.ModelForm.save(self, commit=False)
        account.team = self.team
        account.save()
        return account

class KalturaAccountForm(AccountForm):
    partner_id = forms.IntegerField()

    class Meta:
        model = models.KalturaAccount
        fields = ['partner_id', 'secret']

class BrightcoveAccountForm(AccountForm):
    FEED_ALL_NEW = 'N'
    FEED_WITH_TAGS = 'T'
    FEED_CHOICES = (
        (FEED_ALL_NEW, ugettext_lazy('Import all new videos')),
        (FEED_WITH_TAGS, ugettext_lazy('Import videos with tags:')),
    )

    publisher_id = forms.IntegerField(label=ugettext_lazy("Publisher ID"))
    write_token = forms.CharField(label=ugettext_lazy("Write token"))
    feed_enabled = forms.BooleanField(
        required=False, label=ugettext_lazy("Import Videos From Feed"))
    player_id = forms.CharField(
        required=False, label=ugettext_lazy("Player ID"))
    feed_type = forms.ChoiceField(choices=FEED_CHOICES,
                                  initial=FEED_ALL_NEW,
                                  widget=forms.RadioSelect,
                                  required=False)
    feed_tags = forms.CharField(required=False)

    class Meta:
        model = models.BrightcoveAccount
        fields = ['publisher_id', 'write_token' ]

    def __init__(self, team, data=None, **kwargs):
        AccountForm.__init__(self, team, data, **kwargs)
        if self.instance.import_feed is not None:
            self.fields['feed_enabled'].initial = True

    def add_error(self, field_name, msg):
        self._errors[field_name] = self.error_class([msg])
        if field_name in self.cleaned_data:
            del self.cleaned_data[field_name]

    def clean(self):
        if self.cleaned_data['feed_enabled']:
            if not self.cleaned_data['player_id']:
                self.add_error(
                    'player_id',
                    _('Must specify a player id to import from a feed'))
            if not self.cleaned_data['feed_type']:
                self.add_error(
                    'player_id',
                    _('Must specify a feed type for import'))
            if (self.cleaned_data['feed_type'] == self.FEED_WITH_TAGS and
                not self.cleaned_data['feed_tags']):
                self.add_error('feed_tags',
                               _('Must specify tags to import'))
        return self.cleaned_data

    def save(self):
        account = AccountForm.save(self)
        if self.cleaned_data['feed_enabled']:
            if self.cleaned_data['feed_type'] == self.FEED_ALL_NEW:
                tags = None
            elif self.cleaned_data['feed_type'] == self.FEED_WITH_TAGS:
                tags = self.cleaned_data['feed_tags'].split()
            feed_changed = account.make_feed(self.cleaned_data['player_id'],
                                             tags)
            if feed_changed:
                videos.tasks.import_videos_from_feed.delay(
                    account.import_feed.id)
        else:
            account.remove_feed()
        return account

    def import_feed(self):
        if self.instance:
            return self.instance.import_feed
        else:
            return None

class AccountFormset(object):
    """dict-like object that contains multiple account forms.

    For each form in form classes we will instatiate it with a unique prefix
    to avoid name collisions.  Also we will create another form that controls
    if the accounts are enabled.
    """
    form_classes = {
        'kaltura': KalturaAccountForm,
        'brightcove': BrightcoveAccountForm,
    }
    def __init__(self, team, data=None):
        self.is_bound = data is not None
        existing_accounts = dict(
            (name, form_class.get_account(team))
            for (name, form_class) in self.form_classes.items())

        enabled_accounts = self.make_enabled_accounts(existing_accounts, data)
        # trigger a full clean on enabled_accounts since we want to use
        # it's cleaned_data below
        enabled_accounts.is_valid()
        self.forms = {
            'enabled_accounts': enabled_accounts,
        }

        for name, form_class in self.form_classes.items():
            # if the account is enabled, then we pass it the POST data,
            # otherwise we leave it unbound
            if self.is_bound and enabled_accounts.cleaned_data[name]:
                form_data = data
            else:
                form_data = None
            self.forms[name] = form_class(team, form_data,
                                          instance=existing_accounts[name],
                                          prefix=name)

    def make_enabled_accounts(self, existing_accounts, data):
        fields = {}
        for form_name in self.form_classes:
            fields[form_name] = forms.BooleanField(
                required=False, label=_('Enabled'),
                initial=existing_accounts[form_name] is not None)
        EnabledAccountsForm = type('EnabledAccountsForm', (forms.Form,),
                                   fields)
        return EnabledAccountsForm(data, prefix='enabled_accounts')

    def account_forms(self):
        for form_name, form in self.forms.items():
            if form_name != 'enabled_accounts':
                yield form_name, form

    def account_enabled(self, form_name):
        return self['enabled_accounts'].cleaned_data.get(form_name)

    def is_valid(self):
        if not self.is_bound:
            return False
        return all(form.is_valid()
                   for (form_name, form) in self.account_forms()
                   if self.account_enabled(form_name))

    def save(self):
        if not self.is_valid():
            raise ValueError("form not valid")
        for form_name, form in self.account_forms():
            if self.account_enabled(form_name):
                form.save()
            else:
                form.delete_account()

    def keys(self):
        return self.forms.keys()

    def __getitem__(self, form_name):
        return self.forms[form_name]

