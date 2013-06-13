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
    var $ = root.AmarajQuery;

    /* CurrentEditManager manages the current in-progress edit
     */
    function CurrentEditManager() {
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

    function SubtitleVersionManager(SubtitleStorage) {
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



    function AppController($scope, $timeout, $window, LockService,
            VideoPlayer, SubtitleStorage) {
        var minutesIdle = 0;
        var secondsUntilClosing = 120;
        var regainLockTimer;

        $scope.canSync = $window.editorData.canSync;
        $scope.canAddAndRemove = $window.editorData.canAddAndRemove;
        $scope.scrollingSynced = true;
        $scope.timelineShown = true;
        $scope.currentEdit = new CurrentEditManager();
        $scope.workingSubtitles = new SubtitleVersionManager(SubtitleStorage);
        $scope.referenceSubtitles = new SubtitleVersionManager(SubtitleStorage);

        $scope.toggleScrollingSynced = function() {
            $scope.scrollingSynced = !$scope.scrollingSynced;
        }

        $scope.toggleTimelineShown = function() {
            $scope.timelineShown = !$scope.timelineShown
        }

        $scope.saveSubtitles = function() {
            return SubtitleStorage.saveSubtitles(
                    $scope.videoId,
                    $scope.workingSubtitles.language.code,
                    $scope.workingSubtitles.subtitleList.toXMLString(),
                    $scope.workingSubtitles.title,
                    $scope.workingSubtitles.description);
        };


        function releaseLock() {
            LockService.releaseLock($scope.videoId, $scope.languageCode);
        }

        function regainLock() {
            return LockService.regainLock($scope.videoId,
                    $scope.languageCode);
        }

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
                regainLock();
                regainLockTimer = $timeout(regainLockTimeout, 15 * 1000);
            };

            regainLockTimer = $timeout(regainLockTimeout, 15 * 1000);

        }

        function regainLockAfterIdle() {
            regainLock().then(function onSuccess(response) {
                if (response.data.ok) {
                    minutesIdle = 0;
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

        $scope.handleAppKeyDown = function(evt) {
            // Reset the lock timer.
            minutesIdle = 0;

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
                $scope.$root.$emit("sync-next-start-time");
                evt.preventDefault();
                evt.stopPropagation();
            } else if(evt.keyCode == 38) {
                // Up arrow, set the end time of the first
                // unsynced sub
                $scope.$root.$emit("sync-next-end-time");
                evt.preventDefault();
                evt.stopPropagation();
            }
        };

        $scope.handleAppMouseMove = function(evt) {
            // Reset the lock timer.
            minutesIdle = 0;
        };

        startUserIdleTimer();
        startRegainLockTimer();

        window.onunload = function() {
            releaseLock();
        }
    };

    root.AppController = AppController;

}).call(this);
