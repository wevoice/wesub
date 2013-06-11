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

(function() {

    var root = this;
    var _ = root._.noConflict();
    var $ = root.AmarajQuery;

    /* CurrentEditManager manages in-progress edits of subtitles
     */
    function CurrentEditManager() {
        this.draft = null;
        this.LI = null;
    }

    CurrentEditManager.prototype.start = function(subtitle, LI) {
        this.draft = subtitle.draftSubtitle();
        this.LI = LI;
    }

    CurrentEditManager.prototype.finish = function(commitChanges, subtitleList) {
        var updateNeeded = (commitChanges && this.changed());
        if(updateNeeded) {
            subtitleList.updateSubtitleContent(this.draft.storedSubtitle,
                    this.currentMarkdown());
        }
        this.draft = this.LI = null;
        return updateNeeded;
    }

    CurrentEditManager.prototype.sourceMarkdown = function() {
        return this.draft.storedSubtitle.markdown;
    }

    CurrentEditManager.prototype.currentMarkdown = function() {
        return this.draft.markdown;
    }

    CurrentEditManager.prototype.changed = function() {
        return this.sourceMarkdown() != this.currentMarkdown();
    }

    CurrentEditManager.prototype.update = function(markdown) {
        if(this.draft !== null) {
            this.draft.markdown = markdown;
        }
    }

    CurrentEditManager.prototype.isForSubtitle = function(subtitle) {
        return (this.draft !== null && this.draft.storedSubtitle == subtitle);
    }

    CurrentEditManager.prototype.inProgress = function() {
        return this.draft !== null;
    }

    CurrentEditManager.prototype.lineCounts = function() {
        if(this.draft === null || this.draft.lineCount() < 2) {
            // Only show the line counts if there are 2 or more lines
           return null;
       } else {
           return this.draft.characterCountPerLine();
       }
    }

    var LanguageSelectorController = function($scope, SubtitleStorage, SubtitleListFinder) {
        /**
         * This controller is responsible for the language and version selector
         * widget.  The widget allows the user to select a reference language and
         * version when translating subtitles into another language.
         *
         * The $scope contains 'languages' and 'versions'.  Each list is
         * represented in the UI as a <select> element.  The selected language or
         * version is stored on the $scope as a 'language' and 'version' model.
         *
         * Whenever the language selection is changed, we update the list of
         * versions.  When a new version is selected, we retrieve the subtitles
         * (either from memory or from the API via ajax) and display them in the
         * side panel.
         */

        /**
         * The second param will be either an int or the version data object,
         * depending if this is being set from the bootstrapped value or later
         * fetches.
         */
        $scope.versionNumber = null;
        $scope.versions = [];
        $scope.languageChanged = function(language, versionNumber) {
            if (!language) {
                return;
            }

            $scope.versions = _.sortBy(language.versions, function(item) {
                return item.version_no;
            }).reverse();

            if (isNaN(parseInt(versionNumber))) {
                // No version number given, select the last version (AKA first
                // verison in the dropdown)
                if($scope.versions.length == 0) {
                    $scope.versionNumber = null;
                    return;
                }
                versionNumber = $scope.versions[0].version_no;
            }

            $scope.versionNumber = versionNumber.toString();
        };
        $scope.setReferenceSubs = function(subtitleData) {
            if (!$scope.refSubList) {
                $scope.refSubList = SubtitleListFinder.get('reference-subtitle-set');
            }
            $scope.refSubList.scope.onSubtitlesFetched(subtitleData);
        };
        $scope.findVersion = function(versionNumber) {
            for(var i = 0; i < $scope.versions.length; i++) {
                if($scope.versions[i].version_no == versionNumber) {
                    return $scope.versions[i];
                }
            }
            return null;
        }
        $scope.versionNumberChanged = function(newValue, oldValue) {
            var newVersion = $scope.findVersion(newValue);
            if(!newVersion) {
                return;
            }

            if (!newVersion.subtitlesXML) {
                SubtitleStorage.getSubtitles(
                    $scope.language.language_code,
                    newVersion.version_no,
                    function(subtitleData) {
                        newVersion.subtitlesXML = subtitleData.subtitlesXML;
                        $scope.setReferenceSubs(newVersion);
                    });
            } else {
                $scope.setReferenceSubs(newVersion);
            }
        };

        $scope.setInitialDisplayLanguage = function(allLanguages, languageCode, versionNumber){

            // Hide the loading modal
            $scope.$root.$emit('hide-modal');
            $scope.languages = allLanguages;
            $scope.language = _.find(allLanguages, function(item) {
                return item.language_code == languageCode;
            });
            if(versionNumber !== null) {
                $scope.languageChanged($scope.language, versionNumber);
            }
        }

        $scope.$watch('language', function(newValue, oldValue) {
            $scope.languageChanged(newValue, "");
        });
        $scope.$watch('versionNumber', $scope.versionNumberChanged);
    };

    var SaveSessionController = function($scope, $q, SubtitleListFinder,
                                         SubtitleStorage, OldEditorConfig) {

        $scope.changesMade = false;
        $scope.nextVersionNumber = null;
        $scope.discard = function() {
            $scope.showCloseModal(false);
        };
        $scope.getNotes = function() {
            var collabScope = angular.element($('section.collab').get(0)).scope();
            return collabScope.notes || '';
        };
        $scope.saveAndApprove = function() {
            if($scope.changesMade) {
                var message = 'Subtitles saved, task approved. Redirecting…';
            } else {
                var message = 'Task approved. Redirecting…';
            }

            $scope.saveSession().then(function(versionNumber) {
                if ($scope.status === 'saved') {

                    $scope.status = 'approving';

                    SubtitleStorage.approveTask(versionNumber, $scope.getNotes()).then(function onSuccess(response) {

                        $scope.$root.$emit('show-loading-modal', message);
                        window.location = $scope.primaryVideoURL;

                    }, function onError() {
                        $scope.status = 'error';
                        $scope.showErrorModal();
                    });
                }
            });

        };
        $scope.save = function() {
            if(!$scope.changesMade) {
                return;
            }

            $scope.saveSession().then(function(versionNumber) {
                $scope.nextVersionNumber = versionNumber;
                $scope.showCloseModal(true);
            });
        };
        $scope.saveAndSendBack = function() {
            if($scope.changesMade) {
                var message = 'Subtitles saved, task sent back. Redirecting…';
            } else {
                var message = 'Task sent back. Redirecting…';
            }
            $scope.saveSession().then(function(versionNumber) {
                if ($scope.status === 'saved') {

                    $scope.status = 'sending-back';

                    SubtitleStorage.sendBackTask(versionNumber, $scope.getNotes()).then(function onSuccess(response) {

                        $scope.$root.$emit('show-loading-modal', message);
                        window.location = $scope.primaryVideoURL;
                        
                    }, function onError() {
                        $scope.status = 'error';
                        $scope.showErrorModal();
                    });

                }
            });
        };
        $scope.saveSession = function() {
            // Save the current session
            //
            // Returns a promise that will be resolved with the version number
            // of the new version when the save is complete.  If nothing has
            // changed, then we don't save anything and return the current
            // version number.
            if ($scope.status !== 'saving') {
                var subtitleList = SubtitleListFinder.get('working-subtitle-set').scope;
                var deferred = $q.defer();

                if($scope.changesMade) {
                    // changes have been made, we need to save the subtitles
                    $scope.status = 'saving';
                    var promise = subtitleList.saveSubtitles();
                    promise.then(function onSuccess(response) {
                        $scope.status = 'saved';
                        $scope.changesMade = false;
                        deferred.resolve(response.data.version_number);
                    }, function onError(e) {
                        $scope.status = 'error';
                        $scope.showErrorModal();
                        deferred.reject(e);
                    });
                } else {
                    // no changes made, just return the current version
                    $scope.status = 'saved';
                    deferred.resolve(subtitleList.versionNumber);
                }

                return deferred.promise;
            }
        };
        $scope.setCloseStates = function() {

            var subtitleListScope = SubtitleListFinder.get('working-subtitle-set').scope;

            var oldEditorURL = OldEditorConfig.get()
            $scope.fromOldEditor = Boolean(oldEditorURL);
            $scope.primaryVideoURL = '/videos/' + subtitleListScope.videoID + '/';

            if ($scope.fromOldEditor) {
                $scope.dialogURL = oldEditorURL;
            }
        };
        function resumeEditing() {
            var subtitleListScope = SubtitleListFinder.get('working-subtitle-set').scope;
            $scope.status = '';
            subtitleListScope.versionNumber = $scope.nextVersionNumber;
            $scope.nextVersionNumber = null;
        }
        $scope.showCloseModal = function(allowResume) {

            var buttons = [];

            if (allowResume && $scope.nextVersionNumber)  {
                buttons.push({
                    text: 'Resume editing',
                    class: 'yes',
                    fn: function() {
                        $scope.$root.$emit('hide-modal');
                        resumeEditing();
                    },
                });
            }

            if ($scope.fromOldEditor) {
                buttons.push({
                    'text': 'Back to full editor', 'class': 'yes', 'fn': function() {
                        window.location = $scope.dialogURL;
                    }
                });
            }

            buttons.push({
                'text': 'Exit', 'class': 'no', 'fn': function() {
                    window.location = $scope.primaryVideoURL;
                }
            });

            if ($scope.status !== 'saved') {

                buttons.push({
                    'text': "Wait, don't discard my changes!", 'class': 'last-chance', 'fn': function() {
                        $scope.$root.$emit('hide-modal');
                    }
                });

            }

            if($scope.status === 'saved') {
                var heading = "You've saved a new revision!";
            } else if($scope.changesMade) {
                var heading = 'Your changes will be discarded.';
            } else {
                var heading = 'You are leaving the editor';
            }

            $scope.$root.$emit('show-modal', {
                heading: heading,
                buttons: buttons
            });
        };
        $scope.showErrorModal = function(message) {

            var subtitleListScope = SubtitleListFinder.get('working-subtitle-set').scope;

            $scope.$root.$emit("show-modal", {
                heading: message || "There was an error saving your subtitles. You'll need to copy and save your subtitles below, and upload them to the system later.",
                buttons: [
                    {'text': 'Close editor', 'class': 'no', 'fn': function() {
                        window.location = '/videos/' + subtitleListScope.videoID + "/";
                    }}
                ]
            });
            $scope.$root.$emit('show-modal-download');
        };

        $scope.$root.$on('approve-task', function() {
            $scope.saveAndApprove();
        });
        $scope.$root.$on('send-back-task', function() {
            $scope.saveAndSendBack();
        });
        $scope.$root.$on('subtitles-fetched', function() {
            $scope.setCloseStates();
            $scope.changesMade = false;
        });
        $scope.$root.$on('work-done', function() {
            $scope.changesMade = true;
        });

        window.onbeforeunload = function() {
            if($scope.changesMade) {
              return "You have unsaved work";
            } else {
              return null;
            }
        };
    };

    var SubtitleListController = function($scope, $window, SubtitleStorage) {
        /**
         * Responsible for everything that touches subtitles as a group,
         * souch as populating the list with actual data, removing subs,
         * adding subs.
         * @param $scope
         * @param SubtitleStorage
         * @constructor
         */

        var willSync = {start: null, end:null};

        function updateSyncHelpers() {
            var startIndex = null, endIndex = null;
            if(willSync.start !== null) {
                startIndex = $scope.subtitleList.getIndex(willSync.start);
            }
            if(willSync.end !== null) {
                endIndex = $scope.subtitleList.getIndex(willSync.end);
            }
            $scope.positionSyncHelpers(startIndex, endIndex);
        }

        $scope.currentEdit = new CurrentEditManager();
        $scope.subtitleList = new dfxp.SubtitleList();
        $scope.isEditable = false;
        $scope.isWorkingSubtitles = function() {
            return $scope.isEditable;
        }
        $scope.allowsSyncing = $window.editorData.allowsSyncing;
        $scope.canAddAndRemove = $window.editorData.canAddAndRemove;
        $scope.getSubtitleListHeight = function() {
            return $(window).height() - $scope.subtitlesHeight;
        };
        $scope.getSubtitles = function(languageCode, versionNumber) {

            // If this version has no default source translation language
            // it will be empty, in which case we want to wait for user
            // interaction to request a reference subtitle set.
            if (!languageCode || !versionNumber) {
                $scope.status = 'idle';
                return;
            }

            $scope.status = 'loading';

            var that = this;
            SubtitleStorage.getSubtitles(languageCode, versionNumber, function(subtitleData) {
                $scope.onSubtitlesFetched.call(that, subtitleData);
            });

        };
        $scope.onSubtitlesFetched = function (subtitleData) {

            // Save subtitle data to this scope
            $scope.videoTitle = subtitleData.title;
            $scope.videoDescription = subtitleData.description;

            if ( subtitleData.visibility == 'Public' || $scope.isEditable){
                $scope.subtitleList.loadXML(subtitleData.subtitlesXML);
                $scope.status = 'ready';
            }

            // When we have subtitles for an editable set, emit it.
            if ($scope.isWorkingSubtitles()) {
                $scope.$root.workingSubtitles = $scope;
                $scope.$root.$emit('subtitles-fetched');
            }
        };
        $scope.initEmptySubtitles = function() {
            // Save subtitle data to this scope
            $scope.videoTitle = '';
            $scope.videoDescription = '';

            $scope.subtitleList.loadXML(null);
            $scope.status = 'ready';

            // When we have subtitles for an editable set, emit it.
            if ($scope.isWorkingSubtitles()) {
                $scope.$root.workingSubtitles = $scope;
                $scope.$root.$emit('subtitles-fetched');
            }
        };
        $scope.saveSubtitles = function() {
            $scope.status = 'saving';
            return SubtitleStorage.saveSubtitles($scope.videoID,
                                          $scope.languageCode,
                                          $scope.subtitleList.toXMLString(),
                                          $scope.videoTitle,
                                          $scope.videoDescription);
        };
        $scope.setLanguageCode = function(languageCode) {
            $scope.languageCode = languageCode;
            $scope.languageName = SubtitleStorage.getLanguageName(
                    languageCode);
        };
        $scope.setVideoID = function(videoID) {
            $scope.videoID = videoID;
        };

        $('div.subtitles').height($scope.getSubtitleListHeight());
        $scope.$watch($scope.getSubtitleListHeight, function(newHeight) {
            $($('div.subtitles').height(newHeight));
        });

        $scope.$root.$on('will-sync-changed', function(evt, newWillSync) {
            if($scope.isWorkingSubtitles()) {
                willSync = newWillSync;
                updateSyncHelpers();
            };
        });

        $scope.subtitleList.addChangeCallback(function(change) {
            if(change == 'insert' || change == 'remove') {
                updateSyncHelpers();
            }
        });

        $window.onresize = function() {
            $scope.$digest();
        };
    };

    var WorkingSubtitleItemsController = function($scope, $window) {
        var document = $($window.document);

        function startEdit(subtitle, caretPos) {
            var li = $scope.getSubtitleRepeatItem(subtitle);
            $scope.currentEdit.start(subtitle, li);
            if(caretPos === undefined) {
                caretPos = subtitle.markdown.length;
            }
            $scope.currentEdit.draft.initialCaretPos = caretPos;
            document.on('mousedown.subtitle-edit', function(evt) {
                var clicked = $(evt.target);
                var textarea = $('textarea.subtitle-edit', li);
                if(clicked[0] != textarea[0] &&
                    !clicked.hasClass('info-tray') &&
                    clicked.parents('.info-tray').length == 0) {
                    $scope.$apply(function() {
                        finishEdit(true);
                    });
                }
            });
        }

        function finishEdit(commitChanges) {
            // Tell the root scope that we're no longer editing, now.
            document.off('mousedown.subtitle-edit');
            if($scope.currentEdit.finish(commitChanges,
                        $scope.subtitleList)) {
                $scope.$root.$emit('work-done');
            }
        };

        function insertAndStartEdit(before) {
            var newSub = $scope.subtitleList.insertSubtitleBefore(before);
            startEdit(newSub);
        }

        $scope.onSubtitleClick = function(evt, subtitle, action) {
            var madeChange = false;
            switch(action) {
                case 'insert':
                    insertAndStartEdit(subtitle);
                    madeChange = true;
                    break;

                case 'remove':
                    if($scope.currentEdit.isForSubtitle(subtitle)) {
                        $scope.currentEdit.finish(false);
                    }
                    $scope.subtitleList.removeSubtitle(subtitle);
                    madeChange = true;
                    break;

                case 'edit':
                    if(!$scope.currentEdit.isForSubtitle(subtitle)) {
                        var caretPos = $window.getSelection().anchorOffset;
                        startEdit(subtitle, caretPos);
                        madeChange = true;
                    }
                    break;
            }
            if(madeChange) {
                evt.preventDefault();
                $scope.$root.$emit('work-done');
            }
        }

        $scope.newSubtitleClicked = function(evt) {
            insertAndStartEdit(null);
            evt.preventDefault();
            $scope.$root.$emit('work-done');
        }

        $scope.onEditKeydown = function(evt) {
            var subtitle = $scope.currentEdit.draft.storedSubtitle;

            if (evt.keyCode === 13 && !evt.shiftKey) {
                // Enter without shift finishes editing
                var nextSubtitle = $scope.subtitleList.nextSubtitle(subtitle);
                finishEdit(true);
                if(nextSubtitle === null) {
                    insertAndStartEdit(null);
                } else {
                    startEdit(nextSubtitle);
                }
                evt.preventDefault();
            } else if (evt.keyCode === 27) {
                // Escape cancels editing
                finishEdit(false);
                evt.preventDefault();
            } else if (evt.keyCode == 9) {
                // Tab navigates to other subs
                finishEdit(true);
                if(!evt.shiftKey) {
                    var targetSub = $scope.subtitleList.nextSubtitle(subtitle);
                } else {
                    var targetSub = $scope.subtitleList.prevSubtitle(subtitle);
                }
                if(targetSub !== null) {
                    startEdit(targetSub);
                }
                evt.preventDefault();
            }
        }
    }

    root.LanguageSelectorController = LanguageSelectorController;
    root.SaveSessionController = SaveSessionController;
    root.SubtitleListController = SubtitleListController;
    root.WorkingSubtitleItemsController = WorkingSubtitleItemsController;

}).call(this);
