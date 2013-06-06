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
var LOCK_EXPIRATION = 25;
var USER_IDLE_MINUTES = 5;

(function($) {

    var directives = angular.module('amara.SubtitleEditor.directives.subtitles', []);

    function setCaretPosition(elem, caretPos) {
        /** Move the caret to the specified position.
         * This will work, except for text areas with user inserted line breaks
         */
        if (elem != null) {
            if (elem.createTextRange) {
                var range = elem.createTextRange();
                range.move('character', caretPos);
                range.select();
            }
            else {
                if (elem.selectionStart !== undefined) {
                    elem.focus();
                    elem.setSelectionRange(caretPos, caretPos);
                }
            }
        }
    }
    directives.directive('subtitleEditor', function() {
        return function link(scope, elm, attrs) {
            scope.videoId = attrs.videoId;
            scope.languageCode = attrs.languageCode;
            // For some reason using ng-keydown at the HTML tag doesn't work.
            // Use jquery instead.
            $(document).keydown(function(evt) {
                scope.$apply(function(scope) {
                    scope.handleAppKeyDown(evt);
                });
            });
        };
    });
    directives.directive('workingSubtitlesWrapper', function() {
        return function link(scope, elem, attrs) {
            var startHelper = $('div.sync-help.begin', elem);
            var endHelper = $('div.sync-help.end', elem);
            var subtitleList = $('.subtitles ul', elem);
            var wrapper = $(elem);

            function getSubtitleTop(index) {
                var li = $('li', subtitleList).eq(index);
                var top = li.offset().top - wrapper.offset().top;
                if(top < 0 || top + startHelper.height() >= wrapper.height()) {
                    return null;
                }
                return top;
            }

            var lastSyncStartIndex = null;
            var lastSyncEndIndex = null;

            scope.positionSyncHelpers = function(startIndex, endIndex) {
                if(startIndex === undefined) {
                    startIndex = lastSyncStartIndex;
                }
                if(endIndex === undefined) {
                    endIndex = lastSyncEndIndex;
                }
                var startTop = null;
                var endTop = null;
                if(startIndex !== null) {
                    startTop = getSubtitleTop(startIndex);
                }
                if(endIndex !== null) {
                    endTop = getSubtitleTop(endIndex);
                }
                if(startTop !== null) {
                    startHelper.css('top', startTop + 'px');
                    startHelper.show();
                } else {
                    startHelper.hide();
                }
                if(endTop !== null) {
                    endHelper.css('top', endTop + 'px');
                    endHelper.show();
                } else {
                    endHelper.hide();
                }
                lastSyncStartIndex = startIndex;
                lastSyncEndIndex = endIndex;
            }
        }
    });

    directives.directive('subtitleList', function(SubtitleListFinder) {
        return function link(scope, elem, attrs) {
            // set these *before* calling get subtitle since if
            // the subs are bootstrapped it will return right away
            scope.isEditable = attrs.editable === 'true';
            scope.setVideoID(attrs.videoId);
            SubtitleListFinder.register(attrs.subtitleList, elem,
                    elem.controller(), scope);
            if(attrs.languageCode != "") {
                scope.setLanguageCode(attrs.languageCode);
                if(attrs.versionNumber != "") {
                    scope.getSubtitles(attrs.languageCode, attrs.versionNumber);
                } else {
                    scope.initEmptySubtitles();
                }
            }

            // Handle scroll.
            $(elem).parent().scroll(function() {

                // If scroll sync is locked.
                if (scope.scrollingSynced) {
                    var newScrollTop = $(elem).parent().scrollTop();

                    $('div.subtitles').each(function() {

                        var $set = $(this);

                        if ($set.scrollTop() !== newScrollTop) {
                            $set.scrollTop(newScrollTop);
                        }

                    });
                }

                if(scope.isWorkingSubtitles()) {
                    scope.positionSyncHelpers();
                }
            });
            scope.nthChildScope = function(index) {
                var children = elem.children();
                if(0 <= index && index < children.length) {
                    return angular.element(children[index]).scope();
                } else {
                    return null;
                }
            }
        }
    });
    directives.directive('subtitleListItem', function($timeout) {
        return function link(scope, elem, attrs) {
            var elem = $(elem);
            var textarea = $('textarea', elem);

            scope.nextScope = function() {
                var next = elem.next();
                if(next.length > 0) {
                    return next.scope();
                } else {
                    return null;
                }
            }

            scope.prevScope = function() {
                // need to wrap in jquery, since angular's jqLite doesn't
                // support prev()
                var prev = $(elem).prev();
                if(prev.length > 0) {
                    return angular.element(prev).scope();
                } else {
                    return null;
                }
            }

            scope.showTextArea = function(fromClick) {
                if(fromClick) {
                    var caretPos = window.getSelection().anchorOffset;
                } else {
                    var caretPos = scope.editText.length;
                }
                textarea.val(scope.editText).trigger('autosize');
                textarea.show();
                textarea.focus();
                setCaretPosition(textarea.get(0), caretPos);
                scope.$root.$emit('subtitle-edit', scope.subtitle.content());
                // set line-height to 0 because we don't want the whitespace
                // inside the element to add extra space below the textarea
                elem.css('line-height', '0');
            }

            scope.hideTextArea = function() {
                textarea.hide();
                elem.css('line-height', '');
            }

            textarea.autosize();
            textarea.on('keydown', function(evt) {
                scope.$apply(function() {
                    if (evt.keyCode === 13 && !evt.shiftKey) {
                        // Enter without shift finishes editing
                        scope.finishEditingMode(true);
                        if(scope.lastItem()) {
                            scope.addSubtitleAtEnd();
                            // Have to use a timeout in this case because the
                            // scope for the new subtitle won't be created
                            // until apply() finishes
                            $timeout(function() {
                                scope.nextScope().startEditingMode();
                            });
                        } else {
                            scope.nextScope().startEditingMode();
                        }
                        evt.preventDefault();
                    } else if (evt.keyCode === 27) {
                        // Escape cancels editing
                        scope.finishEditingMode(false);
                        evt.preventDefault();
                    } else if (evt.keyCode == 9) {
                        // Tab navigates to other subs
                        scope.finishEditingMode(true);
                        if(!evt.shiftKey) {
                            var tabTarget = scope.nextScope();
                        } else {
                            var tabTarget = scope.prevScope();
                        }
                        if(tabTarget !== null) {
                            tabTarget.startEditingMode();
                        }
                        evt.preventDefault();

                    }
                });
            });
            textarea.on('keyup', function(evt) {
                scope.$apply(function() {
                    // Update editText and emit the subtitle-edit event
                    scope.editText = textarea.val();
                    var content = scope.subtitleList.contentForMarkdown(
                        scope.editText);
                    scope.$root.$emit('subtitle-edit', content);
                });
            });
            textarea.on('focusout', function(evt) {
                if(scope.isEditing) {
                    scope.$apply(function() {
                        scope.finishEditingMode(true);
                    });
                }
            });
        }
    });

    directives.directive('languageSelector', function(SubtitleStorage) {
        return {
            compile: function compile(elm, attrs, transclude) {
                return {
                    post: function post(scope, elm, attrs) {
                        /* For some reason, if we use ng-select angular
                         * creates an extra option because it thinks
                         * scope.versionNumber is an invalid value for the
                         * options, even though it isn't.  I think it has to
                         * do with the fact that we manually create options
                         * with ng-repeat.  In any case, we handle the
                         * select ourself.
                         */
                        $('select.version-select', elm).change(function(evt) {
                            scope.versionNumber = this.value;
                            scope.$digest();
                        });
                        if(attrs.initialVersionNumber != "") {
                            var versionNumber = attrs.initialVersionNumber;
                        } else {
                            var versionNumber = null;
                        }

                        SubtitleStorage.getLanguages(function(languages){
                            scope.setInitialDisplayLanguage(
                                languages,
                                attrs.initialLanguageCode,
                                versionNumber);
                        });
                    }
                };
            }
        };
    });
})(window.AmarajQuery);
