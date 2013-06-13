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

    var VideoController = function($scope, VideoPlayer) {
        $scope.overlayText = null;
        $scope.showOverlay = false;
        $scope.timelineOverlayText = null;
        $scope.playing = false;
        $scope.currentTime = 0;
        $scope.duration = -1;
        $scope.volumeBarVisible = false;
        $scope.volume = -1.0;

        $scope.$root.$on("video-update", function() {
            $scope.playing = VideoPlayer.isPlaying();
            $scope.currentTime = VideoPlayer.currentTime();
            $scope.duration = VideoPlayer.duration();
            $scope.volume = VideoPlayer.getVolume();
        });
        $scope.$root.$on("video-time-update", function() {
            $scope.currentTime = VideoPlayer.currentTime();
        });

        $scope.playPauseClicked = function(event) {
            VideoPlayer.togglePlay();
            event.preventDefault();
        };

        $scope.setVolume = function(volume) {
            $scope.volume = volume;
            VideoPlayer.setVolume(volume);
        }

        $scope.volumeToggleClicked = function(event) {
            $scope.volumeBarVisible = !$scope.volumeBarVisible;
            event.preventDefault();
        };

        $scope.$watch('workingSubtitles.currentEdit.draft.content()', function(newValue) {
            if(newValue !== null && newValue !== undefined) {
                $scope.overlayText = newValue;
                $scope.showOverlay = true;
            } else if($scope.timelineOverlayText !== null) {
                $scope.overlayText = $scope.timelineOverlayText;
                $scope.showOverlay = true;
            } else {
                $scope.showOverlay = false;
            }
        });
        $scope.$root.$on('subtitle-selected', function($event, scope) {

            if(scope.subtitle.isSynced()) {
                VideoPlayer.playChunk(scope.startTime, scope.duration());
            }
            $scope.overlayText = scope.subtitle.content();
            $scope.showOverlay = true;
        });
        $scope.$root.$on('timeline-subtitle-shown', function(evt, subtitle) {
            if(subtitle !== null) {
                $scope.overlayText = subtitle.content();
                $scope.showOverlay = true;
                $scope.timelineOverlayText = $scope.overlayText;
            } else {
                $scope.showOverlay = false;
                $scope.timelineOverlayText = null;
            }
        });
        $scope.$watch('subtitles-fetched', function(){
              VideoPlayer.init();
        });

    };
    root.VideoController = VideoController;

}).call(this);
