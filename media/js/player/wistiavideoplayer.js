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

goog.provide('unisubs.player.WistiaVideoPlayer');

/**
 * @constructor
 */
 
 /***
 
 UGLY: this is ripped from the YTIFrame player 
 
 
 ***/
 
 
unisubs.player.WistiaVideoPlayer = function(videoSource, opt_forDialog) {
    unisubs.player.AbstractVideoPlayer.call(this, videoSource);
    this.player_ = null;
    this.videoSource_ = videoSource;
    this.playerElemID_ = unisubs.randomString() + "_wistiaplayer";
    this.forDialog_ = !!opt_forDialog;
    this.commands_ = [];
    this.progressTimer_ = new goog.Timer(
        unisubs.player.AbstractVideoPlayer.PROGRESS_INTERVAL);
    this.timeUpdateTimer_ = new goog.Timer(
        unisubs.player.AbstractVideoPlayer.TIMEUPDATE_INTERVAL);
    goog.mixin(unisubs.player.WistiaVideoPlayer.prototype,
               unisubs.player.YoutubeBaseMixin.prototype);
    this.videoPlayerType_ = 'wistia';

    this.embeddedVideo = null;
    this.modeSelect = null;
};
goog.inherits(unisubs.player.WistiaVideoPlayer, unisubs.player.AbstractVideoPlayer);


unisubs.player.WistiaVideoPlayer.prototype.createDom = function() {
    unisubs.player.WistiaVideoPlayer.superClass_.createDom.call(this);
    this.setPlayerSize_();
    var embedUri = new goog.Uri(
        "http://fast.wistia.com/embed/iframe/" + 
            this.videoSource_.getVideoId());
    this.addQueryString_(embedUri);
    this.playerSize_.width = 400;
    div_args = {
        'id': this.playerElemID_,
        'data-video-width': this.playerSize_.width + '',
        'data-video-height': this.playerSize_.height + '', 
        'style': unisubs.style.setSizeInString('', this.playerSize_) 
    };
    var videoDiv = this.getDomHelper().createDom('div', div_args);
    this.getElement().appendChild(videoDiv);
	unisubs.addScript("http://fast.wistia.com/static/E-v1.js", false);
    
    var that = this;
    window.setTimeout( 
      (function (video_id, container_id) {
        return function () {
          that.embeddedVideo = window['Wistia']['embed'](video_id, {
            playerColor: "ff0000",
            fullscreenButton: false,
            container: container_id,
            autoplay: false,
            chromeless: true,
            controlsVisibleOnLoad: false,
            doNotTrack: true,
            fullscreenButton: false,
            playButton: false,
            playBar: false,
            videoFoam: false             
          });
          // add listeners to buttons
          var play_btn = goog.dom.getElementByClass('unisubs-play-beginner');
          var skip_btn = goog.dom.getElementByClass('unisubs-skip');
          goog.events.listen(play_btn, goog.events.EventType.CLICK, that.videoPlay);
          goog.events.listen(skip_btn, goog.events.EventType.CLICK, that.videoSkip);
          // add listeners for TAB key
          var docKh = new goog.events.KeyHandler(document);
          goog.events.listen(docKh, 'key', function (e) {
              if (e.keyCode == 9) { // TAB key
                  if (e.shiftKey) {
                      vid_skip();
                  } else {
                      vid_play();
                  }
              }
          });
          // player controls
          goog.events.listen(goog.dom.getElementByClass('unisubs-playPause'),
                  goog.events.EventType.CLICK, function () {
                      if (! that.embeddedVideo) { return; }
                      that.embeddedVideo['state']() == 'playing' ?
                        that.embeddedVideo['pause']() :
                        that.embeddedVideo['play']();
                  });
        }; // return function
      })(this.videoSource_.getVideoId(), this.playerElemID_)
    , 5500);
};

unisubs.player.WistiaVideoPlayer.prototype.videoPlay = function() {
    if (! this.embeddedVideo) { return; }
    var speedmode = this.videoGetMode();
    if (speedmode == 'no') { // no autopause
        if (this.embeddedVideo['state']() == 'playing') {
            this.embeddedVideo['pause']();
        } else {
            this.embeddedVideo['play']();
        }
    } else if (speedmode == 'au') { // magical autopause
    } else { // beginner {
        this.embeddedVideo['play']();
        var that = this;
        window.setTimeout(function () { that.embeddedVideo['pause'](); }, 4000);
    }
}

unisubs.player.WistiaVideoPlayer.prototype.videoSkip = function() {
    if (! this.embeddedVideo) { return; }
    var speedmode = this.videoGetMode();
    if (speedmode == 'pl') { // beginner
        this.embeddedVideo.time(this.embeddedVideo['time']() - 4)['play']();
        var that = this;
        window.setTimeout(function () { that.embeddedVideo['pause'](); }, 4000);
    } else {
        this.embeddedVideo.time(this.embeddedVideo['time']() - 8)['play']();
    }
}

