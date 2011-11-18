var ACTIVE_CLASS  =- "current";

var CONTAINER_SELECTOR = ".panel-holder";

var ON_PROJECT_SAVED = "onProjectSaved";
var ON_PROJECT_CANCELED = "onProjectCanceled";
var ON_PROJECT_DELETED = "onProjectDeleted";

// Projects -------------------------------------------------------------------
var ProjectModel = BaseModel.$extend({});
var ProjectEditPanel = Class.$extend({
     __init__: function(pModel){
         this.model = pModel;
         // checkbox needs to be normalized
       
         this.el = ich.projectEditPanel(this.model);
         this.onSaveClicked = _.bind(this.onSaveClicked, this);
         this.onDeleteClicked = _.bind(this.onDeleteClicked, this);
         this.onChangeProjectReturned = _.bind(this.onChangeProjectReturned, this);
         this.onCancel  = _.bind(this.onCancel, this);
         var deleteButtonEl = $(".project-delete", this.el);
         if(this.model.isNew()){
             deleteButtonEl.remove();
         }else{
              deleteButtonEl.click(this.onDeleteClicked);
         }
         $(".project-save", this.el).click(this.onSaveClicked);
         $(".project-cancel", this.el).click(this.onCancel);
         captureEnterSubmit($("form", this.el), this.onSaveClicked);
         
    },
    show: function(){
        $(this.el).show();

        
    },
    hide: function(){
        $(this.el).remove();        
    },
    getValuesFromForm: function(form){
        var inputs = $(':input', form);

        var values = {};
        inputs.each(function() {
            values[this.name] = $(this).val() || null;
        });
        return values;

    },
    onSaveClicked: function(e){
        if (e) e.preventDefault();
        var values = this.getValuesFromForm($("form", this.el));
        var wf = $("input[name='workflow_enabled']", $("form", this.el)).attr("checked");
        TeamsApiV2.project_edit(
            TEAM_SLUG,
            values.pk,
            values.name,
            values.slug,
            values.description,
            values.order ,
            wf,
            this.onChangeProjectReturned
        )
        return false;
    },
    onChangeProjectReturned: function(data){
        var res = data;
        if (res && res.success){
            $.jGrowl(res.msg);
            if (res.obj){
                this.model.update(res.obj);
                this.el.trigger(ON_PROJECT_SAVED, this.model);
                
            }
            // show errors
        }else{
            $.jGrowl.error(data.result.message);
            if(data.result && data.result.errors){

            }
        }
    },
    onCancel: function(e){
        e.preventDefault();
        this.el.trigger(ON_PROJECT_CANCELED);
        return false;
    },
    onDeleteClicked: function(e){
        e.preventDefault();
        var that = this;
        this.confirmationDialog = new ConfirmationDialog(
            "Delete project " + this.model.name,
            "Are you sure? This cannot be undone. All videos belongoing to this project will be moved to the team as a whole",
            "Yes, delete it!", 
            function (e){
                if (e) {
                    e.preventDefault()
                }
                that.onDeletionConfimed();
                return false;
            },
            "Nope, leave it alone",
            function(e){
                if (e) {
                    e.preventDefault()
                }
                that.onDeletionCanceled();
                return false;
            })
        this.confirmationDialog.show();
        this.el.append(this.confirmationDialog.el);
        $("form", this.el).hide();
        return false;
    },
    onDeletionCanceled: function(){
        this.confirmationDialog.hide();
        $("form", this.el).show();
        this.confirmationDialog = null;

    },
    onDeletionConfimed: function(){
        var that = this;
        TeamsApiV2.project_delete(
            TEAM_SLUG, 
            this.model.pk,
            function(res){
                if (res && res.success ){
                    $.jGrowl(res.msg);
                    $("form", that.el).hide();
                    that.el.trigger(ON_PROJECT_DELETED, [that.model]);
                    if (that.confirmationDialog){
                        that.confirmationDialog.hide()
                    }
                }
            }
        );
    }
            
    
});
var ProjectListItem = Class.$extend({
    __init__:function(model){
        var vel = this.el = ich.projectListItem(model);
        this.model = model;
        $("a.action-edit", this.el).click(function(e){
            e.preventDefault();
            vel.trigger("onEditRequested", model)
            return false;
        })
    },

})
var ProjectSelectionButton = Class.$extend({
    __init__: function(pModel){
        this.model = pModel;

    }
});
var ProjectPanel = AsyncPanel.$extend({
    __init__: function(){
        this.onProjectListLoaded = _.bind(this.onProjectListLoaded, this);
        this.onNewProjectClicked = _.bind(this.onNewProjectClicked, this);
        this.onProjectSaved = _.bind(this.onProjectSaved, this);
        this.onProjectCanceled = _.bind(this.onProjectCanceled, this);
        this.onProjectDeleted = _.bind(this.onProjectDeleted, this);
        this.onEditRequested = _.bind(this.onEditRequested, this);
        this.el = ich.projectPanel();
        this.projectAddButton =  $("a.project-add", this.el).click(this.onNewProjectClicked);
        scope = this;
        TeamsApiV2.project_list(TEAM_SLUG, this.onProjectListLoaded);
        this.projects = [];
        
    },
    
    addProject: function(pModel){
        var isNew = true;
        _.each(this.projects, function(m){
            if (pModel.pk == m.pk ){
                isNew = false;
            }
        });
        if (isNew){
            this.projects.push(pModel);
        }
    },
    removeProject: function(pModel){
        var index = _.indexOf(this.projects, pModel);
        if (index != -1){
            this.projects.splice(index, 1);
        }
    },
    renderProjectList: function(){
        if (!this.projectListing) {
            this.projectListing = $(".projects.listing", $(this.el).eq(0).parent());
        }
        $("li", this.projectListing).remove();
        _.each(this.projects, function(x){
            var item = new ProjectListItem(x)
            this.projectListing.append(item.el);
            item.el.bind("onEditRequested", this.onEditRequested)
        }, this);
    },
    onEditRequested: function(e, model){
        e.preventDefault();
        this.projectEditPanel  = new ProjectEditPanel(model);
        this.el.eq(0).parent().append(this.projectEditPanel.el);
        this.projectEditPanel.show();
        this.projectListing.hide()
        this.projectEditPanel.el.bind(ON_PROJECT_SAVED, this.onProjectSaved)
        this.projectEditPanel.el.bind(ON_PROJECT_CANCELED, this.onProjectCanceled);
        this.projectEditPanel.el.bind(ON_PROJECT_DELETED, this.onProjectDeleted);
        $(this.projectAddButton).hide();
        return false;
    },
    onProjectListLoaded: function(data){
        _.each(data, function(x){
            this.addProject(new ProjectModel(x))
        }, this);
        this.renderProjectList();
    },
    
    onNewProjectClicked : function(e, model){
        this.onEditRequested(e, new ProjectModel());
        return false;
    },
    _hideEditPanel:function(){
        this.projectEditPanel.hide();
        this.projectEditPanel.el.unbind(ON_PROJECT_SAVED);
        this.projectEditPanel.el.unbind(ON_PROJECT_CANCELED);
        this.projectEditPanel.el.unbind(ON_PROJECT_DELETED);
        this.projectListing.show()
        $(this.projectAddButton).show();
        
    },
    onProjectCanceled: function(e){
        this._hideEditPanel();
    },
    onProjectSaved: function(e, p){
        this._hideEditPanel()
        this.addProject(p);
        this.renderProjectList();
    },
    onProjectDeleted: function(e,p){
        this._hideEditPanel();
        this.removeProject(p);
        this.renderProjectList();
    },
    hide : function(){
        if (this.projectEditPanel){
            this.projectEditPanel.hide()
        }
        this.el.each(function(i,o){
            $(o).remove();
        });
    }
});

