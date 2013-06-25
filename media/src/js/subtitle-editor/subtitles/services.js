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

    var API_BASE_PATH_TEAMS = '/api2/partners/teams/';
    var API_BASE_PATH_VIDEOS = '/api2/partners/videos/';

    var module = angular.module('amara.SubtitleEditor.subtitles.services', []);

    var getSubtitleFetchAPIUrl = function(videoId, languageCode, versionNumber) {
        var url = API_BASE_PATH_VIDEOS + videoId +
            '/languages/' + languageCode + '/subtitles/?format=dfxp';

        if (versionNumber) {
            url = url + '&version=' + versionNumber;
        }
        return url;
    };
    var getSubtitleSaveAPIUrl = function(videoId, languageCode) {
        var url = API_BASE_PATH_VIDEOS + videoId +
            '/languages/' + languageCode + '/subtitles/';
        return url;
    };
    var getTaskSaveAPIUrl = function(teamSlug, taskID) {
        return API_BASE_PATH_TEAMS + teamSlug + '/tasks/' + taskID + '/';
    };
    var getVideoLangAPIUrl = function(videoId) {
        return API_BASE_PATH_VIDEOS + videoId + '/languages/';
    };

    /*
     * Language object that we return from getLanguage()
     */
    function Language(responseData) {
        /*
         * Create a new Language object
         *
         * responseData is either:
         *   - data that we got back from the API
         *   - or data from the editor_data variable
         *
         * This means that editor_data should be formated exactly as the
         * response data is.
         */
        this.responseData = responseData;
        this.name = responseData.name;
        this.code = responseData.language_code;
        if(responseData.is_rtl) {
            this.dir = 'rtl';
        } else {
            this.dir = 'ltr';
        }
        this.isPrimaryAudioLanguage = responseData.is_original;
    }

    module.factory('SubtitleStorage', function($window, $http) {

        var cachedData = $window.editorData;
        var authHeaders = cachedData.authHeaders;

        function ensureLanguageMap() {
            if (cachedData.languageMap) {
                return;
            }
            var langMap = {};
            for (var i=0; i < cachedData.languages.length; i++){
                var language = cachedData.languages[i];
                langMap[language.language_code] = language;
            }
            cachedData.languageMap = langMap;
        }

        return {
            approveTask: function(versionNumber, notes) {

                var url = getTaskSaveAPIUrl(cachedData.team_slug, cachedData.task_id);

                var promise = $http({
                    method: 'PUT',
                    url: url,
                    headers: authHeaders,
                    data:  {
                        complete: true,
                        body: notes,
                        version_number: versionNumber,
                    }
                });

                return promise;

            },
            getCachedData: function() {
                return cachedData;
            },
            getLanguages: function(callback) {

                // If there are no languages in our cached data, ask the API.
                if (cachedData.languages && cachedData.languages.length === 0) {

                    var url = getVideoLangAPIUrl(cachedData.video.id);

                    $http.get(url).success(function(response) {
                        cachedData.languages = response.objects;
                        callback(response.objects);
                    });

                // If we have cached languages, just call the callback.
                } else {
                    callback(cachedData.languages);
                }
            },
            getLanguage: function(languageCode) {
                ensureLanguageMap();
                return new Language(cachedData.languageMap[languageCode]);
            },
            getLanguageName: function(languageCode) {
                ensureLanguageMap();
                return cachedData.languageMap[languageCode].name;
            },
            getLanguageIsRTL: function(languageCode) {
                ensureLanguageMap();
                return cachedData.languageMap[languageCode].is_rtl;
            },
            getSubtitles: function(languageCode, versionNumber, callback){

                // You must supply a language code in order to get subtitles.
                if (!languageCode) {
                    throw Error('You must supply a language code to getSubtitles().');
                }

                var subtitleData;

                // Loop through all of our cached languages to find the correct subtitle version.
                for (var i=0; i < cachedData.languages.length; i++){

                    var language = cachedData.languages[i];

                    // Once we find the language we're looking for, find the version.
                    if (language.language_code === languageCode){

                        for (var j = 0; j < language.versions.length; j++){

                            // We've found the version.
                            if (language.versions[j].version_no === parseInt(versionNumber, 10)){

                                subtitleData = language.versions[j];
                                if (subtitleData.subtitlesXML) {
                                    break;
                                }

                            }
                        }

                        break;
                    }
                }

                // If we found subtitles, call the callback with them.
                if (subtitleData.subtitlesXML !== undefined){
                   callback(subtitleData);

                // Otherwise, ask the API for this version.
                } else {

                    var url = getSubtitleFetchAPIUrl(cachedData.video.id, languageCode, versionNumber);

                    $http.get(url).success(function(response) {

                        // Cache these subtitles on the cached data object.
                        subtitleData.subtitlesXML = response;
                        callback(subtitleData);

                    });
                }
            },
            getPrimaryVideoURL: function() {
                return cachedData.video.primaryVideoURL;
            },
            getVideoURLs: function() {
                return cachedData.video.videoURLs;
            },
            sendBackTask: function(versionNumber, notes) {

                var url = getTaskSaveAPIUrl(cachedData.team_slug, cachedData.task_id);

                var promise = $http({
                    method: 'PUT',
                    url: url,
                    headers: authHeaders,
                    data:  {
                        complete: true,
                        body: notes,
                        send_back: true,
                        version_number: versionNumber,
                    }
                });

                return promise;

            },
            saveSubtitles: function(videoID, languageCode, dfxpString, title,
                                   description, isComplete) {
                var url = getSubtitleSaveAPIUrl(videoID, languageCode);
                // if isComplete is not specified as true or false, we send
                // null, which means keep the complete flag the same as before
                if(isComplete !== true && isComplete !== false) {
                    isComplete = null;
                }

                var promise = $http({
                    method: 'POST',
                    url: url,
                    headers: authHeaders,
                    data:  {
                        video: videoID,
                        language: languageCode,
                        subtitles: dfxpString,
                        sub_format: 'dfxp',
                        title: title,
                        description: description,
                        is_complete: isComplete,
                    }
                });

                return promise;
            }
        };
    });
    module.factory('EditorData', function($window) {
        /**
         * Get the editor data that was passed to us from python
         *
         */
        return $window.editorData;
    });
}).call(this);
