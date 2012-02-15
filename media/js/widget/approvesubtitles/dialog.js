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

goog.provide('unisubs.approvesubtitles.Dialog');

/**
 * @constructor
 */
unisubs.approvesubtitles.Dialog = function(videoSource, serverModel,
                                    subtitles, opt_opener,
                                    opt_skipFinished, originalSubtitles, 
                                   isReviewOrApproval) {
    unisubs.subtitle.Dialog.call(this, videoSource, serverModel,
                                    subtitles, opt_opener,
                                    opt_skipFinished, originalSubtitles, 
                                   isReviewOrApproval) 
    unisubs.SubTracker.getInstance().start(true);

    this.opener_ = opener;
    this.captionSet_ = this.serverModel_.getCaptionSet();
    this.rightPanelListener_ = new goog.events.EventHandler(this);
};
goog.inherits(unisubs.approvesubtitles.Dialog, unisubs.subtitle.Dialog);

unisubs.approvesubtitles.Dialog.prototype.createDom = function() {
    unisubs.approvesubtitles.Dialog.superClass_.createDom.call(this);
    this.approvePanel_ = new unisubs.approvesubtitles.ApproveSubtitlesPanel(
        this.serverModel_.getCaptionSet(), this.getVideoPlayerInternal(),
        this.serverModel_, this.captionManager_);
    this.getCaptioningAreaInternal().addChild(this.approvePanel_, true);

    var rightPanel = this.createRightPanel_();

    this.setRightPanelInternal(rightPanel);
    this.getHandler().
        listen(
            rightPanel, unisubs.RightPanel.EventType.DONE,
            this.handleDoneKeyPress_).
        listen(
            rightPanel, unisubs.RightPanel.EventType.SAVEANDEXIT,
            this.handleSaveAndExitKeyPress_);
    goog.dom.classes.add(this.getContentElement(), 'unisubs-modal-widget-translate');
    this.showGuidelines_();

    this.timelineSubtitleSet_ = new unisubs.timeline.SubtitleSet(this.captionSet_, this.getVideoPlayerInternal());
    this.getTimelinePanelInternal().addChild(
        new unisubs.timeline.Timeline(1, this.timelineSubtitleSet_,
                                      this.getVideoPlayerInternal(), true), true);
};

unisubs.approvesubtitles.Dialog.prototype.showGuidelines_ = function() {
    if (!unisubs.guidelines['approve']) {
        return;
    }

    var guidelinesPanel = new unisubs.GuidelinesPanel(unisubs.guidelines['approve']);
    this.showTemporaryPanel(guidelinesPanel);
    this.displayingGuidelines_ = true;

    var that = this;
    this.getHandler().listenOnce(guidelinesPanel, unisubs.GuidelinesPanel.CONTINUE, function(e) {
        goog.Timer.callOnce(function() {
            that.displayingGuidelines_ = false;
            that.hideTemporaryPanel();
        });
    });
};

unisubs.approvesubtitles.Dialog.prototype.createRightPanel_ = function() {
    var $d = goog.bind(this.getDomHelper().createDom, this.getDomHelper());
    var title = "Approve Subtitles";
    var helpContents = new unisubs.RightPanel.HelpContents(title, [
        $d('p', {}, "Play the video and review the subtitles for both accuracy and timing."),
        $d('p', {}, "Once you're finished reviewing, you can either ",
                    $d('strong', {}, "send the subtitles back"),
                    " to their creator for additional work, or ",
                    $d('strong', {}, "approve"),
                    " them to be published. ",
                    "If you're unable to complete the task at this time, you can also ",
                    $d('strong', {}, "save this task"),
                    " for later."),
        $d('div', {'className': 'unisubs-extra'},
            $d('p', {}, "Enter review notes here. ",
                        "They will be sent to all previous contributors ",
                        "and posted as a ",
                        $d('em', {}, "public comment"),
                        " to the subtitles."),
            $d('span', {'className': 'unisubs-spanarrow'}))
    ]);
    return new unisubs.approvesubtitles.ApproveSubtitlesRightPanel(
        this, this.serverModel_, helpContents, [], false, "Done?", "Submit final Approval");
};

unisubs.approvesubtitles.Dialog.prototype.captionReached_ = function(event) {
    var c = event.caption;
    this.getVideoPlayerInternal().showCaptionText(c ? c.getText() : '');
};

unisubs.approvesubtitles.Dialog.prototype.enterDocument = function() {
    unisubs.approvesubtitles.Dialog.superClass_.enterDocument.call(this);
    unisubs.Dialog.translationDialogOpen = false;
    var doc = this.getDomHelper().getDocument();
    this.getHandler().listen(
            this.captionManager_,
            unisubs.CaptionManager.CAPTION,
            this.captionReached_);
};

unisubs.approvesubtitles.Dialog.prototype.disposeInternal = function() {
    unisubs.approvesubtitles.Dialog.superClass_.disposeInternal.call(this);
    this.serverModel_.dispose();
    this.timelineSubtitleSet_.dispose();
    this.timelineSubtitleSet_ = null;
};

unisubs.approvesubtitles.Dialog.prototype.getSubtitleLanguage = function() {
    return this.subtitleState_.LANGUAGE;
};

unisubs.approvesubtitles.Dialog.prototype.getServerModel = function() {
    return this.serverModel_;
};

unisubs.approvesubtitles.Dialog.prototype.isWorkSaved = function() {
    return this.saved_ || false;
};

unisubs.approvesubtitles.Dialog.prototype.saveWorkInternal = function(closeAfterSave) {
    var that = this;
    this.getRightPanelInternal().showLoading(true);
    this.getRightPanelInternal().finish('In Progress');
};

unisubs.approvesubtitles.Dialog.prototype.onWorkSaved = function(closeAfterSave){
    this.saved_ = true;
    unisubs.widget.ResumeEditingRecord.clear();
    if (this.finishFailDialog_) {
        this.finishFailDialog_.setVisible(false);
        this.finishFailDialog_ = null;
    }
    if (closeAfterSave) {
        this.setVisible(false);
    }
};
