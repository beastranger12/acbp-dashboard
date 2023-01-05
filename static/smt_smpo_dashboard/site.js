/*
 * Site specific JavaScript for the SMT-SMPO-Dashboard website.
 */
/* Function which returns value of the global CSRF token. */
function get_csrf_token_value() {
    return $('#global-csrftoken > [name=csrfmiddlewaretoken]').attr('value');
}

/* Function to set active navbar button based on text. */
function set_active_nav_button_by_text(text) {
    $('#global-navbar-left > li').each(function(index) {
        $(this).removeAttr('class');
    });
    $('#global-navbar-left > li > a')
        .filter(function(index) { return $(this).text() === text; })
        .parent()
        .addClass('active');
}

/* Document ready handler */
$(function() {
    /*
     * Initialize the global search text box. The search box will utilize
     * the bootstrap typeahead plugin. See
     * https://github.com/bassjobsen/Bootstrap-3-Typeahead for docs on using
     * the plugin.
     */
    /*
     * To save on the amount of requests to be made to the site's search
     * handler, make just one request and save the results.
     */
    $('#global-search').data('search-source', null);
    $('#global-search').typeahead({
        source: function(query, process) {
            if ($('#global-search').data('search-source') == null) {
                return $.ajax({
                    url: '/search',
                    type: 'POST',
                    beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", get_csrf_token_value());
                    }
                }).done(function(data) {
                    $('#global-search').data('search-source', data);
                    return process($('#global-search').data('search-source')["names"]);
                });
            } else {
                process($('#global-search').data('search-source')["names"]);
            }
        },
        updater: function(name) {
            window.open("/" + $('#global-search').data('search-source').uriLookup[name].uri, "_self");
        },
        highlighter: function(item) {
            /* Highlight Bold Search Text */
            var query = this.query.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, '\\$&');
            var title = item.replace(new RegExp('(' + query + ')', 'ig'), function($1, match) {
                return $('<strong></strong>').text(match).wrap('<p></p>').parent().html();
            });
            return $('<div></div>').html(title).wrap('<p></p>').parent().html();
        }
    });

    /* On resize, auto-adjust top padding to navbar new height. */
    $(window).resize(function() {
        $('body').css('padding-top', $('body nav.navbar-fixed-top').height());
    });
    $(window).trigger('resize');
});
