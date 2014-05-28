describe('The SessionBackend', function() {
    var $rootScope;
    var $scope;
    var subtitleList;
    var EditorData;
    var SubtitleStorage = SubtitleStorage;
    var initialVersion = 1;

    beforeEach(function() {
        module('amara.SubtitleEditor.mocks');
        module('amara.SubtitleEditor.subtitles.models');
        module('amara.SubtitleEditor.session');
    });

    beforeEach(inject(function($controller, $injector) {
        EditorData = $injector.get('EditorData');
        SubtitleStorage = $injector.get('SubtitleStorage');
        subtitleList = new ($injector.get('SubtitleList'))();
        subtitleList.loadEmptySubs('en');
        $rootScope = $injector.get('$rootScope');
        $scope = $rootScope.$new();
        $scope.workingSubtitles = {
            language: {
                code: EditorData.languageCode,
            },
            versionNumber: initialVersion,
            subtitleList: subtitleList,
            title: 'test title',
            description: 'test description',
            metadata: {}
        };
        $scope.collab = {
            notes: 'test notes'
        };
        $controller('SessionBackend', { $scope: $scope, });
    }));

    function saveSubtitlesResponse(versionNumber) {
        // Mock up the response from saveSubtitles.  Of course the actual
        // response has much more data, but this is all the we care about.
        return {
            data: {
                version_number: versionNumber
            }
        };

    }

    it('saves subtitles', function() {
        var callback = jasmine.createSpy();
        $scope.sessionBackend.saveSubtitles(true).then(callback);
        expect(SubtitleStorage.saveSubtitles).toHaveBeenCalledWith(
            EditorData.video.id,
            $scope.workingSubtitles.language.code,
            $scope.workingSubtitles.subtitleList.toXMLString(),
            $scope.workingSubtitles.title,
            $scope.workingSubtitles.description,
            $scope.workingSubtitles.metadata,
            true);
        // Once the SubtitleStorage.saveSubtitles completes, then we should
        // update the version number and the promise returned by
        // sessionBackend.saveSubtitles() should also complete
        expect(callback).not.toHaveBeenCalled();
        SubtitleStorage.deferreds.saveSubtitles.resolve(
            saveSubtitlesResponse(initialVersion+1));
        $rootScope.$digest();
        expect($scope.workingSubtitles.versionNumber).toEqual(initialVersion+1);
        expect(callback).toHaveBeenCalled();
    });

    it('saves notes', function() {
        var callback = jasmine.createSpy();
        $scope.sessionBackend.saveNotes().then(callback);
        expect(SubtitleStorage.updateTaskNotes).toHaveBeenCalledWith(
            $scope.collab.notes);
        // Once updateTaskNotes() completes, saveNotes() should complete
        expect(callback).not.toHaveBeenCalled();
        SubtitleStorage.deferreds.updateTaskNotes.resolve(true);
        $rootScope.$digest();
        expect(callback).toHaveBeenCalled();
    });

    it('approves tasks', function() {
        var callback = jasmine.createSpy();
        $scope.sessionBackend.approveTask().then(callback);
        expect(SubtitleStorage.approveTask).toHaveBeenCalledWith(
            initialVersion, $scope.collab.notes);
        // Once SubtitleStorage.approveTask() completes,
        // sessionBackend.approveTask() should complete
        expect(callback).not.toHaveBeenCalled();
        SubtitleStorage.deferreds.approveTask.resolve(true);
        $rootScope.$digest();
        expect(callback).toHaveBeenCalled();
    });

    it('sends tasks back', function() {
        var callback = jasmine.createSpy();
        $scope.sessionBackend.sendBackTask().then(callback);
        expect(SubtitleStorage.sendBackTask).toHaveBeenCalledWith(
            initialVersion, $scope.collab.notes);
        // Once SubtitleStorage.sendBackTask() completes,
        // sessionBackend.sendBackTask() should complete
        expect(callback).not.toHaveBeenCalled();
        SubtitleStorage.deferreds.sendBackTask.resolve(true);
        $rootScope.$digest();
        expect(callback).toHaveBeenCalled();
    });

    it('sends tasks the update version number', function() {
        // This is just checking a particular case that may be tricky.  If we
        // save subtitles and approve a task, we should send the new version
        // number to SubtitleStorage.approveTask
        $scope.sessionBackend.saveSubtitles(true)
            .then($scope.sessionBackend.approveTask);
        SubtitleStorage.deferreds.saveSubtitles.resolve(
            saveSubtitlesResponse(initialVersion+1));
        $rootScope.$digest();
        expect(SubtitleStorage.approveTask).toHaveBeenCalledWith(
            initialVersion+1, $scope.collab.notes);
    });
});


