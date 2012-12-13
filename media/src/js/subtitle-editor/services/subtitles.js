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

angular.module('amara.SubtitleEditor.services.SubtitlesFetcher', []);
/**
 * We store a local cache of language data + subtitles in the following format:
 * [
 {
     "code": "en",
     "editingLanguage": true,
     "versions": [
         {
             "number": 1
         },
         {
             "number": 2
         },
         {
             "subtitlesXML": "<tt xmlns=\"http://www.w3.org/ns/ttml\" xml:lang=\"en\">\n            <head>\n                <metadata xmlns:ttm=\"http://www.w3.org/ns/ttml#metadata\">\n                    <ttm:title/>\n                    <ttm:description/>\n                    <ttm:copyright/>\n                </metadata>\n\n                <styling xmlns:tts=\"http://www.w3.org/ns/ttml#styling\">\n                    <style xml:id=\"amara-style\" tts:color=\"white\" tts:fontFamily=\"proportionalSansSerif\" tts:fontSize=\"18px\" tts:textAlign=\"center\"/>\n                </styling>\n\n                <layout xmlns:tts=\"http://www.w3.org/ns/ttml#styling\">\n                    <region xml:id=\"amara-subtitle-area\" style=\"amara-style\" tts:extent=\"560px 62px\" tts:padding=\"5px 3px\" tts:backgroundColor=\"black\" tts:displayAlign=\"after\"/>\n                </layout>\n            </head>\n            <body region=\"amara-subtitle-area\">\n                <div><p begin=\"00:00:01,308\" end=\"00:00:05,946\" new_paragraph=\"true\">We started Universal Subtitle *because* we believe</p><p begin=\"00:00:05,946\" end=\"00:00:08,646\">that every video on the **web**</p><p begin=\"00:00:08,646\" end=\"00:00:11,596\">should be subtitabe. \nMillions of deaf and hard of hearing</p><p begin=\"00:00:12,462\" end=\"00:00:13,195\">viewers require subtitles to access video. Video makers and websites should really care</p><p begin=\"00:00:13,229\" end=\"00:00:14,529\">about this stuff too.</p><p begin=\"00:00:14,966\" end=\"00:00:16,130\">Subtitles can give them access to a wider audience and they also get better search rankings.</p><p begin=\"00:00:16,331\" end=\"00:00:17,167\">Universal subtitles make it incredibly easy to add subtitles to almost any video</p><p begin=\"00:00:17,514\" end=\"00:00:18,230\">Take an existing video on the web</p><p begin=\"00:00:18,831\" end=\"00:00:20,031\">submit the URL through our website</p><p begin=\"00:00:20,530\" end=\"00:00:21,648\">And then type along with the dialog</p>\n                </div>\n            </body>\n        </tt>\n",
             "description": "Amara is the easiest way to caption and translate any video."
         },
         {
             "title": "About Amara",
             "number": 4,
             "subtitlesXML": "<tt xmlns=\"http://www.w3.org/ns/ttml\" xml:lang=\"en\">\n            <head>\n                <metadata xmlns:ttm=\"http://www.w3.org/ns/ttml#metadata\">\n                    <ttm:title/>\n                    <ttm:description/>\n                    <ttm:copyright/>\n                </metadata>\n\n                <styling xmlns:tts=\"http://www.w3.org/ns/ttml#styling\">\n                    <style xml:id=\"amara-style\" tts:color=\"white\" tts:fontFamily=\"proportionalSansSerif\" tts:fontSize=\"18px\" tts:textAlign=\"center\"/>\n                </styling>\n\n                <layout xmlns:tts=\"http://www.w3.org/ns/ttml#styling\">\n                    <region xml:id=\"amara-subtitle-area\" style=\"amara-style\" tts:extent=\"560px 62px\" tts:padding=\"5px 3px\" tts:backgroundColor=\"black\" tts:displayAlign=\"after\"/>\n                </layout>\n            </head>\n            <body region=\"amara-subtitle-area\">\n                <div><p begin=\"00:00:01,308\" end=\"00:00:05,946\" new_paragraph=\"true\">We started Universal Subtitle *because* we believe</p><p begin=\"00:00:05,946\" end=\"00:00:08,646\">that every video on the **web** and *there*.</p><p begin=\"00:00:08,646\" end=\"00:00:11,596\">should be subtitabe. \nMillions of deaf and hard of hearing</p><p begin=\"00:00:12,462\" end=\"00:00:13,195\">viewers require subtitles to access video. Video makers and websites should really care</p><p begin=\"00:00:13,229\" end=\"00:00:14,529\">about this stuff too.</p><p begin=\"00:00:14,966\" end=\"00:00:16,130\">Subtitles can give them access to a wider audience and they also get better search rankings.</p><p begin=\"00:00:16,331\" end=\"00:00:17,167\">Universal subtitles make it incredibly easy to add subtitles to almost any video</p><p begin=\"00:00:17,514\" end=\"00:00:18,230\">Take an existing video on the web</p><p begin=\"00:00:18,831\" end=\"00:00:20,031\">submit the URL through our website</p><p begin=\"00:00:20,530\" end=\"00:00:21,648\">And then type along with the dialog</p>\n                </div>\n            </body>\n        </tt>\n",
             "description": "Amara is the easiest way to caption and translate any video."
         }
     ],
     "numVersions": 4,
     "translatedFrom": {
         "version_number": 3,
         "language_code": "en"
     },
     "pk": 1,
     "name": "English"
 },
 When you request a set of subtitles the api is hit if data is not yet on the cache.
 */
angular.module('amara.SubtitleEditor.services').factory("SubtitlesFetcher", function(){
    var initialData= window.editorData;
    return {
        getSubtitles: function(languageCode, versionNumber){
            var subtitlesXML = undefined;
            // will trigger a subtitlesFetched event when ready
            for (var i=0; i < initialData.languages.length ; i++){
                var langObj = initialDatalanguages[i];
                if (langObj.code == languageCode){
                    for (var j = 0; j < langObj.versions.length; j++){
                        if (langObj.versions[j] == versionNumber){
                            subtitlesXML = langObj.versions[j].subtitlesXML;
                            break;
                        }
                    }
                    break;
                }
            }
            if (subtitlesXML !== undefined){
                // set data and trigger change
            }else{
                // fetch data
            }
            return;
        }
    };
});
