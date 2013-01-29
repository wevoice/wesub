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

var angular = angular || null;
var SubtitleListItemController = SubtitleListItemController || null;

(function($) {

    var directives = angular.module('amara.SubtitleEditor.directives', []);

    directives.directive('saveSessionButton', function(SubtitleStorage) {
        return {
            link: function link(scope, elm, attrs) {
                scope.canSave = '';
            }
        };
    });
    directives.directive('subtitleEditor', function(SubtitleStorage) {
        return {
            compile: function compile(elm, attrs, transclude) {
                return {
                    post: function post(scope, elm, attrs) {

                        $(elm).on('keydown', function(e) {

                            var video = angular.element($('#video').get(0)).scope();

                            // Space with shift, toggle play / pause.
                            if (e.keyCode === 32 && e.shiftKey) {
                                e.preventDefault();
                                video.togglePlay();
                            }

                        });

                    }
                };
            }
        };
    });
    directives.directive('subtitleList', function(SubtitleStorage, SubtitleListFinder, $timeout) {

        var activeTextArea,
            rootEl,
            selectedController,
            selectedScope,
            value;

        function onSubtitleItemSelected(elm) {
            /**
             * Receives the li.subtitle-list-item to be edited.
             * Will put any previously edited ones in display mode,
             * mark this one as being edited, creating the textarea for
             * editing.
             */

            elm = $(elm).hasClass('subtitle-list-item') ?
                      elm : $(elm).parents('.subtitle-list-item');

            var controller = angular.element(elm).controller();
            var scope = angular.element(elm).scope();

            if (controller instanceof SubtitleListItemController) {
                if (selectedScope) {
                    selectedScope.finishEditingMode(activeTextArea.val());
                    selectedScope.$digest();
                }
                activeTextArea = $('textarea', elm);
                selectedScope = scope;

                activeTextArea.val(selectedScope.startEditingMode());
                selectedScope.$digest();

                activeTextArea.focus();
                activeTextArea.autosize();

                selectedScope.$root.$broadcast('subtitleSelected', selectedScope);
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

            var nextSubtitle;

            var $currentSubtitle = $(e.currentTarget).parent();

            // Tab without shift.
            if (e.keyCode === 9 && !e.shiftKey) {

                // Prevent an additional newline from being added to the next subtitle.
                e.preventDefault();

                // If canAddAndRemove is true and this is the last subtitle in the set,
                // save the current subtitle and create a new subtitle at the end.
                if (selectedScope.canAddAndRemove) {
                    if ($currentSubtitle.next().length === 0) {

                        // Save the current subtitle.
                        selectedScope.finishEditingMode(activeTextArea.val());

                        // Passing true as the last argument indicates that we want
                        // to select this subtitle after it is created.
                        selectedScope.addSubtitle(null, {}, '', true);

                        // Apply the current scope.
                        selectedScope.$apply();

                    }
                }

                // Set the next subtitle to be the one after this.
                nextSubtitle = $currentSubtitle.next().get(0);

            }

            // Tab with shift.
            if (e.keyCode === 9 && e.shiftKey) {

                // Keep the cursor in the current subtitle.
                e.preventDefault();

                // Set the next subtitle to be the one before this.
                nextSubtitle = $currentSubtitle.prev().get(0);

            }

            // Space with shift.
            if (e.keyCode === 32 && e.shiftKey) {

                // We're letting this event bubble up to the subtitleEditor directive
                // where it will trigger the appropriate video method.

                // Keep the cursor in the current subtitle.
                e.preventDefault();

            }

            if (nextSubtitle) {

                // Select the next element.
                onSubtitleItemSelected(nextSubtitle);

                // Focus on the active textarea.
                activeTextArea.focus();

            }
        }
        function onSubtitleTextKeyUp(e) {

            var newText = activeTextArea.val();

            // Save the content to the DFXP wrapper.
            selectedScope.parser.content(selectedScope.subtitle, newText);

            // Cache the value for a negligible performance boost.
            value = activeTextArea.val();

            selectedScope.empty = value === '';
            selectedScope.characterCount = value.length;

            selectedScope.$root.$emit('subtitleKeyUp', {
                parser: selectedScope.parser,
                subtitles: $(selectedScope.subtitles),
                subtitle: selectedScope,
                value: value
            });

            selectedScope.$digest();

        }

        return {
            compile: function compile(elm, attrs, transclude) {
                rootEl = elm;
                return {
                    post: function post(scope, elm, attrs) {

                        scope.getSubtitles(attrs.languageCode, attrs.versionNumber);

                        scope.isEditable = attrs.editable === 'true';
                        scope.canAddAndRemove = attrs.canAddAndRemove === 'true';

                        if (scope.isEditable) {
                            $(elm).click(function(e) {
                                onSubtitleItemSelected(e.srcElement || e.target);
                            });
                            $(elm).on('keydown', 'textarea', onSubtitleTextKeyDown);
                            $(elm).on('keyup', 'textarea', onSubtitleTextKeyUp);

                            // In order to catch an <esc> key sequence, we need to catch
                            // the keycode on the document, not the list. Also, keyup must
                            // be used instead of keydown.
                            $(document).on('keyup', function(e) {
                                if (e.keyCode === 27) {
                                    if (selectedScope) {
                                        selectedScope.finishEditingMode(activeTextArea.val());
                                        selectedScope.$digest();
                                    }
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
                        scope.setVideoID(attrs.videoId);
                        scope.setLanguageCode(attrs.languageCode);
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
