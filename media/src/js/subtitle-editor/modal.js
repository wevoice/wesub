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
    var module = angular.module('amara.SubtitleEditor.modal', [
        'amara.SubtitleEditor.blob',
        'amara.SubtitleEditor.subtitles.services',
        ]);

    module.controller('ModalController', function($scope, Blob, SubtitleStorage) {
        /**
         * Responsible for handling the various states of the modal.
         * @param $scope
         * @param SubtitleStorage
         * @constructor
         */

        $scope.isVisible = true;
        $scope.content = null;
        $scope.showDownloadLink = false;

        function canUseBlobURL() {
            // FileSaver doesn't work correctly with Safari, so we disable
            // using blobs to create a direct download link.  See #751 for
            // more info.
            return (navigator.userAgent.indexOf('Safari') == -1 ||
                navigator.userAgent.indexOf('Chrome') > -1);
        }

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

            var data = $scope.workingSubtitles.subtitleList.toXMLString();
            if(canUseBlobURL()) {
                $scope.showDownloadLink = true;
                $scope.downloadBlob = Blob.create(data, 'application/ttaf+xml');
            } else {
                $scope.content.dfxpString = data;
            }
        });
        $scope.onDownloadClick = function($event) {
            $event.preventDefault();
            window.saveAs($scope.downloadBlob, 'SubtitleBackup.dfxp');
        }
        $scope.$root.$on('change-modal-heading', function($event, heading) {
            if ($scope.content) {
                $scope.content.heading = heading;
                $scope.isVisible = true;
            }
        });
    });
    module.controller('DebugModalController', function($scope) {
        $scope.close = function($event) {
            $scope.dialogManager.close();
            $event.stopPropagation();
            $event.preventDefault();
        }
    })

    function DialogManager() {
        this.stack = [];
    }

    DialogManager.prototype = {
        open: function(dialogName) {
            this.stack.push(dialogName);
        },
        close: function() {
            this.stack.pop();
        },
        current: function() {
            if(this.stack.length > 0) {
                return this.stack[this.stack.length - 1];
            } else {
                return null;
            }
        },
        dialogCSSClass: function(dialogName) {
            if(this.current() == dialogName) {
                return 'shown';
            } else {
                return '';
            }
        },
        overlayCSSClass: function() {
            if(this.current() !== null) {
                return 'shown';
            } else {
                return '';
            }
        }
    }

    module.value('DialogManager', DialogManager);
}).call(this);
