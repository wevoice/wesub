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

    var TimelineController = function($scope, SubtitleStorage) {
        $scope.scale = 1.0;
        $scope.currentTime = $scope.duration = null;
        $scope.subtitle = null;

        function updateTime(pop) {
            $scope.currentTime = Math.floor(pop.currentTime() * 1000);
            $scope.duration = Math.floor(pop.duration() * 1000);
            $scope.$digest();
        }

        $scope.$root.$on('video-ready', function($event, pop) {
            console.log("video-ready");
            updateTime(pop);
        });
        $scope.$root.$on('video-timechanged', function($event, pop) {
            console.log("video-timechanged");
            updateTime(pop);
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
