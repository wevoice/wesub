// Universal Subtitles, universalsubtitles.org
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

goog.provide("unisubs.player.BlipTvVideoPlayer");

/**
 * @constructor
 * @param {unisubs.player.BlipTvVideoSource} videoSource
 * @param {boolean=} opt_forDialog
 */
unisubs.player.BlipTvVideoPlayer = function(videoSource, opt_forDialog){
    unisubs.player.AbstractVideoPlayer.call(this, videoSource);

    this.videoSource_ = videoSource;
    this.forDialog_ = !!opt_forDialog;

    this.player_ = null;
    this.playerAPIID_ = [videoSource.getUUID(),
                         '' + new Date().getTime()].join('');

    this.playerElemID_ = videoSource.getUUID() + "_bliptvplayer";

    this.commands_ = [];
    this.playerSize_ = null;
    this.player_ = null;
    this.volume_ = 0.5;
    this.currentTime_ = 0;
    this.ended = false;

    this.swfEmbedded_ = false;
    this.delayer_ = null;

    this.isPlaying_ = false;
}

goog.inherits(unisubs.player.BlipTvVideoPlayer, unisubs.player.AbstractVideoPlayer);

unisubs.player.BlipTvVideoPlayer.DIALOG_SIZE = new goog.math.Size(400, 400);

unisubs.player.BlipTvVideoPlayer.prototype.logger_ = 
    goog.debug.Logger.getLogger('unisubs.player.BlipTvVideoPlayer');

unisubs.player.BlipTvVideoPlayer.prototype.createDom = function() {
    // FIXME: this is copied directly from youtube video player.

    this.setElementInternal(this.getDomHelper().createElement('span'));
    goog.dom.classes.add(this.getElement(), 'unisubs-videoplayer');

    var sizeFromConfig = this.sizeFromConfig_();
    if (!this.forDialog_ && sizeFromConfig){
        this.playerSize_ = sizeFromConfig;
    } else {
        this.playerSize_ = this.forDialog_ ?
        unisubs.player.AbstractVideoPlayer.DIALOG_SIZE :
        unisubs.player.AbstractVideoPlayer.DEFAULT_SIZE;
    }

};

unisubs.player.BlipTvVideoPlayer.prototype.enterDocument = function(){
    unisubs.player.BlipTvVideoPlayer.superClass_.enterDocument.call(this);
    
    if(this.swfEmbedded_){
        return;
    }

    var that = this;

    var jsonp = new goog.net.Jsonp(this.videoSource_.videoURL_ + "?skin=json");
    jsonp.send({}, function(response){
        var post = response[0]['Post'];
        that.duration_ = parseInt(post['media']['duration']);
        that.embedSWF_(post['embedUrl']);
    })

}

unisubs.player.BlipTvVideoPlayer.prototype.embedSWF_ = function(embedUrl){
    if(this.swfEmbedded_){
        return;
    }

    this.swfEmbedded_ = true; 
    var videoDiv = this.getDomHelper().createDom("div");
    videoDiv.id = unisubs.randomString();
    this.getElement().appendChild(videoDiv);
    var params = {'allowScriptAccess': 'always', 'enablejs': 'true', "wmode": "opaque"};
    var atts = { 'id': this.playerElemID_,
                 'style': unisubs.style.setSizeInString(
                  '', this.playerSize_) };

    var chromeless = this.forDialog_ ? "true" : "false";
    var url = embedUrl + "?chromeless=" + chromeless + "&captionson=false&backcolor=#00000"

    var callback = goog.bind(this.swfReady_, this);

    window["swfobject"]["embedSWF"](
        url,
        videoDiv.id, this.playerSize_.width + '',
        this.playerSize_.height + '', "8",
        null, null, params, atts, callback);
}

unisubs.player.BlipTvVideoPlayer.prototype.isPausedInternal = function(){
    return !this.isPlaying_;
}

unisubs.player.BlipTvVideoPlayer.prototype.isPlayingInternal = function(){
    return this.isPlaying_;
}

unisubs.player.BlipTvVideoPlayer.prototype.videoEndedInternal = function(){
    return this.ended_;
}