describe('The SessionController', function() {
    var $sce;
    var $scope;
    var $rootScope;
    var $window;
    var EditorData;
    var session;
    var backendMethodsCalled;
    var simulateSaveError;
    var markAsCompleteArg = null;

    beforeEach(function() {
        module('amara.SubtitleEditor.mocks');
        module('amara.SubtitleEditor.subtitles.models');
        module('amara.SubtitleEditor.session');
    });

    beforeEach(inject(function($controller, $injector) {
        $sce = $injector.get('$sce');
        $rootScope = $injector.get('$rootScope');
        EditorData = $injector.get('EditorData');
        $scope = $rootScope.$new();
        $scope.overrides = {
            forceSaveError: false
        };
        $scope.dialogManager = jasmine.createSpyObj('dialogManager', [
            'open', 'close', 'openDialog', 'showFreezeBox', 'closeFreezeBox'
        ]);
        $window = { location: null };
        $controller('SessionController', {
            $scope: $scope,
            $window: $window,
        });
        session = $scope.session;
    }));

    beforeEach(inject(function($q) {
        backendMethodsCalled = [];
        simulateSaveError = false;
        var backendMethods = [ 'saveSubtitles', 'saveNotes', 'approveTask',
            'sendBackTask'
        ];
        $scope.sessionBackend = {};
        _.each(backendMethods, function(methodName) {
            var spy = jasmine.createSpy().andCallFake(function(arg) {
                if(methodName == 'saveSubtitles') {
                    markAsCompleteArg = arg;
                }
                backendMethodsCalled.push(methodName);
                var deferred = $q.defer();
                if(simulateSaveError) {
                    deferred.reject("error");
                } else {
                    deferred.resolve(true);
                }
                return deferred.promise;
            });
            $scope.sessionBackend[methodName] = spy;
        });
    }));

    beforeEach(function() {
        this.addMatchers({
            'toHaveBeenCalledWithTrusted': function(string) {
                if(this.actual.callCount == 0) {
                    this.message = function() {
                        return 'method not called';
                    }
                    return false;
                }
                var arg = this.actual.mostRecentCall.args[0];
                this.message = function() {
                    return string + " != " + $sce.getTrustedHtml(arg);
                }
                return string == $sce.getTrustedHtml(arg);
            },
        });
    });

    function expectRedirectToVideoPage() {
        var videoPagePath = '/videos/' + EditorData.video.id + '/';
        expect($window.location).toEqual(videoPagePath);
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Exiting&hellip;');
    }

    function expectRedirectToLegacyEditor() {
        expect($window.location).toEqual(EditorData.oldEditorURL);
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Exiting&hellip;');
    }

    function expectNoRedirect() {
        expect($window.location).toEqual(null);
        expect($scope.dialogManager.showFreezeBox).not.toHaveBeenCalled();
    }

    it('handles exiting', function() {
        session.exit();
        expectRedirectToVideoPage();
    });

    it('shows the unsaved changes dialog', function() {
        session.subtitlesChanged();
        session.exit();
        expectNoRedirect();
        expect($scope.dialogManager.openDialog).toHaveBeenCalledWith(
            'unsavedWork', jasmine.any(Object));
    });

    it('shows the unsaved changes dialog for note changes', function() {
        session.notesChanged();
        session.exit();
        expectNoRedirect();
        expect($scope.dialogManager.openDialog).toHaveBeenCalledWith(
            'unsavedWork', jasmine.any(Object));
    });


    it('skips the unsaved changes dialog if resetChanges() is called', function() {
        for(var i=0; i < 10; i ++) {
            session.subtitlesChanged();
            session.notesChanged();
        }
        session.resetChanges();
        session.exit();
        expectRedirectToVideoPage();
    });

    it('handles the exit button on the unsaved work dialog', function() {
        session.subtitlesChanged();
        session.exit();
        var callbacks = $scope.dialogManager.openDialog.mostRecentCall.args[1];
        callbacks.exit();
        expectRedirectToVideoPage();
    });

    it('handles exiting to the legacy editor', function() {
        session.exitToLegacyEditor();
        expectRedirectToLegacyEditor();
    });

    it('shows the unsaved changes dialog when exiting to the legacy editor', function() {
        session.subtitlesChanged();
        session.exitToLegacyEditor();
        expectNoRedirect();
        expect($scope.dialogManager.openDialog).toHaveBeenCalledWith(
            'legacyEditorUnsavedWork', jasmine.any(Object));
    });

    it('handles the exit button on the legacy editor unsaved work dialog', function() {
        session.subtitlesChanged();
        session.exitToLegacyEditor();
        var callbacks = $scope.dialogManager.openDialog.mostRecentCall.args[1];
        callbacks.discardChangesAndOpenLegacyEditor();
        expectRedirectToLegacyEditor();
    });

    it('handles saving subtitles', function() {
        session.subtitlesChanged();
        session.save();
        // While the save is in-progress we should show a freeze box
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Saving&hellip;');
        // After the save is complete, we should close the freezebox and show
        // the subtitles saved dialog
        $rootScope.$digest();
        expect(backendMethodsCalled).toEqual(['saveSubtitles']);
        expect(markAsCompleteArg).toBe(undefined);
        expect($scope.dialogManager.closeFreezeBox).toHaveBeenCalled();
        expect($scope.dialogManager.openDialog).toHaveBeenCalledWith(
            'changesSaved', jasmine.any(Object));
    });

    it('handles saving notes', function() {
        session.notesChanged();
        session.save();
        // While the save is in-progress we should show a freeze box
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Saving&hellip;');
        // After the save is complete, we should close the freezebox and show
        // the subtitles saved dialog
        $rootScope.$digest();
        expect(backendMethodsCalled).toEqual(['saveNotes']);
        expect($scope.dialogManager.closeFreezeBox).toHaveBeenCalled();
        expect($scope.dialogManager.openDialog).toHaveBeenCalledWith(
            'changesSaved', jasmine.any(Object));
    });

    it('handles saving subtitles and notes', function() {
        session.subtitlesChanged();
        session.notesChanged();
        session.save();
        // While the save is in-progress we should show a freeze box
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Saving&hellip;');
        // After the save is complete, we should close the freezebox and show
        // the subtitles saved dialog
        $rootScope.$digest();
        expect(backendMethodsCalled).toEqual(['saveSubtitles', 'saveNotes']);
        expect($scope.dialogManager.closeFreezeBox).toHaveBeenCalled();
        expect($scope.dialogManager.openDialog).toHaveBeenCalledWith(
            'changesSaved', jasmine.any(Object));
    });

    it('handles the exit button after saving subtitles', function() {
        session.subtitlesChanged();
        session.save();
        $rootScope.$digest();
        var callbacks = $scope.dialogManager.openDialog.mostRecentCall.args[1];
        callbacks.exit();
        expectRedirectToVideoPage();
    });

    it('handles errors while saving subtitles', function() {
        simulateSaveError = true;
        session.subtitlesChanged();
        session.save();
        $rootScope.$digest();
        expect($scope.dialogManager.closeFreezeBox).toHaveBeenCalled();
        expect($scope.dialogManager.open).toHaveBeenCalledWith('save-error');
    });

    it('calculates if there unsaved changes', function() {
        expect(session.unsavedChanges()).toBeFalsy();
        session.subtitlesChanged();
        expect(session.unsavedChanges()).toBeTruthy();
        session.resetChanges();
        expect(session.unsavedChanges()).toBeFalsy();
        session.notesChanged();
        expect(session.unsavedChanges()).toBeTruthy();
        session.subtitlesChanged();
        expect(session.unsavedChanges()).toBeTruthy();
        session.save();
        $rootScope.$digest();
        expect(session.unsavedChanges()).toBeFalsy();
    });

    it('handles endorsing subtitles', function() {
        session.subtitlesChanged();
        session.endorse();
        $rootScope.$digest();
        expect(backendMethodsCalled).toEqual(['saveSubtitles']);
        expect(markAsCompleteArg).toBe(true);
        // when endorse is clicked, we should exit the editor
        expectRedirectToVideoPage();
    });

    it('handles endorsing tasks', function() {
        EditorData.task_id = 123;
        session.subtitlesChanged();
        session.notesChanged();
        session.endorse();
        $rootScope.$digest();
        // Note: even though the notes have changed, we shouldn't call
        // updateTaskNotes().  approveTask will handle that.
        expect(backendMethodsCalled).toEqual(['saveSubtitles', 'approveTask']);
        expect(markAsCompleteArg).toBe(true);
        // when endorse is clicked, we should exit the editor
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Exiting&hellip;');
        expectRedirectToVideoPage();
    });

    it('handles endorsing tasks with no subtitle changes', function() {
        EditorData.task_id = 123;
        session.notesChanged();
        session.endorse();
        $rootScope.$digest();
        // Even though no changes have been made, we should still call
        // saveSubtitles, because we want to mark them as complete
        expect(backendMethodsCalled).toEqual(['saveSubtitles', 'approveTask']);
        expect(markAsCompleteArg).toBe(true);
        // when endorse is clicked, we should exit the editor
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Exiting&hellip;');
        expectRedirectToVideoPage();
    });

    it('can approve tasks', function() {
        EditorData.task_id = 123;
        session.notesChanged();
        session.approveTask();
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Accepting subtitles&hellip;');
        $rootScope.$digest();
        expect(backendMethodsCalled).toEqual(['approveTask']);
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Exiting&hellip;');
        expectRedirectToVideoPage();
    });

    it('can approve tasks with changes made', function() {
        EditorData.task_id = 123;
        session.subtitlesChanged();
        session.notesChanged();
        session.approveTask();
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Accepting subtitles&hellip;');
        $rootScope.$digest();
        expect(backendMethodsCalled).toEqual(['saveSubtitles', 'approveTask']);
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Exiting&hellip;');
        expectRedirectToVideoPage();
    });

    it('can reject tasks', function() {
        EditorData.task_id = 123;
        session.notesChanged();
        session.rejectTask();
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Sending subtitles back&hellip;');
        $rootScope.$digest();
        expect(backendMethodsCalled).toEqual(['sendBackTask']);
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Exiting&hellip;');
        expectRedirectToVideoPage();
    });

    it('can reject tasks with changes made', function() {
        EditorData.task_id = 123;
        session.subtitlesChanged();
        session.notesChanged();
        session.rejectTask();
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Sending subtitles back&hellip;');
        $rootScope.$digest();
        expect(backendMethodsCalled).toEqual(['saveSubtitles', 'sendBackTask']);
        expect($scope.dialogManager.showFreezeBox).toHaveBeenCalledWithTrusted('Exiting&hellip;');
        expectRedirectToVideoPage();
    });

    it('prevents closing the window with unsaved changes', function() {
        // No changes yet
        expect($window.onbeforeunload()).toBe(null);
        session.subtitlesChanged();
        expect($window.onbeforeunload()).toBeTruthy();
        session.save()
        $rootScope.$digest();
        expect($window.onbeforeunload()).toBe(null);
    });
});
