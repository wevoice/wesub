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
Subtitle Workflows
==================

Subtitle workflows control how subtitle sets get edited and published.  In
particular they control:

- Work Modes -- Tweak the subtitle editor behavior (for example review mode)
- Actions -- User actions that can be done to subtitle sets (Publish, 
  Approve, Send back, etc).
- Permissions -- Who can edit subtitles, who can view private subtitles

.. autoclass:: Workflow
    :members: get_work_mode, get_actions, user_can_edit_subtitles,
              user_can_view_private_subtitles
.. autofunction:: get_workflow(video, language_code)

Work Modes
----------
.. autoclass:: WorkMode

Actions
-------

Actions are things things that users can do to a subtitle set other than
changing the actual subtitles.  They correspond to the buttons in the editor
at the bottom of the workflow session (publish, endorse, send back, etc).
Actions can occur alongside changes to the subtitle lines or independent of
them.

.. autoclass:: Action
   :members:

.. autoclass:: Publish

"""

from django.utils.translation import ugettext_lazy

from subtitles.exceptions import ActionError
from utils.behaviors import behavior

class Workflow(object):
    """
    Workflow
    --------

    A workflow class controls the overall workflow for editing and publishing
    subtitles.  Workflows control the work modes, actions, and permissions for
    a set of subtitles.

    By default, we use a workflow that makes sense for public videos -- Anyone
    can edit, the only action is Publish, etc.  However, other components can
    create custom workflows for specific videos/languages by:

    - Creating a Workflow subclass
    - Overriding :func:`get_workflow` and returning a custom workflow object
    """
    def __init__(self, video, language_code):
        self.video = video
        self.language_code = language_code

    def get_work_mode(self, user):
        """Get the editor work mode to use

        Args:
            user (User) -- user who is editing

        Returns:
            :class:`WorkMode` object to use
        """
        raise NotImplementedError()

    def get_actions(self, user):
        """Get available actions for a user

        Args:
            user (User) -- user who is editing

        Returns:
            list of :class:`Action` objects that are available to the user.
        """
        raise NotImplementedError()

    def lookup_action(self, user, action_name):
        for action in self.get_actions(user):
            if action.name == action_name:
                return action
        raise LookupError("No action: %s" % action_name)

    def perform_action(self, user, action_name, saved_version):
        action = self.lookup_action(user, action_name)
        subtitle_language = self.video.subtitle_language(self.language_code)
        action.perform(user, self.video, subtitle_language, saved_version)

    def user_can_view_private_subtitles(self, user):
        """Check if a user can view private subtitles

        Private subtitles are subtitles with visibility or visibility_override
        set to "private".  A typical use is to limit viewing of the subtitles
        to members of a team.

        Returns:
            True/False
        """
        raise NotImplementedError()

    def user_can_edit_subtitles(self, user):
        """Check if a user can edit subtitles

        Returns:
            True/False
        """

    def editor_data(self, user):
        """Get data to pass to the editor for this workflow."""
        return {
            'work_mode': self.get_work_mode(user).editor_data(),
            'actions': [action.editor_data() for action in
                        self.get_actions(user) ]
        }

@behavior
def get_workflow(video, language_code):
    """Get the workflow to use for a subtitle set

    This method uses the :doc:`behaviors <behaviors>` module, to allow
    other apps to override this and control the workflow for specific
    subtitles sets.  A typical example is the tasks system which creates a
    custom workflow for videos owned by tasks teams.
    """
    return DefaultWorkflow(video, language_code)

class WorkMode(object):
    """
    Work modes are used to change the workflow section of the editor and
    affect the overall feel of the editing session.  Currently we only have 2
    work modes:

    * .. autoclass:: NormalWorkMode
    * .. autoclass:: ReviewWorkMode
    """

    def editor_data(self):
        """Get data to send to the editor for this work mode."""
        raise NotImplementedError()

class NormalWorkMode(object):
    """The usual work mode with typing/syncing/review steps."""

    def editor_data(self):
        return {
            'type': 'normal',
        }

class ReviewWorkMode(object):
    """Review someone else's work (for example a review/approve task)

    Args:
        heading (str): heading to display in the workflow area
    """

    def __init__(self, heading):
        self.heading = heading

    def editor_data(self):
        return {
            'type': 'review',
            'heading': self.heading,
        }

class Action(object):
    """Base class for actions

    Other components can define new actions by subclassing Action, setting the
    class attributes, then implementing do_perform().

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

    def _check_can_perform(self, subtitle_language, saved_version):
        """Check if we can perform this action.

        Raises:
            ActionError -- this action can't be performed
        """
        if self.complete:
            if saved_version:
                version = saved_version
            else:
                version = subtitle_language.get_tip()
            if (version is None or not version.has_subtitles
                or not version.is_synced()):
                raise ActionError('Subtitles not complete')

    def perform(self, user, video, subtitle_language, saved_version):
        """Perform this action

        Args:
            user (User): User performing the action
            video (Video): Video being changed
            subtitle_language (SubtitleLanguage): SubtitleLanguage being
                changed
            saved_version (SubtitleVersion or None): new version that was
                created for subtitle changes that happened alongside this
                action.  Will be None if no changes were made.
        """
        self._check_can_perform(subtitle_language, saved_version)
        if self.complete is not None:
            subtitle_language.subtitles_complete = self.complete
        self.do_perform(user, video, subtitle_language, saved_version)
        subtitle_language.save()

    def do_perform(self, user, video, subtitle_language, saved_version):
        """
        Does the work to perform this action.  Subclasses must implement this
        method.

        Notes:
            - If complete is set to True or False, we will already have
              updated subtitles_complete at this point.
            - We will save the SubtitleLanguage after do_perform runs, so
              don't save it yourself.
        """
        raise NotImplementedError()

    def editor_data(self):
        """Get a dict of data to pass to the editor for this action."""
        return {
            'name': self.name,
            'label': unicode(self.label),
            'in_progress_text': unicode(self.in_progress_text),
            'class': self.visual_class,
            'complete': self.complete,
        }

