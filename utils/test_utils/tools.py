# Amara, universalsubtitles.org
#
# Copyright (C) 2015 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see
# http://www.gnu.org/licenses/agpl-3.0.html.

"""Testing tools

This module contains a nose-style assert_* functions and other utility
functions.
"""

from nose.tools import *

def reload_obj(model_obj):
    return model_obj.__class__.objects.get(pk=model_obj.pk)

def assert_saved(model_obj):
    assert_true(model_obj.__class__.objects.filter(pk=model_obj.pk).exists())
    assert_equal(model_obj, reload_obj(model_obj))
