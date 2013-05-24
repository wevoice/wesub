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

    var root = this;
    var $ = root.AmarajQuery;

    var VideoController = function($scope, SubtitleStorage, $timeout) {
        /**
         * Responsible for initializing the video and all video controls.
         * @param $scope
         * @param SubtitleStorage
         * @constructor
         */

        // The Popcorn instance.
        //
        // If this is a YouTube video, force controls.

        var videoURLs = SubtitleStorage.getVideoURLs();

        $scope.pop = window.Popcorn.smart('#video', videoURLs);
        $scope.pop.controls(true);

        // We have to broadcast this in a timeout to make sure the TimelineController has
        // loaded and registered it's event listener, first.
        //
        // There most likely is a better way to do this.
        $scope.pop.on('canplay', function() {
            $scope.$root.$broadcast('video-ready', $scope.pop);
        });
        $scope.pop.on('timeupdate', function() {
            $scope.$root.$broadcast('video-timechanged', $scope.pop);
        });

        $scope.playChunk = function(start, duration) {
            // Play a specified amount of time in a video, beginning at 'start',
            // and then pause.

            // Pause the video, first.
            $scope.pop.play();

            // Remove any existing cues that may interfere.
            $scope.removeAllTrackEvents();

            if (start < 0) {
                start = 0;
            }

            // Set the new start time.
            $scope.pop.currentTime(start);

            // Set a new cue to pause the video at the end of the chunk.
            $scope.pop.cue(start + duration, function() {
                $scope.pop.pause();
            });

            // Play the video.
            $scope.pop.play();

        };
        $scope.removeAllTrackEvents = function() {

            var trackEvents = $scope.pop.getTrackEvents();
            for (var i = 0; i < trackEvents.length; i++) {
                $scope.pop.removeTrackEvent(trackEvents[i].id);
            }

        };
        $scope.togglePlay = function() {

            // If the video is paused, play it.
            if ($scope.pop.paused()) {
                $scope.pop.play();

            // Otherwise, pause it.
            } else {
                $scope.pop.pause();
            }

        };

        $scope.updateSubtitleOverlay = function(subtitle) {
           // Update the Popcorn subtitle instance's text.
            $scope.pop.amarasubtitle(subtitle.$id, {
                text: subtitle.content(),
            });
        }
        $scope.$root.$on('subtitle-key-up', function($event, options) {
            $scope.updateSubtitleOverlay(options.subtitle);
        });
        $scope.$root.$on('subtitle-selected', function($event, scope) {

            var startTimeSeconds = scope.subtitle.startTimeSeconds();
            var endTimeSeconds = scope.subtitle.endTimeSeconds();
            if (!isNaN(endTimeSeconds)){
                $scope.playChunk(startTimeSeconds, endTimeSeconds- startTimeSeconds);
            }else{
            // If this video is not a Vimeo video, set the current time to
            // the start of the subtitle.
            //
            // We don't do this for Vimeo videos because their player doesn't support
            // fuzzy-scrubbing to precise keyframes.
            if ($scope.pop.video._util.type !== 'Vimeo') {
                $scope.pop.currentTime(startTimeSeconds);
            }

            }

            $scope.updateSubtitleOverlay(scope.subtitle);
        });

    };
    root.VideoController = VideoController;

}).call(this);
