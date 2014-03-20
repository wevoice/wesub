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

(function() {
    var module = angular.module('amara.SubtitleEditor.modal', [
        'amara.SubtitleEditor.blob',
        'amara.SubtitleEditor.subtitles.services',
        ]);

    module.controller('SaveErrorModalController', function($scope, Blob) {
        $scope.dfxpString = '';

        $scope.$watch('dialogManager.current()', function(value) {
            if(value == 'save-error') {
                // we just became the current dialog.  Get the DFXP for the
                // current subtitle list.
                var subtitleList = $scope.workingSubtitles.subtitleList;
                $scope.dfxpString = subtitleList.toXMLString();
            }
        });

        $scope.canUseBlobURL = function() {
            // FileSaver doesn't work correctly with Safari, so we disable
            // using blobs to create a direct download link.  See #751 for
            // more info.
            return (navigator.userAgent.indexOf('Safari') == -1 ||
                navigator.userAgent.indexOf('Chrome') > -1);
        }

        $scope.onDownload = function($event) {
            $event.preventDefault();
            var downloadBlob = Blob.create($scope.dfxpString, 'application/ttaf+xml');
            window.saveAs(downloadBlob, 'SubtitleBackup.dfxp');
        }

        $scope.onClose = function($event) {
            $scope.dialogManager.close();
            $event.preventDefault();
            $scope.exitToVideoPage();
        }
    })

    function DialogManager(VideoPlayer) {
        this.VideoPlayer = VideoPlayer;
        this.stack = [];
        this.generic = null;
        // Store generic dialogs that are open, but have been replaced with
        // others
        this.genericStack = [];
    }

    DialogManager.prototype = {
        open: function(dialogName) {
            this.VideoPlayer.pause();
            this.stack.push(dialogName);
        },
        close: function() {
            this.stack.pop();
            if(this.current() == 'generic') {
                this.generic = this.genericStack.pop();
            } else {
                this.generic = null;
            }
        },
        onCloseClick: function($event) {
            $event.stopPropagation();
            $event.preventDefault();
            this.close();
        },
        onOpenClick: function(dialogName, $event) {
            $event.preventDefault();
            $event.stopPropagation();
            this.open(dialogName);
        },
        current: function() {
            if(this.stack.length > 0) {
                return this.stack[this.stack.length - 1];
            } else {
                return null;
            }
        },
        dialogCSSClass: function(dialogName) {
            if(this.current() == dialogName) {
                return 'shown';
            } else {
                return '';
            }
        },
        overlayCSSClass: function() {
            if(this.current() !== null) {
                return 'shown';
            } else {
                return '';
            }
        },
        button: function(text, callback, cssClass) {
            return {
                text: text,
                callback: callback,
                cssClass: cssClass || null
            };
        },
        closeButton: function(callback) {
            var that = this;
            return this.button('Close', function() {
                that.close();
                if(callback) {
                    callback();
                }
            });
        },
        linkButton: function(text, callback) {
            return this.button(text, callback, 'link-style');
        },
        /*
         * Open a dialog that doesn't need special HTML/code
         *
         * dialogDef is an object that defines the dialog.  It should contain
         * the following properties:
         *
         *   title: dialog heading
         *   text: dialog description (optional)
         *   allowClose: if present, allow closing the dialog via escape/mouse
         *               clicks outside of the element (optional)
         *   buttons: array defining the buttons.  Each element must be
         *            either a simple string, or an object created by button()
         *            or closeButton().
         */
        openDialog: function(dialogDef) {
            if(this.generic != null) {
                this.genericStack.push(this.generic);
            }
            this.generic = dialogDef;
            this.open('generic');
        }
    }

    module.value('DialogManager', DialogManager);

    module.directive('modalDialog', function($document) {
        return function link($scope, elm, attrs) {
            var dialogName = attrs.modalDialog;
            function allowClose() {
                if(dialogName == 'generic' &&
                    $scope.dialogManager.generic.allowClose) {
                    return true;
                }
                return attrs.allowClose !== undefined;
            }
            function bindCloseActions() {
                if(!allowClose()) {
                    return;
                }
                $document.bind("keydown.modal-" + dialogName, function(evt) {
                    // Escape key closes the modal
                    $scope.$apply(function() {
                        if (evt.keyCode === 27) {
                            $scope.dialogManager.close();
                        }
                    });
                });
                $document.bind("click.modal-" + dialogName, function(evt) {
                    // Clicking outside the modal closes it
                    $scope.$apply(function() {
                        if ($(evt.target).closest('aside.modal').length == 0) {
                            $scope.dialogManager.close();
                        }
                    });
                });
            }
            function unbindCloseActions() {
                $document.unbind("keydown.modal-" + dialogName);
                $document.unbind("click.modal-" + dialogName);
            }

            $scope.$watch('dialogManager.current()', function(current) {
                if(current == dialogName) {
                    elm.addClass('shown');
                    bindCloseActions();
                } else {
                    elm.removeClass('shown');
                    unbindCloseActions();
                }
            });
        };
    });
}).call(this);
