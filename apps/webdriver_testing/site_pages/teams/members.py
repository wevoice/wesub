#!/usr/bin/env python
import time
from nose.tools import assert_equals
from nose.tools import assert_true
from ..a_team_page import ATeamPage

class MembersTab(ATeamPage):

    _URL = "teams/%s/members/"
    _USERNAME = "ul.members.listing li h3 a"
    _USER_LANGS = "ul.members.listing li h3 span.descriptor"
    _ROLE = "ul.members.listing li p"
    _ACTIONs = "ul.members.listing li ul.actions li"
    _INVITE_MEMBERS = "div.tools.group a[href*='members/invite']"

    #INVITATION FORM (NEARLY IMPOSSIBLE TO DEAL With USERNAME via UI
    _INVITEE_USERNAME = ""
    _INVITEE_MESSAGE = ""
    _INVITEE_ROLE = ""
    _INVITATION_SEND = ""

    def user_link(self):
        return self.get_element_attribute(self._USERNAME, 'href')

    def user_languages(self):
        language_list = []
        els = self.browser.find_elements_by_css_selector(self._USER_LANGS)
        for el in els:
            language_list.append(el.text)
        return language_list

    def user_role(self):
        return self.get_text_by_css(self._ROLE)

    def invite_users(self, **kwargs):
        assert_false("This needs to be implemented, just the ui kinda sucks for selenium")

        
    def member_search(self, team_slug, query):
        team_url = self._URL % team_slug
        search_url = "%s?q=%s" %(team_url, query)
        print search_url
        self.open_page(search_url)

    def lang_search(self, team_slug, lang):
        team_url = self._URL % team_slug
        search_url = "%s?lang=%s" %(team_url, lang)
        self.open_page(search_url)






        

