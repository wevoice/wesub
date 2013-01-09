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

    directives.directive('saveSessionButton', function (SubtitleStorage) {
        return {
            link: function link(scope, elm, attrs) {
                scope.canSave = '';
            }
        };
    });
    directives.directive('subtitleList', function (SubtitleStorage, SubtitleListFinder) {

        var isEditable;
        var selectedScope, selectedController, activeTextArea,
            rootEl;

        /**
         * Triggered with a key is down on a text area for editing subtitles.
         * If it's regular text just do the default thing.
         * If we pressed an enter / return, finish editing this sub and
         * focus o the next one. Same for tab.
         * @param e The jQuery key event
         */
        function onSubtitleTextKeyDown(e) {

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
                    selectedScope.addSubtitle({'text': ''}, index);
                    selectedScope.finishEditingMode(activeTextArea.val());
                }

                selectedScope.$apply();
                // TODO: Render the subtitle list, again.

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

            } else if (keyCode === 27){
                // if it's an esc on the textarea, finish editing
                // TODO: This won't work unless we bind to keyup instead of keydown.
                selectedScope.finishEditingMode(activeTextArea.val());
                selectedScope.$digest();
            }

            if (elementToSelect) {
                onSubtitleItemSelected(elementToSelect);
                activeTextArea.focus();
            } else {
                selectedScope.finishEditingMode(activeTextArea.val());
            }

        }

        /**
         * Receives the li.subtitle-list-item to be edited.
         * Will put any previously edited ones in display mode,
         * mark this one as being edited, creating the textarea for
         * editing.
         */
        function onSubtitleItemSelected(elm) {
            // make sure this works if the event was trigger in the
            // originating li or any descendants
            elm = $(elm).hasClass('.subtitle-list-item') ?
                      elm : $(elm).parents('.subtitle-list-item');

            var controller = angular.element(elm).controller();
            var scope = angular.element(elm).scope();

            if (scope === selectedScope) {
                return;
            }

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

                var parser = selectedScope.parser;
                var subtitle = selectedScope.subtitle;
                var subtitles = selectedScope.subtitles;
                var subtitleIndex = parser.getSubtitleIndex(subtitle, subtitles);

                activeTextArea.val(editableText);
                angular.element(rootEl).scope().setSelectedIndex(subtitleIndex);
                selectedScope.$digest();

                activeTextArea.focus();
                activeTextArea.autosize();
            }
        }

        return {
            compile: function compile(elm, attrs, transclude) {
                // should be on post link so to give a chance for the
                // nested directive (subtitleListItem) to run
                rootEl = elm;
                return {
                    post: function post(scope, elm, attrs) {
                        scope.getSubtitles(attrs.languageCode, attrs.versionNumber);

                        isEditable = attrs.editable === 'true';
                        // if is editable, hook up event listeners
                        if (isEditable) {
                            $(elm).click(function (e) {
                                onSubtitleItemSelected(e.srcElement || e.target);
                            });
                            $(elm).on('keydown', 'textarea', onSubtitleTextKeyDown);
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
    directives.directive('subtitleListItem', function (SubtitleStorage) {
        return {
            link: function link(scope, elm, attrs) {}
        };
    });

})(window.AmarajQuery);
