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

    module.controller('VideoController', ['$scope', '$sce', 'EditorData', 'VideoPlayer', function($scope, $sce, EditorData, VideoPlayer) {
        $scope.subtitleText = null;
        $scope.showSubtitle = false;
        if(EditorData.work_mode.type == 'normal') {
            $scope.showOverlay = true;
        } else {
            $scope.showOverlay = false;
        }

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
        $scope.$root.$on("video-playback-changes", function() {
            $scope.showOverlay = false;
        });
        $scope.$root.$on("app-click", function() {
            $scope.showOverlay = false;
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
}).call(this);