class Publish(Action):
    """Publish action

    Publish sets the subtitles_complete flag to True
    """
    name = 'publish'
    label = ugettext_lazy('Publish')
    in_progress_text = ugettext_lazy('Saving')
    visual_class = 'endorse'
    complete = True

    def do_perform(self, user, video, subtitle_language, saved_version):
        # complete=True causes all the work to be done
        pass

class Unpublish(Action):
    """Unpublish action

    Unpublish sets the subtitles_complete flag to False
    """
    name = 'unpublish'
    label = ugettext_lazy('Unpublish')
    in_progress_text = ugettext_lazy('Saving')
    visual_class = 'send-back'
    complete = False

    def do_perform(self, user, video, subtitle_language, saved_version):
        # complete=False causes all the work to be done
        pass

class APIComplete(Action):
    """Action that handles complete=True from the API

    We have some strange rules here to maintain API compatibility:
        - If the subtitle set is synced or there are no subtitles, then we set
          subtitles_complete=True
        - If not, we set to to False
    """
    name = 'api-complete'
    label = ugettext_lazy('API Complete')
    in_progress_text = ugettext_lazy('Saving')
    visual_class = 'endorse'
    complete = None

    def do_perform(self, user, video, subtitle_language, saved_version):
        # we only use this action from pipeline.add_subtitles, so we can
        # assume saved_version is not None
        if (saved_version is None or not saved_version.is_synced()):
            subtitle_language.subtitles_complete = False
        else:
            subtitle_language.subtitles_complete = True

class DefaultWorkflow(Workflow):
    def get_work_mode(self, user):
        return NormalWorkMode()

    def get_actions(self, user):
        return [Publish()]

    def user_can_view_private_subtitles(self, user):
        return user.is_staff

    def user_can_edit_subtitles(self, user):
        return True
