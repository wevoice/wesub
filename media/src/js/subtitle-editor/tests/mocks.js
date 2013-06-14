(function() {

    var module = angular.module('amara.SubtitleEditor.mocks', []);

    module.factory('VideoPlayer', function() {
        return jasmine.createSpyObj('VideoPlayer', [
            'init',
            'play',
            'pause',
            'seek',
            'togglePlay',
            'currentTime',
            'duration',
            'isPlaying',
            'getVolume',
            'setVolume',
            'playChunk',
        ]);
    });

    module.factory('MockEvents', function() {
        function makeEvent(type) {
            return {
                type: type,
                preventDefault: jasmine.createSpy(),
                stopPropagation: jasmine.createSpy(),
            }
        }
        return {
            keydown: function(keyCode) {
                var evt = makeEvent('keydown');
                evt.keyCode = keyCode;
                evt.shiftKey = false;
                evt.ctrlKey = false;
                evt.altKey = false;
                evt.target = { type: 'div' };
                return evt;
            },
            click: function() {
                return makeEvent('click');
            },
        }
    });

    module.value('EditorData', {
        "canSync": true,
        "canAddAndRemove": true,
        "languageCode": "en",
        "editingVersion": {
            "languageCode": "en",
            "versionNumber": null,
        },
        "video": {
            "id": "4oqOXzpPk5rU",
            "videoURLs": [
                "http://vimeo.com/25082970"
            ],
            "primaryVideoURL": "http://vimeo.com/25082970"
        },
        "languages": [
            {
                "is_rtl": false,
                "numVersions": 0,
                "editingLanguage": true,
                "language_code": "en",
                "pk": 23,
                "versions": [],
                "is_primary_audio_language": true,
                "name": "English"
            },
        ],
    });
}).call(this);
