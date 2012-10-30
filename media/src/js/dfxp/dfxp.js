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

    this.addSubtitle = function(after, newAttrs) {
        /*
         * For adding a new subtitle to this set.
         *
         * If `after` is provided, we'll place the new subtitle directly
         * after that one. Otherwise, we'll place the new subtitle at the
         * end.
         *
         * `newAttrs` is an optional JSON object specifying the attributes to
         * be applied to the new element.
         *
         * Returns: new subtitle element
         */

        if (!after) {
            after = this.getLastSubtitle();
        }

        // Create the new element and any specified attributes.
        var newSubtitle = $('<p begin="" end=""></p>').attr(newAttrs || {});

        // Finally, place the new subtitle.
        $(after).after(newSubtitle);

        return newSubtitle.get(0);
    };
    this.changesMade = function() {
        /*
         * Check to see if any changes have been made to the working XML.
         *
         * Returns: true || false
         */

        var originalString = that.utils.xmlToString(that.$originalXml.get(0));
        var xmlString = that.utils.xmlToString(that.$xml.get(0));

        return originalString != xmlString;
    };
    this.removeSubtitle = function(index) {
        /*
         * Given the zero-index of the subtitle to be removed,
         * remove it from the node tree.
         *
         * Returns: true || false
         */

        // If an index is not provided, throw an error.
        if (!index) {
            throw new Error('DFXP: You must supply an index to removeSubtitle()');
        }

        var subtitle = this.getSubtitles().get(index);

        if (subtitle) {
            $(subtitle).remove();
            return true;
        } else {
            throw new Error('DFXP: No subtitle exists with that index.');
        }
    };
    this.getLastSubtitle = function() {
        /*
         * Retrieve the last subtitle in this set.
         *
         * Returns: last subtitle element
         */

        // Cache the selection.
        var $subtitles = this.getSubtitles();

        return $subtitles[$subtitles.length - 1];
    };
    this.getSubtitles = function() {
        /*
         * Retrieve the current set of subtitles.
         *
         * Returns: jQuery selection of nodes.
         */

        return $('div > p', this.$xml);
    };
    this.needsSyncing = function(index) {
        /*
         * Given the zero-index of the subtitle to be checked,
         * determine whether the subtitle needs to be synced.
         *
         * In most cases, if a subtitle has either no start time,
         * or no end time, it needs to be synced. However, if the
         * subtitle is the last in the list, the end time may be
         * omitted.
         *
         * Returns: true || false
         */

        // If an index is not provided, throw an error.
        if (!index) {
            throw new Error('DFXP: You must supply an index to needsSyncing()');
        }

        var subtitle = this.getSubtitles().get(index);

        if (subtitle) {

            var $subtitle = $(subtitle);

            var startTime = $subtitle.attr('begin');
            var endTime = $subtitle.attr('end');

            // If start time is empty, it always needs to be synced.
            if (startTime === '') {
                return true;
            }

            // If the end time is empty and this is not the last subtitle,
            // it needs to be synced.
            if (endTime === '' && (subtitle !== this.getLastSubtitle())) {
                return true;
            }

            // Otherwise, we're good.
            return false;

        } else {
            throw new Error('DFXP: No subtitle exists with that index.');
        }
    };
    this.needsAnySynced = function() {
        /*
         * Determine whether any of the subtitles in the set need
         * to be synced.
         *
         * Returns: true || false
         */
    };
    this.setEndTime = function(index, endTime) {
        /*
         * Given the zero-index of the subtitle to be updated,
         * set the end time.
         *
         * Returns: true
         */

        var subtitle = this.getSubtitles().get(index);

        if (subtitle) {
            $(subtitle).attr('end', endTime);
            return true;
        } else {
            throw new Error('DFXP: No subtitle exists with that index.');
        }
    };
    this.setStartTime = function(index, startTime) {
        /*
         * Given the zero-index of the subtitle to be updated,
         * set the start time.
         *
         * Returns: true
         */

        var subtitle = this.getSubtitles().get(index);

        if (subtitle) {
            $(subtitle).attr('begin', startTime);
            return true;
        } else {
            throw new Error('DFXP: No subtitle exists with that index.');
        }
    };
    this.subtitlesCount = function() {
        /*
         * Retrieve the current number of subtitles.
         *
         * Returns: integer
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