// Workflows ------------------------------------------------------------------
var WorkflowModel = Class.$extend({
    __init__: function(data) {
        this.pk = data.pk;
        this.team = data.team;
        this.project = data.project;
        this.team_video = data.team_video;

        this.autocreate_subtitle = data.autocreate_subtitle;
        this.autocreate_translate = data.autocreate_translate;
        this.review_allowed = data.review_allowed;
        this.approve_allowed = data.approve_allowed;
    }
});
var WorkflowItem = Class.$extend({
    __init__: function(model) {
        // Rebind functions
        this.render = _.bind(this.render, this);
        this.onSubmit = _.bind(this.onSubmit, this);
        this.onSaved = _.bind(this.onSaved, this);

        // Store data
        this.model = model;

        // Render template
        this.el = $("<div></div>");
        this.render();
    },

    render: function() {
        $(this.el).html(ich.workflow(this.model));

        // Fill values
        $('[name=autocreate_subtitle]', this.el).attr('checked', this.model.autocreate_subtitle);
        $('[name=autocreate_translate]', this.el).attr('checked', this.model.autocreate_translate);
        $('[name=review_allowed]', this.el).val(this.model.review_allowed);
        $('[name=approve_allowed]', this.el).val(this.model.approve_allowed);

        // Bind events
        $(".submit", this.el).click(this.onSubmit);
    },
    onSubmit: function(e) {
        e && e.preventDefault();

        TeamsApiV2.workflow_set(this.model.team, this.model.project, this.model.team_video, {
            autocreate_subtitle: $('[name=autocreate_subtitle]', this.el).attr('checked'),
            autocreate_translate: $('[name=autocreate_translate]', this.el).attr('checked'),
            review_allowed: $('[name=review_allowed]', this.el).val(),
            approve_allowed: $('[name=approve_allowed]', this.el).val()
        }, this.onSaved);
    },
    onSaved: function(data) {
        if (data && data.error) {
            $.jGrowl(data.error);
        } else {
            this.model = new WorkflowModel(data);
            this.render();
        }
    }
});

