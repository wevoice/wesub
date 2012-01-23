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
unisubs.editmetadata.Panel = function(subtitles, videoPlayer, serverModel, captionManager, originalSubtitles, inSubtitlingDialog) {
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
    this.originalSubtitles_ = originalSubtitles;
    // when in the translate dialog, there are only 2 stepts, for the subtitling, there are 4
    if (inSubtitlingDialog){

        this.numSteps_ = 4;
        this.nextButtonText_ = "Next step, Sync";
    }else{
        
        this.numSteps_ = "Submit subtitles";
        this.nextButtonText_ = "Next step, Sync";
    }
};
goog.inherits(unisubs.editmetadata.Panel, goog.ui.Component);

unisubs.editmetadata.Panel.prototype.enterDocument = function() {
    unisubs.editmetadata.Panel.superClass_.enterDocument.call(this);
    var handler = this.getHandler();
};
unisubs.editmetadata.Panel.prototype.createDom = function() {
    unisubs.editmetadata.Panel.superClass_.createDom.call(this);
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());

    var $t = goog.bind(this.getDomHelper().createTextNode, this.getDomHelper());
    var el = this.getElement().appendChild(this.contentElem_ = $d('div'));
    // for original languages we won't have original subtitles
    var source = this.originalSubtitles_ ? this.originalSubtitles_ : this.subtitles_;
    var originalTitle = source.title ? source.title : " no title ";
    var originalDescription = source.description? source.description : " no description" ;
    var title = this.subtitles_.title ? this.subtitles_.title : "";
    var description = this.subtitles_.description ? this.subtitles_.description : "";

    var originalDescription = source.description? source.description : " no description" ;
    this.titleTranslationWidget_ = 
        new unisubs.translate.TitleTranslationWidget(
            originalTitle, this.subtitles_);
    this.descriptionTranslationWidget_ = 
        new unisubs.translate.DescriptionTranslationWidget(
            originalDescription, this.subtitles_);
    //this.

    this.setElementInternal(this.getDomHelper().createDom('ul', "unisubs-titlesList"));
    this.addChild(this.titleTranslationWidget_, true);
    this.addChild(this.descriptionTranslationWidget_, true);
    this.descriptionTranslationWidget_.setTranslation(description);
    this.titleTranslationWidget_.setTranslation(title);
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

unisubs.editmetadata.Panel.prototype.createRightPanel_ = function(numSteps) {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var title = "Edit language attributes"
    var desc = "You should edit title and description for " + this.subtitles_.languageName;
    var helpContents = new unisubs.RightPanel.HelpContents(
        title, 
        [
            $d('p', {}, desc)
        ], this.numSteps_, 1);
    return new unisubs.editmetadata.RightPanel(this, 
                                               this.serverModel,
                                               helpContents,
                                               [],
                                               true,
                                               "Done? ",
                                               this.nextButtonText_);

};

