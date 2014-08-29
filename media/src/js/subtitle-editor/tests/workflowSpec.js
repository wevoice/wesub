describe('The Workflow class', function() {
    var subtitleList = null;
    var workflow = null;

    beforeEach(function() {
        module('amara.SubtitleEditor.subtitles.models');
        module('amara.SubtitleEditor.workflow');
    });

    beforeEach(inject(function(SubtitleList, Workflow) {
        subtitleList = new SubtitleList();
        subtitleList.loadEmptySubs('en');
        workflow = new Workflow(subtitleList);
    }));

    it('starts in the typing stage', function() {
        expect(workflow.stage).toBe('typing');
    });

    it('starts in the review stage if we already have subs',
            inject(function(Workflow) {
        var sub = subtitleList.insertSubtitleBefore(null);
        subtitleList.updateSubtitleContent(sub, 'sub text');
        subtitleList.updateSubtitleTime(sub, 100, 200);
        workflow = new Workflow(subtitleList);
        expect(workflow.stage).toBe('review');
    }));

    it('can complete the typing stage once there is a subtitle with content', function() {
        expect(workflow.canCompleteStage('typing')).toBeFalsy();
        var sub = subtitleList.insertSubtitleBefore(null);
        expect(workflow.canCompleteStage('typing')).toBeFalsy();

        subtitleList.updateSubtitleContent(sub, 'content');
        expect(workflow.canCompleteStage('typing')).toBeTruthy();
    });

    it('can complete the syncing stage once subs are complete and synced', function() {
        expect(workflow.canCompleteStage('syncing')).toBeFalsy();

        var sub = subtitleList.insertSubtitleBefore(null);
        expect(workflow.canCompleteStage('syncing')).toBeFalsy();

        subtitleList.updateSubtitleContent(sub, 'content');
        expect(workflow.canCompleteStage('syncing')).toBeFalsy();

        subtitleList.updateSubtitleTime(sub, 500, 1000);
        expect(workflow.canCompleteStage('syncing')).toBeTruthy();
    });

    it('handles the active/inactive CSS states', function() {
        workflow.stage = 'review';
        expect(workflow.stageCSSClass('typing')).toEqual('inactive');
        expect(workflow.stageCSSClass('syncing')).toEqual('inactive');
        expect(workflow.stageCSSClass('review')).toEqual('active');
    });

    describe('checkbox handling', function() {
        // Insert a synced subtitle.  We don't want to worry about checking
        // if changing the checkboxes should be valid, the above tests handle
        // that
        beforeEach(function() {
            var sub = subtitleList.insertSubtitleBefore(null);
            subtitleList.updateSubtitleContent(sub, 'content');
            subtitleList.updateSubtitleTime(sub, 500, 1000);
        });

        it('handles typing checked', function() {
            workflow.stage = 'typing';
            workflow.typingCheckboxChanged(true);
            expect(workflow.stage).toEqual('syncing');
        });

        it('handles typing unchecked', function() {
            workflow.stage = 'syncing';
            workflow.typingCheckboxChanged(false);
            expect(workflow.stage).toEqual('typing');
        });

        it('handles typing unchecked from review stage', function() {
            workflow.stage = 'review';
            workflow.typingCheckboxChanged(false);
            expect(workflow.stage).toEqual('typing');
        });

        it('handles syncing checked', function() {
            workflow.stage = 'syncing';
            workflow.syncingCheckboxChanged(true);
            expect(workflow.stage).toEqual('review');
        });

        it('handles syncing checked from typing stage', function() {
            workflow.stage = 'typing';
            workflow.syncingCheckboxChanged(true);
            expect(workflow.stage).toEqual('review');
        });

        it('handles syncing unchecked', function() {
            workflow.stage = 'review';
            workflow.syncingCheckboxChanged(false);
            expect(workflow.stage).toEqual('syncing');
        });
    });

    it('moves back to syncing with unsynced subs', function() {
        var sub = subtitleList.insertSubtitleBefore(null);
        workflow.stage = 'review';
        // Workflow stage is review, but we have an unsynced subtitle.
        workflow.checkSubtitleListChanges();
        expect(workflow.stage).toBe('syncing');
    });

    it('moves back to typing when all subs are deleted', function() {
        workflow.stage = 'review';
        // Workflow stage is review, but no subtitles are in the list.
        workflow.checkSubtitleListChanges();
        expect(workflow.stage).toBe('typing');
    });
});

