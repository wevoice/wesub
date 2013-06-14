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
(function(){
    var root, module;
    root = this;
    module = angular.module('amara.SubtitleEditor.filters.subtitles', []);
    var HIDES_ON = ['Deleted', 'Private']

    function leftPad(number, width, character) {
        /*
        * Left Pad a number to the given width, with zeros.
        * From: http://stackoverflow.com/a/1267338/22468
        *
        * Returns: string
        */

        character = character || '0';
        width -= number.toString().length;

        if (width > 0) {
            return new Array(width + (/\./.test(number) ? 2 : 1))
                                .join(character) + number;
        }
        return number.toString();
    };

    /*
    * Display a human friendly format.
     */
    function displayTime(milliseconds, showFraction) {
        if (milliseconds === -1 ||
            isNaN(Math.floor(milliseconds)) ||
            milliseconds === undefined ||
            milliseconds === null) {
                return "--";
            }
        var time = Math.floor(milliseconds / 1000);
        var hours = ~~(time / 3600);
        var minutes = ~~((time % 3600) / 60);
        var seconds = time % 60;

        var components = [];
        if(hours) {
            components.push(hours);
            components.push(leftPad(minutes, 2));
        } else {
            components.push(minutes);
        }
        components.push(leftPad(seconds, 2));
        var result = components.join(":");

        if(showFraction) {
            var fraction = Math.round((milliseconds % 1000) / 10);
            result += '.' + leftPad(fraction, 2);
        }
        return result

    };

    module.filter('displayTime', function(){
        return function(milliseconds) {
            return displayTime(milliseconds, true);
        }
    });
    module.filter('displayTimeSeconds', function(){
        return function(milliseconds) {
            return displayTime(milliseconds, false);
        }
    });
    module.filter('versionDropDownDisplay', function(){
        return function (versionData){
            var res =  'Version ' + versionData.version_no +
                        (HIDES_ON.indexOf(versionData.visibility) > -1 ?
                            " (" + versionData.visibility + ")":
                            "");
            return res;
        }
    })

}).call(this);