// Basic Settings -------------------------------------------------------------
var TeamModel = Class.$extend({
    __init__: function(data) {
        this.pk = data.pk;
        this.name = data.name;
        this.description = data.description;
        this.membership_policy = data.membership_policy;
        this.video_policy = data.video_policy;
        this.task_assign_policy = data.task_assign_policy;
        this.subtitle_policy = data.subtitle_policy;
        this.translate_policy = data.translate_policy;
        this.logo = data.logo;
        this.logo_full = data.logo_full;
        this.workflowEnabled = data.workflow_enabled;
    }
});
var BasicPanel  = AsyncPanel.$extend({
    __init__: function() {
        // Rebind functions
        this.saveImage = _.bind(this.saveImage, this);
        this.saveData = _.bind(this.saveData, this);
        this.onSubmit = _.bind(this.onSubmit, this);
        this.onLoaded = _.bind(this.onLoaded, this);
        this.fillFromModel = _.bind(this.fillFromModel, this);

        this.onImageUploadClick = _.bind(this.onImageUploadClick, this);
        this.onImageUploaded = _.bind(this.onImageUploaded, this);

        // Render template
        this.el = ich.basicPanel();

        // Bind events
        $('form.team-settings', this.el).submit(this.onSubmit);
        $('button', this.el).click(this.onImageUploadClick);

        // Load initial data
        this.team = null;
        TeamsApiV2.team_get(TEAM_SLUG, this.onLoaded);
    },

    saveImage: function(callback) {
        var that = this;
        if ($('form.logo input', this.el).val()) {
            $('form.logo', this.el).ajaxSubmit({
                success: function(resp, status, xhr, from) {
                    that.onImageUploaded(resp);
                    callback && callback();
                },
                dataType: 'json'
            });
        } else {
            callback && callback();
        }
    },
    onImageUploadClick: function(e, callback) {
        e.preventDefault();
        this.saveImage(callback);
        return false;
    },
    onImageUploaded: function(resp) {
        this.team.logo = resp['url'];
        this.team.logo_full = resp['url_full'];
        this.fillFromModel();
    },

    saveData: function() {
        var data = {
            name: $('#basic_name', this.el).val(),
            description: $('#basic_description', this.el).val(),
            membership_policy: $('#id_membership_policy', this.el).val(),
            video_policy: $('#id_video_policy', this.el).val(),
            workflow_enabled: $('#basic_workflows_enabled', this.el).attr('checked')
        };
        TeamsApiV2.team_set(TEAM_SLUG, data, this.onLoaded);

        this.workflow && this.workflow.onSubmit();
    },
    onSubmit: function(e) {
        e.preventDefault();
        this.saveImage(this.saveData);
        return false;
    },
    onLoaded: function(data) {
        this.team = new TeamModel(data);
        this.fillFromModel();
    },

    fillFromModel: function() {
        $('#basic_name', this.el).val(this.team.name);
        $('#basic_description', this.el).val(this.team.description);

        if (this.team.logo) {
            $('#current_logo', this.el).attr('src', this.team.logo);
            $('.content img.logo').attr('src', this.team.logo_full);
        } else {
            // TODO: Fill in placeholder image.
            $('#current_logo', this.el).attr('src', 'some/placeholder.jpg');
            $('.content img.logo').attr('src',  'some/placeholder.jpg');
        }

        // We edit the page-level title here too.  It's not part of the
        // template, but in this one case we should update it.
        $('.hd h2').text(this.team.name);
    }
});

