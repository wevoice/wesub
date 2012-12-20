// Amara, universalsubtitles.org
//
// Copyright (C) 2012 Participatory Culture Foundation
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

/*
 * We store a local cache of language data + subtitles in the following format:
 * [
 *   {
 *      "code": "en",
 *      "editingLanguage": true,
 *      "versions": [
 *        {
 *          "title": "About Amara",
 *          "number": 4,
 *          "subtitlesXML": "<dfxp subs>",
 *          "description": "<some description>"
 *        }
 *      ],
 *      "numVersions": 1,
 *      "translatedFrom": {
 *        "version_number": 3,
 *        "language_code": "en"
 *      },
 *      "pk": 1,
 *      "name": "English"
 *   }
 * ]
 *
 * When you request a set of subtitles the api is hit if data is not yet on
 * the cache.
 */

(function() {

    var root, module;

    root = this;
    module = angular.module('amara.SubtitleEditor.services', []);

    module.factory("SubtitleFetcher", function($http) {
        var cachedData = window.editorData ;
        return {

            getSubtitles: function(languageCode, versionNumber, callback){
                var subtitlesXML = undefined;
                // will trigger a subtitlesFetched event when ready
                for (var i=0; i < cachedData.languages.length ; i++){
                    var langObj = cachedData.languages[i];
                    if (langObj.code == languageCode){
                        for (var j = 1; j < langObj.versions.length + 1; j++){
                            if (langObj.versions[j].number == versionNumber){
                                subtitlesXML = langObj.versions[j].subtitlesXML;
                                break;
                            }
                        }
                        break;
                    }
                }
                if (subtitlesXML !== undefined){
                   callback(subtitlesXML);
                }else{
                    // fetch data
                }
                return;
            }
        };
    });

}).call(this);
