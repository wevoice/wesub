#!/usr/bin/env python

from apps.webdriver_testing.page import Page

class EditorDialogs(Page):

    _DIALOG = 'div.unisubs-modal-widget-content'
    _WARNING = 'div.unisubs-modal-lang-content' #Resume editing
    #DIALOG TYPES
    _HOW_TO = 'div.unisubs-howtopanel'
    _TYPING = _DIALOG + '.unisubs-modal-widget-transcribe'
    _SYNCING = _DIALOG + '.unisubs-modal-widget-sync'
    _TITLE_DESCRIPTION = '.unisubs-help-heading'  #NOT GOOD
    _REVIEW = _DIALOG + '.unisubs-model-widget-review'
    _GUIDELINES = 'div.unisubs-guidelinespanel'
    _GUIDELINE_TEXT = _GUIDELINES + ' div p'


    _DONE = 'a.unisubs-done span'
    _SKIP = 'span.goog-checkbox'
    _CLOSE = 'span.unisubs-modal-widget-title-close'


    def wait_for_dialog_present(self):
        self.wait_for_element_present(self._DIALOG)


    def close_dialog(self):
        self.click_by_css(self._CLOSE)

    def continue(self):
        self.click_by_css(self._DONE)

    def continue_past_help(self):
        if self.is_element_present(self._HOW_TO):
            self.continue()

    





    

