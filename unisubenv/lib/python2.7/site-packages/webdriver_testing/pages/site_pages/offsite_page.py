#!/usr/bin/env python
from webdriver_testing.pages.site_pages import UnisubsPage


class OffsitePage(UnisubsPage):
    """Main page for all offsite testing to drive playback and menus.

    """
    _CAPTIONS = "span.unisubs-captionSpan"
    _WIDGET_MENU = "span.unisubs-tabTextchoose"

    def start_playback(self, video_position):
        self.browser.execute_script("return unisubs.widget.Widget.getAllWidgets()[%d].play();" % video_position)

    def pause_playback(self, video_position):
        self.browser.execute_script("unisubs.widget.Widget.getAllWidgets()[%d].pause()" % video_position)

    def open_subs_menu(self, video_position):
        self.browser.execute_script("unisubs.widget.Widget.getAllWidgets()[%d].openMenu()" % video_position)

    def displays_subs_in_correct_position(self):
        """Return true if subs are found in correct position on video.

        """
        size = self.get_size_by_css(self._CAPTIONS)
        height = size["height"]
        if 10 < height < 80:
            return True

    def open_offsite_page(self, page_url):
        self.browser.set_page_load_timeout(60)
        try:
            self.open_page(page_url)
        except:
            print "page didn't finish loading in 60 seconds, continuing..."
        self.wait_for_element_present(self._WIDGET_MENU)

    def pause_playback_when_subs_appear(self, video_position):
        self.scroll_to_video(video_position)
        self.wait_for_element_visible(self._CAPTIONS)
        self.pause_playback(video_position)

    def scroll_to_video(self, video_position):
        self.wait_for_element_present(self._WIDGET_MENU)
        elements_found = self.browser.find_elements_by_css_selector(
            self._WIDGET_MENU)
        elem = elements_found[video_position]
        elem.send_keys("PAGE_DOWN")