unisubs.player.BlipTvVideoPlayer.prototype.playInternal = function(){
    if(this.player_){
        this.player_['sendEvent']("play");
    } else {
        this.commands_.push(goog.bind(this.playInternal, this));
    }
}

unisubs.player.BlipTvVideoPlayer.prototype.pauseInternal = function(){
    if(this.player_){
        this.player_['sendEvent']("pause");
    } else {
        this.commands_.push(goog.bind(this.pauseInternal, this));
    }
}

unisubs.player.BlipTvVideoPlayer.prototype.stopLoadingInternal = function(){
    this.pause();
}

unisubs.player.BlipTvVideoPlayer.prototype.resumeLoadingInternal = function(playheadTime){
    this.play();
}

unisubs.player.BlipTvVideoPlayer.prototype.getPlayheadTimeInternal = function(){
    return this.currentTime_;
}

unisubs.player.BlipTvVideoPlayer.prototype.setPlayheadTime = function(playheadTime){
    if (this.player_) {
        this.player_['sendEvent']("seek", playheadTime);
        this.sendTimeUpdateInternal();
    } else {
        this.commands_.push(goog.bind(this.setPlayheadTime, this, playheadTime));
    }
    
}

unisubs.player.BlipTvVideoPlayer.prototype.getDuration = function(){
    return this.duration_;
}

//unisubs.player.BlipTvVideoPlayer.prototype.getBufferedLength = function(){
    //return this.player_ ? 1 : 0;
//}

//unisubs.player.BlipTvVideoPlayer.prototype.getBufferedStart = function(index){
    //return 0;
//}

//unisubs.player.BlipTvVideoPlayer.prototype.getBufferedEnd = function(index){
    //return this.currentTime_ * this.getDuration();
//}

unisubs.player.BlipTvVideoPlayer.prototype.getVolume = function(index){
    return this.volume_;
}

unisubs.player.BlipTvVideoPlayer.prototype.setVolume = function(volume){
    if(this.player_){
        this.player_['sendEvent']("volume", volume);
        this.volume_ = volume;
    } else {
        this.commands_.push(goog.bind(this.setVolume, this));
    }
}

unisubs.player.BlipTvVideoPlayer.prototype.getVideoSize = function(index){
    return this.playerSize_;
}

unisubs.player.BlipTvVideoPlayer.prototype.swfReady_ = function(index){
    this.player_ = goog.dom.$(this.playerElemID_);

    if(!this.player_['addJScallback']){
        this.callback_ = goog.bind(this.swfReady_, this);
        setTimeout(this.callback_, 500)
        return;
    }

    this.swfLoaded_ = true;

    goog.array.forEach(this.commands_, function(cmd) { cmd(); });
    this.commands_ = [];

    var that = this;
    var et = unisubs.player.AbstractVideoPlayer.EventType;
    var randomString = unisubs.randomString();

    var onPlayerStateChange = "onPlayerState" + randomString;

    window[onPlayerStateChange] = function(newState){
        that.logger_.info("new state is " + newState);
        switch(newState) {
            case 'playing':
                that.isPlaying_ = true;
                that.dispatchEvent(et.PLAY);
                break;
            case "paused":
                that.isPlaying_ = false;
                that.dispatchEvent(et.PAUSE);
                break;
        }
    };

    this.player_['addJScallback']("player_state_change", "window." + onPlayerStateChange);

    var onCurrentTimeChange = "onCurrentTimeCha" + randomString;

    window[onCurrentTimeChange] = function(time){
        that.currentTime_ = time;
        that.sendTimeUpdateInternal();
    };

    this.player_['addJScallback']("current_time_change", "window." + onCurrentTimeChange);

    var onVideoEnded = "onVideoEnde" + randomString;

    window[onVideoEnded] = function(){
        that.ended_ = true;
        that.dispatchEndedEvent();
    };
    this.player_['addJScallback']("complete", "window." + onVideoEnded);

    this.player_['sendEvent']("volume", this.volume_);
}

unisubs.player.BlipTvVideoPlayer.prototype.sizeFromConfig_ = function() {
    // FIXME: duplicates same method in youtube player
    var config = this.videoSource_.getVideoConfig();
    if (config && config['width'] && config['height'])
        return new goog.math.Size(
            parseInt(config['width']), parseInt(config['height']));
    else
        return null;
};
