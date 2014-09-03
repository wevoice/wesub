function insertSyncedAndCompletedSubtitle(subtitleList) {
    var sub = subtitleList.insertSubtitleBefore(null);
    subtitleList.updateSubtitleContent(sub, 'content');
    subtitleList.updateSubtitleTime(sub, 500, 1000);
}

function makeWorkflow(Workflow, subtitleList) {
    var translatingSpy = jasmine.createSpy().andReturn(false);
    return new Workflow(subtitleList, translatingSpy);
}


describe('The Workflow class', function() {
    var subtitleList = null;
    var workflow = null;

    beforeEach(function() {
        module('amara.SubtitleEditor.subtitles.models');
        module('amara.SubtitleEditor.workflow');
        module('amara.SubtitleEditor.mocks');
    });

    beforeEach(inject(function(SubtitleList, Workflow) {
        subtitleList = new SubtitleList();
        subtitleList.loadEmptySubs('en');
        workflow = makeWorkflow(Workflow, subtitleList);
    }));

    it('starts in the type stage', function() {
        expect(workflow.stage).toBe('type');
    });

    it('can move to the sync stage anytime', function() {
        workflow.switchStage('sync');
        expect(workflow.stage).toBe('sync');
    });

    it('can move to the the review/title stage once subs are complete and synced', function() {
        workflow.switchStage('sync');
        expect(workflow.canMoveToNext()).toBeFalsy();
        var sub = subtitleList.insertSubtitleBefore(null);
        expect(workflow.canMoveToNext()).toBeFalsy();
        subtitleList.updateSubtitleContent(sub, 'content');
        expect(workflow.canMoveToNext()).toBeFalsy();
        subtitleList.updateSubtitleTime(sub, 500, 1000);
        expect(workflow.canMoveToNext()).toBeTruthy();

        var sub2 = subtitleList.insertSubtitleBefore(null);
        expect(workflow.canMoveToNext()).toBeFalsy();
        subtitleList.updateSubtitleTime(sub2, 1500, 2000);
        expect(workflow.canMoveToNext()).toBeFalsy();
        subtitleList.updateSubtitleContent(sub2, 'content');
        expect(workflow.canMoveToNext()).toBeTruthy();
    });

    it('can move past the title stage at any point', function() {
        workflow.switchStage('sync');
        insertSyncedAndCompletedSubtitle(subtitleList);
        workflow.translating.andReturn(true);
        workflow.switchStage('title');
        expect(workflow.canMoveToNext()).toBeTruthy();
    });

    it('can never move paste the review stage', function() {
        workflow.switchStage('sync');
        insertSyncedAndCompletedSubtitle(subtitleList);
        workflow.switchStage('review');
        expect(workflow.canMoveToNext()).toBeFalsy();
    });

    it('moves back to sync if new unsynced subs are added', function() {
        workflow.switchStage('sync');
        insertSyncedAndCompletedSubtitle(subtitleList);
        expect(workflow.canMoveToNext()).toBeTruthy();
        workflow.switchStage('review');
        expect(workflow.stage).toBe('review');

        subtitleList.insertSubtitleBefore(null);
        expect(workflow.stage).toBe('sync');
    });

    it('knows which stages are done', function() {
        expect(workflow.stageDone('type')).toBeFalsy();
        expect(workflow.stageDone('sync')).toBeFalsy();
        workflow.switchStage('sync');
        expect(workflow.stageDone('type')).toBeTruthy();
        expect(workflow.stageDone('sync')).toBeFalsy();
        insertSyncedAndCompletedSubtitle(subtitleList);
        workflow.switchStage('review');
        expect(workflow.stageDone('type')).toBeTruthy();
        expect(workflow.stageDone('sync')).toBeTruthy();
    });

    it('starts in the review stage if we already have subs',
            inject(function(Workflow) {
        var sub = subtitleList.insertSubtitleBefore(null);
        subtitleList.updateSubtitleContent(sub, 'sub text');
        subtitleList.updateSubtitleTime(sub, 100, 200);
        workflow = makeWorkflow(Workflow, subtitleList);
        expect(workflow.stage).toBe('review');
    }));
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
        $scope.workflow = makeWorkflow(Workflow, subtitleList);
        spyOn($scope, '$emit');
        $controller('WorkflowProgressionController', {
            $scope: $scope,
        });
    }));

    describe('The click handling', function() {
        it('changes the workflow stage', function() {
            var evt = {
                preventDefault: jasmine.createSpy(),
                stopPropagation: jasmine.createSpy(),
            };
            $scope.onNextClicked(evt);
            expect($scope.workflow.stage).toBe('sync')
            expect(evt.preventDefault).toHaveBeenCalled();
            expect(evt.stopPropagation).toHaveBeenCalled();
            insertSyncedAndCompletedSubtitle(subtitleList);
            $scope.onNextClicked(evt);
            expect($scope.workflow.stage).toBe('review')
        });

        it('shows the timeline for the sync step', inject(function(MockEvents) {
            expect($scope.toggleTimelineShown.callCount).toBe(0);
            $scope.onNextClicked(MockEvents.click());
            expect($scope.workflow.stage).toBe('sync')
            expect($scope.toggleTimelineShown.callCount).toBe(1);
        }));

        it('restarts video playback when switching steps', inject(function(MockEvents, VideoPlayer) {
            $scope.onNextClicked(MockEvents.click());
            expect(VideoPlayer.pause).toHaveBeenCalled();
            expect(VideoPlayer.seek).toHaveBeenCalledWith(0);
        }));
    });
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
