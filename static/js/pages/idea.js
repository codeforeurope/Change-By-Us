/*--------------------------------------------------------------------
  Copyright (c) 2014 Code for Europe. All rights reserved.
  Licensed under the Affero GNU GPL v3, see LICENSE for more details.
 --------------------------------------------------------------------*/
app_page.features.push(function(app) {
    tc.util.log('Give A Minute: Show Idea');


    app.components.handlers = {
			flag_idea_handler:function(e){
				e.preventDefault();
				tc.jQ.ajax({
					type:"POST",
					url:'/idea/flag',
					data:{
						idea_id:e.target.hash.split(',')[1]
					},
					context:tc.jQ(e.target),
					dataType:"text",
					success: function(data, ts, xhr) {
						if (data == "False") {
							return false;
						}
						this.parent().text('Flagged');
					}
				});
			},
			remove_idea_handler:function(e){
				e.preventDefault();
				var $t;
				$t = tc.jQ(e.target);
				e.data.app.components.modal.show({
					app:e.data.app,
					source_element:tc.jQ('.modal-content.remove-idea'),
					submit:function(){
						tc.jQ.ajax({
							type:'POST',
							url:'/idea/remove',
							data:{
								idea_id: e.target.hash.split(',')[1]
							},
							context:$t,
							dataType:'text',
							success:function(data,ts,xhr){
								var newcount;
								if(data == 'False'){
									return false;
								}
								newcount = (Number(this.parents('.results-ideas').find('.counter.active').text()) - 1);
								this.parents('.results-ideas').find('.counter.active').text(newcount);
								tc.jQ('.sidebar-item.ideas .counter').text(newcount);
								this.parent().parent().parent().animate({
									width:0
								}, 400, 'easeOutCubic', function(e,d){
									tc.jQ(this).hide();
								}).remove();
								tc.jQ('ul.ideas-list li').removeClass('every-third').filter(function(index) {
									return index % 3 == 2;
								}).addClass('every-third');
							}
						});
					}
				});
			},
            like_idea_handler:function(e){
				e.preventDefault();
                ideaId = e.target.hash.split(',')[1];
				tc.jQ.ajax({
					type:"POST",
					url:'/idea/like',
					data:{
						idea_id:ideaId
					},
					context:tc.jQ(e.target),
					dataType:"text",
					success: function(data, ts, xhr) {
						if (data == "False") {
							return false;
						}
                        alert(e.data.app.app_page.messages['liked-idea']);
                        //increase likes
                        elem = this.parent().parent().children(".likers");
                        likes = parseInt(elem.text());
                        elem.text(likes + 1);
						this.text(app_page.messages['unlike-idea']);
                        this.addClass('unlike-idea').removeClass('like-idea');
                        this.unbind();
                        this.bind('click', {app:app}, app.components.handlers.unlike_idea_handler);
                        this.attr('href','#unlikeIdea,'+ideaId);
					}
				});
			},
            unlike_idea_handler:function(e){
				e.preventDefault();
                ideaId = e.target.hash.split(',')[1];
				tc.jQ.ajax({
					type:"POST",
					url:'/idea/unlike',
					data:{
						idea_id:ideaId
					},
					context:tc.jQ(e.target),
					dataType:"text",
					success: function(data, ts, xhr) {
						if (data == "False") {
							return false;
						}
                        alert(app_page.messages['unliked-idea']);
                        //Decrease likes
                        elem = this.parent().parent().children(".likers");
                        likes = parseInt(elem.text());
                        elem.text(likes - 1);
						this.text(app_page.messages['like-idea']);
                        this.unbind();
                        this.bind('click', {app:app}, app.components.handlers.like_idea_handler);
                        this.attr('href','#likeIdea,'+ideaId);
					}
				});
			}
		};

		tc.jQ('a.flag-idea').bind('click', {app:app}, app.components.handlers.flag_idea_handler);
		tc.jQ('a.remove-idea').bind('click', {app:app}, app.components.handlers.remove_idea_handler);
        tc.jQ('a.like-idea').bind('click', {app:app}, app.components.handlers.like_idea_handler);
        tc.jQ('a.unlike-idea').bind('click', {app:app}, app.components.handlers.unlike_idea_handler);


		// random note-card backgrounds
		tc.randomNoteCardBg(tc.jQ('.ideas-list'));


});