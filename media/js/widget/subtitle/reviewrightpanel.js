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

goog.provide('unisubs.subtitle.ReviewRightPanel');
/**
* @constructor
* @extends unisubs.RightPanel
*/
unisubs.subtitle.ReviewRightPanel = function(dialog,
                                             serverModel,
                                             helpContents,
                                             extraHelp,
                                             legendKeySpecs,
                                             showRestart,
                                             doneStrongText,
                                             doneText,
                                             reviewOrApprovalType,
                                             notesInput_
                                            ) {
    unisubs.RightPanel.call(this, serverModel, helpContents, extraHelp,
                             legendKeySpecs,
                             showRestart, doneStrongText, doneText);
    this.reviewOrApprovalType_  = reviewOrApprovalType;
    this.showDoneButton = ! reviewOrApprovalType;
    this.notesInput_ = notesInput_;
    this.dialog_ = dialog;
};
goog.inherits(unisubs.subtitle.ReviewRightPanel, unisubs.RightPanel);

unisubs.subtitle.ReviewRightPanel.prototype.appendMiddleContentsInternal = function($d, el) {
    if (this.reviewOrApprovalType_){
        return;
    }
    el.appendChild(this.makeExtra_($d,
        'Drag edges in timeline to adjust subtitle timing'));
    el.appendChild(this.makeExtra_($d,
        'Double click any subtitle to edit text. Rollover subtitles and use buttons to tweak time, add / remove subtitles.'));
};

// FIXME: dupliaction with editmetadatarightpanel
unisubs.subtitle.ReviewRightPanel.prototype.finish = function(e, approvalCode) {
    if (e){
        e.preventDefault();
    }
    var dialog = this.dialog_;
    var that = this;
    var actionName = this.reviewOrApprovalType_ == unisubs.Dialog.REVIEW_OR_APPROVAL['APPROVAL'] ? 
        'approve' : 'review';
    var successCallback = function(serverMsg) {
        unisubs.subtitle.OnSavedDialog.show(serverMsg, function() {
            dialog.onWorkSaved(true);
        }, actionName);
    };

    var failureCallback = function(opt_status) {
        if (dialog.finishFailDialog_) {
            dialog.finishFailDialog_.failedAgain(opt_status);
        } else {
            dialog.finishFailDialog_ = unisubs.finishfaildialog.Dialog.show(
                that.serverModel_.getCaptionSet(), opt_status,
                goog.bind(dialog.saveWorkInternal, dialog, false));
        }
    };

    this.serverModel_.finishApproveOrReview({
        'task_id': unisubs.task_id,
        'body': goog.dom.forms.getValue(this.notesInput_),
        'approved': approvalCode
    }, actionName == 'review', successCallback, failureCallback);
};

// FIXME: dupliaction with editmetadatarightpanel
unisubs.subtitle.ReviewRightPanel.prototype.appendCustomButtonsInternal = function($d, el) {
    if (!this.reviewOrApprovalType_ ){
        // for the subtitling dialog, we need the button to advance to the next painel
        return;
    }
    var buttonText = this.reviewOrApprovalType_ == unisubs.Dialog.REVIEW_OR_APPROVAL['APPROVAL'] ? 
        'Approve' : 'Review';

    this.sendBackButton_ = $d('a', {'class': 'unisubs-done widget-button'}, 'Send Back');
    this.saveForLaterButton_ = $d('a', {'class': 'unisubs-done widget-button'}, 'Save for Later');
    this.approveButton_ = $d('a', {'class': 'unisubs-done widget-button'}, buttonText);

    el.appendChild(this.sendBackButton_);
    el.appendChild(this.saveForLaterButton_);
    el.appendChild(this.approveButton_);

    var handler = this.getHandler();
    var that = this;
    handler.listen(this.sendBackButton_, 'click', function(e){
        that.finish(e, unisubs.Dialog.MODERATION_OUTCOMES.SEND_BACK);
    });
    handler.listen(this.saveForLaterButton_, 'click', function(e){
        that.finish(e, unisubs.Dialog.MODERATION_OUTCOMES.SAVE_FOR_LATER);
    });
    handler.listen(this.approveButton_, 'click', function(e){
        that.finish(e, unisubs.Dialog.MODERATION_OUTCOMES.APPROVED);
    });
};


unisubs.subtitle.ReviewRightPanel.prototype.makeExtra_ = function($d, text) {
    return $d('div', 'unisubs-extra unisubs-extra-left',
              $d('p', null, text),
              $d('span', 'unisubs-spanarrow'));
};
