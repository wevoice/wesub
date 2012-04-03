// Universal Subtitles, universalsubtitles.org
// 
// Copyright (C) 2010 Participatory Culture Foundation
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

goog.provide('unisubs.player.BliptvVideoSource');

/**
 * @constructor
 * @implements {unisubs.player.MediaSource}
 * @param {string} youtubeVideoID Youtube video id
 * @param {Object.<string, *>=} opt_videoConfig Params to use for 
 *     youtube query string, plus optional 'width' and 'height' 
 *     parameters.
 */
unisubs.player.BliptvVideoSource = function() {
};
unisubs.player.BliptvVideoSource.BLIP_URL_REGEX = /^\s*https?:\/\/([^\.]+\.)*blip\.tv\/file\/get\//;

/**
* Checks if this video url is indeed for this MediaSource type, returns a
* mediaSource subclass if it is, null if it isn't
*/
unisubs.player.BliptvVideoSource.getMediaSource = function(videoURL, opt_videoConfig) {
    if(/^\s*https?:\/\/([^\.]+\.)?blip\.tv/.test(videoURL)  && 
       !blipFileGetRegex.test(videoURL)){
        return new unisubs.player.BlipTVPlaceholder(videoURL);
    }
    return null;
}

// add this mediaSource to our registry
unisubs.player.MediaSource.addMediaSource(unisubs.player.BliptvVideoSource.getMediaSource);
