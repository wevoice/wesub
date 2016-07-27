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

        // When paused, we want to know if we have been paused by auto-pause

        function ModeHandler() {}
        ModeHandler.prototype = { 
            onActivate: function() {},
            onDeactivate: function() {},
            onTextEditKeystroke: function() {},
            onVideoUpdate: function() {}
        }

        function MagicModeHandler() {}
        MagicModeHandler.prototype = Object.create(ModeHandler.prototype);
        _.extend(MagicModeHandler.prototype, {
            keystrokeTimeout: null,
            continuousTypingTimeout: null,
            magicResumeTimeout: null,
            magicPaused: false,
            onVideoUpdate: function() {
                // TODO: it would be better to have explicit user paused events instead of having to check the video player service
                // and acting on its current state
                if(VideoPlayer.isPlaying() && this.magicPaused) {
                    this.magicPaused = false;
                    if(this.magicResumeTimeout !== null) {
                        $timeout.cancel(this.magicResumeTimeout);
                        this.magicResumeTimeout = null;
                    }
                } else if(!VideoPlayer.isPlaying() && !this.magicPaused) {
                    if(this.keystrokeTimeout !== null) {
                        $timeout.cancel(this.keystrokeTimeout);
                        this.keystrokeTimeout = null;
                    }
                    if(this.continuousTypingTimeout !== null) {
                        $timeout.cancel(this.continuousTypingTimeout);
                        this.continuousTypingTimeout = null;
                    }
                }
            },
            onTextEditKeystroke: function() {
                // TODO: make this into a state machine to clean it up
                // TODO: onVideoUpdate: if(VideoPlayer.isPlaying() && this.magicPaused)
                var self = this;

                if(this.magicResumeTimeout !== null) {
                    $timeout.cancel(this.magicResumeTimeout);
                    self.magicResumeTimeout = $timeout(function() {
                        VideoPlayer.seek(VideoPlayer.currentTime() - 4000);
                        self.magicPaused = false;
                        self.magicResumeTimeout = null;
                        VideoPlayer.play();
                    }, 1000);
                }

                if(!VideoPlayer.isPlaying()) return;

                if(this.continuousTypingTimeout === null) {
                    $log.log('starting continuous typing timeout');
                    this.continuousTypingTimeout = $timeout(function() {
                        $log.log('continuous typing timeout completed');
                        self.magicPaused = true;
                        self.continuousTypingTimeout = null;

                        if(self.keystrokeTimeout !== null) {
                            $timeout.cancel(self.keystrokeTimeout)
                            self.keystrokeTimeout = null;
                        }

                        if(self.magicResumeTimeout === null) {
                            self.magicResumeTimeout = $timeout(function() {
                                self.magicPaused = false;
                                self.magicResumeTimeout = null;
                                VideoPlayer.seek(VideoPlayer.currentTime() - 4000);
                                VideoPlayer.play();
                            }, 1000);
                        }

                        VideoPlayer.pause();
                    }, 4000);
                }


                if(this.keystrokeTimeout !== null) {
                    $timeout.cancel(this.keystrokeTimeout);
                    this.keystrokeTimeout = null;
                }

                this.keystrokeTimeout = $timeout(function() {
                    self.keystrokeTimeout = null;

                    // At least 1 second has elapsed without an edit keystroke
                    if(self.continuousTypingTimeout !== null) {
                        $log.log('cancelled continuous typing timeout');
                        $timeout.cancel(self.continuousTypingTimeout);
                        self.continuousTypingTimeout = null;
                    }
                }, 1000);
            }
        });

        var currentModeHandler = new MagicModeHandler();

        // TODO: if the user types for 4 seconds continuously (at least 1 keystroke per second) pause

        // when a key is pressed, we want to start tracking the time since the last keystroke
        //   if it is more than one second, start this timer over
        //   if it is less than one second, keep counting until we get to 4 seconds
        //   then pause the video

        $scope.$root.$on('text-edit-keystroke', function($event) {
            currentModeHandler.onTextEditKeystroke();
        });

        $scope.$root.$on('video-update', function($event) {
            $log.log('video update');
        });

        $scope.$watch('playbackMode', function(newMode, oldMode) {
            VideoPlayer.pause();
            $log.log('playbackMode changed to ' + newMode);
        });
    }]);
}).call(this);
