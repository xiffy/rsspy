$( document ).ready(function() {
	$('.menudrop').click( function(e) {
		$('.slider').toggle('slide', 150);
		e.preventDefault();
	});

	$('a.hide-feeds').click( function(e) {
		that = this
    groupid = $(this).data('groupid');
    $('.group-feeds-feed'+groupid).each( function() {
    	$(this).toggle();
    });
    if ($(that).hasClass('closed')) {
    	$(that).removeClass('closed')
    	$(that).html('<span class="simple-svg" data-icon="mdi-chevron-up"></span>');
    } else {
    	$(that).addClass('closed')
    	$(that).html('<span class="simple-svg" data-icon="mdi-chevron-down"></span>');
    }
	});

	$('.add_bookmark').click( function(e) {
		that = this
		entryid = $(that).data('entryid');
		$.post('/bookmark/'+entryid, function(data) {
			if (data.bookmarkid) {
				$(that).removeClass('inactive add_bookmark');
				$(that).addClass('active remove_bookmark');
				$(that).data('bookmarkid', data.bookmarkid);
				$(that).html('<span class="simple-svg" data-icon="iwwa-star" data-inline="false"></span>');
			}
		});
		e.preventDefault();
	});

	$('.remove_bookmark').click( function(e) {
		that = this
		bookmarkid = $(that).data('bookmarkid');
		$.ajax({
			url: '/bookmark/'+bookmarkid,
			type: 'DELETE'
		});
		$(that).removeClass('active remove_bookmark');
		$(that).addClass('inactive add_bookmark');
		$(that).html('<span class="simple-svg" data-icon="iwwa-star-o" data-inline="false"></span>');
		e.preventDefault();
	});

	$('.disabled').hide();

	$('.group_add_feed').click( function(e) {
		groupid = $(this).data('groupid');
		$.get('/widget/feedlist?groupid='+groupid,
		    function(data) {
		    	$('.forms').html(data)
		    	$('.forms').toggle('slide', 150);
		    }
		);
		e.preventDefault();
	});

	$('.forms').on('click', '.cancel', function(e) {
		$('.forms').toggle('slide', 150);
		e.preventDefault();
	});

	$('.forms').on('click', '.url_form .submit', function(e) {
		$.post('/feed/add', {url: $('#form_url').val()},
		        function(data) {
		        	$('.forms').toggle('slide', 150);
		        	if (data.id) {
		        		window.location.href = '/feed/'+data.id
		        	}
		        }
		);
		e.preventDefault();
	});

	$('.group_form').on('click', '.add_group_add', function(e) {
		$.post('/group/add',  {description: $('#description').val(),
		                     aggragation: $('#aggragation').is(":checked"),
		                     frequency: $('#frequency').val()},
		      function(data) {
		      	console.log(data)
		      }
	  );
	  e.preventDefault();
	});

	$('.top_add_feed').click( function(e) {
		feed_form = '<div class="widget entry url_form"><h1>feed url:</h1><form> <input name="url" id="form_url" size="40" type="text" class="form_feed"/></p> <input type="submit" class="form_button submit" value="Add"> <input type="submit" class="cancel form_button" value="Cancel" ></form></div>';
		$('.forms').html(feed_form);
		$('.slider').toggle('slide', 150);
		$('.forms').toggle('slide', 150);
		e.preventDefault();
	});

	$("iframe[src*='https://www.youtube.com'], iframe[src*='https://player.vimeo.com']").each(function() {
		var $el = $(this);
		ratio = this.height / this.width;
		console.log(ratio);
		$(this).removeAttr('height')
		       .removeAttr('width');
		var newWidth = $(this).parent().parent().width();
		console.log(newWidth);
		$el.width(newWidth)
   	   .height(newWidth * ratio);
	});

});

