var tc = tc || {};
tc.gam = tc.gam || {};
tc.gam.project_widgets = tc.gam.project_widgets || {};

tc.gam.project_widgets.needs = function(options) {
    tc.util.log('project.needs');
    var dom = options.dom, merlin;
    
    /**
     * Function: isProjectMember
     * Is the user a member of this project?
     * TODO: find a common place for this to live.
     */
    var isProjectMember = function() {
        return ( 
            (options.project_user.is_member) || 
            (options.project_user.is_project_admin) || 
            (options.user && options.user.is_admin) ||
            (options.user && options.user.is_leader) 
        );
    };
    
    /**
     * Function: volunteer
     * The user can volunteer for a specific need.
     */
    var volunteer = function(need, message) {
        console.log('User', options.user, 'has volunteered for', need, 'with message', message);
    };
    
    /**
     * Function: initMerlin
     * Initialize the merlin object for validation of the modal dialog.
     */
    var initMerlin = function(need) {
        var merlin;
        
        //Please note that this is very tricky due to the fact that the 
        //content of the modal is actually being cloned by the modal widget.
        //This means that there are duplicate elements in the DOM, even
        //ids. This means you should be very specific and careful with your
        //selectors. Also, Pretty Checkboxes rely on label[for] input[id]
        //matching. You will have issues if you have duplicates of these.
        //Yes, this is from experience. =)

        //Make the Pretty Checkbox elements relative to the #modal have
        //ids that you unique from the template.
        tc.jQ('#modal .volunteer-agree-section input').attr('id', 'unique-volunteer-agree');
        tc.jQ('#modal .volunteer-agree-section label').attr('for', 'unique-volunteer-agree');
        tc.jQ('#modal input[type=checkbox]').prettyCheckboxes();
        
        //We are using merlin only for the built-in validation in this case.
        
        merlin =  new tc.merlin(options.app, {
            name:'volunteer',
            dom:tc.jQ('#modal .user-volunteer-modal.merlin'),
            next_button:tc.jQ('#modal .user-volunteer-modal.merlin a.send'),
            first_step:'volunteer_agree',
            use_hashchange:false,
            steps: {
                'volunteer_agree': {
                    selector:'.step.user-volunteer',
                    //These selectors are within the context of the "merlin" root element
                    inputs:{
                        //This is the message being sent to the organizer.
                        'volunteer_agree_msg': {
                            selector:'.volunteer-agree-msg',
                            validators:['max-300'],
                            hint:'',
                            counter: {
                                // selector: jQuery selectory for element to fill with counter.
                                selector: '.charlimit.charlimit-volunteer-agree-msg',
                                // limit: Character limit for counter.  This should be in align
                                // with a validator of max-X.
                                limit: 300
                            }
                        },
                        //This is the checkbox to agree to sign up.
                        'volunteer_agree':{
                            selector:'input.volunteer-agree',
                            validators:['required']
                        }
                    },
                    init:function(merlin, dom) {
                        console.log('^^^^^^^^^^^^^^^^^^^^^^^', merlin, dom);
                        
                        merlin.options.next_button.click(function(event) {
                            var $this = tc.jQ(this),
                                message = merlin.options.steps.volunteer_agree.inputs.volunteer_agree_msg.dom.val();
                                
                            if (!$this.hasClass('disabled')) {
                                volunteer(need, message);
                            } else {
                                console.log('nottttttttttttt sending');
                            }
                        });
                    }
                }
            }
        });
        
        merlin.show_step('volunteer_agree');
    };
    
    /**
     * Function: getNeedDetails
     * Fetch the detail for a given need_id
     */
    var getNeedDetails = function(need_id, callback) {
        tc.jQ.ajax({
            url:'/rest/v1/needs/' + need_id + '/',
            dataType:'json',
            success:function(need_details, ts, xhr) {
                if (callback) {
                    callback(need_details);
                }
            }
        });
    };
    
    /**
     * Function: showModal
     * Show the volunteer modal to the user
     */
    var showModal = function(need) {
        //use ICanHaz to fill in the modal content template
        var $needDetailsContent = tc.jQ('.modal-content .volunteer-agree-section .volunteer-agree-label'),
            h = ich.add_vol_need_tmpl({ 
                need_request: need.request,
                need_datetime: need.datetime,
                need_reason: need.reason,
                has_reason: function() { if (need.reason) return true; else return false; },
                has_datetime: function() { if (need.datetime) return true; else return false; }
            });

        $needDetailsContent.html(h);
        
        //NOTE: the source_element gets cloned here, so be careful
        //binding events!
        options.app.components.modal.show({
            app:options.app,
            source_element:tc.jQ('.template-content.user-volunteer-modal')
        });
        
        initMerlin(need);
    };
    
    /**
     * Function: bindEvents
     * Bind events for this widget
     */
    var bindEvents = function() {        
        tc.jQ(tc).bind('show-project-widget', function(event, widgetName) {
            if (options.name === widgetName) {
                tc.util.log('&&& showing ' + options.name);
                dom.show();
            } else {
                tc.util.log('&&& hiding ' + options.name);
                dom.hide();
            }
        });
        
        tc.jQ('.help-link').click(function(event) {
            event.preventDefault();
            var need_id = tc.jQ(this).parents('li.need').attr('data-id');
            
            if (isProjectMember()) {
                getNeedDetails(need_id, showModal);
            } else {
                options.app.components.modal.show({
                    app:options.app,
                    source_element:tc.jQ('.modal-content.join-no-user')
                });
            }
        });
    };
    
    bindEvents();
};