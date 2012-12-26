// Amara, universalsubtitles.org
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

(function ($) {

    var directives = angular.module("amara.SubtitleEditor.directives", []);
    directives.directive("subtitleList", function (SubtitleStorage, SubtitleListFinder) {
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
            // return or tab WITHOUT shift
            var elementToSelect;
            if (keyCode == 13 && !event.shiftKey ||
                keyCode == 9 && !event.shiftKey ) {
                // enter with shift means new line
                selectedScope.textChanged($(e.currentTarget).text());
                e.preventDefault();

                // what is the next element?
                elementToSelect = $("span.subtitle-text", $(".subtitle-list-item", rootEl)[selectedScope.subtitle.index + 1]);

                selectedScope.$digest();
            }else if (keyCode == 9 && event.shiftKey){
                // tab with shift, move backwards
                elementToSelect = $("span.subtitle-text", $(".subtitle-list-item", rootEl)[selectedScope.subtitle.index - 1]);
                e.preventDefault();

            }
            if (elementToSelect){
                onSubtitleItemSelected(elementToSelect);
                activeTextArea.select();
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
            var elm = $(elm).hasClass(".subtitle-list-item") ?
                elm :
                $(elm).parents(".subtitle-list-item");
            var controller = angular.element(elm).controller();
            var scope = angular.element(elm).scope();
            if (scope == selectedScope){
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
                activeTextArea = $("textarea", elm);
                selectedScope = scope;
                var editableText = selectedScope.startEditingMode();

                activeTextArea.val(editableText);
                angular.element(rootEl).scope().setSelectedIndex(selectedScope.subtitle.index);
                selectedScope.$digest();
            }
        }


        return {

            compile:function compile(elm, attrs, transclude) {
                // should be on post link so to give a chance for the
                // nested directive (subtitleListItem) to run
                rootEl = elm;
                return {
                    post:function post(scope, elm, attrs) {
                        scope.getSubtitles(attrs.languageCode, attrs.versionNumber);

                        isEditable = attrs.editable === 'true';
                        // if is editable, hook up event listeners
                        if (isEditable) {
                            $(elm).click(function (e) {
                                onSubtitleItemSelected(e.srcElement);
                            });
                            $(elm).on("keydown", "textarea", onSubtitleTextKeyDown);
                        }
                        scope.setVideoID (attrs['videoId'])
                        scope.setVideoID (attrs['languageCode'])
                        SubtitleListFinder.register(attrs.subtitleList, elm, angular.element(elm).controller(), scope);
                    }
                };
            }
        };
    });
    directives.directive("subtitleListItem", function (SubtitleStorage) {
        return {
            link:function link(scope, elm, attrs) {

            }
        };

    });

})(window.AmarajQuery);
