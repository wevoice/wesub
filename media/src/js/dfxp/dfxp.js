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

var DFXP = function(DFXP) {
    /*
     * A utility for working with DFXP subs.
     */

    var that = this;

    this.init = function(xml) {

        // Store the original XML for comparison later.
        this.$originalXml = $(xml.documentElement).clone();

        // Store the working XML for local edits.
        this.$xml = $(xml.documentElement).clone();

    };

    // Helper methods.
    this.utils = {

        xmlToString: function(xml) {
            /*
             * Convert an XML document to a string.
             * Accepts: document object (XML tree)
             * Returns: string
             */

            var xmlString;

            // For Internet Explorer.
            if (window.ActiveXObject) {
                xmlString = xml.xml;

            // Everyone else.
            } else {
                xmlString = (new XMLSerializer()).serializeToString(xml);
            }
            
            return xmlString;
        }

    };

    this.addSubtitle = function(after) {
        /*
         * For adding a new subtitle to this set.
         *
         * If `after` is provided, we'll place the new subtitle directly
         * after that one. Otherwise, we'll place the new subtitle at the
         * end.
         */

        var subtitles = this.getSubtitles();

        if (!after) {
            after = subtitles[subtitles.length - 1];
        }

        // We need to create the element manually first, so we can return it.
        var newSubtitle = document.createElement('p');

        // Place the new subtitle.
        $(after).after(newSubtitle);

        // Init some basic attributes that we need for subtitles.
        $(newSubtitle).attr({
            'begin': '',
            'end': ''
        });

        return newSubtitle;
    };
    this.changesMade = function() {
        /*
         * Check to see if any changes have been made to the working XML.
         * Returns: true || false
         */

        var originalString = that.utils.xmlToString(that.$originalXml.get(0));
        var xmlString = that.utils.xmlToString(that.$xml.get(0));

        return originalString != xmlString;
    };
    this.getSubtitles = function() {
        /*
         * Retrieve the current set of subtitles.
         */

        return $('div > p', this.$xml);
    };
    this.subtitlesCount = function() {
        /*
         * Retrieve the current number of subtitles.
         */

        return this.getSubtitles().length;
    };
};

$(function() {
    $.ajax({
        type: 'get',
        url: '/site_media/src/js/dfxp/sample.dfxp.xml',
        dataType: 'xml',
        success: function(resp) {
            window.unisubs = window.unisubs || [];
            window.unisubs.DFXP = DFXP;

            // Create an instance of the DFXP wrapper with this XML.
            window.x = new window.unisubs.DFXP();
            window.x.init(resp);
        }
    });
});
