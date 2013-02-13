#!/usr/bin/env python
from apps.webdriver_testing.pages.site_pages.teams import ATeamPage
import time

class TasksTab(ATeamPage):
    """Actions for the Videos tab of a Team Page.

    """
    _URL = 'teams/%s/tasks/'
    _SEARCH = 'form.search input[name="q"]'
    _SEARCHING_INDICATOR = "img.placeholder"
    _NO_RESULTS = 'p.empty'


    _TASK = 'ul.tasks > li'
    _TASK_KIND = 'h3' # title is an attribute of a
    _TASK_VIDEO = 'p a'
    _ASSIGNEE = 'ul.actions li h4'
    _TASK_TRIGGER = 'h5.trigger'
    _TASK_THUMB = 'a.thumb'

    _FILTERED_VIDEO = 'p.view-notice strong'

    _ADD_TASK = "a.button[href*='create-task']"

    #CREATE TASK FORM
    _TASK_TYPE = 'select#id_type'
    _TASK_ASSIGNEE = 'div#id_assignee_chzn'
    _TASK_SAVE = "div.submit button"

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

    def _task_info(self):
        task_els = self.get_elements_list(self._TASK)
        task_list = []
        for el in task_els:
            task = dict(
                kind = el.find_element_by_css_selector(self._TASK_KIND).text,
                video =  el.find_element_by_css_selector(self._TASK_VIDEO).text,
                assignee = el.find_element_by_css_selector(self._ASSIGNEE).text,
                trigger = el.find_element_by_css_selector(self._TASK_TRIGGER)
                )
            task_list.append(task)
        return task_list

    def task_present(self, task_type, title):
        all_tasks = self._task_info()
        for task in all_tasks:
            if task_type in task['kind'] and title in task['video']:
                return True


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


    def add_task(self, task_type=None, task_assignee=None):
        self.click_by_css(self._ADD_TASK)
        if task_type:
            self.select_option_by_text(self._TASK_TYPE, task_type)
        if task_assignee:
            self.select_from_chosen(self._TASK_ASSIGNEE, task_assignee)
        
        self.submit_by_css(self._TASK_SAVE)

 

 

        
    
