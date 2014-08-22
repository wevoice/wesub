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
from django.core.urlresolvers import reverse
from django.forms.util import ErrorDict
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy

from auth.models import CustomUser as User
from teams.models import Team
from externalsites import models
from utils.forms import SubmitButtonField
import videos.tasks

class AccountForm(forms.ModelForm):
    """Base class for forms on the teams or user profile tab."""

    enabled = forms.BooleanField(required=False)

    def __init__(self, owner, data=None, **kwargs):
        super(AccountForm, self).__init__(data=data,
                                          instance=self.get_account(owner),
                                          **kwargs)
        self.owner = owner
        # set initial to be True if an account already exists
        self.fields['enabled'].initial = (self.instance.pk is not None)

    @classmethod
    def get_account(cls, owner):
        ModelClass = cls._meta.model
        try:
            return ModelClass.objects.for_owner(owner).get()
        except ModelClass.DoesNotExist:
            return None

    def full_clean(self):
        if not self.find_enabled_value():
            self.cleaned_data = {
                'enabled': False,
            }
            self._errors = ErrorDict()
        else:
            return super(AccountForm, self).full_clean()

    def find_enabled_value(self):
        widget = self.fields['enabled'].widget
        return widget.value_from_datadict(self.data, self.files,
                                          self.add_prefix('enabled'))

    def save(self):
        if not self.is_valid():
            raise ValueError("form has errors: %s" % self.errors.as_text())
        if not self.cleaned_data['enabled']:
            self.delete_account()
            return
        account = forms.ModelForm.save(self, commit=False)
        if isinstance(self.owner, Team):
            account.type = models.ExternalAccount.TYPE_TEAM
            account.owner_id = self.owner.id
        elif isinstance(self.owner, User):
            account.type = models.ExternalAccount.TYPE_USER
            account.owner_id = self.owner.id
        else:
            raise TypeError("Invalid owner type: %s" % self.owner)
        account.save()
        return account

    def delete_account(self):
        if self.instance.id is not None:
            self.instance.delete()

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
    write_token = forms.CharField(
        label=ugettext_lazy("Sync subtitles with this write token"),
        required=False)
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
            player_id, tags = self.instance.feed_info()
            self.fields['player_id'].initial = player_id
            if tags is not None:
                self.fields['feed_type'].initial = self.FEED_WITH_TAGS
                self.fields['feed_tags'].initial = ', '.join(tags)
            else:
                self.fields['feed_type'].initial = self.FEED_ALL_NEW
                self.fields['feed_tags'].initial = ''

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
        if not self.cleaned_data['enabled']:
            return None
        if self.cleaned_data['feed_enabled']:
            feed_changed = account.make_feed(self.cleaned_data['player_id'],
                                             self._calc_feed_tags())
            if feed_changed:
                videos.tasks.import_videos_from_feed.delay(
                    account.import_feed.id)
        else:
            account.remove_feed()
        return account

    def _calc_feed_tags(self):
        if self.cleaned_data['feed_type'] == self.FEED_ALL_NEW:
            return None
        elif self.cleaned_data['feed_type'] == self.FEED_WITH_TAGS:
            return [tag.strip()
                    for tag in self.cleaned_data['feed_tags'].split(',')]

    def import_feed(self):
        if self.instance:
            return self.instance.import_feed
        else:
            return None

class AddYoutubeAccountForm(forms.Form):
    add_button = SubmitButtonField(label=ugettext_lazy('Add YouTube account'),
                                   required=False)

    def __init__(self, owner, data=None, **kwargs):
        super(AddYoutubeAccountForm, self).__init__(data=data, **kwargs)
        self.owner = owner

    def save(self):
        pass

    def redirect_path(self):
        if self.cleaned_data['add_button']:
            path = reverse('externalsites:youtube-add-account')
            if isinstance(self.owner, Team):
                return '%s?team_slug=%s' % (path, self.owner.slug)
            elif isinstance(self.owner, User):
                return '%s?username=%s' % (path, self.owner.username)
            else:
                raise ValueError("Unknown owner type: %s" % self.owner)
        else:
            return None

class YoutubeAccountForm(forms.Form):
    remove_button = SubmitButtonField(label=ugettext_lazy('Remove account'),
                                      required=False)
    sync_teams = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False)

    def __init__(self, admin_user, account, data=None, **kwargs):
        super(YoutubeAccountForm, self).__init__(data=data, **kwargs)
        self.account = account
        self.admin_user = admin_user
        self.setup_sync_teams()

    def setup_sync_teams(self):
        choices = []
        initial = []
        # allow the admin to uncheck any of the current sync teams
        current_sync_teams = list(self.account.sync_teams.all())
        for team in current_sync_teams:
            choices.append((team.id, team.name))
            initial.append(team.id)
        # allow the admin to check any of the other teams they're an admin for
        exclude_team_ids = [t.id for t in current_sync_teams]
        exclude_team_ids.append(self.account.owner_id)
        member_qs = (self.admin_user.team_members.admins()
                     .exclude(team_id__in=exclude_team_ids)
                     .select_related('team'))
        choices.extend((member.team.id, member.team.name)
                       for member in member_qs)
        self['sync_teams'].field.choices = choices
        self['sync_teams'].field.initial = initial

    def save(self):
        if not self.is_valid():
            raise ValueError("Form not valid")
        if self.cleaned_data['remove_button']:
            self.account.delete()
        else:
            self.account.sync_teams = Team.objects.filter(
                id__in=self.cleaned_data['sync_teams']
            )

    def show_sync_teams(self):
        return len(self['sync_teams'].field.choices) > 0

class AccountFormset(dict):
    """Container for multiple account forms.

    For each form in form classes we will instatiate it with a unique prefix
    to avoid name collisions.
    """
    def __init__(self, admin_user, owner, data=None):
        super(AccountFormset, self).__init__()
        self.admin_user = admin_user
        self.data = data
        self.make_forms(owner)

    def make_forms(self, owner):
        self.make_form('kaltura', KalturaAccountForm, owner)
        self.make_form('brightcove', BrightcoveAccountForm, owner)
        self.make_form('add_youtube', AddYoutubeAccountForm, owner)
        for account in models.YouTubeAccount.objects.for_owner(owner):
            name = 'youtube_%s' % account.id
            self.make_form(name, YoutubeAccountForm, self.admin_user, account)

    def make_form(self, name, form_class, *args, **kwargs):
        kwargs['prefix'] = name.replace('_', '-')
        kwargs['data'] = self.data
        self[name] = form_class(*args, **kwargs)

    def youtube_forms(self):
        return [form for name, form in self.items()
                if name.startswith('youtube_')]

    def is_valid(self):
        return all(form.is_valid() for form in self.values())

    def save(self):
        for form in self.values():
            form.save()

    def redirect_path(self):
        for form in self.values():
            if hasattr(form, 'redirect_path'):
                redirect_path = form.redirect_path()
                if redirect_path is not None:
                    return redirect_path
