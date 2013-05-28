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
    directives.directive('subtitleEditor', function(SubtitleStorage, LockService, $timeout) {

        var minutesIdle = 0;
        var secondsUntilClosing = 120;
        var videoId, languageCode, selectedScope, regainLockTimer;

        function startUserIdleTimer() {
            var userIdleTimeout = function() {

                minutesIdle++;

                if (minutesIdle >= USER_IDLE_MINUTES) {
                    showIdleModal();
                    $timeout.cancel(regainLockTimer);
                } else {
                    $timeout(userIdleTimeout, 60 * 1000);
                }
            };

            $timeout(userIdleTimeout, 60 * 1000);
        }
        function startRegainLockTimer() {
            var regainLockTimeout = function() {
                LockService.regainLock(videoId, languageCode);
                regainLockTimer = $timeout(regainLockTimeout, 15 * 1000);
            };

            regainLockTimer = $timeout(regainLockTimeout, 15 * 1000);

        }
        function showIdleModal() {

            var heading = "Warning: you've been idle for more than " + USER_IDLE_MINUTES + " minutes. " +
                "To ensure no work is lost we will close your session in ";

            var closeSessionTimeout;

            var closeSession = function() {

                secondsUntilClosing--;

                if (secondsUntilClosing <= 0) {

                    LockService.releaseLock(videoId, languageCode);

                    selectedScope.$root.$emit("show-modal", {
                        heading: 'Your session has ended. You can try to resume, close the editor, or download your subtitles',
                        buttons: [
                            {'text': 'Try to resume work', 'class': 'yes', 'fn': function() {
                                // TODO: Remove this duplication from below.
                                if (closeSessionTimeout) {
                                    $timeout.cancel(closeSessionTimeout);
                                }

                                var promise = LockService.regainLock(videoId, languageCode);

                                promise.then(function onSuccess(response) {
                                    if (response.data.ok) {
                                        minutesIdle = 0;
                                        selectedScope.$root.$broadcast('hide-modal');
                                        startRegainLockTimer();
                                        startUserIdleTimer();
                                    } else {
                                        window.alert("Sorry, could not restart your session.");
                                        window.location = '/videos/' + videoId + "/";
                                    }
                                }, function onError() {
                                    window.alert("Sorry, could not restart your session.");
                                    window.location = '/videos/' + videoId + "/";
                                });
                            }},
                            {'text': 'Download subtitles', 'class': 'no', 'fn': function() {
                                selectedScope.$root.$emit('show-modal-download');
                            }},
                            {'text': 'Close editor', 'class': 'no', 'fn': function() {
                                window.location = '/videos/' + videoId + "/";
                            }}
                        ]
                    });

                } else {

                    selectedScope.$root.$emit('change-modal-heading', heading + secondsUntilClosing + " seconds.");
                    closeSessionTimeout = $timeout(closeSession, 1000);

                }
            };

            selectedScope.$root.$emit("show-modal", {
                heading: heading + secondsUntilClosing + " seconds.",
                buttons: [
                    {'text': 'Try to resume work', 'class': 'yes', 'fn': function() {
                        if (closeSessionTimeout) {
                            $timeout.cancel(closeSessionTimeout);
                        }

                        var promise = LockService.regainLock(videoId, languageCode);

                        promise.then(function onSuccess(response) {
                            if (response.data.ok) {
                                minutesIdle = 0;
                                selectedScope.$root.$broadcast('hide-modal');
                                startRegainLockTimer();
                                startUserIdleTimer();
                            } else {
                                window.alert("Sorry, could not restart your session.");
                                window.location = '/videos/' + videoId + "/";
                            }
                        }, function onError() {
                            window.alert("Sorry, could not restart your session.");
                            window.location = '/videos/' + videoId + "/";
                        });
                    }}
                ]
            });

            closeSessionTimeout = $timeout(closeSession, 1000);

        }

        return {
            compile: function compile(elm, attrs, transclude) {
                return {
                    post: function post(scope, elm, attrs) {

                        scope.scrollingSynced = true;
                        scope.timelineShown = true;
                        scope.subtitlesHeight = 366;

                        scope.$watch('timelineShown', function() {
                            if (scope.timelineShown) {
                                scope.subtitlesHeight = 431;
                            } else {
                                scope.subtitlesHeight = 366;
                            }
                        });

                        $(elm).on('keydown', function(e) {

                            // Reset the lock timer.
                            minutesIdle = 0;

                            var video = angular.element($('#video').get(0)).scope();

                            // Space with shift, toggle play / pause.
                            if (e.keyCode === 32 && e.shiftKey) {
                                e.preventDefault();
                                video.togglePlay();
                            }

                        });
                        $(elm).on('mousemove', function() {

                            // Reset the lock timer.
                            minutesIdle = 0;

                        });

                        videoId = attrs.videoId;
                        languageCode = attrs.languageCode;
                        selectedScope = scope;

                        startUserIdleTimer();
                        startRegainLockTimer();
                    }
                };
            }
        };
    });
    directives.directive('subtitleList', function(SubtitleListFinder) {
        return function link(scope, elm, attrs) {
            // set these *before* calling get subtitle since if
            // the subs are bootstrapped it will return right away
            scope.isEditable = attrs.editable === 'true';
            scope.getSubtitles(attrs.languageCode, attrs.versionNumber);


            // Cache the jQuery selection of the element.
            var $elm = $(elm);

            // Handle scroll.
            $elm.parent().scroll(function() {

                // If scroll sync is locked.
                if (scope.$root.scrollingSynced) {
                    var newScrollTop = $elm.parent().scrollTop();

                    $('div.subtitles').each(function() {

                        var $set = $(this);

                        if ($set.scrollTop() !== newScrollTop) {
                            $set.scrollTop(newScrollTop);
                        }

                    });
                }
            });

            scope.setVideoID(attrs.videoId);
            scope.setLanguageCode(attrs.languageCode);
            SubtitleListFinder.register(attrs.subtitleList, elm,
                    angular.element(elm).controller(), scope);
        }
    });
    directives.directive('subtitleListItem', function($timeout) {
        return function link(scope, elem, attrs) {
            var textarea = $('textarea', elem);

            scope.nextScope = function() {
                return angular.element(elem.next()).scope();
            }

            scope.showTextArea = function(fromClick) {
                if(fromClick) {
                    var caretPos = window.getSelection().anchorOffset;
                } else {
                    var caretPos = scope.editText.length;
                }
                textarea.val(scope.editText);
                textarea.show();
                textarea.focus();
                setCaretPosition(textarea.get(0), caretPos);
                scope.$root.$emit('subtitle-edit', scope.subtitle.content());
            }

            scope.hideTextArea = function() {
                textarea.hide();
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
                scope.$apply(function() {
                    scope.finishEditingMode(true);
                });
            });
        }
    });

    directives.directive('languageSelector', function(SubtitleStorage) {
        return {
            compile: function compile(elm, attrs, transclude) {
                return {
                    post: function post(scope, elm, attrs) {
                        SubtitleStorage.getLanguages(function(languages){
                            scope.setInitialDisplayLanguage(
                                languages,
                                attrs.initialLanguageCode,
                                attrs.initialVersionNumber);
                        });
                    }
                };
            }
        };
    });
})(window.AmarajQuery);
