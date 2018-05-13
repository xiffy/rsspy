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

});

