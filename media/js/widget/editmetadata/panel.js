// Universal Subtitles, universalsubtitles.org
//
// Copyright (C) 2011 Participatory Culture Foundation
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

goog.provide('unisubs.editmetadata.Panel');

/**
 * @constructor
 * @param {unisubs.subtitle.EditableCaptionSet} subtitles The subtitles
 *     for the video, so far.
 * @param {unisubs.player.AbstractVideoPlayer} videoPlayer
 * @param {unisubs.CaptionManager} Caption manager, already containing subtitles
 *     with start_time set.
 */
unisubs.editmetadata.Panel = function(subtitles, videoPlayer, serverModel, captionManager) {
    goog.ui.Component.call(this);
    /**
     * @type {unisubs.subtitle.EditableCaptionSet}
     */
    this.subtitles_ = subtitles;

    this.videoPlayer_ = videoPlayer;
    /**
     * @protected
     */
    this.serverModel = serverModel;
    this.captionManager_ = captionManager;
};
goog.inherits(unisubs.editmetadata.Panel, goog.ui.Component);

unisubs.editmetadata.Panel.prototype.enterDocument = function() {
    unisubs.editmetadata.Panel.superClass_.enterDocument.call(this);
    var handler = this.getHandler();
};
unisubs.editmetadata.Panel.prototype.createDom = function() {
    unisubs.editmetadata.Panel.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    this.getElement().appendChild(this.contentElem_ = $d('div'));

    this.getElement().appendChild(this.contentElem_ = $d('h1', "Edit title and description for video"));
};
unisubs.editmetadata.Panel.prototype.getRightPanel = function() {
   if (!this.rightPanel_) {
        this.rightPanel_ = this.createRightPanel_();
        //this.listenToRightPanel_();
    }
    return this.rightPanel_;

}
unisubs.editmetadata.Panel.prototype.disposeInternal = function() {
    unisubs.editmetadata.Panel.superClass_.disposeInternal.call(this);
    if (this.rightPanel_) {
        this.rightPanel_.dispose();
    }
};

unisubs.editmetadata.Panel.prototype.suspendKeyEvents = function(suspended) {
    this.keyEventsSuspended_ = suspended;
};

unisubs.editmetadata.Panel.prototype.createRightPanel_ = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var title = "Edit attributes for ";
    var helpContents = new unisubs.RightPanel.HelpContents(title, [
        $d('p', {}, "Fx meteadata"),
    ], 4, 1);
    return new unisubs.editmetadata.RightPanel(this, 
                                               this.serverModel,
                                               helpContents,
                                               [],
                                               true,
                                               "Done? ",
                                               "Next step, Sync");

};

