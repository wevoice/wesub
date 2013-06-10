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
    directives.directive('workingSubtitlesWrapper', function($timeout) {
        return function link(scope, elem, attrs) {
            var startHelper = $('div.sync-help.begin', elem);
            var endHelper = $('div.sync-help.end', elem);
            var infoTray = $('div.info-tray', elem);
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

            scope.positionInfoTray = function() {
                var li = scope.currentEdit.LI;
                if(li) {
                    var top = li.offset().top - wrapper.offset().top;
                    if(top >= 0 && top < wrapper.height()) {
                        infoTray.css('top', top + 'px');
                        infoTray.show();
                    } else {
                        infoTray.hide();
                    }
                }
            }

            scope.$watch("currentEdit.LI", function() {
                // When we finish an edit, we do a bunch of CSS tricks to
                // re-show the text and hide the textarea.  Use a timeout to
                // make sure that positionInfoTray() gets called after those
                // are done.
                $timeout(scope.positionInfoTray);
            });
        };
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
                    scope.versionNumber = parseInt(attrs.versionNumber);
                    scope.getSubtitles(attrs.languageCode, attrs.versionNumber);
                } else {
                    scope.versionNumber = null;
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
                    scope.positionInfoTray();
                }
            });
            scope.scrollToSubtitle = function(subtitle) {
                scopeForSubtitle(subtitle).scrollTo();
            }
            scope.scopeForSubtitle = function(subtitle) {
                var pos = scope.subtitleList.getIndex(subtitle);
                return scope.nthChildScope(pos);
            }
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
            var scroller = elem.closest('div.subtitles');
            var textarea = $('textarea', elem);

            scope.LI = elem;
            scope.nextScope = function() {
                var next = elem.next();
                if(next.length > 0) {
                    return angular.element(next).scope();
                } else {
                    return null;
                }
            }

            scope.prevScope = function() {
                // need to wrap in jquery, since angular's jqLite doesn't
                // support prev()
                var prev = elem.prev();
                if(prev.length > 0) {
                    return angular.element(prev).scope();
                } else {
                    return null;
                }
            }

            scope.scrollTo = function() {
                // Scroll so that this subtitle is visible.
                //
                // Note: to give the user a bit more context, this method
                // scrolls so that the previous subtitle is on top of the
                // list.
                var prev = elem.prev();
                if(prev) {
                    var target = prev;
                } else {
                    var target = elem;
                }
                scroller.scrollTop(scroller.scrollTop() +
                        target.offset().top - scroller.offset().top);
            }

            scope.showTextArea = function(fromClick) {
                var initialText = scope.currentEdit.sourceMarkdown();
                if(fromClick) {
                    var caretPos = window.getSelection().anchorOffset;
                } else {
                    var caretPos = initialText.length;
                }
                textarea.autosize();
                textarea.val(initialText).trigger('autosize');
                textarea.show();
                textarea.focus();
                setCaretPosition(textarea.get(0), caretPos);
                scope.$root.$emit('subtitle-edit', scope.subtitle.content());
                // set line-height to 0 because we don't want the whitespace
                // inside the element to add extra space below the textarea
                elem.css('line-height', '0');
                $(document).on('mousedown.subtitle-edit', function(evt) {
                    var clicked = $(evt.target);
                    if(clicked[0] != textarea[0] &&
                        !clicked.hasClass('info-tray') &&
                        clicked.parents('.info-tray').length == 0) {
                        scope.$apply(function() {
                            scope.finishEditingMode(true);
                        });
                    }
                });
            }

            scope.hideTextArea = function() {
                textarea.hide();
                $(document).off('mousedown.subtitle-edit');
                elem.css('line-height', '');
            }

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
                    scope.currentEdit.update(textarea.val());
                    scope.$root.$emit('subtitle-edit',
                        scope.currentEdit.currentMarkdown());
                });
            });
        }
    });

    directives.directive('subtitleRepeat', function($interpolate) {
        /* Specialized repeat directive to work with subtitleList
         *
         * Because we need to deal potentially thousands of subtitles,
         * ng-repeat is not ideal.  subtitleRepeat does a couple things to
         * speed up performance:
         *
         *   - it hooks up to the change callback of subtitleList to calculate
         *   changes quickly.
         *
         *   - it doesn't create a child scope for each subtitle.  This means
         *   that it doesn't support the full angular templating language.
         *   However simple string interpolation is supported.
         */
        return function link($scope, elm, attrs) {
            function createNodeForSubtitle(subtitle) {
                var context = {
                    subtitle: subtitle
                };
                for(var i=0; i < interpolations.length; i++) {
                    var interp = interpolations[i];
                    interp.node.textContent = interp.func(context);
                }
                var rv = elm.clone();
                subtitleMap[subtitle.id] = rv;
                rv.data('subtitle', subtitle);
                return rv;
            }

            function findInterpolations() {
                // Jquery doesn't have a great way of finding text nodes, use
                // the plain DOM API instead
                var toSearch = [elm[0]];
                var rv = [];
                while(toSearch.length > 0) {
                    var node = toSearch.pop();
                    if(node.nodeType == 3) {
                        // Text node
                        var func = $interpolate(node.textContent, true);
                        if(func != null) {
                            rv.push({node: node, func: func});
                        }
                    } else {
                        toSearch.push.apply(toSearch, node.childNodes);
                    }
                }
                return rv;
            }

            function findSubtitleClickValue(node) {
                // Find the value of the subtitle-click attribute, starting
                // with node and moving up the DOM tree
                var parentNode = parent[0];
                while(node && node != parentNode) {
                    if(node.hasAttribute("subtitle-click")) {
                        return node.getAttribute("subtitle-click");
                    } else {
                        node = node.parentNode;
                    }
                }
                return null;
            }
            function findSubtitleData(node) {
                // Find the value of the subtitle-click attribute, starting
                // with node and moving up the DOM tree
                var parentNode = parent[0];
                while(node && node != parent) {
                    var subtitle = $(node).data('subtitle');
                    if(subtitle) {
                        return subtitle;
                    } else {
                        node = node.parentNode;
                    }
                }
                return null;
            }

            function onChange(change) {
                var subtitle = change.subtitle;
                switch(change.type) {
                    case 'remove':
                        var node = subtitleMap[subtitle.id];
                        node.remove();
                        delete subtitleMap[subtitle.id];
                        break;
                    case 'update':
                        var node = subtitleMap[subtitle.id];
                        node.replaceWith(createNodeForSubtitle(subtitle));
                        break;
                    case 'insert':
                        var node = subtitleMap[change.before.id];
                        node.before(createNodeForSubtitle(subtitle));
                        break;
                }
            }

            function startEditOn(draft) {
                var li = subtitleMap[draft.storedSubtitle.id];
                li.addClass('edit');
                var textarea = $('<textarea class="subtitle-edit" />');
                textarea.val(draft.markdown);
                li.append(textarea);
                textarea.on('keyup', function(evt) {
                    $scope.$apply(function() {
                        draft.markdown = textarea.val();
                    });
                });
                if(attrs.editKeydown) {
                    textarea.on('keydown', function(evt) {
                        $scope.$apply(function() {
                            var handler = $scope[attrs.editKeydown];
                            handler(evt);
                        });
                    });
                }
            }
            function stopEditOn(draft) {
                var li = subtitleMap[draft.storedSubtitle.id];
                li.removeClass('edit');
                $('textarea.subtitle-edit', li).remove();
            }

            $scope.reloadSubtitleRepeat = function() {
                parent.empty();
                subtitleMap = {}
                for(var i=0; i < subtitleList.length(); i++) {
                    var subtitle = subtitleList.subtitles[i];
                    parent.append(createNodeForSubtitle(subtitle));
                }
            }

            // On our first pass we remove the element from its parent, then
            // add a copy for each subtitle
            elm = $(elm);
            var subtitleList = $scope[attrs.subtitleRepeat];
            var parent = elm.parent();
            var interpolations = findInterpolations();
            // Map subtitle ID to node for that subtitle
            var subtitleMap = {};

            elm.remove();
            $scope.reloadSubtitleRepeat();

            subtitleList.addChangeCallback(onChange);

            if(attrs.bindToEdit) {
                $scope.$watch(attrs.bindToEdit, function(newValue, oldValue) {
                    if(oldValue) {
                        stopEditOn(oldValue);
                    }
                    if(newValue) {
                        startEditOn(newValue);
                    }
                });
            }
            // We connect to the click event of the parent element.  If we
            // have many subtitles, creating a handler for each <li> isn't
            // good.
            parent.on('click', function(evt) {
                if(!$scope.onSubtitleClick) {
                    return;
                }
                var action = findSubtitleClickValue(evt.target);
                var subtitle = findSubtitleData(evt.target);
                if(action !== null) {
                    $scope.onSubtitleClick(evt, subtitle, action);
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
