#!/usr/bin/env python

from webdriver_testing.pages.site_pages.profiles import ProfilePage

class ProfileDashPage(ProfilePage):
    """
    User Profile personal page.
    """

    _URL = "profiles/dashboard/"
    _CURRENT_TASKS = 'ul.tasks li'
    _VIDEO_ACTIVITY = 'div.section:nth-child(2) ul li'
    _TEAM_ACTIVITY = 'div.section:nth-child(3) ul li'

    def open_profile_dashboard(self):
        self.open_page(self._URL)

    def current_tasks(self):
        task_els = self.get_elements_list(self._CURRENT_TASKS)
        return [el.text for el in task_els]

    def video_activity(self):
        video_els = self.get_elements_list(self._VIDEO_ACTIVITY)
        return [el.text for el in task_els]

    def team_activity(self):
        team_els = self.get_elements_list(self._TEAM_ACTIVITY)
        return [el.text for el in team_els]
