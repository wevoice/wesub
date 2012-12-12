#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Basic webdriver commands used in all pages.

"""

import time
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.keys import Keys


class Page(object):
    """Basic webdriver commands available to all pages.

    All pages inherit from Page.

    """
    _DEBUG_ERROR = ".exception_value"
    _MULTIPLE_ELS = "More than 1 of this element was found on the page."

    def __init__(self, testsetup):
        self.browser = testsetup.browser  # BROWSER TO USE FOR TESTING
        self.base_url = testsetup.base_url
        self.testcase = testsetup

    def _safe_find(self, element):
        self.wait_for_element_present(element)
        elem = self.browser.find_element_by_css_selector(element)
        return elem

    def quit(self):
        """Quit the browser.

        """
        self.browser.quit()

    def close_browser(self):
        self.browser.close()

    def page_refresh(self):
        self.browser.refresh()

    def page_error(self):
        """Return django debug page error information.

        """
        error_text = None
        if self.is_element_present(self._DEBUG_ERROR):
            error_text = self.get_text_by_css(self._DEBUG_ERROR)
        return [error_text, self.current_url()]

    def current_url(self):
        """Return the current page url.

        """
        return self.browser.current_url

    def handle_js_alert(self, action):
        """Accept or reject js alert.

        """
        try:
            print 'Got an alert dialog'
            time.sleep(2)
            a = self.browser.switch_to_alert()
            if action == "accept":
                a.accept()
            elif action == "reject":
                a.dismiss()
        except:
            self.record_error('failed handling the expected alert')

    def check(self, element):
        """Check the box for the element provided by css selector.

        """
        el = self._safe_find(element)
        if not el.is_selected():
            el.click()

    def uncheck(self, element):
        """Uncheck the box for the element provided by css selector.

        """

        el = self._safe_find(element)
        if el.is_selected():
            el.click()

    def select_option_by_text(self, element, text):
        """Select an option based on text of the css selector.

        """
        select = Select(self._safe_find(element))
        select.select_by_visible_text(text)

    def hover_by_css(self, page_element):
        """Hover over element of provided css selector.

        """
        element = self._safe_find(page_element)
        mouseAction = webdriver.ActionChains(self.browser)
        mouseAction.move_to_element(element).perform()





    def click_item_from_pulldown(self, menu_el, menu_item_el):
        """Open a hover pulldown and choose a displayed item.

        """
        self.browser.implicitly_wait(5)        
        menu_element = self._safe_find(menu_el)
        menu_item_element = self._safe_find(menu_item_el)
        mouseAction = (webdriver.ActionChains(self.browser)
                       .move_to_element(menu_element)
                       .click(menu_item_element)
                       .perform())

    def click_item_after_hover(self, menu_el, menu_item_el):
        """Open a hover pulldown and choose a displayed item.

        """
        self.browser.implicitly_wait(5)        
        menu_element = self._safe_find(menu_el)
        mouseAction = (webdriver.ActionChains(self.browser)
                       .move_to_element(menu_element)
                       #.click(menu_item_element)
                       .perform())
        menu_item_element = self._safe_find(menu_item_el)
        self.wait_for_element_visible(menu_item_el)
        mouseAction = (webdriver.ActionChains(self.browser)
                       .move_to_element(menu_item_element)
                       .click(menu_item_element)
                       .perform())


    def hover_by_element(self, webdriver_object, page_element):
        """Find the css element below the webdriver element object and hover.

        """
        element = webdriver_object.find_element_by_css_selector(page_element)
        mouse = webdriver.ActionChains(self.browser)
        mouse.move_to_element(element).perform()

    def click_by_css(self, element, wait_for_element=None):
        """click based on the css given.

        kwargs no_wait, then use send keys to no wait for page load.
               wait_for_element, wait for a passed in element to display
        """
        elem = self.wait_for_element_present(element)
        elem.click()
        if wait_for_element:
            self.wait_for_element_present(wait_for_element)

    def clear_text(self, element):
        """Clear text of css element in form.

        """
        elem = self._safe_find(element)
        elem.clear()



    def click_link_text(self, text, wait_for_element=None):
        """Click link text of the element exists, or fail.

        """
        try:
            elem = self.browser.find_element_by_link_text(text)
        except Exception as e:
            self.record_error(e)
        elem.click()
        if wait_for_element:
            self.wait_for_element_present(wait_for_element)

    def click_link_partial_text(self, text, wait_for_element=None):
        """Click by partial link text or report error is not present.

        """
        try:
            elem = self.browser.find_element_by_partial_link_text(text)
        except Exception as e:
            self.record_error(e)
        elem.click()
        if wait_for_element:
            self.wait_for_element_present(wait_for_element)

    def has_link_text(self, text, wait_for_element=None):
        """Return whether or not partial link text is present.
        """
        try:
            elem = self.browser.find_element_by_link_text(text)
            return True
        except NoSuchElementException:
            return False


    def type_by_css(self, element, text):
        """Enter text for provided css selector.

        """
        elem = self.wait_for_element_present(element)
        elem.send_keys(text)

    def type_special_key(self, key_name, element="body"):
        """Type a special key -see selenium/webdriver/common/keys.py.
   
        ex: ARROR_DOWN, TAB, ENTER, SPACE, DOWN... 
        If no element is specified, just send the key press to the body.
        """
        elem = self._safe_find(element)
        elem.send_keys(key_name)


    def get_text_by_css(self, element):
        """Get text of given css selector.

        """
        elem = self.wait_for_element_present(element)
        return elem.text

    def get_size_by_css(self, element):
        """Return dict of height and width of element by css selector.

        """
        elem = self._safe_find(element)
        return elem.size

    def submit_form_text_by_css(self, element, text):
        """Submit form using css selector for form element.
 
        """
        elem = self._safe_find(element)
        elem.send_keys(text)
        time.sleep(1)
        elem.submit()

    def is_element_present(self, element):
        """Return when an element is found on the page.

        """
        try:
            elements_found = self.browser.find_elements_by_css_selector(
                element)
        except NoSuchElementException:
            return False
        return True

    def count_elements_present(self, element):
        """Return the number of elements (css) found on page.

        """
        try:
            elements_found = self.browser.find_elements_by_css_selector(
                element)
        except NoSuchElementException:
            return 0
        return len(elements_found)

    def is_element_visible(self, element):
        """Return whether element (by css) is visible on the page.

        """
        if not self.is_element_present(element):
            return False
        else:
            return any([e.is_displayed() for e in
                        self.browser.find_elements_by_css_selector(element)])

    def is_unique_text_present(self, element, text):
        """Return whether element (by css) text is unique).

        """
        try:
            elements_found = self.browser.find_elements_by_css_selector(
                element)
        except NoSuchElementException:
            return False
        if len(elements_found) > 1:
            self.record_error(MULTIPLE_ELS % element)
        else:
            element_text = self.browser.find_element_by_css_selector(
                element).text
            if str(element_text) == text:
                return True
            else:
                return False

    def is_text_present(self, element, text):
        """Return whether element (by css) text is present.

        """
        try:
            elements_found = self.browser.find_elements_by_css_selector(
                element)
        except NoSuchElementException:
            return False
        for elem in elements_found:
            if text == elem.text:
                return True
            else:
                return False

    def verify_text_present(self, element, text):
        """Verify element (by css) text is present.

        """
        elements_found = self.browser.find_elements_by_css_selector(element)
        if len(elements_found) > 1:
            self.record_error(MULTIPLE_ELS % element)
        else:
            element_text = elements_found[0].text
            if text == element_text:
                return True
            else:
                self.record_error('found:' + element_text +
                                'but was expecting: ' + text)
                return False

    def wait_for_element_present(self, element):
        """Wait for element (by css) present on page, within 20 seconds.

        """
        for i in range(20):
            try:
                time.sleep(1)
                if self.is_element_present(element):
                    return self.browser.find_element_by_css_selector(element) 
            except:
                pass
        else:
            self.record_error("Element %s is not present." % element)
    
    def wait_for_element_not_present(self, element):
        """Wait for element (by css) to disappear on page, within 20 seconds.

        """

        for i in range(20):
            try:
                time.sleep(1)
                if self.is_element_present(element) is False:
                    break
            except:
                pass
        else:
            self.record_error("Element %s is still present." % element)
 
    def wait_for_text_not_present(self, text):
        """Wait for text to disappear on page, within 20 seconds.

        """
        for i in range(20):
            try:
                time.sleep(1)
                if self.is_text_present(text) is False:
                    break
            except:
                pass
        else:
            self.record_error('The text: %s is still present after 20 seconds' % text)

    def wait_for_element_visible(self, element):
        """Wait for element (by css) visible on page, within 20 seconds.

        """

        for i in range(20):
            time.sleep(1)
            if self.is_element_visible(element):
                break
        else:
            self.record_error('The element %s is not visible after 20 seconds' % element)

    def wait_for_element_not_visible(self, element):
        """Wait for element (by css) to be hidden on page, within 20 seconds.

        """
        for i in range(20):
            try:
                time.sleep(1)
                self.browser.find_elements_by_css_selector(
                    element).is_displayed()
            except:
                break
        else:
            self.record_error('The element: %s is still visible after 20 seconds' % element)

    def get_absolute_url(self, url):
        """Return the full url.

        """
        if url.startswith("http"):
            full_url = url
        else:
            full_url = str(self.base_url) + url
        return full_url

    def get_element_attribute(self, element, html_attribute):
        """Return the attribute of an element (by css).
  
        """
        try:
            elements_found = self.browser.find_elements_by_css_selector(
                element)
        except NoSuchElementException:
            self.record_error("%s does not exist on the page" % element)
        if len(elements_found) > 1:
            self.record_error(MULTIPLE_ELS % element)
        return elements_found[0].get_attribute(html_attribute)

    def get_elements_list(self, element):
        """Return the list of elements (webdriver objects).
  
        """
        self.wait_for_element_present(element)
        elements_found = self.browser.find_elements_by_css_selector(element)
        return elements_found

    def get_sub_elements_list(self, parent_el, child_el):
        """If the parent element exists, return a list of the child elements.
  
        """
        if isinstance(parent_el, basestring):
            if not self.is_element_present(parent_el):
                return None
            else: 
                parent_el = self.browser.find_element_by_css_selector(parent_el)
        try:
            print 'looking for %s under %s' % (child_el, parent_el.tag_name)
            child_els = parent_el.find_elements_by_css_selector(child_el)
            return child_els
        except NoSuchElementException:
            print 'Did not find any elements'
            return None



    def open_page(self, url):
        """Open a page by the full url.

        """
        self.browser.get(self.get_absolute_url(url))

    def go_back(self):
        """Go back to previous page.

        """
        self.browser.back()

    def page_down(self, elements):
        """Page down to element (by css).

        elements are a list not a single element to try to page down.
        """
        if not isinstance(elements, basestring):
            for x in elements:
                if self.is_element_present(x):
                    elem = self.browser.find_element_by_css_selector(x)
                    break
        else:
            if self.is_element_present(elements):
                elem = self.browser.find_element_by_css_selector(elements)
        try:
            elem.send_keys("PAGE_DOWN")
        except: 
            pass #Stupid but Chrome has page down issues.

    def select_from_chosen(self, ui_elem, values):
        """modified from https://gist.github.com/1768479.
        
        Given the id and value, select the option from the chozen-styled menu.
        This is a total pain in the ass.
        """
        

        #Find all the chosen parts and pieces.
        chosen_selects = self.browser.find_elements_by_css_selector(ui_elem)
        select = chosen_selects[0]
        select_id = select.get_attribute("id")
        chosen = self.browser.find_element_by_id(select_id + '_chzn')
        results = chosen.find_elements_by_css_selector(".chzn-results li")
        
        #Work for either a simple string or a list of options.
        if isinstance(values, basestring):
            values = [values]

        #Choose the chosen ones.
        for value in values:
            found = False
            for result in results:
                if result.text == value:
                    found = True
                    print '##### found it!!! %s' % value
                    break

            #In some cases (team videos tab) it would choose the option after the 
            # the one that was specified.  So paging down and not doing the found_el
            # resolves that issue.  However, sometimes the page down gets a
            # MoveTargetOutOfBoundsException - but works the other way. So going to 
            # try one then do the other.

            if found:
                try:
                    result.send_keys("PAGE_DOWN")
                except:
                    pass #this is stupid but Chrome won't page down.
                try:
                    result.click()
                except:
                    found_el = chosen.find_element_by_css_selector("input").click()
                    result.click()

    def record_error(self, e=None):
        """
            Records an error.
        """
        if not e:
            e = 'webdriver error' + self.browser.current_url
        print '-------------------'
        print 'Error at ' + self.browser.current_url
        print '-------------------'
        raise ValueError(str(e))


