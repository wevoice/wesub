from dialogs import EditorDialogs
import codecs
import os
import sys
import time

class SubtitleEditor(EditorDialogs):

    _EDITOR = 'div.unisubs-modal-widget'

    #UNISUBS ON-VIDEO CONTROLS
    _VIDEO_PLAYBACK = 'div.unisubs-videoControls'
    _PLAY = 'span.unisubs-playPause.play'
    _PAUSE = 'span.unisubs-playPause.pause'
    _BUFFERED = 'div.unisubs-buffered' # width 250 is 100% buffered


    #SUBS ENTRY AND DISPLAY (LEFT SIDE)
    _TEXT_INPUT = 'textarea.goog-textarea.trans'
    _ACTIVE_SUB_EDIT = 'span.unisubs-title textarea'
    _SUBS = 'ul.unisubs-titlesList li span.unisubs-title span:nth-child(1)'
    _TIMINGS = 'ul.unisubs-titlesList li span.unisubs-timestamp'
    _REVIEW_TIMINGS = 'span.unisubs-timestamp-time'
    _CURRENT_CAPTION = 'span.unisubs-captionSpan'

    _TRANSCRIBE_PAGE_TIMINGS = 'span.unisubs-timestamp-time-fixed'

    #CONTROL BUTTON (RIGHT SIDE)
    _SYNC = 'div.unisubs-begin span:nth-child(2)'
    _PLAY_PAUSE = 'div.unisubs-play span'
    _SKIP_BACK = 'div.unisubs-skip span.unisubs-control'
    _RESTART = 'a.unisubs-restart'
    _PREVIOUS_STEP = 'a.unisubs-backTo'

    #EXTRA OPTIONS
    _SAVE_AND_EXIT = 'div.unisubs-saveandexit a span'
    _DOWNLOAD_SUBTITLES = 'a.unisubs-download-subs'
    _DOWNLOAD_FORMAT = 'select.copy-dialog-select'


    def type_subs(self, subs_file=None):
        typed_sub_list = []
        if not subs_file:
            subs_file = os.path.join(os.path.dirname
                (os.path.abspath(__file__)), 'default_sub_text.txt')
        for i, line in enumerate(codecs.open(subs_file, encoding='utf-8')):
            self.type_by_css(self._TEXT_INPUT, line)
            typed_sub_list.append(line.strip())
        return typed_sub_list

    def edit_subs(self, subs_file=None):
        typed_sub_list = []
        if not subs_file:
            subs_file = os.path.join(os.path.dirname
                (os.path.abspath(__file__)), 'default_sub_text.txt')

        existing_subs = self.get_elements_list(self._SUBS)
        for i, line in enumerate(codecs.open(subs_file, encoding='utf-8')):
            existing_subs[i].click()
            self.clear_text(self._ACTIVE_SUB_EDIT)
            self.type_by_css(self._ACTIVE_SUB_EDIT, line + '\n')
            typed_sub_list.append(line.strip())
        return typed_sub_list


    def play(self):
        self.wait_for_element_present(self._VIDEO_PLAYBACK)
        if self.is_element_present(self._PLAY):
            print 'starting playback'
            self.click_by_css(self._PLAY)

    def pause(self):
        self.wait_for_element_present(self._VIDEO_PLAYBACK)
        if self.is_element_present(self._PAUSE):
            print 'pausing playback'
            self.click_by_css(self._PAUSE)

    def buffer_video(self):
        """Start and Stop playback to get the video buffered up to about 30%'
     
        """
        self.play()
        time.sleep(4)
        self.pause()
        buffered = 0
        time.sleep(4)
        if self.is_element_present(self._BUFFERED):
            sys.stdout.write('buffering.')
            while buffered < 50:
                buffered = self.get_size_by_css(self._BUFFERED)['width']
                time.sleep(2)
                sys.stdout.write('.')
        else:
            time.sleep(10) #If no buffer, give it 10 secs to load a bit.
      

    def sync_subs(self, num_subs):
        """Syncs the given number of subtitles.

        """
        print '## SYNCING SUBS'
        self.buffer_video()
        self.play()
        time.sleep(2)
        self.click_by_css(self._SYNC)

        for x in range(num_subs):
            time.sleep(3)
            self.click_by_css(self._SYNC)
        time.sleep(1)
        self.pause()
        time.sleep(2)

    def sub_timings(self, check_step=None):
        if check_step:
            timing_element = self._REVIEW_TIMINGS
        else:
            timing_element = self._TIMINGS
        timing_list = []
        self.wait_for_element_present(timing_element)
        timing_els = self.browser.find_elements_by_css_selector(
            timing_element)
        for el in timing_els:
            timing_list.append(el.text.strip())
        return timing_list

            
    def save_and_exit(self):
        self.page_down(self._SAVE_AND_EXIT)
        self.click_by_css(self._SAVE_AND_EXIT)
        #self.mark_subs_complete()
        self.click_saved_ok()


    def subtitles_list(self):
        time.sleep(3)
        sub_list = []
        subtitle_els = self.browser.find_elements_by_css_selector(self._SUBS)
        for el in subtitle_els:
            sub_list.append(el.text.strip())
        return sub_list

    def download_subtitles(self, sub_format='SRT'):
        self.click_by_css(self._DOWNLOAD_SUBTITLES)
        self.select_option_by_text(self._DOWNLOAD_FORMAT, sub_format)
        # don't ever wait more than 15 seconds for this
        # but keep pooling for a terminating value
        start_time = time.time()
        while time.time() - start_time < 15:
            time.sleep(2)
            stored_subs = self.browser.execute_script(
            "return document.getElementsByTagName('textarea')[0].value")
            # server errored out
            if stored_subs == "Something went wrong, we're terribly sorry.":
                raise ValueError("Call to convert formats failed")
            # server hasn't returned yet
            elif stored_subs and stored_subs.startswith("Processing.") is False:
                break
        else:
            raise ValueError("More than 15 seconds passed, and subs weren't converted")
        #self.close_lang_dialog()
        return stored_subs

    def submit(self, complete=True):
        self.continue_to_next_step()
        time.sleep(2)
        self.mark_subs_complete(complete)
        time.sleep(2)
        self.click_saved_ok()
        