describe('WorkflowProgressionController', function() {
    var $scope = null;
    var subtitleList = null;

    beforeEach(function() {
        module('amara.SubtitleEditor.subtitles.models');
        module('amara.SubtitleEditor.workflow');
        module('amara.SubtitleEditor.mocks');
    });

    beforeEach(inject(function ($controller, $rootScope, SubtitleList, Workflow) {
        subtitleList = new SubtitleList();
        $scope = $rootScope;
        $scope.translating = function() { return false; }
        $scope.timelineShown = false;
        $scope.toggleTimelineShown = jasmine.createSpy();
        $scope.currentEdit = {
            'start': jasmine.createSpy()
        };
        $scope.dialogManager = {
            'showFreezeBox': jasmine.createSpy()
        };
        subtitleList.loadEmptySubs('en');
        $scope.workingSubtitles = { subtitleList: subtitleList };
        $scope.workflow = new Workflow(subtitleList);
        spyOn($scope, '$emit');
        $controller('WorkflowProgressionController', {
            $scope: $scope,
        });

        // Create a subtitle so we can move to the next stage
        var sub = subtitleList.insertSubtitleBefore(null);
        subtitleList.updateSubtitleTime(sub, 500, 1000);
    }));

    it('checks checkboxes when starting in review stage ', function() {
        $scope.workflow.stage = 'review';
        $scope.setCheckboxesForWorkflowStage();
        expect($scope.typingChecked).toBeTruthy();
        expect($scope.syncingChecked).toBeTruthy();
    });

    it('calls typingChecked() on changes', function() {
        spyOn($scope.workflow, 'typingCheckboxChanged');
        $scope.typingChecked = true;
        $scope.typingCheckboxChanged();
        expect($scope.workflow.typingCheckboxChanged).toHaveBeenCalled();
    });

    it('calls syncingChecked() on changes', function() {
        spyOn($scope.workflow, 'syncingCheckboxChanged');
        $scope.syncingChecked = true;
        $scope.syncingCheckboxChanged();
        expect($scope.workflow.syncingCheckboxChanged).toHaveBeenCalled();
    });

    it('checks typing when syncing is checked', function() {
        $scope.typingChecked = false;
        $scope.syncingChecked = true;
        $scope.syncingCheckboxChanged();
        expect($scope.typingChecked).toBeTruthy();
    });

    it('unchecks syncing when typing is unchecked', function() {
        $scope.typingChecked = false;
        $scope.syncingChecked = true;
        $scope.typingCheckboxChanged();
        expect($scope.syncingChecked).toBeFalsy();
    });

    it('calls checkSubtitleListChanges on changes', function() {
        spyOn($scope.workflow, 'checkSubtitleListChanges');
        subtitleList.insertSubtitleBefore(null);
        expect($scope.workflow.checkSubtitleListChanges).toHaveBeenCalled();
    });

    it('updates checkboxes on changes', function() {
        spyOn($scope.workflow, 'checkSubtitleListChanges');
        $scope.workflow.checkSubtitleListChanges.andCallFake(function() {
            $scope.workflow.stage = 'review';
        });
        subtitleList.insertSubtitleBefore(null);

        expect($scope.typingChecked).toBeTruthy();
        expect($scope.syncingChecked).toBeTruthy();
    });

    it('shows the timeline for the sync step', function() {
        expect($scope.toggleTimelineShown.callCount).toBe(0);
        $scope.$apply('workflow.stage="syncing"');
        expect($scope.toggleTimelineShown.callCount).toBe(1);
    });

    it('restarts video playback when switching steps', inject(function(VideoPlayer) {
        $scope.$apply('workflow.stage="syncing"');
        expect(VideoPlayer.pause).toHaveBeenCalled();
        expect(VideoPlayer.seek).toHaveBeenCalledWith(0);
    }));
});

describe('when up and down sync subtitles', function() {
    var $scope;

    beforeEach(function() {
        module('amara.SubtitleEditor');
        module('amara.SubtitleEditor.subtitles.models');
        module('amara.SubtitleEditor.mocks');
    });

    beforeEach(inject(function($rootScope, $controller, Workflow) {
        $scope = $rootScope;
        $scope.timelineShown = false;
        $controller("AppControllerEvents", {
            $scope: $scope,
        });
        spyOn($scope, '$emit');
    }));

    it('syncs when the timeline is shown', inject(function(MockEvents) {
        $scope.handleAppKeyDown(MockEvents.keydown(40));
        expect($scope.$root.$emit).not.toHaveBeenCalled();
        $scope.handleAppKeyDown(MockEvents.keydown(38));
        expect($scope.$root.$emit).not.toHaveBeenCalled();

        $scope.timelineShown = true;
        $scope.handleAppKeyDown(MockEvents.keydown(40));
        expect($scope.$root.$emit).toHaveBeenCalledWith("sync-next-start-time");
        $scope.handleAppKeyDown(MockEvents.keydown(38));
        expect($scope.$root.$emit).toHaveBeenCalledWith("sync-next-end-time");
    }));
});

