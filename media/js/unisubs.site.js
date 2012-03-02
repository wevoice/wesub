// Universal Subtitles, universalsubtitles.org
// 
// Copyright (C) 2012 Participatory Culture Foundation
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see 
// http://www.gnu.org/licenses/agpl-3.0.html.

var Site = function(Site) {
    /*
     * This is the master javascript file for
     * the Universal Subtitles website.
     */

    var that = this;

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
        /*
         * These are reusable utilities that are
         * usually run on multiple pages. If you
         * find duplicate code that runs on multiple
         * pages, it should be converted to a
         * utility function in this object and
         * called from each of the specific views,
         * like this:
         *     
         *     that.Utils.chosenify();
         *
         */

        chosenify: function() {
            $('select', '.v1 .content').filter(function() {
                return !$(this).parents('div').hasClass('ajaxChosen');
            }).chosen().change(function() {
                $select = $(this);

                // New message
                if ($('body').hasClass('new-message')) {
                    $option = $('option:selected', $select);

                    if ($select.attr('id') === 'id_team') {
                        if ($option.val() !== '') {
                            $('div.recipient, div.or').addClass('disabled');
                            $('select#id_user').attr('disabled', 'disabled').trigger('liszt:updated');
                        } else {
                            $('div.recipient, div.or').removeClass('disabled');
                            $('select#id_user').removeAttr('disabled').trigger('liszt:updated');
                        }
                    }
                }
            });
        },
        resetLangFilter: function($select) {
            if (typeof $select == 'undefined') {
                $select = $('select#lang-filter');
            }
            if (window.REQUEST_GET_LANG) {
                $opt = $('option[id="lang-opt-' + window.REQUEST_GET_LANG + '"]');
            } else {
                $opt = $('option[id="lang-opt-any"]');
            }
            $select.children().removeAttr('selected');
            $opt.attr('selected', 'selected');
            $select.trigger('liszt:updated');
        }
    };
    this.Views = {
        /*
         * Each of these views runs on a specific
         * page on the Universal Subtitles site
         * (except for base, which runs on every
         * page that extends base.html)
         *
         * Adding a view is as simple as adding an
         * ID attribute to the specific page's <html>
         * element, and adding the corresponding view
         * below.
         */

        // Global
        base: function() {

            /*
             * TODO: The modules in this section need to
             * be pulled out into that.Utils and only
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

        // Public
        video_view: function() {
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

            $('.tabs').tabs();
            unisubs.messaging.simplemessage.displayPendingMessages();
        },

        // Teams
        team_applications: function() {
            that.Utils.chosenify();
        },
        team_members_list: function() {
            that.Utils.resetLangFilter();
            that.Utils.chosenify();
        },
        team_tasks: function() {
            $('a.action-assign').click(function(e) {

                $('div.assignee-choice').hide();

                $form = $(e.target).parents('.admin-controls').siblings('form.assign-form');

                $assignee_choice = $form.children('div.assignee-choice');
                $assignee_choice.fadeIn('fast');

                if (!window.begin_typing_trans) {
                    window.begin_typing_trans = $('option.begin-typing-trans').eq(0).text();
                }
                $select = $form.find('select');
                $select.children('option').remove();
                $select.append('<option value="">-----</option>');
                $select.append('<option value="">' + window.begin_typing_trans + '</option>');
                $select.trigger('liszt:updated');

                $chzn_container = $assignee_choice.find('.chzn-container');
                $chzn_container.css('width', '100%');

                $chzn_drop = $chzn_container.find('.chzn-drop');
                $chzn_drop.css('width', '99%');

                $chzn_input = $chzn_drop.find('input');
                $chzn_input.css('width', '82%');

                return false;
            });
            $('.assignee-choice a.cancel').click(function(e) {
                $(e.target).parents('.assignee-choice').fadeOut('fast');
                return false;
            });
            $('a.action-assign-submit').click(function(e) {
                $(e.target).closest('form').submit();
                return false;
            });
            $('a.assign-and-perform').click(function(e) {
                var $target = $(e.target);
                $target.text('Loading...');

                $.ajax({
                    url: window.ASSIGN_TASK_AJAX_URL,
                    type: 'POST',
                    data: {
                        task: $target.attr('data-id'),
                        assignee: window.ASSIGNEE
                    },
                    success: function(data, textStatus, jqXHR) {
                        $target.hide();

                        $li = $target.parent().siblings('li.hidden-perform-link');
                        $li.show();

                        $link = $li.children('a.perform');
                        $link.text('Loading...');
                        if ($link.attr('href') !== '') {
                            window.location = $link.attr('href');
                        } else {
                            $link.click();
                        }
                    }
                });

                return false;
            });
            $('div.member-ajax-chosen select', '.v1 .content').ajaxChosen({
                method: 'GET',
                url: '/en/teams/' + window.TEAM_SLUG + '/members/search/',
                dataType: 'json'
            }, function (data) {
                var terms = {};
                $.each(data.results, function (i, val) {
                    var can_perform_task = data.results[i][2];

                    if (can_perform_task) {
                        terms[data.results[i][0]] = data.results[i][1];
                    }
                });
                return terms;
            });

            unisubs.widget.WidgetController.makeGeneralSettings(window.WIDGET_SETTINGS);
            that.Utils.resetLangFilter($('select#id_task_language'));
            that.Utils.chosenify();
        },
        team_videos_list: function() {
            $form = $('form', 'div#remove-modal');

            $('a.remove-video').click(function() {
                $form.attr('action', $(this).siblings('form').attr('action'));
            });
            $form.submit(function() {
                var $checked = $('input[name="del-opt"]:checked', 'div#remove-modal');
                if ($checked.val() == 'total-destruction') {
                    $form.attr('action', $form.attr('action').replace('remove', 'delete'));
                    if (confirm('Are you sure you want to permanently delete this video? This action is irreversible.')) {
                        return true;
                    }
                    else {
                        return false;
                    }
                } else {
                    if (confirm('All open tasks for this video will be aborted, and in-progress subtitles will be published. Do you want to proceed?')) {
                        return true;
                    }
                    else {
                        return false;
                    }
                }
            });

            that.Utils.resetLangFilter();
            that.Utils.chosenify();
        },

        // Profile
        profile_dashboard: function() {
            unisubs.widget.WidgetController.makeGeneralSettings(window.WIDGET_SETTINGS);
        }
    };
};

$(function() {
    window.site = new Site();
    window.site.init();
});
