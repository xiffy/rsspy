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
	});
});

