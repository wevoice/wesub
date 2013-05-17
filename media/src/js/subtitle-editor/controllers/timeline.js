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

        $scope.$root.$on('video-ready', function($event, pop) {
            console.log("video-ready");
            $scope.currentTime = pop.currentTime();
            $scope.duration = pop.duration();
            $scope.$digest();

        });
        $scope.$root.$on('video-timechanged', function($event, pop) {
            console.log("video-timechanged");
            $scope.currentTime = pop.currentTime();
            $scope.duration = pop.duration();
            $scope.$digest();
        });
    };

    root.TimelineController = TimelineController;

}).call(this);
