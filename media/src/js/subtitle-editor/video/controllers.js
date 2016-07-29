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

    var module = angular.module('amara.SubtitleEditor.video.controllers', []);

    module.controller('VideoController', ['$scope', '$sce', 'EditorData', 'VideoPlayer', 'PreferencesService', function($scope, $sce, EditorData, VideoPlayer, PreferencesService) {
        $scope.subtitleText = null;
        $scope.showSubtitle = false;

        $scope.videoState = {
            loaded: false,
            playing: false,
            currentTime: null,
            duration: null,
            volumeBarVisible: false,
            volume: 0.0,
        }

        $scope.$root.$on("video-update", function() {
            $scope.videoState.loaded = true;
            $scope.videoState.playing = VideoPlayer.isPlaying();
            $scope.videoState.currentTime = VideoPlayer.currentTime();
            $scope.videoState.duration = VideoPlayer.duration();
            $scope.videoState.volume = VideoPlayer.getVolume();
        });
        $scope.$root.$on("video-time-update", function(evt, currentTime) {
            $scope.videoState.currentTime = currentTime;
        });
        $scope.$root.$on("video-volume-update", function(evt, volume) {
            $scope.videoState.volume = volume;
        });
        $scope.$root.$on("user-action", function() {
            $scope.toggleTutorial(false);
            if ($scope.hideTutorialNextTime) {
                PreferencesService.tutorialShown();
                $scope.hideTutorialNextTime = false;
                $scope.hideNextTime();
	    }
	});

        $scope.playPauseClicked = function(event) {
            VideoPlayer.togglePlay();
            event.preventDefault();
        };

        $scope.volumeToggleClicked = function(event) {
            $scope.volumeBarVisible = !$scope.volumeBarVisible;
            event.preventDefault();
        };

        $scope.$watch('currentEdit.draft.content()', function(newValue) {
            if(newValue !== null && newValue !== undefined) {
                $scope.subtitleText = $sce.trustAsHtml(newValue);
                $scope.showSubtitle = true;
            } else if($scope.timeline.shownSubtitle !== null) {
                $scope.subtitleText = $sce.trustAsHtml($scope.timeline.shownSubtitle.content());
                $scope.showSubtitle = true;
            } else {
                $scope.showSubtitle = false;
            }
        });
        $scope.$root.$on('subtitle-selected', function($event, scope) {
            if(scope.subtitle.isSynced()) {
                VideoPlayer.playChunk(scope.startTime, scope.duration());
            }
            $scope.subtitleText = $sce.trustAsHtml(scope.subtitle.content());
            $scope.showSubtitle = true;
        });
        $scope.$watch('timeline.shownSubtitle', function(subtitle) {
            if(subtitle !== null) {
                $scope.subtitleText = $sce.trustAsHtml(subtitle.content());
                $scope.showSubtitle = true;
            } else {
                $scope.showSubtitle = false;
            }
        });

        // use evalAsync so that the video player gets loaded after we've
        // rendered all of the subtitles.
        $scope.$evalAsync(function() {
              VideoPlayer.init();
        });

    }]);

    module.controller('PlaybackModeController', ['$scope', '$timeout', '$log', 'VideoPlayer',
                      function($scope, $timeout, $log, VideoPlayer) {
        $scope.playbackMode = 'magic';

        function ModeHandler() {}
        ModeHandler.prototype = { 
            onActivate: function() {},
            onDeactivate: function() {},
            onTextEditKeystroke: function() {},
            onUserVideoResume: function() {},
            onUserVideoPause: function() {}
        }

        // TODO: how to test this?
        function MagicModeHandler() {}
        MagicModeHandler.prototype = Object.create(ModeHandler.prototype);
        _.extend(MagicModeHandler.prototype, {
            keystrokeTimeout: null,
            continuousTypingTimeout: null,
            magicPauseStartTime: -1,
            anticipatePauseStartTime: -1,
            state: 'inactive', // inactive, anticipating-pause, magic-paused

            cancelKeystrokeTimeout: function() {
                if(this.keystrokeTimeout !== null) {
                    $timeout.cancel(this.keystrokeTimeout);
                    this.keystrokeTimeout = null;
                }
            },
            cancelContinuousTypingTimeout: function() {
                if(this.continuousTypingTimeout !== null) {
                    $timeout.cancel(this.continuousTypingTimeout);
                    this.continuousTypingTimeout = null;
                }
            },

            reset: function() {
                $log.log('[magic-pause] reset');
                this.state = 'inactive';
                this.cancelKeystrokeTimeout();
                this.cancelContinuousTypingTimeout();
                this.magicPauseStartTime = -1;
                this.anticipatePauseStartTime = -1;
            },
            startAnticipatingPause: function() {
                $log.log('[magic-pause] start anticipating pause');
                this.anticipatePauseStartTime = VideoPlayer.currentTime();

                var self = this;
                self.continuousTypingTimeout = $timeout(function() {
                    // At least 4 seconds have elapsed while the user is continuously typing
                    self.continuousTypingTimeout = null;
                    self.startMagicPause();
                }, 4000);

                this.continueAnticipatingPause();
            },
            continueAnticipatingPause: function() {
                if(!VideoPlayer.isPlaying()) {
                    this.reset();
                    return;
                }

                $log.log('[magic-pause] continue anticipating pause');

                this.state = 'anticipating-pause';

                var self = this;
                self.cancelKeystrokeTimeout();
                self.keystrokeTimeout = $timeout(function() {
                    // At least 1 second has elapsed without an edit keystroke
                    self.keystrokeTimeout = null;
                    self.reset();
                }, 1000);
            },
            startMagicPause: function() {
                $log.log('[magic-pause] start magic pause');
                if(!VideoPlayer.isPlaying()) {
                    // We have been paused by the user or some external piece of code
                    this.reset();
                    return;
                }

                // If we're more than half a second away from the expected pause time,
                // assume we have been seeked by the user or some external piece of code
                // 
                // NOTE: This is a little bit ugly. It solves the problem, but if we do subsecond seeks
                // somewhere else during a magic pause, this may cause unexpected behavior.
                //
                // That being said, we will probably have to modify this code if there's a use case
                // which involves sub-second seeking during a magic pause.
                //
                // The alternative is to truly differentiate between user initiated video updates, and those initiated by external code.
                // And in that case, we'd have to ignore non-user initiated events generated by calling the VideoPlayer API from within
                // this mode handler.
                var currentTime = VideoPlayer.currentTime();
                var expectedTime = this.anticipatePauseStartTime + 4000;
                var error = Math.abs(expectedTime - currentTime);
                if(error > 500) {
                    this.reset();
                    return;
                }

                this.state = 'magic-paused';
                VideoPlayer.pause();
                this.magicPauseStartTime = VideoPlayer.currentTime();
                this.continueMagicPause();
            },
            continueMagicPause: function() {
                var self = this;

                $log.log('[magic-pause] continue magic pause');

                this.cancelKeystrokeTimeout();
                self.keystrokeTimeout = $timeout(function() {
                    // At least 1 second has elapsed without an edit keystroke
                    self.keystrokeTimeout = null;

                    // If we haven't been unpaused and the video time is exactly the magic pause start time,
                    // then the magic pause completed without user or external code intervention.
                    // So we can safely seek backwards.
                    $log.log('[magic-pause] magic resume, current time = ' +  VideoPlayer.currentTime() + ', pause start = ' + self.magicPauseStartTime);
                    var deltaTime = Math.abs(VideoPlayer.currentTime() - self.magicPauseStartTime);
                    if(!VideoPlayer.isPlaying() && deltaTime < 100) {
                        // TODO: if the user hits resume withing 100ms of the magic resume, this may still seek backwards, and be upsetting for the user
                        $log.log('[magic-pause] magic resume succeeded');
                        VideoPlayer.seek(self.magicPauseStartTime - 3000);
                        VideoPlayer.play();
                    }

                    self.reset();
                }, 1000);
            },

            onActivate: function() {
                // This mode has just been activated. Return to the initial state.
                this.reset();
            },
            onDeactivate: function() {
                this.reset();
            },
            onTextEditKeystroke: function() {
                switch(this.state) {
                    case 'inactive':
                        this.startAnticipatingPause();
                        break;
                    case 'anticipating-pause':
                        this.continueAnticipatingPause();
                        break;
                    case 'magic-paused':
                        this.continueMagicPause();
                        break;
                }
            }
        });

        var currentModeHandler = new MagicModeHandler();

        $scope.$root.$on('text-edit-keystroke', function($event) {
            currentModeHandler.onTextEditKeystroke();
        });

        $scope.$watch('playbackMode', function(newMode, oldMode) {
            VideoPlayer.pause();
            $log.log('playbackMode changed to ' + newMode);
            currentModeHandler.onDeactivate();
            // TODO: switch the current mode handler
            currentModeHandler.onActivate();
        });
    }]);
}).call(this);
