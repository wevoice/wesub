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

var AmaraDFXPParser = function(AmaraDFXPParser) {
    /*
     * A utility for working with DFXP subs.
     */

    var that = this;
    var $ = window.jQuery.noConflict();

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

    this.addSubtitle = function(after, newAttrs, content) {
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
         * `content` is an optional string to set the initial content.
         *
         * Returns: new subtitle element
         */

        if (typeof after != 'number') {
            after = this.getLastSubtitle();
        }

        // Create the new element manually. If you create with jQuery, it'll use
        // the document's namespace as the default namespace, which is ugly.
        var newSubtitle = document.createElementNS('', 'p');

        // Init the default attrs and combine them with the defined newAttrs if
        // required.
        newAttrs = $.extend({
            'begin': '',
            'end': ''
        }, newAttrs);

        var $newSubtitle = $(newSubtitle).attr(newAttrs);

        if (typeof content !== 'undefined') {
            this.content($newSubtitle, content);
        }

        // Finally, place the new subtitle.
        //
        // If after is -1, we need to place the subtitle at the beginning.
        if (after === -1) {

            // Get the very first subtitle.
            var $firstSubtitle = this.getSubtitle(0);

            // Place this new subtitle before the first subtitle.
            $firstSubtitle.before($newSubtitle);

        // Otherwise, place it after the designated subtitle.
        } else {

            // First just make sure that the previous subtitle exists.
            var $previousSubtitle = this.getSubtitle(after);

            // Then place it.
            $previousSubtitle.after($newSubtitle);
        }

        return $newSubtitle.get(0);
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
    this.content = function(indexOrElement, content) {
        /*
         * Either get or set the HTML content for the subtitle.
         *
         * Returns: current content (string)
         */

        var $subtitle = this.getSubtitle(indexOrElement);

        if (typeof content !== 'undefined') {
            $subtitle.text(content);
        }

        // OK. So, when parsing an XML node, you can't just get the HTML content.
        // We need to retrieve the total contents of the node by using "contents()",
        // but that returns an array of objects, like ['<b>', 'hi', '</b>', '<br />'],
        // etc. So we create a temporary div, and append the array to it, and retrieve
        // the rendered HTML that way. Then remove the temporary div.
        //
        // Reference: http://bit.ly/SwbPeR
        return $('<div>').append($subtitle.contents().clone()).remove().html();

    };
    this.endTime = function(indexOrElement, endTime) {
        /*
         * Either get or set the end time for the subtitle.
         *
         * Returns: current end time (string)
         */

        var $subtitle = this.getSubtitle(indexOrElement);

        if (typeof endTime !== 'undefined') {
            if (parseFloat(endTime)) {
                $subtitle.attr('end', endTime);
            } else {
                $subtitle.attr('end', '');
            }
        }

        return $subtitle.attr('end');
    };
    this.getFirstSubtitle = function() {
        /*
         * Retrieve the first subtitle in this set.
         *
         * Returns: first subtitle element
         */

        return this.getSubtitle(0).get(0);
    };
    this.getLastSubtitle = function() {
        /*
         * Retrieve the last subtitle in this set.
         *
         * Returns: last subtitle element
         */

        // Cache the selection.
        var $subtitles = this.getSubtitles();

        return this.getSubtitle($subtitles.length - 1).get(0);
    };
    this.getSubtitle = function(indexOrElement) {
        /*
         * Returns: jQuery selection of element
         */

        // If an index or an object is not provided, throw an error.
        if (typeof indexOrElement !== 'number' && typeof indexOrElement !== 'object') {
            throw new Error('DFXP: You must supply either an index or an element.');
        }

        var subtitle;

        // If indexOrElement is a number, we'll need to query the DOM to
        // get the element.
        //
        // Note: you should only use this approach for checking one-off
        // subtitles. If you're checking more than one subtitle, it's much
        // faster to pass along pre-selected elements instead.
        if (typeof indexOrElement === 'number') {
            subtitle = this.getSubtitles().get(indexOrElement);

        // Otherwise, just use the element.
        } else {
            subtitle = indexOrElement;
        }

        if (!subtitle) {
            throw new Error('DFXP: No subtitle exists with that index.');
        }

        return $(subtitle);
    };
    this.getSubtitles = function() {
        /*
         * Retrieve the current set of subtitles.
         *
         * Returns: jQuery selection of nodes
         */

        return $('div > p', this.$xml);
    };
    this.needsAnySynced = function() {
        /*
         * Determine whether any of the subtitles in the set need
         * to be synced.
         *
         * Returns: true || false
         */

        var needsAnySynced = false;

        // Caching the current subtitle set drastically cuts down on processing
        // time for iterating through large subtitle sets.
        var $subtitles = this.getSubtitles();

        for (var i = 0; i < $subtitles.length; i++) {

            // We're going to pass the actual element instead of an integer. This
            // means needsSyncing doesn't need to hit the DOM to find the element.
            if (this.needsSyncing($subtitles.get(i))) {
                needsAnySynced = true;
            }
        }

        return needsAnySynced;
    };
    this.needsSyncing = function(indexOrElement) {
        /*
         * Given the zero-index or the element of the subtitle to be
         * checked, determine whether the subtitle needs to be synced.
         *
         * In most cases, if a subtitle has either no start time,
         * or no end time, it needs to be synced. However, if the
         * subtitle is the last in the list, the end time may be
         * omitted.
         *
         * Returns: true || false
         */

        var $subtitle = this.getSubtitle(indexOrElement);

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
    };
    this.originalXmlToString = function() {
        return this.utils.xmlToString(this.$originalXml.get(0));
    };
    this.removeSubtitle = function(indexOrElement) {
        /*
         * Given the zero-index of the subtitle to be removed,
         * remove it from the node tree.
         *
         * Returns: true
         */

        var $subtitle = this.getSubtitle(indexOrElement);

        $subtitle.remove();

        return true;
    };
    this.startTime = function(indexOrElement, startTime) {
        /*
         * Either get or set the start time for the subtitle.
         *
         * Returns: current start time (string)
         */

        var $subtitle = this.getSubtitle(indexOrElement);

        if (typeof startTime !== 'undefined') {
            if (parseFloat(startTime)) {
                $subtitle.attr('begin', startTime);
            } else {
                $subtitle.attr('begin', '');
            }
        }

        return $subtitle.attr('begin');
    };
    this.subtitlesCount = function() {
        /*
         * Retrieve the current number of subtitles.
         *
         * Returns: integer
         */

        return this.getSubtitles().length;
    };
    this.xmlToString = function() {
        return this.utils.xmlToString(this.$xml.get(0));
    };
};
