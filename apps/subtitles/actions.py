# Amara, universalsubtitles.org
#
# Copyright (C) 2014 Participatory Culture Foundation
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
Subtitle Actions
================

Extensible user actions for subtitle sets

Actions are things things that users can do to a subtitle set other than
changing the actual subtitles.  They correspond to the buttons in the editor
at the bottom of the workflow session (publish, endorse, send back, etc).
Actions can occur alongside changes to the subtitle lines or independent of
them.

.. autofunction:: get_actions

.. autoclass:: Action
   :members:

.. autoclass:: Publish

"""

from django.utils.translation import ugettext_lazy

from utils.behaviors import behavior

class Action(object):
    """Base class for actions

    Other components can define new actions by subclassing Action, setting the
    class attributes, then implementing handle().

    """

    name = NotImplemented 
    """Machine-friendly name"""

    label = NotImplemented
    """human-friendly label.  Strings should be run through ugettext_lazy()
    """
    in_progress_text = NotImplemented
    """text to display in the editor while this action is being performed.
    Strings should be run through ugettext_lazy()
    """

    visual_class = None
    """
    visual class to render the action with.  This controls things like the
    icon we use in our editor button.  Must be one of the `CLASS_` constants
    """

    complete = None
    """
    complete defines how to handle subtitles_complete. There are 3 options:

        - True -- this action sets subtitles_complete
        - False -- this action unsets subtitles_complete
        - None (default) - this action doesn't change subtitles_complete
    """

    CLASS_ENDORSE = 'endorse'
    """endorse/approve buttons"""
    CLASS_SEND_BACK = 'send-back'
    """reject/send-back buttons"""

    def handle(self, user, video, language_code, saved_version):
        """Handle this action being performed.

        Args:
            user (User): User performing the action
            video (Video): Video being changed
            language_code (str): language being changed
            saved_version (SubtitleVersion or None): new version that was
                created for subtitle changes that happened alongside this
                action.  Will be None if no changes were made.
        """
        raise NotImplementedError()

class Publish(Action):
    """Publish action

    Publish simply sets the subtitles_complete flag to True
    """
    name = 'publish'
    label = ugettext_lazy('Publish')
    in_progress_text = ugettext_lazy('Saving')
    visual_class = 'endorse'
    complete = True

    def handle(self, user, video, language_code, saved_version):
        pass

@behavior
def get_actions(user, video, language_code):
    """Get a list of Action objects for a subtitle set.

    The return value of this function defines the valid actions for a subtitle
    set.  It uses the :doc:`behaviors <behaviors>` system so that other
    components can override the actions for certain subtitle sets.

    If you override this function, you probably also want to create one or
    more Action subclasses to return.
    """
    return [Publish()]

def _lookup_action(user, video, language_code, action_name):
    actions = get_actions(user, video, language_code)
    for action in actions:
        if action.name == action_name:
            return action
    raise ValueError("No action: %s" % action_name)

def _check_can_perform(action, subtitle_language):
    """Check if we can perform an action.

    Returns:
        None if an action can be performed, otherwise a string that explains
        why not.
    """
    if action.complete:
        tip = subtitle_language.get_tip()
        if tip is None or not tip.has_subtitles or not tip.is_synced():
            return 'Subtitles not complete'
    return None

def lookup_action(user, video, language_code, action_name):
    subtitle_language = video.subtitle_language(language_code)
    action = _lookup_action(user, video, language_code, action_name)
    cant_perform_reason = _check_can_perform(action, subtitle_language)
    if cant_perform_reason is not None:
        raise ValueError(cant_perform_reason)
    else:
        return action

def perform_action(user, video, language_code, action_name, saved_version):
    subtitle_language = video.subtitle_language(language_code)
    action = lookup_action(user, video, language_code, action_name)
    if (action.complete is not None and
        action.complete != subtitle_language.subtitles_complete):
        subtitle_language.subtitles_complete = action.complete
        subtitle_language.save()
    action.handle(user, video, language_code, saved_version)

def can_perform_action(user, video, language_code, action_name):
    subtitle_language = video.subtitle_language(language_code)
    action = _lookup_action(user, video, language_code, action_name)
    return _check_can_perform(action, subtitle_language) is None

def editor_actions(user, video, language_code):
    """Get the list of actions to send to the editor.

    Returns:
        the actions from get_actions() serialized into dicts to add to the
        javascript object editor_data.
    """
    data = []
    for action in get_actions(user, video, language_code):
        data.append({
            'name': action.name,
            'label': unicode(action.label),
            'in_progress_text': unicode(action.in_progress_text),
            'class': action.visual_class,
            'complete': action.complete,
        })
    return data
