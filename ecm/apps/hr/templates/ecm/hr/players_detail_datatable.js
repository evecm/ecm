/*************************
 * "Player Details" table setup *
 *************************/
/**
 * Needs global constants to be defined:
 *      - DIRECTOR_ACCESS_LVL
 *      - COLOR_THRESHOLDS
 **/
DIRECTOR_ACCESS_LVL = {{ directorAccessLvl }};
COLOR_THRESHOLDS = {{ colorThresholds|safe }};

function playerDetailRowCallback( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
    /* apply color to all access level cells */
    accessLvl = aData[3];
    if (accessLvl == DIRECTOR_ACCESS_LVL) {
        $('td:eq(3)', nRow).html('<b>DIRECTOR</b>');
    }
    $('td:eq(3)', nRow).addClass("row-" + getAccessColor(accessLvl, COLOR_THRESHOLDS));

    /* hide titles column */
    $('td:eq(7)', nRow).hide()

    /* set titles tooltip on each row */
    titles = aData[7]
    if (titles != "") {
        $('td:eq(3)', nRow).attr("title", titles)
        $('td:eq(3)', nRow).cluetip({
            splitTitle: '|',
            dropShadow: false,
            cluetipClass: 'jtip',
            positionBy: 'mouse',
            tracking: true
        });
    }

    return nRow;
}
        
$(document).ready(function () {
	
	  /* trigger the search when pressing return in the text field */
    $("#search_form").submit(function(event) {
        event.preventDefault();
        $('#players_table').fnFilter($("#search_text").val());
    });

    /* trigger the search when clicking the "search" button */
    $("#search_button").click(function() {
    	$('#players_table').fnFilter($("#search_text").val());
    });

    /* reset the search when clicking the "reset" button */
    $("#clear_search").click(function() {
        $("#search_text").val("");
        $('#players_table').fnFilter("");
    });


    /* disable multi column sorting */
    $('#players_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });
    
});

