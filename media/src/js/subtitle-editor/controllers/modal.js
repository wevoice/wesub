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

    var ModalController = function($scope, SubtitleStorage) {
        /**
         * Responsible for handling the various states of the modal.
         * @param $scope
         * @param SubtitleStorage
         * @constructor
         */

        $scope.loading = false;
        $scope.content = null;

        // Sample usage:
        //
        //$scope.content = {
            //'heading': null,
            //'text': null,
            //'buttons': [
                //{'text': 'No',
                 //'class': 'no',
                    //'fn': function($event) {
                        //$scope.hide($event);
                    //}
                //},
                //{'text': 'Yes, please',
                 //'class': 'yes',
                    //'fn': function($event) {
                        //$scope.hide($event);
                    //}
                //}
            //]
        //};

        $scope.hide = function($event) {
            $scope.content = null;
            $scope.loading = null;
            $event.preventDefault();
        };

        $scope.$root.$on('show-loading-modal', function($event, content) {

            // Clear out any existing modal.
            $scope.hide($event);

            $scope.loading = content;
        });
        $scope.$root.$on('show-modal', function($event, content) {

            // Clear out any existing modal.
            $scope.hide($event);

            $scope.content = content;
        });

    };

    root.ModalController = ModalController;

}).call(this);
