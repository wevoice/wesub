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
    directives.directive('subtitleList', function(SubtitleStorage, SubtitleListFinder) {

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
            elm = $(elm).hasClass('.subtitle-list-item') ?
                      elm : $(elm).parents('.subtitle-list-item');

            var controller = angular.element(elm).controller();
            var scope = angular.element(elm).scope();

            // make sure the user clicked on the list item
            if (controller instanceof SubtitleListItemController) {
                if (selectedScope) {
                    // if there were an active item, deactivate it
                    selectedScope.finishEditingMode(activeTextArea.val());
                    // trigger updates
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
            /**
             * Triggered with a key is down on a text area for editing subtitles.
             * If it's regular text just do the default thing.
             * If we pressed an enter / return, finish editing this sub and
             * focus o the next one. Same for tab.
             * @param e The jQuery key event
             */

            var keyCode = e.keyCode;
            var elementToSelect;

            var parser = selectedScope.parser;
            var subtitle = selectedScope.subtitle;
            var subtitles = selectedScope.subtitles;

            // return or tab WITHOUT shift
            if (keyCode === 13 && !e.shiftKey ||
                keyCode === 9 && !e.shiftKey ) {

                // enter with shift means new line
                selectedScope.textChanged($(e.currentTarget).text());
                e.preventDefault();

                var index = parser.getSubtitleIndex(subtitle, subtitles) + 1;

                // if it's the last subtitle of the set and the user pressed enter without shift,
                // add a new empty subtitle and select it to edit
                if (selectedScope.subtitles[index] === undefined) {
                    selectedScope.finishEditingMode(activeTextArea.val());
                    selectedScope.addSubtitle({'text': ''}, index);
                }

                selectedScope.$apply();

                elementToSelect = $('span.subtitle-text', $('.subtitle-list-item', rootEl)[index]);

            } else if (keyCode === 9 && e.shiftKey) {
                // tab with shift, move backwards
                var lastIndex = parser.getSubtitleIndex(subtitle, subtitles) - 1;
                var lastSubtitle = parser.getSubtitle(lastIndex);
                if (lastSubtitle) {
                    elementToSelect = $('span.subtitle-text', $('.subtitle-list-item',
                                        rootEl)[lastIndex]);
                }
                e.preventDefault();
            }

            if (elementToSelect) {
                onSubtitleItemSelected(elementToSelect);
                activeTextArea.focus();
            } else {
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

})(window.AmarajQuery);
