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
        // Controller for the save-error dialog and resume-error dialog

        $scope.dfxpString = '';

        $scope.$watch('dialogManager.current()', function(value) {
            if(value == 'save-error' || value == 'resume-error') {
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

    function makeButton(text, cssClass) {
        // Make a button for the generic dialog
        return {
            text: text,
            cssClass: cssClass || null
        };
    };

    function DialogManager(VideoPlayer) {
        this.VideoPlayer = VideoPlayer;
        this.stack = [];
        this.generic = null;
        // Store generic dialogs that are open, but have been replaced with
        // others
        this.genericStack = [];
        this.freezeBoxText = "";
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
            if(this.freezeBoxText) {
                return 'freeze-box';
            } else if(this.stack.length > 0) {
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
        buttons: {
            continueEditing: makeButton('Continue editing'),
            continueButton: makeButton('Continue'),
            // Note: we shouldn't use "continue" as a key because it's a
            // javascript keyword
            cancel: makeButton('Cancel'),
            close: makeButton('Close'),
            closeEditor: makeButton('Close Editor'),
            resume: makeButton('Try to resume work'),
            restore: makeButton('Restore'),
            discard: makeButton('Discard'),
            discardChanges: makeButton('Discard changes'),
            exit: makeButton('Exit'),
            waitDontDiscard: makeButton("Wait, don't discard my changes!",
                    'link-style')
        },
        dialogs: {
            subtitlesSaved: {
                title: "Subtitles saved",
                buttons: ['exit', 'resume', 'waitDontDiscard']
            },
            legacyEditorUnsavedWork: {
                title: "You have unsaved changes.  If you switch now you will lose your work.",
                buttons: [ 'discardChanges', 'continueEditing']
            },
            confirmCopyTiming: {
                title: 'Confirm Copy Timing',
                text: 'This will copy all subtitle timing from reference to working subtitles. Do you want to continue?',
                buttons: [ 'continueButton', 'cancel' ]
            },
            confirmTimingReset: {
                title: 'Confirm Timing Reset',
                text: 'This will remove all subtitle timing. Do you want to continue?',
                buttons: [ 'continueButton', 'cancel' ]
            },
            confirmTextReset: {
                title: 'Confirm Text Reset',
                text: 'This will remove all subtitle text. Do you want to continue?',
                buttons: [ 'continueButton', 'cancel' ]
            },
            confirmChangesReset: {
                title: 'Confirm Changes Reset',
                text: 'This will revert all changes made since the last saved revision. Do you want to continue?',
                buttons: [ 'continueButton', 'cancel' ]
            },
            sessionWillClose: {
                title: 'Warning: Your session will close',
                buttons: ['resume', 'closeEditor']
            },
            sessionEnded: {
                title: 'Your session has ended. You can try to resume, or close the editor.',
                buttons: ['resume', 'closeEditor']
            },
            restoreAutoBackup: {
                title: 'You have an unsaved backup of your subtitling work, do you want to restore it?',
                buttons: ['restore', 'discard']
            },
        },
        /*
         * Open a dialog that doesn't need special HTML/code
         *
         * dialogName specifies which dialog to open.  It's a key from the
         * dialogs dict.
         *
         * callbacks is a dict that maps button key names to functions to
         * call if that button is clicked.
         *
         * overrides is a dict of data to override the default title/text for
         * the dialog.
         *
         */
        openDialog: function(dialogName, callbacks, overrides) {
            var dialog = this._makeGenericDialog(dialogName, callbacks,
                    overrides);
            if(this.generic != null) {
                this.genericStack.push(this.generic);
            }
            this.generic = dialog;
            this.open('generic');
        },
        _makeGenericDialog: function(dialogName, callbacks, overrides) {
            if(callbacks === undefined) {
                callbacks = {};
            }
            // Creates the dialog object for openDialog
            var that = this;
            var dialogDef = this.dialogs[dialogName];
            if(dialogDef === undefined) {
                throw "no dialog named " + dialogName;
            }
            var dialog = _.clone(dialogDef);
            if(overrides) {
                dialog = _.extend(dialog, overrides);
            }
            // The buttons array contains button names.  Replace that with
            // actual objects.  Also setup the callback function.
            dialog.buttons = _.map(dialog.buttons, function(buttonName) {
                var buttonDef = that.buttons[buttonName];
                if(buttonDef === undefined) {
                    throw "no button named " + buttonName;
                };
                return {
                    text: buttonDef.text,
                    cssClass: buttonDef.cssClass,
                    callback: callbacks[buttonName] || null
                };
            });
            return dialog;
        },
        onButtonClicked: function(button, $event) {
            this.close();
            $event.preventDefault();
            $event.stopPropagation();
            if(button.callback) {
                button.callback();
            }
        },
        showFreezeBox: function(text) {
            /* Show the "freeze box". 
             *
             * The freeze box displays a simple message and the user can't
             * close.  This to prevents any user-actions and obviously should
             * be used very sparingly, for example while saving a copy and
             * waiting for a response from the server.
             *
             * The Freeze box uses a separate system from the dialog stack.
             * If the freeze box is active, then it will display regardless of
             * any dialogs that are also open.
             */
            this.freezeBoxText = text;
        },
        closeFreezeBox: function() {
            this.freezeBoxText = '';
        },
        freezeBoxCSSClass: function() {
            if(this.freezeBoxText) {
                return 'shown';
            } else {
                return '';
            }
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
