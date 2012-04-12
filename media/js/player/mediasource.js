// Amara, universalsubtitles.org
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

/**
 * @fileoverview An interface for a media source
 *
 */

goog.provide('unisubs.player.MediaSource');

/**
 *
 * @interface
 */
unisubs.player.MediaSource = function() {};

/** 
* A global registry of media source types. See #videoSourceForUrl
*
*/
unisubs.player.MediaSource.SourceRegistry = []

/**
 * Creates a player for the page, not the widget.
 * @return {unisubs.player.AbstractVideoPlayer} 
 */
unisubs.player.MediaSource.prototype.createPlayer = function() {};
/**
 * Creates a player for the widget.
 * @return {unisubs.player.ControlledVideoPlayer}
 */
unisubs.player.MediaSource.prototype.createControlledPlayer = function() {};

/**
 * @return {string}
 */
unisubs.player.MediaSource.prototype.getVideoURL = function() {};

/**
 * @param {Array.<unisubs.player.MediaSource>} videoSources
 */
unisubs.player.MediaSource.bestHTML5VideoSource_ = function(videoSources) {
    var vt = unisubs.player.Html5VideoType;
    var preferenceOrdering = [vt.OGG, vt.WEBM, vt.H264];
    for (var i = 0; i < preferenceOrdering.length; i++) {
        if (unisubs.player.supportsVideoType(preferenceOrdering[i])) {
            var videoSource = unisubs.player.MediaSource.html5VideoSource_(
                videoSources, preferenceOrdering[i]);
            if (videoSource != null)
                return videoSource;
        }
    }
    return null;
};

/**
 *
 * @param {Array} videoSpecs This is an array in which each element is either 
 *   a string (for a url) or an object with properties "url" and "config".
 * @return {?unisubs.player.MediaSource} video source, or null if none found.
 */
unisubs.player.MediaSource.bestVideoSource = function(videoSpecs) {
    var videoSources = goog.array.map(videoSpecs, function(spec) {
        return unisubs.player.MediaSource.videoSourceForSpec_(spec);
    });
    var videoSource = null;
    if (!goog.userAgent.IE) {
        // not providing IE the opportunity to display HTML5 video yet,
        // since IE9 support appears buggy
        // (see https://unisubs.sifterapp.com/projects/12298/issues/442336/comments)
        videoSource = unisubs.player.MediaSource.bestHTML5VideoSource_(
            videoSources);
        if (videoSource != null)
            return videoSource;
    }
    // browser does not support any available html5 formats. Return a flash format.
    videoSource = goog.array.find(
        videoSources,
        function(v) { return !(v instanceof unisubs.player.Html5VideoSource); });
    if (videoSource != null)
        return videoSource;
    // if we got this far, first return mp4 for flowplayer fallback. then return anything.
    videoSource = unisubs.player.MediaSource.html5VideoSource_(
        videoSources, vt.H264);
    if (videoSource != null)
        return videoSource;
    return videoSources.length > 0 ? videoSources[0] : null;
};

unisubs.player.MediaSource.videoSourceForSpec_ = function(videoSpec) {
    if (goog.isString(videoSpec))
        return unisubs.player.MediaSource.videoSourceForURL(
            videoSpec);
    else
        return unisubs.player.MediaSource.videoSourceForURL(
            videoSpec['url'], videoSpec['config']);
};

unisubs.player.MediaSource.html5VideoSource_ = function(videoSources, videoType) {
    return goog.array.find(
        videoSources, 
        function(v) { 
            return (v instanceof unisubs.player.Html5VideoSource) && 
                v.getVideoType() == videoType; 
        });
};

/**
 * Tries to guess the video source of a given URL, if successful will return the correct mediasource
*  subclass
*/
unisubs.player.MediaSource.videoSourceForURL = function(videoURL, opt_videoConfig) {
    var mediaSource = null;
    for (var i=0; i < unisubs.player.MediaSource.SourceRegistry.length; i++){
        var source = unisubs.player.MediaSource.SourceRegistry[i](videoURL, opt_videoConfig);
        if (source){
            mediaSource = source;
            break;
        }
    }
    // The Html5VideoSource is always our last resource
    if (!mediaSource){
        mediaSource = unisubs.player.Html5VideoSource.getMediaSource (videoURL, opt_videoConfig);
    }
    if (mediaSource){
        return mediaSource;
    }
    throw new Error("Unrecognized video url " + videoURL);
};

/**
 * Adds a media source function to the global SourceRegistry
*/
unisubs.player.MediaSource.addMediaSource = function(mediaSourceFunc) {
    // no need to add this twice 
    if( goog.array.indexOf(unisubs.player.MediaSource.SourceRegistry, mediaSourceFunc) > - 1){
        return false;
    }
    unisubs.player.MediaSource.SourceRegistry.push(mediaSourceFunc);
    return true;
};
