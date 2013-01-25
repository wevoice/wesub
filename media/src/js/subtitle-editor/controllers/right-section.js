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

    var RightSectionController = function($scope, $timeout) {

        // Default module opened/closed states.
        $scope.modulesOpen = {
            approval: true,
            collab: false,
            notes: true
        };

        $scope.approve = function($event) {
            console.log('send back');
            $event.preventDefault();
        };
        $scope.toggleModule = function($event, module) {
            $scope.modulesOpen[module] = !$scope.modulesOpen[module];
            $event.preventDefault();
        };
        $scope.sendBack = function($event) {
            console.log('send back');
            $event.preventDefault();
        };

        $scope.$root.$on('subtitleKeyUp', function($event, options) {
            if (options.parser.needsAnyTranscribed(options.subtitles)) {
                $scope.error = 'You have empty subtitles.';
            } else {
                $scope.error = null;
            }
            $scope.$digest();
        });
        
    };

    root.RightSectionController = RightSectionController;

}).call(this);
