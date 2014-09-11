describe('The Notes Controller', function() {
    var EditorData;
    var SubtitleStorage;
    var $scope;
    var $timeout;

    beforeEach(function() {
        module('amara.SubtitleEditor.mocks');
        module('amara.SubtitleEditor.notes');
    });

    beforeEach(inject(function($rootScope, $injector, $controller) {
        $scope = $rootScope.$new();
        $scope.scrollToBottom = jasmine.createSpy('scrollToBottom');
        $scope.fadeInLastNote = jasmine.createSpy('fadeInLastNote');

        $timeout = $injector.get('$timeout');
        EditorData = $injector.get('EditorData');
        EditorData.notes = [
            {
                user: 'ben',
                created: '3pm',
                body: 'note content'
            }
        ];
        EditorData.notesHeading = 'Note heading';
        SubtitleStorage = $injector.get('SubtitleStorage');

        $controller('NotesController', {
            $scope: $scope,
        });
    }));

    it('gets the heading from EditorData', function() {
        expect($scope.heading).toEqual(EditorData.notesHeading);
    });

    it('gets the notes from EditorData', function() {
        expect($scope.notes).toEqual(EditorData.notes);
    });

    it('posts notes to the API', function() {
        $scope.newNoteText = 'new note';
        $scope.postNote();
        expect(SubtitleStorage.postNote).toHaveBeenCalledWith('new note');
    });

    it('adds new notes to the list', function() {
        $scope.newNoteText = 'new note';
        $scope.postNote();
        expect($scope.notes.length).toEqual(2);
        // the note should be added to the end of the list
        expect($scope.notes[1].body).toEqual('new note');
        expect($scope.notes[1].user).toEqual(EditorData.username);
        expect($scope.notes[1].created).toEqual('Just now');
    });

    it('clears the note text after adding a new', function() {
        $scope.newNoteText = 'new note';
        $scope.postNote();
        expect($scope.newNoteText).toEqual("");
    });

    it('scrolls to the bottom on startup', function() {
        $timeout.flush();
        expect($scope.scrollToBottom).toHaveBeenCalled();
    });

    it('scrolls to the bottom after posting a new', function() {
        $scope.scrollToBottom.reset();
        $scope.newNoteText = 'new note';
        $scope.postNote();
        $timeout.flush();
        expect($scope.scrollToBottom).toHaveBeenCalled();
    });

    it('fades new notes in', function() {
        $scope.newNoteText = 'new note';
        $scope.postNote();
        $timeout.flush();
        expect($scope.fadeInLastNote).toHaveBeenCalled();
    });
});