describe('when the enter key creates a new subtitle', function() {
    var keyCodeForEnter = 13;
    var subtitleList;
    var $scope;

    beforeEach(function() {
        module('amara.SubtitleEditor.subtitles.controllers');
        module('amara.SubtitleEditor.subtitles.models');
        module('amara.SubtitleEditor.mocks');
    });

    beforeEach(inject(function($rootScope, $controller, CurrentEditManager, SubtitleList) {
        $scope = $rootScope;
        subtitleList = new SubtitleList();
        subtitleList.loadEmptySubs('en');
        $scope.workingSubtitles = {
            subtitleList: subtitleList,
        }
        $scope.timelineShown = false;
        $scope.currentEdit = new CurrentEditManager();
        $scope.getSubtitleRepeatItem = function() {
            return null;
        }
        subtitleList.insertSubtitleBefore(null);
        // FIXME: we should mock window, but that's tricky to do.  Especially
        // since we wrap it in jquery.
        $controller('WorkingSubtitlesController', {
            $scope: $scope,
        });
        spyOn(subtitleList, 'insertSubtitleBefore').andCallThrough();
    }));

    it('creates a new subtitle when the timeline is hidden',
            inject(function(MockEvents) {
        $scope.currentEdit.start(subtitleList.subtitles[0]);
        var evt = MockEvents.keydown(keyCodeForEnter);
        $scope.onEditKeydown(evt);
        expect(subtitleList.insertSubtitleBefore).toHaveBeenCalled();
        expect(evt.preventDefault).toHaveBeenCalled();

        $scope.timelineShown = true;
        $scope.onEditKeydown(MockEvents.keydown(keyCodeForEnter));
        expect(subtitleList.insertSubtitleBefore.callCount).toBe(1);
    }));
});

describe('when enter creates a new subtitle', function() {
    var keyCodeForEnter = 13;
    var $scope;
    var subtitleList;
    var MockEvents;

    beforeEach(function() {
        module('amara.SubtitleEditor');
        module('amara.SubtitleEditor.subtitles.models');
        module('amara.SubtitleEditor.mocks');
    });

    beforeEach(inject(function($rootScope, $controller, $injector,
                CurrentEditManager, SubtitleList) {
        MockEvents = $injector.get('MockEvents');
        $scope = $rootScope;
        $scope.timelineShown = false;
        $scope.currentEdit = new CurrentEditManager();
        subtitleList = new SubtitleList();
        subtitleList.loadEmptySubs('en');
        $scope.workingSubtitles = { subtitleList: subtitleList };
        $controller("AppControllerEvents", {
            $scope: $scope,
        });
        spyOn(subtitleList, 'insertSubtitleBefore').andCallThrough();
    }));

    it('creates a new subtitle', function() {
        $scope.handleAppKeyDown(MockEvents.keydown(keyCodeForEnter));
        expect(subtitleList.insertSubtitleBefore).toHaveBeenCalled();
    });

    it('calls preventDefault', function() {
        var evt = MockEvents.keydown(keyCodeForEnter);
        $scope.handleAppKeyDown(evt);
        expect(evt.preventDefault).toHaveBeenCalled();
    });

    it('starts editing the new subtitle', function() {
        $scope.handleAppKeyDown(MockEvents.keydown(keyCodeForEnter));
        expect($scope.currentEdit.draft).not.toBe(null);
    });

    it('does not creates a new subtitle if its inside a textarea', function() {
        $scope.handleAppKeyDown(MockEvents.keydown(keyCodeForEnter, {
            'target': {
                'type': 'textarea',
            },
        }));
        expect(subtitleList.insertSubtitleBefore).not.toHaveBeenCalled();
    });

    it('does not creates a new subtitle if the timeline is shown', function() {
        $scope.timelineShown = true;
        $scope.handleAppKeyDown(MockEvents.keydown(keyCodeForEnter));
        expect(subtitleList.insertSubtitleBefore).not.toHaveBeenCalled();
    });
});
