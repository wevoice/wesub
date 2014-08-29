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

var angular = angular || null;

(function() {
    var module = angular.module('amara.SubtitleEditor.workflow', []);

    /*
     * App-level Workflow object
     */

    Workflow = function(subtitleList) {
        this.subtitleList = subtitleList;
        this.stageOrder = [ 'typing', 'syncing', 'review' ];
        if(this.subtitleList.isComplete()) {
            this.stage = 'review';
        } else {
            this.stage = 'typing';
        }
    }

    Workflow.prototype = {
        stageIndex: function(stage) {
            var stageIndex = this.stageOrder.indexOf(stage);
            if(stageIndex == -1) {
                throw "invalid stage: " + stage;
            }
            return stageIndex;
        },
        stageCSSClass: function(stage) {
            return this.stage == stage ? 'active' : 'inactive';
        },
        canCompleteStage: function(stage) {
            if(stage == 'typing') {
                return (this.subtitleList.length() > 0 &&
                        !this.subtitleList.needsAnyTranscribed());
            } else if(stage == 'syncing') {
                return this.subtitleList.isComplete();
            } else {
                return false;
            }
        },
        typingCheckboxChanged: function(checked) {
            if(checked) {
                this.stage = 'syncing';
            } else {
                this.stage = 'typing';
            }
        },
        syncingCheckboxChanged: function(checked) {
            if(checked) {
                this.stage = 'review';
            } else {
                this.stage = 'syncing';
            }
        },
        checkSubtitleListChanges: function() {
            if(this.stage != 'typing' && this.subtitleList.length() == 0) {
                this.stage = 'typing';
            } else if(this.stage == 'review' && !this.subtitleList.isComplete()) {
                this.stage = 'syncing';
            }
        },
    }
    module.value('Workflow', Workflow);

    module.controller('WorkflowProgressionController', ["$scope", "$sce", "EditorData", "VideoPlayer", function($scope, $sce, EditorData, VideoPlayer) {

        $scope.showOverlay = true;
        $scope.$root.$on("video-playback-changes", function() {
            $scope.showOverlay = false;
        });
        $scope.$root.$on("app-click", function() {
            $scope.showOverlay = false;
        });

        // If a blank list of subs start, we automatically start editing
        if ($scope.workflow.subtitleList.length() == 0) {
            var newSub = $scope.workflow.subtitleList.insertSubtitleBefore(null);
            $scope.currentEdit.start(newSub);
        }
        $scope.workflow.subtitleList.addChangeCallback(function() {
            $scope.workflow.checkSubtitleListChanges();
            $scope.setCheckboxesForWorkflowStage();

        });

        function rewindPlayback() {
            VideoPlayer.pause();
            VideoPlayer.seek(0);
        }

        $scope.setCheckboxesForWorkflowStage = function() {
            if($scope.workflow.stage == 'review') {
                $scope.typingChecked = $scope.syncingChecked = true;
            } else if($scope.workflow.stage == 'syncing') {
                $scope.typingChecked = true;
                $scope.syncingChecked = false;
            } else if($scope.workflow.stage == 'typing') {
                $scope.typingChecked = $scope.syncingChecked = false;
            }
        }
        $scope.setCheckboxesForWorkflowStage();

        $scope.typingCheckboxChanged = function() {
            if(!$scope.typingChecked && $scope.syncingChecked) {
                $scope.syncingChecked = false;
            }
            $scope.workflow.typingCheckboxChanged($scope.typingChecked);
        }

        $scope.syncingCheckboxChanged = function() {
            if(!$scope.typingChecked && $scope.syncingChecked) {
                $scope.typingChecked = true;
            }
            $scope.workflow.syncingCheckboxChanged($scope.syncingChecked);
        }

        $scope.$watch('workflow.stage', function(newStage) {
            if(newStage == 'syncing' && !$scope.timelineShown) {
                $scope.toggleTimelineShown();
            }
            rewindPlayback();
        });

    }]);


})(this);
