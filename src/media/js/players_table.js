/*************************
 * "Players" table setup *
 *************************/
/**
 * Needs three global constants to be defined:
 *      - DIRECTOR_ACCESS_LVL
 *      - COLOR_THRESHOLDS
 *      - AJAX_URL
 **/
$(document).ready(function() {
      var table = $('#players_table').dataTable( {
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25, /* default display 25 items */
        "bStateSave": true, /* table state persistance */
        "iCookieDuration": 60 * 60, /* persistance duration 1 hour */
        "sAjaxSource": "/players/data",
        "sDom": 'lprtip', /* table layout. see http://www.datatables.net/usage/options */
        "aoColumns": [
            { /* Username */    "sWidth": "30%",   "sType": "html"    },
            { /* Char count */  "sWidth": "20%",   "sType": "string",   "bSortable": false  },
            { /* Group count */ "sWidth": "20%",   "sType": "string",   "bSortable": false  },
            { /* Joined date */ "sWidth": "30%",   "sType": "string"  }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            /* if the player has no roles display him/her in red */
            var group_count = aData[2];
            if (group_count == 0) {
                $(nRow).addClass("row-red");
            }          
            return nRow;
        },
        /* the search field being outside the table object, we need to save its status
         * explicitly here in order to restore it with the rest */
        "fnStateSaveCallback": function (oSettings, sValue) {
            var sFilter = $("#search_text").val();
            sValue = sValue.replace( /"sFilter":".*?"/, '"sFilter":"' + sFilter + '"' );
            return sValue;
        },
        /* restore the search field content */
        "fnStateLoadCallback": function (oSettings, oData) {
            $("#search_text").val(oData.sFilter);
            return true;
        }
    });
    
    /* trigger the search when pressing return in the text field */
    $("#search_form").submit(function(event) {
        event.preventDefault();
        table.fnFilter($("#search_text").val());
    });

    /* trigger the search when clicking the "search" button */
    $("#search_button").click(function() {
        table.fnFilter($("#search_text").val());
    });

    /* reset the search when clicking the "reset" button */
    $("#clear_search").click(function() {
        $("#search_text").val("");
        table.fnFilter("");
    });


    /* disable multi column sorting */
    $('#players_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });
    
} );
