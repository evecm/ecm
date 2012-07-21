/*************************
 * Search form setup *
 *************************/
/**
 * Needs three global constants to be defined:
 *      - a table, some where on the page.
 *      - dont know what else
 **/

        
$(document).ready(function () {
	

    /* trigger the search when pressing return in the text field */
    $("#search_form").on('submit', function(event) {
        event.preventDefault();
        $('table').dataTable().fnFilter($("#search_text").val());
    });

    /* reset the search when clicking the "reset" button */
    $("#clear_search").on('click', function() {
        $("#search_text").val("");
        $('table').dataTable().fnFilter("");
    });

    /* disable multi column sorting */
    $('table thead th').on('click', function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });
});