unisubs.player.WistiaVideoPlayer.prototype.videoGetMode = function() {
    if (! this.modeSelect) {
        var nodes = goog.dom.getChildren(goog.dom.getElementByClass('unisubs-speedmode'));
        for (ii = 0; ii < nodes.length; ++ii) {
            if (nodes[ii].nodeName == 'SELECT') { 
                this.modeSelect = nodes[ii];
                break;
            }
        }
    }
    return this.modeSelect == null ? 'pl' : goog.dom.forms.getValue(this.modeSelect);
}

unisubs.player.WistiaVideoPlayer.prototype.addQueryString_ = function(uri) {
    var config = this.videoSource_.getVideoConfig();
    if (!this.forDialog_ && config) {
        for (var prop in config) {
            if (prop != 'width' && prop != 'height')
                uri.setParameterValue(prop, config[prop]);
        }
    }
    var locationUri = new goog.Uri(window.location);
    var domain = window.location.protocol + "//" + 
        locationUri.getDomain() + 
        (locationUri.getPort() != null ? (':' + locationUri.getPort()) : '');
    uri.setParameterValue('origin', domain).
        setParameterValue('wmode', 'opaque').
        setParameterValue('videoWidth',400).
        setParameterValue('videoHeight',300).
        setParameterValue('doNotTrack',true);
        
    if (this.forDialog_) {
        uri.setParameterValue('playbar',false).
        setParameterValue('chromeless', true);
    }
};

unisubs.player.WistiaVideoPlayer.prototype.setPlayerSize_ = function() {
    /*var sizeFromConfig = this.videoSource_.sizeFromConfig();
    if (!this.forDialog_ && sizeFromConfig)
        this.playerSize_ = sizeFromConfig;
    else
        this.playerSize_ = this.forDialog_ ?
        unisubs.player.AbstractVideoPlayer.DIALOG_SIZE :
        unisubs.player.AbstractVideoPlayer.DEFAULT_SIZE;
        */
      this.playerSize_ = unisubs.player.AbstractVideoPlayer.DEFAULT_SIZE
    this.setDimensionsKnownInternal();
};

unisubs.player.WistiaVideoPlayer.prototype.decorateInternal = function(elem) {
    unisubs.player.WistiaVideoPlayer.superClass_.decorateInternal.call(this, elem);
    this.iframe_ = elem;
    if (elem.id) {
        this.playerElemID_ = elem.id;
    }
    else {
        elem.id = this.playerElemID_;
    }
    
    this.playerSize_ = new goog.math.Size(
        parseInt(400), parseInt(300));
    this.setDimensionsKnownInternal();
};

unisubs.player.WistiaVideoPlayer.prototype.enterDocument = function() {
    unisubs.player.WistiaVideoPlayer.superClass_.enterDocument.call(this);
    var w = window;
    if (w['Wistia'] && w['Wistia']['Player'])
        this.makePlayer_();
    else {
        var readyFunc = "onYouTubePlayerAPIReady";
        var oldReady = goog.nullFunction;
        if (w[readyFunc])
            oldReady = w[readyFunc];
        var myOnReady = goog.bind(this.makePlayer_, this);
        window[readyFunc] = function() {
            oldReady();
            myOnReady();
        };
    }
};

unisubs.player.WistiaVideoPlayer.prototype.makePlayer_ = function() {
    var playerStateChange = goog.bind(this.playerStateChange_, this);
    this.almostPlayer_ = new window['Wistia']['Player'](
        this.playerElemID_, {
            'events': {
                'onReady': goog.bind(this.playerReady_, this),
                'onStateChange': function(state) {
                    playerStateChange(state['data']);
                }
            }
        });
};

unisubs.player.WistiaVideoPlayer.prototype.playerReady_ = function(e) {
    this.player_ = this.almostPlayer_;
    goog.array.forEach(this.commands_, function(cmd) { cmd(); });
    this.commands_ = [];
    this.getHandler().
        listen(this.progressTimer_, goog.Timer.TICK, this.progressTick_).
        listen(this.timeUpdateTimer_, goog.Timer.TICK, this.timeUpdateTick_);
    this.progressTimer_.start();
};

unisubs.player.WistiaVideoPlayer.prototype.getVideoElements = function() {
    return [this.iframe_];
};

unisubs.player.WistiaVideoPlayer.prototype.disposeInternal = function() {
    unisubs.player.WistiaVideoPlayer.superClass_.disposeInternal.call(this);
    this.progressTimer_.dispose();
    this.timeUpdateTimer_.dispose();
};

unisubs.player.WistiaVideoPlayer.prototype.exitDocument = function() {
    unisubs.player.WistiaVideoPlayer.superClass_.exitDocument.call(this);
    this.progressTimer_.stop();
    this.timeUpdateTimer_.stop();
};
