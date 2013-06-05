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

    var TimelineController = function($scope, $timeout, SubtitleStorage, VideoPlayer) {
        $scope.scale = 1.0;
        $scope.currentTime = $scope.duration = null;
        $scope.subtitle = null;
        var lastTimeReturned = null;
        var lastTimeReturnedAt = null;
        var lastTime = null;

        // Handle animating the timeline.  We don't use the timeupdate event
        // from popcorn because it doesn't fire granularly enough.
        var timeoutPromise = null;
        function startTimer() {
            if(timeoutPromise === null) {
                var delay = 30; // aim for 30 FPS or so
                timeoutPromise = $timeout(handleTimeout, delay, false);
            }
        }

        function cancelTimer() {
            if(timeoutPromise !== null) {
                $timeout.cancel(timeoutPromise);
                timeoutPromise = null;
            }
        }

        function handleTimeout() {
            updateTimeline();
            timeoutPromise = null;
            startTimer();
        }

        function updateTime() {
            var newTime = VideoPlayer.currentTime();
            $scope.currentTime = newTime;
            // On the youtube player, popcorn only updates the time every 250
            // ms, which is not enough granularity for our animation.  Try to
            // get more granularity by starting a timer of our own.
            if(VideoPlayer.isPlaying() && lastTimeReturned === newTime) {
                var timePassed = Date.now() - lastTimeReturnedAt;
                // If lots of time has bassed since the last new time, it's
                // possible that the video is slowing down for some reason.
                // Don't adjust the time too much.
                timePassed = Math.min(timePassed, 250);
                $scope.currentTime = newTime + timePassed;
            }
            lastTimeReturned = newTime;
            lastTimeReturnedAt = Date.now();

            // If we adjust the time with the code above, then get a new time
            // from popcorn, it's possible that the time given will be less
            // that our adjusted time.  Try to fudge things a little so that
            // time doesn't go backwards while we're playing.
            if(lastTime !== null && $scope.currentTime < lastTime &&
                $scope.currentTime > lastTime - 250) {
                $scope.currentTime = lastTime;
            }
            lastTime = $scope.currentTime;
        }

        function updateTimeline() {
            updateTime();
            $scope.redrawCanvas();
            $scope.redrawSubtitles();
        }

        $scope.$root.$on('video-update', function() {
            $scope.duration = VideoPlayer.duration();
            updateTimeline();
            if(VideoPlayer.isPlaying()) {
                startTimer();
            } else {
                cancelTimer();
            }
        });

        // Update the timeline subtitles when the underlying data changes.
        $scope.$root.$on('work-done', function() {
            $scope.redrawSubtitles({forcePlace: true});
        });
        $scope.$root.$on('subtitles-fetched', function() {
            $scope.redrawSubtitles({forcePlace: true});
        });

        $scope.$root.$on('sync-next-start-time', function($event) {
            if($scope.currentTime === null) {
                return;
            }
            var subtitleList = $scope.workingSubtitles.subtitleList;
            var lastSynced = subtitleList.lastSyncedSubtitle();
            var firstUnsynced = subtitleList.firstUnsyncedSubtitle();
            var nextUnsynced = subtitleList.secondUnsyncedSubtitle();

            if($scope.currentTime < lastSynced.endTime) {
                // We haven't moved past the last synced subtitle, just ignore
                // the event.
                return;
            }
            if(firstUnsynced !== null &&
                firstUnsynced.startTime < 0) {
                // The first unsynced subtitle needs a start time, set it
                subtitleList.updateSubtitleTime(firstUnsynced,
                    $scope.currentTime, firstUnsynced.endTime);
                $scope.$root.$emit("work-done");
            } else {
                // Set both the first unsynced subtitle's end time and the
                // second unsynced subtitle's start time to the current time.
                subtitleList.updateSubtitleTime(firstUnsynced,
                    firstUnsynced.startTime, $scope.currentTime);
                if(nextUnsynced !== null) {
                    subtitleList.updateSubtitleTime(nextUnsynced,
                            $scope.currentTime, nextUnsynced.endTime);
                }
                $scope.$root.$emit("work-done");
            }
        });
        $scope.$root.$on('sync-next-end-time', function($event) {
            if($scope.currentTime === null) {
                return;
            }
            var subtitleList = $scope.workingSubtitles.subtitleList;
            var lastSynced = subtitleList.lastSyncedSubtitle();
            var firstUnsynced = subtitleList.firstUnsyncedSubtitle();

            if($scope.currentTime < lastSynced.endTime) {
                // We haven't moved past the last synced subtitle, just ignore
                // the event.
                return;
            }
            if(firstUnsynced !== null &&
                firstUnsynced.startTime >= 0 &&
                firstUnsynced.endTime < 0) {
                subtitleList.updateSubtitleTime(firstUnsynced,
                    firstUnsynced.startTime, $scope.currentTime);
                $scope.$root.$emit("work-done");
            }
        });
    };

    root.TimelineController = TimelineController;

}).call(this);
