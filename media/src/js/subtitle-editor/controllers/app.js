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

    var module = angular.module('amara.SubtitleEditor.controllers.app', []);

    module.controller("AppController", function($scope, $controller,
            EditorData, Workflow) {

        $controller('AppControllerSubtitles', {$scope: $scope});
        $controller('AppControllerLocking', {$scope: $scope});
        $controller('AppControllerEvents', {$scope: $scope});

        $scope.videoId = EditorData.video.id;
        $scope.canSync = EditorData.canSync;
        $scope.canAddAndRemove = EditorData.canAddAndRemove;
        $scope.scrollingSynced = true;
        $scope.workflow = new Workflow($scope.workingSubtitles.subtitleList);
        $scope.timelineShown = !($scope.workflow.stage == 'type');

        $scope.toggleScrollingSynced = function() {
            $scope.scrollingSynced = !$scope.scrollingSynced;
        }

        $scope.toggleTimelineShown = function() {
            $scope.timelineShown = !$scope.timelineShown
        }
    });

    /* AppController is large, so we split it into several components to
     * keep things a bit cleaner.  Each controller runs on the same scope.
     */

    module.controller("AppControllerLocking", function($scope, $timeout,
                EditorData, LockService) {
        var secondsUntilClosing = 120;
        var regainLockTimer;

        $scope.minutesIdle = 0;

        function releaseLock() {
            LockService.releaseLock($scope.videoId, 
                    EditorData.editingVersion.languageCode);
        }

        function regainLock() {
            return LockService.regainLock($scope.videoId,
                    EditorData.editingVersion.languageCode);
        }

        function startUserIdleTimer() {
            var userIdleTimeout = function() {

                $scope.minutesIdle++;

                if ($scope.minutesIdle >= USER_IDLE_MINUTES) {
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
                regainLock();
                regainLockTimer = $timeout(regainLockTimeout, 15 * 1000);
            };

            regainLockTimer = $timeout(regainLockTimeout, 15 * 1000);

        }

        function regainLockAfterIdle() {
            regainLock().then(function onSuccess(response) {
                if (response.data.ok) {
                    $scope.minutesIdle = 0;
                    $scope.$root.$emit('hide-modal');
                    startRegainLockTimer();
                    startUserIdleTimer();
                } else {
                    window.alert("Sorry, could not restart your session.");
                    window.location = '/videos/' + $scope.videoId + "/";
                }
            }, function onError() {
                window.alert("Sorry, could not restart your session.");
                window.location = '/videos/' + $scope.videoId + "/";
            });
        }
        function showIdleModal() {

            var heading = "Warning: you've been idle for more than " + USER_IDLE_MINUTES + " minutes. " +
                "To ensure no work is lost we will close your session in ";

            var closeSessionTimeout;

            var closeSession = function() {

                secondsUntilClosing--;

                if (secondsUntilClosing <= 0) {

                    releaseLock();

                    $scope.$root.$emit("show-modal", {
                        heading: 'Your session has ended. You can try to resume, close the editor, or download your subtitles',
                        buttons: [
                            {'text': 'Try to resume work', 'class': 'yes', 'fn': function() {
                                // TODO: Remove this duplication from below.
                                if (closeSessionTimeout) {
                                    $timeout.cancel(closeSessionTimeout);
                                }

                                regainLockAfterIdle();
                            }},
                            {'text': 'Download subtitles', 'class': 'no', 'fn': function() {
                                $scope.$root.$emit('show-modal-download');
                            }},
                            {'text': 'Close editor', 'class': 'no', 'fn': function() {
                                window.location = '/videos/' + $scope.videoId + "/";
                            }}
                        ]
                    });

                } else {

                    $scope.$root.$emit('change-modal-heading', heading + secondsUntilClosing + " seconds.");
                    closeSessionTimeout = $timeout(closeSession, 1000);

                }
            };

            $scope.$root.$emit("show-modal", {
                heading: heading + secondsUntilClosing + " seconds.",
                buttons: [
                    {'text': 'Try to resume work', 'class': 'yes', 'fn': function() {
                        if (closeSessionTimeout) {
                            $timeout.cancel(closeSessionTimeout);
                        }

                        regainLockAfterIdle();
                    }}
                ]
            });

            closeSessionTimeout = $timeout(closeSession, 1000);
        }

        startUserIdleTimer();
        startRegainLockTimer();

        window.onunload = function() {
            releaseLock();
        }
    });

    module.controller("AppControllerEvents", function($scope, VideoPlayer) {
        function insertAndEditSubtitle() {
            var sub = $scope.workingSubtitles.subtitleList.insertSubtitleBefore(null);
            $scope.currentEdit.start(sub);
        }

        $scope.handleAppKeyDown = function(evt) {
            // Reset the lock timer.
            $scope.minutesIdle = 0;

            // Shortcuts that should work while editing a subtitle
            if (evt.keyCode === 32 && evt.shiftKey) {
                // Space with shift, toggle play / pause.
                evt.preventDefault();
                evt.stopPropagation();
                VideoPlayer.togglePlay();
            }
            else if(evt.target.type == 'textarea') {
                return;
            }
            // Shortcuts that should be disabled while editing a subtitle
            else if(evt.keyCode == 40) {
                // Down arrow, set the start time of the first
                // unsynced sub
                if($scope.timelineShown) {
                    $scope.$root.$emit("sync-next-start-time");
                    evt.preventDefault();
                    evt.stopPropagation();
                }
            } else if(evt.keyCode == 38) {
                // Up arrow, set the end time of the first
                // unsynced sub
                if($scope.timelineShown) {
                    $scope.$root.$emit("sync-next-end-time");
                    evt.preventDefault();
                    evt.stopPropagation();
                }
            } else if(evt.keyCode == 13) {
                if(!$scope.timelineShown) {
                    insertAndEditSubtitle();
                    evt.preventDefault();
                }

            }
        };

        $scope.handleAppMouseMove = function(evt) {
            // Reset the lock timer.
            $scope.minutesIdle = 0;
        };
    });

    module.controller("AppControllerSubtitles", function($scope, EditorData,
                SubtitleStorage, CurrentEditManager, SubtitleVersionManager) {
        $scope.currentEdit = new CurrentEditManager();
        $scope.workingSubtitles = new SubtitleVersionManager(SubtitleStorage);
        $scope.referenceSubtitles = new SubtitleVersionManager(
                SubtitleStorage);

        var editingVersion = EditorData.editingVersion;

        if(editingVersion.versionNumber) {
            $scope.workingSubtitles.getSubtitles(editingVersion.languageCode,
                    editingVersion.versionNumber);
        } else {
            $scope.workingSubtitles.initEmptySubtitles(
                    editingVersion.languageCode);
        }

        $scope.saveSubtitles = function(markComplete) {
            return SubtitleStorage.saveSubtitles(
                    $scope.videoId,
                    $scope.workingSubtitles.language.code,
                    $scope.workingSubtitles.subtitleList.toXMLString(),
                    $scope.workingSubtitles.title,
                    $scope.workingSubtitles.description,
                    markComplete);
        };
    });

    /*
     * Handles the workflow progression area
     */

    module.controller('WorkflowProgressionController', function($scope, EditorData, VideoPlayer) {

        function rewindPlayback() {
            VideoPlayer.pause();
            VideoPlayer.seek(0);
        }

        $scope.endorse = function() {
            if(EditorData.task_id === undefined || 
                    EditorData.task_id === null) {
                $scope.$root.$emit('save', {
                    allowResume: false,
                    markComplete: true,
                });
            } else {
                $scope.$root.$emit('approve-task');
            }
        }

        $scope.onNextClicked = function(evt) {
            if($scope.workflow.stage == 'type') {
                $scope.workflow.switchStage('sync');
                if(!$scope.timelineShown) {
                    $scope.toggleTimelineShown();
                }
                rewindPlayback();
            } else if ($scope.workflow.stage == 'sync') {
                $scope.workflow.switchStage('review');
                rewindPlayback();
            }
            evt.preventDefault();
        }
    });

    /* CurrentEditManager manages the current in-progress edit
     */
    CurrentEditManager = function() {
        this.draft = null;
        this.LI = null;
    }

    CurrentEditManager.prototype = {
        start: function(subtitle, LI) {
            this.draft = subtitle.draftSubtitle();
            this.LI = LI;
        },
        finish: function(commitChanges, subtitleList) {
            var updateNeeded = (commitChanges && this.changed());
            if(updateNeeded) {
                subtitleList.updateSubtitleContent(this.draft.storedSubtitle,
                        this.currentMarkdown());
            }
            this.draft = this.LI = null;
            return updateNeeded;
        },
        storedSubtitle: function() {
            if(this.draft !== null) {
                return this.draft.storedSubtitle;
            } else {
                return null;
            }
        },
        sourceMarkdown: function() {
            return this.draft.storedSubtitle.markdown;
        },
        currentMarkdown: function() {
            return this.draft.markdown;
        },
        changed: function() {
            return this.sourceMarkdown() != this.currentMarkdown();
        },
         update: function(markdown) {
            if(this.draft !== null) {
                this.draft.markdown = markdown;
            }
         },
         isForSubtitle: function(subtitle) {
            return (this.draft !== null && this.draft.storedSubtitle == subtitle);
         },
         inProgress: function() {
            return this.draft !== null;
         },
         lineCounts: function() {
             if(this.draft === null || this.draft.lineCount() < 2) {
                 // Only show the line counts if there are 2 or more lines
                 return null;
             } else {
                 return this.draft.characterCountPerLine();
             }
         },
    };

    /*
     * SubtitleVersionManager: handle the active subtitle version for the
     * reference and working subs.
     *
     */

    SubtitleVersionManager = function(SubtitleStorage) {
        this.SubtitleStorage = SubtitleStorage;
        this.subtitleList = new dfxp.SubtitleList();
        this.versionNumber = null;
        this.language = null;
        this.title = null;
        this.description = null;
        this.state = 'waiting';
    }

    SubtitleVersionManager.prototype = {
        getSubtitles: function(languageCode, versionNumber) {
            this.setLanguage(languageCode);
            this.versionNumber = versionNumber;
            this.state = 'loading';

            var that = this;

            this.SubtitleStorage.getSubtitles(languageCode, versionNumber,
                    function(subtitleData) {
                that.state = 'loaded';
                that.title = subtitleData.title;
                that.description = subtitleData.description;
                that.subtitleList.loadXML(subtitleData.subtitlesXML);
            });
        },
        initEmptySubtitles: function(languageCode) {
            this.setLanguage(languageCode);
            this.versionNumber = null;
            this.title = this.description = '';
            this.subtitleList.loadXML(null);
            this.state = 'loaded';
        },
        setLanguage: function(code) {
            this.language = this.SubtitleStorage.getLanguage(code);
        },
    };

    Workflow = function(subtitleList) {
        var self = this;
        this.subtitleList = subtitleList;
        if(this.subtitleList.length() == 0) {
            this.stage = 'type';
        } else {
            this.stage = 'sync';
        }
        this.subtitleList.addChangeCallback(function() {
            if(self.stage == 'review' && !self.canMoveToReview()) {
                self.stage = 'sync';
            }
        });
    }

    Workflow.prototype = {
        switchStage: function(newStage) {
            if(newStage == 'review' && !this.canMoveToReview()) {
                return;
            }
            this.stage = newStage;
        },
        canMoveToReview: function() {
            return (this.subtitleList.length() > 0 &&
                    !this.subtitleList.needsAnyTranscribed() &&
                    !this.subtitleList.needsAnySynced());
        },
        stageDone: function(stageName) {
            if(stageName == 'type') {
                return (this.stage == 'review' || this.stage == 'sync');
            } else if(stageName == 'sync') {
                return this.stage == 'review'
            } else {
                return false;
            }
        },
    }

    /* Export modal classes as values.  This makes testing and dependency
     * injection easier.
     */

    module.value('CurrentEditManager', CurrentEditManager);
    module.value('SubtitleVersionManager', SubtitleVersionManager);
    module.value('Workflow', Workflow);
}).call(this);
