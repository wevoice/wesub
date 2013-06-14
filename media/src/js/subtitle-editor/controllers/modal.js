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
    var module = angular.module('amara.SubtitleEditor.controllers.modal', []);

    module.controller('ModalController', function($scope, SubtitleStorage) {
        /**
         * Responsible for handling the various states of the modal.
         * @param $scope
         * @param SubtitleStorage
         * @constructor
         */

        $scope.isVisible = true;
        $scope.content = null;

        $scope.hide = function() {

            $scope.content = null;
            $scope.isVisible = false;
        };

        $scope.$root.$on('hide-modal', function($event) {
            $scope.hide();
        });
        $scope.$root.$on('show-loading-modal', function($event, content) {
            // Clear out any existing modal.
            $scope.hide();
            $scope.content = content;
            $scope.isVisible = true;
        });
        $scope.$root.$on('show-modal', function($event, content) {
            // Clear out any existing modal.
            $scope.hide();
            $scope.content = content;
            $scope.isVisible = true;
        });
        $scope.$root.$on('show-modal-download', function($event) {

            $scope.content.dfxpString = $scope.workingSubtitles.subtitleList.toXMLString();
        });
        $scope.$root.$on('change-modal-heading', function($event, heading) {
            if ($scope.content) {
                $scope.content.heading = heading;
                $scope.isVisible = true;
            }
        });
    });
}).call(this);
