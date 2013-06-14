function insertSyncedAndCompletedSubtitle(subtitleList) {
    var sub = subtitleList.insertSubtitleBefore(null);
    subtitleList.updateSubtitleContent(sub, 'content');
    subtitleList.updateSubtitleTime(sub, 500, 1000);
}

beforeEach(function() {
    module('amara.SubtitleEditor.controllers.app');
    module('amara.SubtitleEditor.mocks');
});


describe('The Workflow class', function() {
    var subtitleList = null;
    var workflow = null;

    beforeEach(inject(function(Workflow) {
        subtitleList = new dfxp.SubtitleList();
        subtitleList.loadXML(null);
        workflow = new Workflow(subtitleList);
    }));

    it('starts in the type stage', function() {
        expect(workflow.stage).toBe('type');
    });

    it('can move to the sync stage anytime', function() {
        workflow.switchStage('sync');
        expect(workflow.stage).toBe('sync');
    });

    it('can move to the the review stage once subs are complete and synced', function() {
        workflow.switchStage('sync');
        expect(workflow.canMoveToReview()).toBeFalsy();
        var sub = subtitleList.insertSubtitleBefore(null);
        expect(workflow.canMoveToReview()).toBeFalsy();
        subtitleList.updateSubtitleContent(sub, 'content');
        expect(workflow.canMoveToReview()).toBeFalsy();
        subtitleList.updateSubtitleTime(sub, 500, 1000);
        expect(workflow.canMoveToReview()).toBeTruthy();

        var sub2 = subtitleList.insertSubtitleBefore(null);
        expect(workflow.canMoveToReview()).toBeFalsy();
        subtitleList.updateSubtitleTime(sub2, 1500, 2000);
        expect(workflow.canMoveToReview()).toBeFalsy();
        subtitleList.updateSubtitleContent(sub2, 'content');
        expect(workflow.canMoveToReview()).toBeTruthy();
    });

    it('only switches to the the review stage when canMoveToReview() is true', function() {
        workflow.switchStage('sync');
        workflow.switchStage('review');
        expect(workflow.stage).toBe('sync');

        insertSyncedAndCompletedSubtitle(subtitleList);
        workflow.switchStage('review');
        expect(workflow.stage).toBe('review');
    });

    it('moves back to sync if new unsynced subs are added', function() {
        workflow.switchStage('sync');
        insertSyncedAndCompletedSubtitle(subtitleList);
        expect(workflow.canMoveToReview()).toBeTruthy();
        workflow.switchStage('review');
        expect(workflow.stage).toBe('review');

        subtitleList.insertSubtitleBefore(null);
        expect(workflow.stage).toBe('sync');
    });

    it('knows whichs stage are done', function() {
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

    it('starts in the sync stage if we already have subs',
            inject(function(Workflow) {
        subtitleList.insertSubtitleBefore(null);
        workflow = new Workflow(subtitleList);
        expect(workflow.stage).toBe('sync');
    }));
});

describe('WorkflowProgressionController', function() {
    var $scope = null;
    var subtitleList = null;

    beforeEach(inject(function ($controller, $rootScope, Workflow) {
        subtitleList = new dfxp.SubtitleList();
        $scope = $rootScope;
        $scope.timelineShown = false;
        subtitleList.loadXML(null);
        $scope.workingSubtitles = { subtitleList: subtitleList };
        $scope.workflow = new Workflow(subtitleList);
        spyOn($scope, '$emit');
        $controller('WorkflowProgressionController', {
            $scope: $scope,
        });
    }));

    describe('The endorse() method', function() {
        it('normally marks the work complete and saves', function() {
            expect($scope.$emit).not.toHaveBeenCalled();
            $scope.endorse();
            // should send the false paramater to not allow resuming after an
            // endoresment
            expect($scope.$emit).toHaveBeenCalledWith('save', false);
            // FIXME: should test that we mark the language complete
        });

        it('approves a task if we have one', inject(function(EditorData) {
            EditorData.task_id = 123

            expect($scope.$emit).not.toHaveBeenCalled();
            $scope.endorse();
            expect($scope.$emit).toHaveBeenCalledWith('approve-task');
        }));
    });

    describe('The click handling', function() {
        it('changes the workflow stage', function() {
            var evt = {
                preventDefault: jasmine.createSpy(),
            };
            $scope.onNextClicked(evt);
            expect($scope.workflow.stage).toBe('sync')
            expect(evt.preventDefault).toHaveBeenCalled();
            insertSyncedAndCompletedSubtitle(subtitleList);
            $scope.onNextClicked(evt);
            expect($scope.workflow.stage).toBe('review')
        });

        it('shows the timeline for the sync step', inject(function(MockEvents) {
            $scope.onNextClicked(MockEvents.click());
            expect($scope.workflow.stage).toBe('sync')
            expect($scope.timelineShown).toBeTruthy();
        }));

        it('restarts video playback when switching steps', inject(function(MockEvents, VideoPlayer) {
            $scope.onNextClicked(MockEvents.click());
            expect(VideoPlayer.pause).toHaveBeenCalled();
            expect(VideoPlayer.seek).toHaveBeenCalledWith(0);
        }));
    });
});

describe('up and down keys with workflows', function() {
    var subtitleList;
    var $scope;

    beforeEach(inject(function($rootScope, $controller, Workflow) {
        var VideoPlayer = {};
        $scope = $rootScope;
        subtitleList = new dfxp.SubtitleList();
        subtitleList.loadXML(null);
        $scope.workflow = new Workflow(subtitleList);
        $controller("AppControllerEvents", {
            $scope: $scope,
            VideoPlayer: VideoPlayer,
        });
        spyOn($scope, '$emit');
    }));

    it('syncs during the sync stage', inject(function(MockEvents) {
        $scope.handleAppKeyDown(MockEvents.keydown(40));
        expect($scope.$root.$emit).not.toHaveBeenCalled();
        $scope.handleAppKeyDown(MockEvents.keydown(38));
        expect($scope.$root.$emit).not.toHaveBeenCalled();

        $scope.workflow.switchStage('sync');
        $scope.handleAppKeyDown(MockEvents.keydown(40));
        expect($scope.$root.$emit).toHaveBeenCalledWith("sync-next-start-time");
        $scope.handleAppKeyDown(MockEvents.keydown(38));
        expect($scope.$root.$emit).toHaveBeenCalledWith("sync-next-end-time");
    }));
});

describe('enter key in the last text area with workflows', function() {
    var subtitleList;
    var $scope;

    beforeEach(inject(function($rootScope, Workflow, CurrentEditManager) {
        $scope = $rootScope;
        subtitleList = new dfxp.SubtitleList();
        subtitleList.loadXML(null);
        $scope.workflow = new Workflow(subtitleList);
        $scope.workingSubtitles = {
            subtitleList: subtitleList,
        }
        $scope.currentEdit = new CurrentEditManager();
        $scope.getSubtitleRepeatItem = function() {
            return null;
        }
        subtitleList.insertSubtitleBefore(null);
        // FIXME: we should mock window, but that's tricky to do.  Especially
        // since we wrap it in jquery.
        WorkingSubtitlesController($scope, window);
        spyOn(subtitleList, 'insertSubtitleBefore').andCallThrough();
    }));

    it('creates a new subtitle during the type stage',
            inject(function(MockEvents) {
        $scope.currentEdit.start(subtitleList.subtitles[0]);
        $scope.onEditKeydown(MockEvents.keydown(13));
        expect(subtitleList.insertSubtitleBefore).toHaveBeenCalled();

        $scope.workflow.switchStage('sync');
        $scope.onEditKeydown(MockEvents.keydown(13));
        expect(subtitleList.insertSubtitleBefore.callCount).toBe(1);
    }));
});
