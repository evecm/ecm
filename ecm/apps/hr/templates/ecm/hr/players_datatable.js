/*************************
 * "Players" table setup *
 *************************/

function playersRowCallback( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
    /* if the player has no roles, display him/her in red */
    var group_count = aData[4];
    if (group_count == 0) {
        $(nRow).addClass("row-red");
    }
    var admin = aData[1];
    if (admin) {
        $('td:eq(1)', nRow).html('<img src="/static/admin/img/icon-yes.gif" alt="True">');
    } else {
        $('td:eq(1)', nRow).html('<img src="/static/admin/img/icon-no.gif" alt="False">');
    }
    return nRow;
}
        
$(document).ready(function () {
	
    /* trigger the search when pressing return in the text field */
    $("#search_form").submit(function(event) {
        event.preventDefault();
        $("#players_table").fnFilter($("#search_text").val());
    });

    /* trigger the search when clicking the "search" button */
    $("#search_button").click(function() {
    	$("#players_table").fnFilter($("#search_text").val());
    });

    /* reset the search when clicking the "reset" button */
    $("#clear_search").click(function() {
        $("#search_text").val("");
        $("#players_table").fnFilter("");
    });

    /* disable multi column sorting */
    $('#players_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });
    
});

