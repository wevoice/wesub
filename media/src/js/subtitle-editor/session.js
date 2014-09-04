// Amara, universalsubtitles.org
//
// Copyright (C) 2014 Participatory Culture Foundation
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
    var module = angular.module('amara.SubtitleEditor.session', []);

    module.controller('SessionBackend', ["$scope", "$q", "EditorData", "SubtitleStorage", function($scope, $q, EditorData, SubtitleStorage) {
        /* SessionControllerBackend handles the low-level details for
         * SessionController.  This includes things like saving the subtitles,
         * approving/recting tasks, etc.
         */
        $scope.sessionBackend = {
            saveSubtitles: function(markComplete) {
                return SubtitleStorage.saveSubtitles(
                    EditorData.video.id,
                    $scope.workingSubtitles.language.code,
                    $scope.workingSubtitles.subtitleList.toXMLString(),
                    $scope.workingSubtitles.title,
                    $scope.workingSubtitles.description,
                    $scope.workingSubtitles.metadata,
                    markComplete).then(function onSuccess(response) {
                        $scope.workingSubtitles.versionNumber = response.data.version_number;
                        return true;
                });
            },
            saveNotes: function() {
                return SubtitleStorage.updateTaskNotes($scope.collab.notes);
            },
            approveTask: function() {
                return SubtitleStorage.approveTask(
                        $scope.workingSubtitles.versionNumber,
                        $scope.collab.notes);
            },
            sendBackTask: function() {
                return SubtitleStorage.sendBackTask(
                        $scope.workingSubtitles.versionNumber,
                        $scope.collab.notes);
            },
        };
    }]);

    module.controller('SessionController', ["$scope", "$sce", "$q", "$window", "EditorData", function($scope, $sce, $q, $window, EditorData) {
        /*
         * SessionController handles the high-level issues involved with
         * sending the user's work back to the server.  SessionController
         * works on the AppController's scope and creates a session object
         * there.  That object is responsible for:
         *   - Saving, approving/rejecting tasks, exiting, etc.
         *   - Tracking user changes to the subtitles, task notes, etc.
         *   - Popping up confirmation dialogs if the user wants to exit while
         *     there are outstanding changes
         *   - Popping up freeze boxes while we are waiting for the server to
         *     respond to our requests.
         */

        var changes = {
            subtitles: false,
            notes: false
        };
        var exiting = false;

        function redirectTo(location) {
            $scope.dialogManager.showFreezeBox($sce.trustAsHtml('Exiting&hellip;'));
            exiting = true;
            $window.location = location;
        }

        function redirectToVideoPage() {
            redirectTo('/videos/' + EditorData.video.id + '/');
        }

        function redirectToLegacyEditor() {
            redirectTo(EditorData.oldEditorURL);
        }

        function saveSubtitles(markComplete) {
            if($scope.overrides.forceSaveError) {
                var deferred = $q.defer();
                deferred.reject('Simulated Error');
                return deferred.promise;
             }else if(changes.subtitles || markComplete !== undefined) {
                return $scope.sessionBackend.saveSubtitles(markComplete)
                    .then(function() {
                        changes.subtitles = false;
                    });
            } else {
                // No changes need to be saved, just return a dummy promise.
                var deferred = $q.defer();
                deferred.resolve(true);
                return deferred.promise;
            }
        }

        function saveChanges(markComplete) {
            var promise = saveSubtitles(markComplete);
            if(changes.notes) {
                promise = promise.then($scope.sessionBackend.saveNotes)
                    .then(function() {
                    changes.notes = false;
                });
            }
            return promise;
        }

        $scope.session = {
            subtitlesChanged: function() {
                changes.subtitles = true;
            },
            notesChanged: function() {
                changes.notes = true;
            },
            resetChanges: function() {
                changes = {
                    subtitles: false,
                    notes: false
                };
            },
            unsavedChanges: function() {
                return changes.subtitles || changes.notes;
            },
            exit: function() {
                if(!this.unsavedChanges()) {
                    redirectToVideoPage();
                } else {
                    $scope.dialogManager.openDialog('unsavedWork', {
                        'exit': redirectToVideoPage
                    });
                }
            },
            exitToLegacyEditor: function() {
                if(!this.unsavedChanges()) {
                    redirectToLegacyEditor();
                } else {
                    $scope.dialogManager.openDialog('legacyEditorUnsavedWork', {
                        'discardChangesAndOpenLegacyEditor': redirectToLegacyEditor
                    });
                }
            },
            save: function() {
                var msg = $sce.trustAsHtml('Saving&hellip;');
                $scope.dialogManager.showFreezeBox(
                        $sce.trustAsHtml('Saving&hellip;'));
                saveChanges().then(function onSuccess() {
                    $scope.dialogManager.closeFreezeBox();
                    $scope.dialogManager.openDialog('changesSaved', {
                        exit: redirectToVideoPage
                    });
                }, function onError() {
                    $scope.dialogManager.closeFreezeBox();
                    $scope.dialogManager.open('save-error');
                });
            },
            endorse: function() {
                $scope.dialogManager.showFreezeBox(
                        $sce.trustAsHtml('Publishing subtitles&hellip;'));
                if(EditorData.task_id) {
                    var promise = saveSubtitles(true)
                        .then($scope.sessionBackend.approveTask);
                } else {
                    var promise = saveChanges(true);
                }
                promise.then(function() {
                    redirectToVideoPage();
                });
            },
            canEndorse: function() {
                return $scope.workingSubtitles.subtitleList.isComplete();
            },
            approveTask: function() {
                $scope.dialogManager.showFreezeBox(
                        $sce.trustAsHtml('Accepting subtitles&hellip;'));
                saveSubtitles()
                    .then($scope.sessionBackend.approveTask)
                    .then(redirectToVideoPage);
            },
            rejectTask: function() {
                $scope.dialogManager.showFreezeBox(
                        $sce.trustAsHtml('Sending subtitles back&hellip;'));
                saveSubtitles()
                    .then($scope.sessionBackend.sendBackTask)
                    .then(redirectToVideoPage);
            }
        };

        $scope.onExitClicked = function($event) {
            $event.preventDefault();
            $event.stopPropagation();
            $scope.session.exit();
        }

        $scope.onLegacyEditorClicked = function($event) {
            $event.preventDefault();
            $event.stopPropagation();
            $scope.session.exitToLegacyEditor();
        }

        $scope.onSaveClicked = function($event) {
            $event.preventDefault();
            $event.stopPropagation();
            $scope.session.save();
        }

        $scope.$root.$on('work-done', function() {
            $scope.session.subtitlesChanged();
        });

        $window.onbeforeunload = function() {
            if($scope.session.unsavedChanges() && !exiting) {
              return "You have unsaved work";
            } else {
              return null;
            }
        };
    }]);
}).call(this);
