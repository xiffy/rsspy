$( document ).ready(function() {
	$('.menudrop').on('click', function() {
		$('.slider').toggle('slide', 150);
	});

	$('a.hide-feeds').click( function() {
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
});

