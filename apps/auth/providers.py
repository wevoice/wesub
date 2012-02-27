# Universal Subtitles, universalsubtitles.org
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


authentication_provider_registry = {}

def add_authentication_provider(ap_class):
    if ap_class.code in authentication_provider_registry:
        if authentication_provider_registry[ap_class.code] != ap_class:
            assert False, "Authentication provider code collision!"

    authentication_provider_registry[ap_class.code] = ap_class

def get_authentication_provider(key):
    return authentication_provider_registry.get(key)

def get_authentication_provider_choices():
    choices = []
    for provider in authentication_provider_registry.values():
        choices.append((provider.code, provider.verbose_name))
    return choices


class AuthenticationProvider(object):
    """The base class that other authentication providers should implement.

    In a nutshell, an AuthenticationProvider is a simple class that has:

    * A code attribute.  This should be a unique string less than
      24 characters long that will be stored as an attribute of Teams.

    * A verbose_name attribute, for admin labels.

    * A url() method, which takes a TeamMember object and a "next" URL, and
      returns the URL we should send the user to where they can log in with the
      provider.

    * An image_url() method, which returns the URL for an image we should
      display to the user when they're deciding whether or not to continue and
      log in.

    """
    code = None
    verbose_name = None

    def url(self, member, next=None):
        """Return the URL someone should be sent to where they will log in."""
        assert False, "Not Implemented"

    def image_url(self):
        """Return the URL of an image to display (probably a logo) or None."""
        assert False, "Not Implemented"


class SampleAuthProvider(AuthenticationProvider):
    code = 'sample'
    verbose_name = 'Sample Provider'

    def url(self, member, next=None):
        return 'http://example.com/'

    def image_url(self):
        return 'http://placekitten.com/200/200/'

# add_authentication_provider(SampleAuthProvider)
