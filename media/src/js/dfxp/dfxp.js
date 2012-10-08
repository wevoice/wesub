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
        this.$o = $(xml.documentElement).clone();

        // Store the working XML for local edits.
        this.$w = $(xml.documentElement).clone();

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

    this.changesMade = function() {
        /*
         * Check to see if any changes have been made to the working XML.
         * Returns: true || false
         */

        var oString = that.utils.xmlToString(that.$o.get(0));
        var wString = that.utils.xmlToString(that.$w.get(0));

        return oString != wString;
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
