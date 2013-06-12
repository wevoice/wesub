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

    var module = angular.module('amara.SubtitleEditor.services.video', []);

    module.factory('VideoPlayer', function($rootScope, SubtitleStorage) {
        var videoURLs = [];
        var pop = null;
        var playing = false;

        function emitSignal(signalName) {
            $rootScope.$apply(function() {
                $rootScope.$emit(signalName);
            });
        }

        function handlePopcornEvents() {
            // Handle popcorn events
            pop.on('canplay', function() {
                emitSignal('video-update');
            }).on('playing', function() {
                playing = true;
                emitSignal('video-update');
            }).on('pause', function() {
                playing = false;
                emitSignal('video-update');
            }).on('ended', function() {
                playing = false;
                emitSignal('video-update');
            }).on('durationchange', function() {
                emitSignal('video-update');
            }).on('timeupdate', function() {
                emitSignal('video-time-update');
            }).on('seeked', function() {
                emitSignal('video-update');
            });
        }

        // private methods
        function removeAllTrackEvents() {
            var trackEvents = pop.getTrackEvents();
            for (var i = 0; i < trackEvents.length; i++) {
                pop.removeTrackEvent(trackEvents[i].id);
            }
        };

        // Public methods
        return {
            init: function() {
                videoURLs = SubtitleStorage.getVideoURLs();
                pop = window.Popcorn.smart('#video', videoURLs, {
                    controls: false,
                });
                handlePopcornEvents();
            },
            play: function() {
                pop.play();
            },
            pause: function() {
                pop.pause();
            },
            seek: function(time) {
                pop.currentTime(time / 1000);
            },
            togglePlay: function() {
                if (pop.paused()) {
                    pop.play();
                } else {
                    pop.pause();
                }
            },
            currentTime: function() {
                return Math.floor(pop.currentTime() * 1000);
            },
            duration: function() {
                return Math.floor(pop.duration() * 1000);
            },
            isPlaying: function() {
                return playing;
            },
            playChunk: function(start, duration) {
                // Play a specified amount of time in a video, beginning at
                // 'start', and then pause.

                pop.pause();

                // Remove any existing cues that may interfere.
                removeAllTrackEvents();

                if (start < 0) {
                    start = 0;
                }
                pop.currentTime(start / 1000);
                pop.cue((start + duration) / 1000, function() {
                    pop.pause();
                });
                pop.play();
            },
        };
    });
}).call(this);
