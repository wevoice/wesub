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

goog.provide('unisubs.player.BliptvVideoSource');

/**
 * @constructor
 * @implements {unisubs.player.MediaSource}
 * @param {string} videoID BlipTv video id (unrelated to unisubs.player id)
 * @param {string} videoURL URL of BlipTv page
 * @param {Object.<string, *>=} opt_videoConfig Params to use for player.
 */
unisubs.player.BlipTvVideoSource = function(videoID, videoURL, opt_videoConfig) {
    this.videoID_ = videoID;
    this.videoURL_ = videoURL;
    this.uuid_ = unisubs.randomString();
    this.videoConfig_ = opt_videoConfig;
};

unisubs.player.BlipTvVideoSource.prototype.createPlayer = function() {
    return this.createPlayer_(false);
};

unisubs.player.BlipTvVideoSource.prototype.createControlledPlayer = function() {
    return new unisubs.player.ControlledVideoPlayer(this.createPlayer_(true));
};

unisubs.player.BlipTvVideoSource.prototype.createPlayer_ = function(forDialog) {
    return new unisubs.player.BlipTvVideoPlayer(
        new unisubs.player.BlipTvVideoSource(
            this.videoID_, this.videoURL_, this.videoConfig_),
        forDialog);
};

unisubs.player.BlipTvVideoSource.prototype.getVideoId = function() {
    return this.videoID_;
};

unisubs.player.BlipTvVideoSource.prototype.getUUID = function() {
    return this.uuid_;
};

unisubs.player.BlipTvVideoSource.prototype.getVideoConfig = function() {
    return this.videoConfig_;
};

unisubs.player.BlipTvVideoSource.prototype.getVideoURL = function() {
    return this.videoURL_;
};

/**
* Checks if this video url is indeed for this MediaSource type, returns a
* mediaSource subclass if it is, null if it isn't
* @param {string} youtubeVideoID Youtube video id
* @param {Object.<string, *>=} opt_videoConfig Params to use for 
*     youtube query string, plus optional 'width' and 'height' 
*     parameters.
*/
unisubs.player.BliptvVideoSource.getMediaSource = function(videoURL, opt_videoConfig) {
    if(/^\s*https?:\/\/([^\.]+\.)?blip\.tv/.test(videoURL)){
        return new unisubs.player.BlipTvVideoSource("", videoURL, opt_videoConfig);
    }
    return null;
}

// add this mediaSource to our registry
unisubs.player.MediaSource.addMediaSource(unisubs.player.BliptvVideoSource.getMediaSource);