// Guidelines and Messages ----------------------------------------------------
var GuidelinesPanel  = AsyncPanel.$extend({
    __init__: function() {
        // Rebind functions
        this.onSubmit = _.bind(this.onSubmit, this);
        this.onLoaded = _.bind(this.onLoaded, this);

        // Render template
        this.el = ich.guidelinesPanel();

        // Bind events
        $('form', this.el).submit(this.onSubmit);

        // Load initial data
        TeamsApiV2.guidelines_get(TEAM_SLUG, this.onLoaded);

        // Constants
        this.SETTING_KEYS = [
            'messages_invite', 'messages_manager', 'messages_admin',
            'guidelines_subtitle', 'guidelines_translate', 'guidelines_review'
        ];
    },

    onSubmit: function(e) {
        e.preventDefault();

        var data = {};
        _.each(this.SETTING_KEYS, function(key) {
            data[key] = $('#id_' + key, this.el).val();
        });

        TeamsApiV2.guidelines_set(TEAM_SLUG, data, this.onLoaded);
    },
    onLoaded: function(data) {
        _.each(data, function(setting) {
            $('#id_' + setting.key, this.el).val(setting.data);
        }, this);
    }
});

// Permissions ----------------------------------------------------
var PermissionsPanel = AsyncPanel.$extend({
    __init__: function() {
        this.onWorkflowStatusChange = _.bind(this.onWorkflowStatusChange, this);
        this.onWorkflowLoaded = _.bind(this.onWorkflowLoaded, this);
        this.showWorkflow = _.bind(this.showWorkflow, this);
        this.hideWorkflow = _.bind(this.hideWorkflow, this);
        this.onLoaded = _.bind(this.onLoaded, this);
        this.onSubmit = _.bind(this.onSubmit, this);
        this.fillFromModel = _.bind(this.fillFromModel, this);

        // Render template
        this.el = ich.permissionsPanel();

        // Bind events
        $('#permissions_workflows_enabled', this.el).change(this.onWorkflowStatusChange);
        $('form.permissions', this.el).submit(this.onSubmit);

        // Load initial data
        this.workflow = null;
        this.team = null;
        TeamsApiV2.team_get(TEAM_SLUG, this.onLoaded);
    },
    onWorkflowStatusChange: function(e) {
        if ($('#permissions_workflows_enabled', this.el).attr('checked')) {
            if (!this.workflow) {
                this.showWorkflow();
            }
        } else {
            this.hideWorkflow();
        }
    },
    onWorkflowLoaded: function(data) {
        this.workflow = new WorkflowItem(new WorkflowModel(data));
        $('.workflow', this.el).html(this.workflow.el);
    },
    showWorkflow: function(e) {
        TeamsApiV2.workflow_get(TEAM_SLUG, null, null, this.onWorkflowLoaded);
    },
    hideWorkflow: function(e) {
        $('.workflow', this.el).html('');
        this.workflow = null;
    },
    onLoaded: function(data) {
        this.team = new TeamModel(data);
        this.fillFromModel();
    },
    onSubmit: function(e) {
        e.preventDefault();

        var data = {
            membership_policy: $('#id_membership_policy', this.el).val(),
            video_policy: $('#id_video_policy', this.el).val(),
            task_assign_policy: $('#id_task_assign_policy', this.el).val(),
            subtitle_policy: $('#id_subtitle_policy', this.el).val(),
            translate_policy: $('#id_translate_policy', this.el).val(),
            workflow_enabled: $('#permissions_workflows_enabled', this.el).attr('checked')
        };

        TeamsApiV2.permissions_set(TEAM_SLUG, data, this.onLoaded);

        this.workflow && this.workflow.onSubmit();
    },
    fillFromModel: function() {
        $('#id_membership_policy', this.el).val(this.team.membership_policy);
        $('#id_video_policy', this.el).val(this.team.video_policy);
        $('#id_task_assign_policy', this.el).val(this.team.task_assign_policy);
        $('#id_subtitle_policy', this.el).val(this.team.subtitle_policy);
        $('#id_translate_policy', this.el).val(this.team.translate_policy);

        if (this.team.workflowEnabled) {
            $('#permissions_workflows_enabled', this.el).attr('checked', 'checked');
        } else {
            $('#permissions_workflows_enabled', this.el).attr('checked', '');
        }

        this.onWorkflowStatusChange();
    }
});

