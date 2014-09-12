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
                    $scope.workingSubtitles.subtitleList.toXMLString(),
                    $scope.workingSubtitles.title,
                    $scope.workingSubtitles.description,
                    $scope.workingSubtitles.metadata,
                    markComplete, null).then(this.afterSaveSubtitles);
            },
            saveSubtitlesWithAction: function(action) {
                return SubtitleStorage.saveSubtitles(
                    $scope.workingSubtitles.subtitleList.toXMLString(),
                    $scope.workingSubtitles.title,
                    $scope.workingSubtitles.description,
                    $scope.workingSubtitles.metadata,
                    null, action).then(this.afterSaveSubtitles);
            },
            performAction: function(action) {
                return SubtitleStorage.performAction(action);
            },
            afterSaveSubtitles: function(response) {
                $scope.workingSubtitles.versionNumber = response.data.version_number;
                return true;
            },
            subtitlesComplete: function() {
                return $scope.workingSubtitles.subtitleList.isComplete();
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
         *   - Tracking user changes to the subtitles
         *   - Popping up confirmation dialogs if the user wants to exit while
         *     there are outstanding changes
         *   - Popping up freeze boxes while we are waiting for the server to
         *     respond to our requests.
         */

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
             } else if($scope.session.subtitlesChanged || markComplete !== undefined) {
                return $scope.sessionBackend.saveSubtitles(markComplete)
                    .then(function() {
                        $scope.session.subtitlesChanged = false;
                    });
            } else {
                // No changes need to be saved, just return a dummy promise.
                var deferred = $q.defer();
                deferred.resolve(true);
                return deferred.promise;
            }
        }

        $scope.session = {
            exit: function() {
                if(!$scope.session.subtitlesChanged) {
                    redirectToVideoPage();
                } else {
                    $scope.dialogManager.openDialog('unsavedWork', {
                        'exit': redirectToVideoPage
                    });
                }
            },
            exitToLegacyEditor: function() {
                if(!$scope.session.subtitlesChanged) {
                    redirectToLegacyEditor();
                } else {
                    $scope.dialogManager.openDialog('legacyEditorUnsavedWork', {
                        'discardChangesAndOpenLegacyEditor': redirectToLegacyEditor
                    });
                }
            },
            save: function() {
                var msg = $sce.trustAsHtml('Saving&hellip;');
                $scope.dialogManager.showFreezeBox(msg);
                saveSubtitles().then(function onSuccess() {
                    $scope.dialogManager.closeFreezeBox();
                    $scope.dialogManager.openDialog('changesSaved', {
                        exit: redirectToVideoPage
                    });
                }, function onError() {
                    $scope.dialogManager.closeFreezeBox();
                    $scope.dialogManager.open('save-error');
                });
            },
            /*
            endorse: function() {
                $scope.dialogManager.showFreezeBox(
                        $sce.trustAsHtml('Publishing subtitles&hellip;'));
                if(EditorData.task_id) {
                    var promise = saveSubtitles(true)
                        .then($scope.sessionBackend.approveTask);
                } else {
                    var promise = saveSubtitles(true);
                }
                promise.then(function() {
                    redirectToVideoPage();
                });
            },
            */
        };

        $scope.actions = _.map(EditorData.actions, function(action) {
            var sessionAction = {
                label: action.label,
                class: action.class,
                canPerform: function() {
                    if(action.complete === true) {
                        return $scope.sessionBackend.subtitlesComplete();
                    } else {
                        return true;
                    }
                },
                perform: function() {
                    var msg = $sce.trustAsHtml(action.in_progress_text + '&hellip;');
                    $scope.dialogManager.showFreezeBox(msg);
                    if($scope.session.subtitlesChanged) {
                        var promise = $scope.sessionBackend.saveSubtitlesWithAction(action.name);
                    } else {
                        var promise = $scope.sessionBackend.performAction(action.name);
                    }

                    promise.then(
                        function onSuccess() {
                            $scope.dialogManager.closeFreezeBox();
                            redirectToVideoPage();
                        },
                        function onError() {
                            $scope.dialogManager.closeFreezeBox();
                            $scope.dialogManager.open('save-error');
                        });
                }
            };

            return sessionAction;
        });

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

        $scope.onSaveDraftClicked = function($event) {
            $event.preventDefault();
            $event.stopPropagation();
            $scope.session.save();
        }

        $scope.$root.$on('work-done', function() {
            $scope.session.subtitlesChanged = true;
        });

        $window.onbeforeunload = function() {
            if($scope.session.subtitlesChanged && !exiting) {
              return "You have unsaved work";
            } else {
              return null;
            }
        };
    }]);
}).call(this);
