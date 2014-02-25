describe('The Collab Controller', function() {
    var $scope = null;
    var subtitleList = null;

    beforeEach(function() {
        module('amara.SubtitleEditor.mocks');
        module('amara.SubtitleEditor.subtitles.models');
        module('amara.SubtitleEditor.collab');
    });

    beforeEach(inject(function(SubtitleList) {
        subtitleList = new SubtitleList();
        subtitleList.loadXML(null);
        var sub = subtitleList.insertSubtitleBefore(null);
        subtitleList.updateSubtitleContent(sub, 'content');
        subtitleList.updateSubtitleTime(sub, 500, 1000);
    }));

    beforeEach(inject(function($controller, $injector) {
        $scope = $injector.get('$rootScope').$new();
        var locals = {
            $scope: $scope,
            $timeout: $injector.get('$timeout'),
            EditorData: $injector.get('EditorData')
        };
        $scope.workingSubtitles = {
            subtitleList: subtitleList
        };
        var collabController = $controller('CollabController', locals);

        this.addMatchers({
            'toAllowApproval': function() {
                var $scope = this.actual;
                var canApprove = $scope.canApprove();
                var errorMessage = $scope.errorMessage();

                if(!this.isNot) {
                    var correctCanApprove = true;
                    var correctError = null;
                } else {
                    var correctCanApprove = false;
                    var correctError = 'Not all lines are completed';
                }
                if(canApprove !== correctCanApprove) {
                    this.message = function() {
                        return 'canApprove() returned ' + canApprove + ' instead of ' + correctCanApprove;
                    }
                    return this.isNot;
                }

                if(errorMessage !== correctError) {
                    this.message = function() {
                        return '$scope.errorMessage() returned ' + errorMessage + ' instead of ' + correctError;
                    }
                    return this.isNot;
                }
                return !this.isNot;
            }
        });

    }));

    it('allows approval when subtitles are complete', function() {
        expect($scope).toAllowApproval();
        // Add a new subtitle, this should prevent approval
        var sub = subtitleList.insertSubtitleBefore(null);
        expect($scope).not.toAllowApproval();
        // Setting the content shouldn't change that
        subtitleList.updateSubtitleContent(sub, 'content');
        expect($scope).not.toAllowApproval();
        // But having the content and time set should allow approval again
        subtitleList.updateSubtitleTime(sub, 500, 1000);
        expect($scope).toAllowApproval();
    });
});


