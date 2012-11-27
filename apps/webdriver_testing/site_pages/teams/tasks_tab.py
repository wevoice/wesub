#!/usr/bin/env python
from apps.webdriver_testing.site_pages.a_team_page import ATeamPage
import time

class TasksTab(ATeamPage):
    """Actions for the Videos tab of a Team Page.

    """
    _URL = 'teams/%s/tasks/'
    _SEARCH = 'form.search input[name="q"]'
    _SEARCHING_INDICATOR = "img.placeholder"
    _NO_RESULTS = 'p.empty'

    _TASK_TITLE = 'h3' # title is an attribute of a
    _TASK_THUMB = 'ul.tasks li a.thumb'

    _FILTERED_VIDEO = 'p.view-notice strong'

   #ERRORS
    _ERROR = '.errorlist li'
 

    #TASK OPTIONS
    _PERFORM = 'div.action-group h5' #Opens on hover

    def open_tasks_tab(self, team):
        """Open the team with the provided team slug.

        """
        self.open_page(self._URL % team)

    def search(self, search_text):
        self.wait_for_element_present(self._SEARCH)
        self.submit_form_text_by_css(self._SEARCH, search_text)
        self.wait_for_element_not_visible(self._SEARCHING_INDICATOR)



    def _hover_perform(self): 
        """Hover over 1st displayed task.

        """
        self.wait_for_element_present(self._PERFORM)
        self.click_by_css(self._PERFORM)
 

 
    def click_perform_task_action(self, action):
        """Hover over the task perform and choose the action link.

        Current options are 'Start now', 'Upload draft, Resume'
        """
        url = self.get_element_attribute('a.perform', 'href')
        print url

    def filtered_video(self):
        return self.get_text_by_css(self._FILTERED_VIDEO)


 

        
    
