var Site = function(Site) {

    this.init = function() {

        // Global cached jQuery objects
        this.$html = $('html');
        this.$body = $('html');

        // Base JS (any page that extends base.html)
        if (this.$html.hasClass('base')) {
            this.Views['base']();
        }

        // Page specific JS
        if (this.$html.attr('id')) {
            this.Views[this.$html.attr('id')]();
        }

    };
    this.Utils = {
        resetLangFilter: function() {
            $select = $('select#lang-filter');
            if (window.request_get_lang) {
                $opt = $('option[id="lang-opt-' + window.request_get_lang + '"]');
            } else {
                $opt = $('option[id="lang-opt-any"]');
            }
            $select.children().removeAttr('selected');
            $opt.attr('selected', 'selected');
            $select.trigger('liszt:updated');
        }
    };
    this.Views = {
        base: function() {

            /*
             * TODO: The modules in this section need to be
             * pulled out into individual sub-views and only
             * initialized on pages that use them.
             */
            if ($('.abbr').length) {
                $('.abbr').each(function(){
                    var container = $(this);
                    var content = $(this).children('div');
                    var oheight = content.css('height', 'auto').height();
                    content.css('height','6em');
                    $(this).find('.expand').live('click', function(e){
                        e.preventDefault();
                        if(container.hasClass('collapsed')){
                            content.animate({
                                height: oheight
                            }, 'fast');
                            $(this).text('Collapse ↑');
                        } else {
                            content.animate({
                                height: '6em'
                            }, 'fast');
                            $(this).text('Show all ↓');
                        }
                        container.toggleClass('collapsed expanded');
                    });
                });
            }
            if ($('#sort-filter').length) {
                $('#sort-filter').click(function(e) {
                    e.preventDefault();
                    $('.filters').toggle();
                    $(this).children('span').toggleClass('open');
                });
                $('select', '.filters').change(function(e) {
                    window.location = $(this).children('option:selected').attr('value');
                });
            }
            if ($('a.open-modal').length) {
                $('a.open-modal').live('click',function(e){
                    e.preventDefault();
                    $target = $($(this).attr('href'));
                    $target.show();

                    $('body').append('<div class="well"></div>');

                    $target.click(function(event){
                        event.stopPropagation();
                    });
                    $('html').bind('click.modal', function() {
                        closeModal($target);
                    });
                });
                $('.action-close, .close', '.bootstrap').click(function(){
                    closeModal($(this).parents('.modal'));
                    return false;
                });
                function closeModal(e) { 
                    e.hide();
                    $('body div.well').remove();
                    $('html').unbind('click.modal');
                }
            }
            $.fn.tabs = function(options){
                this.each(function(){
                    var $this = $(this);
                    
                    var $last_active_tab = $($('li.current a', $this).attr('href'));
                    $('a', $this).add($('a.link_to_tab')).click(function(){
                        var href = $(this).attr('href');
                        $last_active_tab.hide();
                        $last_active_tab = $(href).show();
                        $('li', $this).removeClass('current');
                        $('a[href='+href+']', $this).parent('li').addClass('current');
                        document.location.hash = href.split('-')[0];
                        return false;
                    });            
                });
                if (document.location.hash){
                    var tab_name = document.location.hash.split('-', 1);
                    if (tab_name) {
                        $('a[href='+tab_name+'-tab]').click();
                        document.location.href = document.location.href;
                    }
                }
                return this;        
            };
            function addCSRFHeader($){
                /* Django will guard against csrf even on XHR requests, so we need to read
                   the value from the cookie and add the header for it */
                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        function getCookie(name) {
                            var cookieValue = null;
                            if (document.cookie && document.cookie !== '') {
                                var cookies = document.cookie.split(';');
                                for (var i = 0; i < cookies.length; i++) {
                                    var cookie = jQuery.trim(cookies[i]);
                                    // Does this cookie string begin with the name we want?
                                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                                        break;
                                    }
                                }
                            }
                            return cookieValue;
                        }
                        if (!((/^http:.*/).test(settings.url) || (/^https:.*/).test(settings.url))) {
                            // Only send the token to relative URLs i.e. locally.
                            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                        }
                    }
                });
            }
            $('#closeBut').click(function(){
                $('#messages').remove();
                return false;
            });
            $('li.search input').keypress(function(e) {
                if ((e.which && e.which == 13) || (e.keyCode && e.keyCode == 13)) {
                    $('li.search form').submit();
                    return false;
                }
                else
                    return true;
            });
            jQuery.Rpc.on('exception', function(e){
                jQuery.jGrowl.error(e.message);
            });
            if (window.OLD_MODAL) {
                $.mod();
                $.metadata.setType("attr", "data");
            }

            window.usStartTime = (new Date()).getTime();
            window.addCSRFHeader = addCSRFHeader;
            addCSRFHeader($);
        },
        home: function() {

        },
        members_list: function() {
            site.Utils.resetLangFilter();
        },
        video_view: function() {
            $('.tabs').tabs();

            $('.add_subtitles').click(function() {
                widget_widget_div.selectMenuItem(
                unisubs.widget.DropDown.Selection.IMPROVE_SUBTITLES);
                return false;
            });
            $('.add-translation-behavior').click(function() {
                widget_widget_div.selectMenuItem(
                unisubs.widget.DropDown.Selection.ADD_LANGUAGE);
                return false;
            });
            $('.edit-title').click( function() {
                $('#edit-title-dialog .title-input').val($('.title-container').html());
            });
            $('#edit-title-dialog .save-title').click(function() {
                var title = $('#edit-title-dialog .title-input').val();
                if (title) {
                    $('.title-container').html(title).hide().fadeIn();
                    VideosApi.change_title_video(window.VIDEO_ID, title, function(response) {
                        if (response.error) {
                            $.jGrowl.error(response.error);
                        } else {
                            $('.title-container').html(title);
                            document.title = title + ' | Universal Subtitles';
                        }
                    });
                    $('#edit-title-dialog').modClose();
                } else {
                    $.jGrowl.error(window.TITLE_ERROR);
                }
            });

            unisubs.messaging.simplemessage.displayPendingMessages();

            if (window.TASK) {
                var videoSource = unisubs.player.MediaSource.videoSourceForURL('{{ task.team_video.video.get_video_url }}');
                var opener = new unisubs.widget.SubtitleDialogOpener(
                                     window.TASK_TEAM_VIDEO_ID,
                                     window.TASK_TEAM_VIDEO_URL,
                                     videoSource,
                                     null,
                                     null);
                opener.showStartDialog();
            }
        }
    };
};

$(function() {
    window.site = new Site();
    window.site.init();
});
