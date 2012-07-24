{% load static from staticfiles %}
/*************************
 * "Title Details" table setup *
 *************************/
/**
 * Needs global constants to be defined:
 *      - DIRECTOR_ACCESS_LVL
 *      - COLOR_THRESHOLDS
 **/
COLOR_THRESHOLDS = {{ colorThresholds|safe }};

function titleCompositionRowCallback( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
    // apply color to all access level cells
    accessLvl = aData[2];
    $('td:eq(2)', nRow).addClass("row-" + getAccessColor(accessLvl, COLOR_THRESHOLDS));
    return nRow;
}

function titleLastModifiedRowCallback(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
    if (aData[0]) {
        $('td:eq(0)', nRow).html('<img src="{% static 'ecm/img/plus.png' %}"></img>');
    } else {
        $('td:eq(0)', nRow).html('<img src="{% static 'ecm/img/minus.png' %}"></img>');
    }
    return nRow;
}
        
//$(document).ready(function () {
//	
//	  /* trigger the search when pressing return in the text field */
//    $("#search_form").submit(function(event) {
//        event.preventDefault();
//        $('#players_table').fnFilter($("#search_text").val());
//    });
//
//    /* trigger the search when clicking the "search" button */
//    $("#search_button").click(function() {
//    	$('#players_table').fnFilter($("#search_text").val());
//    });
//
//    /* reset the search when clicking the "reset" button */
//    $("#clear_search").click(function() {
//        $("#search_text").val("");
//        $('#players_table').fnFilter("");
//    });
//
//
//    /* disable multi column sorting */
//    $('#players_table thead th').click(function(event) {
//        if (!$(event.target).hasClass('sorthandle')) {
//            event.shiftKey = false;
//        }
//    });
//    
//});

