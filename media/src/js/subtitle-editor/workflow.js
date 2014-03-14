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

    Workflow = function(subtitleList, translating, titleEdited) {
	this.translating = translating;
	this.titleEdited = titleEdited;
	this.showOverlay = true;
        var self = this;
        this.subtitleList = subtitleList;
        if(this.subtitleList.isComplete()) {
            this.stage = 'review';
        } else {
            this.stage = 'type';
        }
        this.subtitleList.addChangeCallback(function() {
            if(self.stage == 'review' && !self.subtitleList.isComplete()) {
                self.stage = 'sync';
            }
        });
    }

    Workflow.prototype = {
	tabPressed: function(){
           if (this.showOverlay) this.showOverlay = false;
	},
        switchStage: function(newStage) {
	    if (newStage == 'title') {
                this.showOverlay = false; 
		this.titleEdited(true);
	    }
            this.showOverlay = true;
            this.stage = newStage;
        },
        canMoveToNext: function() {
            switch(this.stage) {
                case 'type':
                    return true;
                    
                case 'sync':
                    return this.subtitleList.isComplete();

                case 'title':
                    return this.titleEdited();

                case 'review':
                    return false;

                default:
                    throw "invalid value for Workflow.stage: " + this.stage;
            }
        },
        stageDone: function(stageName) {
            if(stageName == 'type') {
                return (this.stage == 'review' || this.stage == 'sync' || this.stage == 'title');
            } else if(stageName == 'sync') {
                return (this.stage == 'review' || this.stage == 'title');
            } else if(stageName == 'title') {
                return this.stage == 'review'
            } else {
                return false;
            }
        },
    }
    module.value('Workflow', Workflow);

    module.controller('WorkflowProgressionController', function($scope, EditorData, VideoPlayer) {

        // If a blank list of subs start, we autimatically start edition
        if ($scope.workflow.subtitleList.length() == 0) {
            var newSub = $scope.workflow.subtitleList.insertSubtitleBefore(null);
            $scope.currentEdit.start(newSub);
        }

        var notATask = !EditorData.task_needs_pane;

        $scope.showOverlay = function() {
            return (notATask && $scope.workflow.showOverlay);
        }

        function rewindPlayback() {
            VideoPlayer.pause();
            VideoPlayer.seek(0);
        }

        $scope.endorse = function() {
            if(EditorData.task_id === undefined || 
                    EditorData.task_id === null) {
                $scope.$root.$emit('save', {
                    allowResume: false,
                    markComplete: true,
                });
            } else {
                $scope.$root.$emit('approve-task');
            }
        }

        $scope.onNextClicked = function(evt) {
            if($scope.workflow.stage == 'type') {
                $scope.workflow.switchStage('sync');
                if(!$scope.timelineShown) {
                    $scope.toggleTimelineShown();
                }
                rewindPlayback();
            } else if ($scope.workflow.stage == 'title') {
                $scope.workflow.switchStage('review');
                rewindPlayback();
	    }
	    else if ($scope.workflow.stage == 'sync') {
		if ($scope.translating()) {
                    $scope.dialogManager.open('metadata');
                    $scope.workflow.switchStage('title');
                } else {
                    $scope.workflow.switchStage('review');
                }
                rewindPlayback();
            }
            evt.preventDefault();
        }
    });


})(this);
