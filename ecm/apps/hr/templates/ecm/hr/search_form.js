/*************************
 * Search form setup *
 *************************/
/**
 * Needs three global constants to be defined:
 *      - a table to search within with css-class "searchable_table" some where on the page.
 *      WARNING: EVERY TABLE WITH THIS ATTRIBUTE IS LINKED TO THE _SAME_ SEARCH
 **/

        
$(document).ready(function () {
	

    /* trigger the search when pressing return in the text field */
    $("#search_form").on('submit', function(event) {
        event.preventDefault();
        $('.searchable_table').dataTable().fnFilter($("#search_text").val());
    });

    /* trigger the search when clicking the "search" button */
    $("#search_button").click(function() {
    	$('.searchable_table').fnFilter($("#search_text").val());
    });

    /* reset the search when clicking the "reset" button */
    $("#clear_search").on('click', function() {
        $("#search_text").val("");
        $('.searchable_table').dataTable().fnFilter("");
    });

    /* disable multi column sorting */
    $('.searchable_table thead th').on('click', function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });
});

