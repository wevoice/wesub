# Amara, universalsubtitles.org
#
# Copyright (C) 2013 Participatory Culture Foundation
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see http://www.gnu.org/licenses/agpl-3.0.html.

"""
Work Modes
----------

Work modes are used to change the workflow section of the editor and affect
the overall feel of the editing session.  Currently we only have 2 work modes:

* .. autoclass:: NormalWorkMode
* .. autoclass:: ReviewWorkMode


Work modes are controlled by the `editor_work_mode` function.

.. autofunction:: editor_work_mode(user, video, language_code)


"""

from utils.behaviors import behavior

class NormalWorkMode(object):
    """The usual work mode with typing/syncing/review steps."""

    def __init__(self):
        self.editor_data = {
            'type': 'normal',
        }

class ReviewWorkMode(object):
    """Review someone else's work (for example a review/approve task)

    Args:
        heading (str): heading to display in the workflow area
    """

    def __init__(self, heading):
        self.editor_data = {
            'type': 'review',
            'heading': heading,
        }

@behavior
def editor_work_mode(user, video, language_code):
    """Get the work mode to use for an editor session.

    The default return value a NormalWorkMode object.  It uses the
    :doc:`behaviors <behaviors>` module to allow other apps to override this
    for certain videos.
    """
    return NormalWorkMode()

def editor_work_data(user, video, language_code):
    return editor_work_mode(user, video, language_code).editor_data
