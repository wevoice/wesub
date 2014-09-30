describe('The SubtitleStorage service', function() {
    var $httpBackend;
    var $rootScope;
    var videoId;
    var languageCode;
    var SubtitleStorage;
    var subtitlesURL;
    var actionsURL;
    var notesURL;


    beforeEach(function() {
        module('amara.SubtitleEditor.mocks');
        module('amara.SubtitleEditor.subtitles.services');
    });

    beforeEach(inject(function ($injector, EditorData) {
        $httpBackend = $injector.get('$httpBackend');
        $rootScope = $injector.get('$rootScope');
        SubtitleStorage = $injector.get('SubtitleStorage');
        videoId = EditorData.video.id;
        languageCode = EditorData.editingVersion.languageCode;

        subtitlesURL = ('/api2/partners/videos/' + videoId + '/languages/' +
            languageCode + '/subtitles/');
        actionsURL = subtitlesURL + 'actions/';
        notesURL = subtitlesURL + 'notes/';
    }));

    afterEach(function() {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
    });

    it('saves subtitles', function() {
        SubtitleStorage.saveSubtitles('dfxp-string', 'title', 'description',
            'metadata', true, null);
        $httpBackend.expectPOST(subtitlesURL, {
            video: videoId,
            language: languageCode,
            subtitles: 'dfxp-string',
            sub_format: 'dfxp',
            title: 'title',
            description: 'description',
            from_editor: true,
            metadata: 'metadata',
            is_complete: true,
            action: null,

        }).respond('200', '');
        $rootScope.$digest();
        $httpBackend.flush();
    });

    it('saves subtitles with actions', function() {
        SubtitleStorage.saveSubtitles('dfxp-string', 'title', 'description',
            'metadata', true, 'test-action');
        $httpBackend.expectPOST(subtitlesURL, {
            video: videoId,
            language: languageCode,
            subtitles: 'dfxp-string',
            sub_format: 'dfxp',
            title: 'title',
            description: 'description',
            from_editor: true,
            metadata: 'metadata',
            is_complete: true,
            action: 'test-action',
        }).respond('200', '');
        $rootScope.$digest();
        $httpBackend.flush();
    });

    it('performs actions', function() {
        SubtitleStorage.performAction('action-name');
        $httpBackend.expectPOST(actionsURL, {
            'action': 'action-name'
        }).respond('200', '');
        $rootScope.$digest();
        $httpBackend.flush();
    });

    it('posts notes', function() {
        SubtitleStorage.postNote('note text');
        $httpBackend.expectPOST(notesURL, {
            'body': 'note text'
        }).respond('200', '');
        $rootScope.$digest();
        $httpBackend.flush();
    });
});

