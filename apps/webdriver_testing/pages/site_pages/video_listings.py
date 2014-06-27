#!/usr/bin/env python
from webdriver_testing.pages.site_pages import UnisubsPage
from video_page import VideoPage


class VideoListings(UnisubsPage):
    """
    The layout of vidoes are the same on the watch pages and search results pages.  
    This page has the elements common to the video layout.
    """

    _VIDEOS = "ul.video_list li.Video_list_item"  
    _VIDEO_THUMB = "span.video_thumb span.clip"
    _VIDEO_VIEWS = "ul.details li.views"
    _VIDEO_LANGS = "ul.details li.languages"
    _EMPTY = 'p.empty'


    def _videos_on_page(self):
        video_els = self.get_elements_list(self._VIDEOS)
        return video_els


    def _video_list_item(self, title):
        """Return the element of video by title
        """
        video_elements = self._videos_on_page()
        for el in video_elements:
            vid_title = el.find_element_by_css_selector("a").get_attribute(
                'title')
            if title == vid_title:
                return el
        else:
            return None
 
    def page_has_video(self, title):
        if self._video_list_item(title):
            return True

    def video_has_default_thumb(self, title):
        video_el =  self._video_list_item(title)
        thumb_el = video_el.find_element_by_css_selector(self._VIDEO_THUMB 
            + " img")
        img_link = thumb_el.get_attribute("src")
        if  "video-no-thumbnail-small.png" in img_link:
            return True

    def click_thumb(self, title):
        video_el =  self._video_list_item(title)
        thumb_el = video_el.find_element_by_css_selector(self._VIDEO_THUMB)
        thumb_el.click()
        return VideoPage(self.testcase)


    def num_views(self, title):
        video_el = self._video_list_item(title)
        return video_el.find_element_by_css_selector(self._VIDEO_VIEWS).text

    def num_languages(self, title):
        video_el = self._video_list_item(title)
        return video_el.find_element_by_css_selector(self._VIDEO_LANGS + 
            ' span').text

    def page_videos(self):
        video_els = self._videos_on_page()
        title_list = []
        for el in video_els:
            vid_title = el.find_element_by_css_selector("a").get_attribute(
                    'title')
            print vid_title
            title_list.append(vid_title)
        if 'About Amara' in title_list:
            title_list.remove('About Amara') #Video isn't always present in index.
        return title_list

        