// Main -----------------------------------------------------------------------
var TabMenuItem = Class.$extend({
    __init__: function (data){
        this.el = ich.subMenuItem(data)[0];
        this.buttonEl = $("a", this.el)[0];
        this.klass = data.klass;
        this.panelEl = $(data.painelSelector);
    },
    markActive: function(isActive){
        if (isActive){
            $(this.el).addClass(ACTIVE_CLASS);
        }else{
            $(this.el).removeClass(ACTIVE_CLASS);
        }
    },
    showPanel: function(shows){
        if (shows){
            $(this.panelEl).show();
            if(this.klass){
                return  new this.klass();
            }
        }else{
            $(this.panelEl).hide();
        }
        return null;
    }
});
var TabViewer = Class.$extend({
    __init__: function(buttons, menuContainer, panelContainer){
        this.menuItems = _.map(buttons, function(x){
            var item = new TabMenuItem(x);
            $(menuContainer).append(item.el);
            return item;
        });

        $(menuContainer).click(_.bind(this.onClick, this));
        this.panelContainer = panelContainer;
    },
    openDefault: function(){
        $(this.menuItems[0].buttonEl).trigger("click");
    },
    onClick: function(e){
        e.preventDefault();
        var scope = this;
        if (this.currentItem){
            this.currentItem.showPanel(false);
            this.currentItem.markActive(false);
            if (this.currentKlass){
                if (_.isFunction(this.currentKlass.hide)){
                    this.currentKlass.hide();
                }else{
                    this.currentKlass.el.hide();
                }
            }
        }
        _.each(this.menuItems, function(x){
            if (x.buttonEl == e.target){
                x.markActive(true);
                this.currentKlass = x.showPanel(true);
                if (this.currentKlass){
                    this.panelContainer.append(this.currentKlass.el);
                }
                
                scope.currentItem = x;
            }

            return;
        }, this);
        
    }
});
var ConfirmationDialog = Class.$extend({
    __init__: function(title, body, okText, okCallback, cancelText, cancelCallback){
        this.title = title;
        this.body = body;
        this.okText = okText || "Yeah";;
        this.okCallback = okCallback ;
        this.cancelText = cancelText || "No";
        this.cancelCallback = cancelCallback;
        this.onCancel = _.bind(this.onCancel, this);
        this.onConfirm = _.bind(this.onConfirm, this);
        
        
    },
    _createDom: function(){
        this.el = ich.confirmationDialog(this);
    },
        
    show: function(){
        if(!this.el){
            this._createDom();
            $(".cancel", this.el).click(this.onCancel);
            $(".confirm", this.el).click(this.onConfirm);
        }
        $(this.el).show();
    },
    onCancel: function(e){
        if (e){
            e.preventDefault();
        }
        if (this.cancelCallback()){
            this.cancelCallback();
        }
        this.hide();
    },
    onConfirm: function(e){
        if (e){
            e.preventDefault();
        }
        if (this.okCallback()){
            this.okCallback();
        }
    },
    hide: function(){
        $(this.el).hide();
        $(this.el).remove();
    }


});

function bootstrapTabs(){
    var buttons = [
        {label:"Basic Settings", panelSelector:".panel-basic", klass:BasicPanel},
        {label:"Guidelines and messages", panelSelector:".panel-guidelines", klass:GuidelinesPanel},
        {label:"Permissions", panelSelector:".panel-permissions", klass:PermissionsPanel},
        {label:"Projects", panelSelector:".panel-projects", klass:ProjectPanel},
    ];
    var viewer = new TabViewer(buttons, $(".sub-settings-panel"), $(CONTAINER_SELECTOR));
    viewer.openDefault();
}
bootstrapTabs();
