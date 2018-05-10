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
		console.log(entryid);
		$.post('/bookmark/'+entryid);
		e.preventDefault();
	});
});

