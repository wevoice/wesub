// Amara, universalsubtitles.org
//
// Copyright (C) 2013 Participatory Culture Foundation
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

(function($) {

    var directives = angular.module('amara.SubtitleEditor.directives', []);

    directives.directive('saveSessionButton', function(SubtitleStorage) {
        return {
            link: function link(scope, elm, attrs) {
                scope.canSave = '';
            }
        };
    });
    directives.directive('subtitleList', function(SubtitleStorage, SubtitleListFinder, $timeout) {

        var isEditable;
        var selectedScope, selectedController, activeTextArea,
            rootEl;

        function onSubtitleItemSelected(elm) {
            /**
             * Receives the li.subtitle-list-item to be edited.
             * Will put any previously edited ones in display mode,
             * mark this one as being edited, creating the textarea for
             * editing.
             */
            // make sure this works if the event was trigger in the
            // originating li or any descendants

            elm = $(elm).hasClass('subtitle-list-item') ?
                      elm : $(elm).parents('.subtitle-list-item');

            var controller = angular.element(elm).controller();
            var scope = angular.element(elm).scope();

            // make sure the user clicked on the list item
            if (controller instanceof SubtitleListItemController) {
                if (selectedScope) {
                    selectedScope.finishEditingMode(activeTextArea.val());
                    selectedScope.$digest();
                }
                activeTextArea = $('textarea', elm);
                selectedScope = scope;

                var editableText = selectedScope.startEditingMode();

                activeTextArea.val(editableText);
                selectedScope.$digest();

                activeTextArea.focus();
                activeTextArea.autosize();
            }
        }
        function onSubtitleTextKeyDown(e) {
            /*
             * When a key is down, check to see if we need to do something:
             *
             * Enter / return: finish editing current sub and focus on the next one.
             * Shift + Enter / return: enter a newline in the current subtitle.
             * Tab: send the event to the video controller for playback control.
             * Shift + Tab: send the event to the video controller for playback control.
             * Any other key: do nothing.
             */

            var keyCode = e.keyCode;

            var parser = selectedScope.parser;
            var subtitle = selectedScope.subtitle;
            var subtitles = selectedScope.subtitles;

            var video = angular.element($('#video').get(0)).scope();

            var nextSubtitle;

            // Enter / return without shift.
            if (keyCode === 13 && !e.shiftKey) {

                var $currentSubtitle = $(e.currentTarget).parent();

                // Prevent an additional newline from being added to the next subtitle.
                e.preventDefault();

                var index = parser.getSubtitleIndex(subtitle, subtitles) + 1;

                // If this is the last subtitle in the set, save the current subtitle,
                // and create a new subtitle at the end.
                if (selectedScope.subtitles[index] === undefined) {

                    // Save the current subtitle.
                    selectedScope.finishEditingMode(activeTextArea.val());

                    // Passing true as the last argument indicates that we want
                    // to select this subtitle after it is created.
                    selectedScope.addSubtitle(index - 1, {}, '', true);

                }

                // Apply the current scope.
                selectedScope.$apply();

                // Set the element to select.
                nextSubtitle = $currentSubtitle.next().get(0);

            }

            // Tab without shift.
            if (keyCode === 9 && !e.shiftKey) {

                // TODO: This needs to bubble up so we can handle tab
                // and shift + tab on the document level, not only when
                // you're selected into a subtitle.

                // Keep the cursor in the current subtitle.
                e.preventDefault();
                
                // Move the video forward four seconds.
                video.playChunk(video.pop.currentTime(), 4);

            }
            
            // Tab with shift.
            if (keyCode === 9 && e.shiftKey) {

                // TODO: This needs to bubble up so we can handle tab
                // and shift + tab on the document level, not only when
                // you're selected into a subtitle.

                // Keep the cursor in the current subtitle.
                e.preventDefault();

                // Move the video backwards four seconds.
                video.playChunk(video.pop.currentTime() - 4, 4);

            }

            if (nextSubtitle) {

                // Select the next element.
                onSubtitleItemSelected(nextSubtitle);

                // Focus on the active textarea.
                activeTextArea.focus();

            } else {

                // Otherwise, just save the current subtitle.
                selectedScope.textChanged(activeTextArea.val());

            }

        }

        return {
            compile: function compile(elm, attrs, transclude) {
                rootEl = elm;
                return {
                    post: function post(scope, elm, attrs) {

                        scope.getSubtitles(attrs.languageCode, attrs.versionNumber);
                        isEditable = attrs.editable === 'true';

                        if (isEditable) {
                            $(elm).click(function(e) {
                                onSubtitleItemSelected(e.srcElement || e.target);
                            });
                            $(elm).on('keydown', 'textarea', onSubtitleTextKeyDown);

                            // In order to catch an <esc> key sequence, we need to catch
                            // the keycode on the document, not the list. Also, keyup must
                            // be used instead of keydown.
                            $(document).on('keyup', function(e) {
                                if (e.keyCode === 27) {
                                    selectedScope.finishEditingMode(activeTextArea.val());
                                    selectedScope.$digest();
                                }
                            });

                            // Create a custom event handler to select a subtitle.
                            //
                            // See the subtitleListItem directive below. This gets called
                            // if a subtitleListItem is created and its index matches the
                            // focus index that is set when adding the new subtitle from the
                            // controller.
                            $(elm).on('selectFocusedSubtitle', function() {

                                var $subtitle = $('li', elm).eq(scope.focusIndex);

                                // Select the subtitle.
                                //
                                // We have to timeout here, otherwise we'll try to select
                                // the new subtitle before it's been added to DOM.
                                $timeout(function() {
                                    onSubtitleItemSelected($subtitle.get(0));
                                });

                            });
                        }
                        scope.setVideoID(attrs['videoId']);
                        scope.setLanguageCode(attrs['languageCode']);
                        SubtitleListFinder.register(attrs.subtitleList, elm,
                            angular.element(elm).controller(), scope);
                    }
                };
            }
        };
    });
    directives.directive('subtitleListItem', function() {
        return {
            compile: function compile(elm, attrs, transclude) {
                return {
                    post: function post(scope, elm, attrs) {

                        // If we need to focus this subtitle.
                        if (scope.getSubtitleIndex() === scope.$parent.focusIndex) {

                            // Trigger the custom event selectFocusedSubtitle on the UL,
                            // which was bound in the subtitleList directive above.
                            $(elm).parent().trigger('selectFocusedSubtitle');

                        }

                    }
                };
            }
        };
    });

})(window.AmarajQuery);
