// Amara, universalsubtitles.org
//
// Copyright (C) 2015 Participatory Culture Foundation
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

(function(){
    var module = angular.module('amara.SubtitleEditor.preferences', []);

    function getPreferencesUrl(type){
	if (type === "tutorial_shown")
            return '/en/subtitles/editor/tutorial_shown';
    }

    module.factory('PreferencesService', ["$http", "$cookies", function($http, $cookies){
        return {
            makePreferencesRequest: function(type) {
                return $http({
                    method: 'POST',
                    headers: {'X-CSRFToken': $cookies.csrftoken},
                    url: getPreferencesUrl(type)
                });
            },

            tutorialShown: function(){
                return this.makePreferencesRequest('tutorial_shown')
            }
        }
    }]);

}).call(this);
