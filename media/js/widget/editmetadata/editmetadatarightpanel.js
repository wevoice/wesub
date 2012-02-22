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

goog.provide('unisubs.editmetadata.RightPanel');


/**
 * @constructor
 * @extends unisubs.RightPanel
 */
unisubs.editmetadata.RightPanel = function(dialog, 
                                           serverModel, 
                                           helpContents, 
                                           extraHelp,
                                           legendKeySpecs, 
                                           showRestart, 
                                           doneStrongText, 
                                           doneText, 
                                           reviewOrApprovalType,
                                           notesInput,
                                           inSubtitlingDialog
                                          ) {
    unisubs.RightPanel.call(this,  serverModel, helpContents, extraHelp,
                            legendKeySpecs, showRestart, doneStrongText, doneText);

    this.showSaveExit = false;
    this.showDoneButton = true;
    if (reviewOrApprovalType && ! inSubtitlingDialog){
        this.showDoneButton = false;
    }    
    this.helpContents = helpContents;
    // TODO: See if there's a way to avoid the circular reference here.
    this.dialog_ = dialog;
    this.reviewOrApprovalType_ = reviewOrApprovalType;
    this.inSubtitlingDialog_ = inSubtitlingDialog;
    this.notesInput_ = notesInput;
};
goog.inherits(unisubs.editmetadata.RightPanel, unisubs.RightPanel);


unisubs.editmetadata.RightPanel.prototype.appendHelpContentsInternal = function($d, el) {
    var helpHeadingDiv = $d('div', 'unisubs-help-heading');
    el.appendChild(helpHeadingDiv);
    helpHeadingDiv.appendChild($d('h2', null, this.helpContents_.header));
    if (this.helpContents_.numSteps) {
        var that = this;
        var stepsUL = $d('ul', null, $d('span', null, 'Steps'));
        for (var i = 0; i < this.helpContents_.numSteps; i++) {
            var linkAttributes = { 'href' : '#' };
            if (i == this.helpContents_.activeStep)
                linkAttributes['className'] = 'unisubs-activestep';
            var link = $d('a', linkAttributes, i + 1 + '');
            this.getHandler().listen(
                link, 'click', goog.partial(function(step, e) {
                    e.preventDefault();
                    that.dispatchEvent(
                        new unisubs.RightPanel.GoToStepEvent(step));
                }, i));
            stepsUL.appendChild($d('li', null, link));
        }
        helpHeadingDiv.appendChild(stepsUL);
    }
    if (this.helpContents_.html) {
        var div = $d('div');
        div.innerHTML = this.helpContents_.html;
        el.appendChild(div);
    }
    else{
        goog.array.forEach(this.helpContents_.paragraphs, function(p) {
            el.appendChild($d('p', null, p));
        });
    }
    
    // FIXME : check if not needed when not in review mode
    if (false && this.showDoneButton){
        
        var stepsDiv = $d('div', 'unisubs-steps', this.loginDiv_);
        this.doneAnchor_ = this.createDoneAnchor_($d);
        stepsDiv.appendChild(this.doneAnchor_);
        el.appendChild(stepsDiv);
        
        this.getHandler().listen(this.doneAnchor_, 'click', this.doneClicked_);
    }
};

// FIXME: remove duplication from the subtitle.reviewpanel
unisubs.editmetadata.RightPanel.prototype.finish = function(e, approvalCode) {
    if (e){
        e.preventDefault();
    }
    var dialog = this.dialog_;
    var that = this;
    
    var actionName = this.reviewOrApprovalType == unisubs.Dialog.REVIEW_OR_APPROVAL['APPROVAL'] ? 
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

    var data = {
        'task_id': unisubs.task_id,
        'body': goog.dom.forms.getValue(this.notesInput_),
        'approved': approvalCode
    }
    this.serverModel_.finishApproveOrReview(data, actionName == 'review', successCallback, failureCallback);
};

unisubs.editmetadata.RightPanel.prototype.appendCustomButtonsInternal = function($d, el) {
    if (!this.reviewOrApprovalType_ || this.inSubtitlingDialog_){
        // for the subtitling dialog, we need the button to advance to the next painel
        return;
    }
    this.sendBackButton_ = $d('a', {'class': 'unisubs-done widget-button'}, 'Send Back');
    this.saveForLaterButton_ = $d('a', {'class': 'unisubs-done widget-button'}, 'Save for Later');
    var buttonText = this.reviewOrApprovalType == unisubs.Dialog.REVIEW_OR_APPROVAL['APPROVAL'] ? 
        'Approve' : 'Review';
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


