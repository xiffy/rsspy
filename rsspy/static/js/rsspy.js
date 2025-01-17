$(document).ready(function () {
    $('.menudrop').click(function (e) {
        $('.slider').toggle('slide', {direction: "right"}, 150);
        e.preventDefault();
    });

    $('a.hide-feeds').click(function (e) {
        let that = this
        let groupid = $(this).data('groupid');
        $('.group-feeds-feed' + groupid).each(function () {
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

    $('.toggle_bookmark').click(function (e) {
        let that = this
        let entryid = $(that).data('entryid');
        let state = $(that).data('state');
        if (state === 'inactive') {
            $.post('/bookmark/' + entryid, function (data) {
                if (data.bookmarkid) {
                    $(that).removeClass('inactive add_bookmark');
                    $(that).addClass('active remove_bookmark');
                    $(that).data('bookmarkid', data.bookmarkid);
                    $(that).data('state', 'active')
                    $(that).html('<iconify-icon class="_svg" icon="material-symbols:star" inline="true" width="24"></iconify-icon>');
                }
            });
        } else {
            let bookmarkid = $(that).data('bookmarkid')
            $.ajax({
                url: '/bookmark/' + bookmarkid,
                type: 'DELETE'
            });
            $(that).removeClass('active remove_bookmark');
            $(that).addClass('inactive add_bookmark');
            $(that).html('<iconify-icon class="_svg" icon="ic:twotone-star-outline" width="24"></iconify-icon>');
            $(that).data('state', 'inactive')
        }
        e.preventDefault();
    });

    $('.disabled').hide();

    $('.group_add_feed').click(function (e) {
        let groupid = $(this).data('groupid');
        $.get('/widget/feedlist?groupid=' + groupid,
            function (data) {
                $('.forms').html(data)
                $('.forms').toggle('slide', 150);
            }
        );
        e.preventDefault();
    });

    $('.forms').on('click', '.cancel', function (e) {
        $('.forms').toggle('slide', 150);
        e.preventDefault();
    });

    $('.forms').on('click', '.url_form .submit', function (e) {
        $.post('/feed/add', {url: $('#form_url').val()},
            function (data) {
                $('.forms').toggle('slide', 150);
                if (data.id) {
                    window.location.href = '/feed/' + data.id
                }
            }
        );
        e.preventDefault();
    });

    $('.group_form').on('click', '.add_group_add', function (e) {
        $.post('/group/add', {
                description: $('#description').val(),
                aggragation: $('#aggragation').is(":checked"),
                frequency: $('#frequency').val()
            },
            function (data) {
                console.log(data)
            }
        );
        e.preventDefault();
    });

    $('.top_add_feed').click(function (e) {
        feed_form = '<div class="widget entry url_form"><h1>feed url:</h1><form> <input name="url" id="form_url" size="40" type="text" class="form_feed"/></p> <input type="submit" class="form_button submit" value="Add"> <input type="submit" class="cancel form_button" value="Cancel" ></form></div>';
        $('.forms').html(feed_form);
        $('.slider').toggle('slide', 150);
        $('.forms').toggle('slide', 150);
        e.preventDefault();
    });

    $("iframe[src*='https://www.youtube.com'], \
	   iframe[src*='https://player.vimeo.com/video'],  \
	   iframe[src*='https://www.kickstarter.com']").each(
        function () {
            var $el = $(this);
            ratio = this.height / this.width;
            $(this).removeAttr('height')
                .removeAttr('width');
            var newWidth = $(this).parent().parent().width();
            $el.width(newWidth)
                .height(newWidth * ratio);
        });

});

