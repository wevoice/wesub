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

goog.provide('unisubs.reviewsubtitles.ReviewApproveRightPanel');


/**
 * @constructor
 * @extends unisubs.RightPanel
 */
unisubs.reviewsubtitles.ReviewApproveRightPanel = function(
    dialog, serverModel, helpContents, legendKeySpecs, showRestart, doneStrongText, doneText, reviewOrApprovalType) {
    unisubs.RightPanel.call(this, serverModel, helpContents, null,
                            legendKeySpecs, showRestart, doneStrongText, doneText);

    this.showSaveExit = false;
    this.showDoneButton = false;

    // TODO: See if there's a way to avoid the circular reference here.
    this.dialog_ = dialog;
    this.reviewOrApprovalType_ = reviewOrApprovalType;
};
goog.inherits(unisubs.reviewsubtitles.ReviewApproveRightPanel, unisubs.RightPanel);

/**
 * Values for approval stages.
 * @const
 * @type {object}
 * @private
 */
unisubs.reviewsubtitles.ReviewApproveRightPanel.APPROVAL_STAGES_ = {
    'In Progress': 10,
    'Approved': 20,
    'Rejected': 30
};

unisubs.reviewsubtitles.ReviewApproveRightPanel.prototype.appendCustomButtonsInternalApprove = function($d, el) {
    this.sendBackButton_ = $d('a', {'class': 'unisubs-done widget-button'}, 'Send Back');
    this.saveForLaterButton_ = $d('a', {'class': 'unisubs-done widget-button'}, 'Save for Later');
    this.approveButton_ = $d('a', {'class': 'unisubs-done widget-button'}, 'Approve');

    el.appendChild(this.sendBackButton_);
    el.appendChild(this.saveForLaterButton_);
    el.appendChild(this.approveButton_);

    var handler = this.getHandler();
    handler.listen(this.sendBackButton_, 'click', this.sendBackButtonClicked_);
    handler.listen(this.saveForLaterButton_, 'click', this.saveForLaterButtonClicked_);
    handler.listen(this.approveButton_, 'click', this.approveButtonClicked_);
};

unisubs.reviewsubtitles.ReviewApproveRightPanel.prototype.finishApprove = function(approved) {
    var approval_code = unisubs.reviewsubtitles.ReviewApproveRightPanel.APPROVAL_STAGES_[approved];
    var dialog = this.dialog_;

    var actionName = 'review';
    if (this.reviewOrApprovalType_ == unisubs.Dialog.REVIEW_OR_APPROVAL['APPROVAL']){
        actionName = 'approve';
    }
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
                goog.bind(dialog.saveWorkInternal, dialog, closeAfterSave));
        }
    };

    this.serverModel_.finishReview({
        'task_id': unisubs.task_id,
        'body': goog.dom.forms.getValue(this.bodyInput_),
        'approved': approval_code
    }, successCallback, failureCallback);
};
unisubs.reviewsubtitles.ReviewApproveRightPanel.prototype.approveButtonClicked_ = function(e){
    e.preventDefault();
    this.finish('Approved');
};
unisubs.reviewsubtitles.ReviewApproveRightPanel.prototype.saveForLaterButtonClicked_ = function(e){
    e.preventDefault();
    this.finish('In Progress');
};
unisubs.reviewsubtitles.ReviewApproveRightPanel.prototype.sendBackButtonClicked_ = function(e){
    e.preventDefault();
    this.finish('Rejected');
};
