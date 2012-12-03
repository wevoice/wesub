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

goog.provide('unisubs.CaptionManager');

/**
 * @constructor
 *
 * @param {unisubs.player.AbstractVideoPlayer} videoPlayer
 * @param {unisubs.subtitle.EditableCaptionSet} captionSet
 */
unisubs.CaptionManager = function(videoPlayer, captionSet) {
    goog.events.EventTarget.call(this);

    this.captions_ = captionSet.captionsWithTimes();
    this.x = captionSet.x;

    var that = this;

    this.binaryCompare_ = function(time, caption) {
        return time - that.x['startTime'](caption);
    };
    this.binaryCaptionCompare_ = function(c0, c1) {
        return that.x['startTime'](c0) - that.x['startTime'](c1);
    };
    this.videoPlayer_ = videoPlayer;
    this.eventHandler_ = new goog.events.EventHandler(this);

    this.eventHandler_.listen(
	videoPlayer,
	unisubs.player.AbstractVideoPlayer.EventType.TIMEUPDATE,
	this.timeUpdate_);
    this.eventHandler_.listen(
	captionSet,
        goog.array.concat(
            goog.object.getValues(
                unisubs.subtitle.EditableCaptionSet.EventType),
            unisubs.subtitle.EditableCaption.CHANGE),
	this.captionSetUpdate_);

    this.currentCaptionIndex_ = -1;
    this.lastCaptionDispatched_ = null;
    this.eventsDisabled_ = false;
};
goog.inherits(unisubs.CaptionManager, goog.events.EventTarget);

unisubs.CaptionManager.CAPTION = 'caption';
unisubs.CaptionManager.CAPTIONS_FINISHED = 'captionsfinished';

unisubs.CaptionManager.prototype.captionSetUpdate_ = function(event) {
    var et = unisubs.subtitle.EditableCaptionSet.EventType;
    if (event.type == et.CLEAR_ALL ||
        event.type == et.CLEAR_TIMES ||
        event.type == et.RESET_SUBS) {
	this.captions_ = [];
        this.currentCaptionIndex_ = -1;
	this.dispatchCaptionEvent_(null);
    }
    else if (event.type == et.ADD) {
        var caption = event.caption;
        if (caption.getStartTime() != -1) {
            goog.array.binaryInsert(
                this.captions_, caption, this.binaryCaptionCompare_);
            this.sendEventForRandomPlayheadTime_(
                this.videoPlayer_.getPlayheadTime());
        }
    }
    else if (event.type == et.DELETE) {
        var caption = event.caption;
        if (caption.getStartTime() != -1) {
            goog.array.binaryRemove(
                this.captions_, caption, this.binaryCaptionCompare_);
            this.sendEventForRandomPlayheadTime_(
                this.videoPlayer_.getPlayheadTime());
        }
    }
    else if (event.type == unisubs.subtitle.EditableCaption.CHANGE) {
	if (event.timesFirstAssigned) {
	    this.captions_.push(event.target);
	    this.timeUpdate_();
	}
    }
};

unisubs.CaptionManager.prototype.timeUpdate_ = function() {
    // players will emit playhead time in seconds
    // the rest of the system will use milliseconds
    this.sendEventsForPlayheadTime_(
	this.videoPlayer_.getPlayheadTime() * 1000);
};

unisubs.CaptionManager.prototype.sendEventsForPlayheadTime_ =
    function(playheadTime)
{
    var subs = this.x['getSubtitles']();

    if (subs.length === 0)
        return;
    if (this.currentCaptionIndex_ == -1 &&
        playheadTime < this.x['startTime'](this.x['getSubtitle'](0)))
        return;

    var curCaption = this.currentCaptionIndex_ > -1 ?
        this.x['getSubtitle'](this.currentCaptionIndex_) : null;
    if (this.currentCaptionIndex_ > -1 &&
        curCaption != null &&
	this.x['isShownAt'](curCaption, playheadTime))
        return;

    var nextCaptionIndex =  this.currentCaptionIndex_ < subs.length -1 ?
        this.currentCaptionIndex_ + 1 : null;
    var nextCaption = this.currentCaptionIndex_ < subs.length - 1 ?
        this.captions_[this.currentCaptionIndex_ + 1] : null;
    if (nextCaption != null &&
	this.x['isShownAt'](this.x['getSubtitle'](nextCaptionIndex), playheadTime)) {
        this.currentCaptionIndex_++;
        this.dispatchCaptionEvent_(nextCaption, nextCaptionIndex);
        return;
    }
    if ((nextCaption == null ||
         playheadTime < this.x['startTime'](nextCaption)) &&
        (curCaption == null ||
         playheadTime >= this.x['startTime'](curCaption))) {
        this.dispatchCaptionEvent_(null);
        if (nextCaption == null && !this.eventsDisabled_)
            this.dispatchEvent(unisubs.CaptionManager.CAPTIONS_FINISHED);
        return;
    }
    this.sendEventForRandomPlayheadTime_(playheadTime);
};

unisubs.CaptionManager.prototype.sendEventForRandomPlayheadTime_ =
    function(playheadTime)
{
    var subs = this.x['getSubtitles']();
    var lastCaptionIndex = goog.array.binarySearch(subs,
        playheadTime, this.binaryCompare_);
    if (lastCaptionIndex < 0)
        lastCaptionIndex = -lastCaptionIndex - subs.length -1;
    this.currentCaptionIndex_ = lastCaptionIndex;
    if (lastCaptionIndex >= 0 &&
	this.x['isShownAt'](lastCaptionIndex, playheadTime)) {
        this.dispatchCaptionEvent_(this.captions_[lastCaptionIndex], lastCaptionIndex);
    }
    else {
        this.dispatchCaptionEvent_(null);
    }
};

unisubs.CaptionManager.prototype.dispatchCaptionEvent_ = function(caption, index) {
    if (caption == this.lastCaptionDispatched_)
        return;
    if (this.eventsDisabled_)
        return;
    this.lastCaptionDispatched_ = caption;
    this.dispatchEvent(new unisubs.CaptionManager.CaptionEvent(caption, index));
};

unisubs.CaptionManager.prototype.disposeInternal = function() {
    unisubs.CaptionManager.superClass_.disposeInternal.call(this);
    this.eventHandler_.dispose();
};

unisubs.CaptionManager.prototype.disableCaptionEvents = function(disabled) {
    this.eventsDisabled_ = disabled;
};

/**
* @constructor
*/
unisubs.CaptionManager.CaptionEvent = function(editableCaption, index) {
    this.type = unisubs.CaptionManager.CAPTION;
    this.caption = editableCaption;
    this.index = index;
};
