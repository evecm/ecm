/*************************
 * "POS" table setup *
 *************************/
/**
 * Needs 4 global constants to be defined in the HTML page.
 *      - POS_CSS_STATUS
 *      - POS_TEXT_STATUS
 *      - AJAX_URL
 *      - DISPLAY_MODE
 **/
$(document).ready(function() {
    updateButtons();
    var table = $('#pos_table').dataTable( {
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 10, 		/* default display 10 items */
        "bStateSave": true, 		/* table state persistance */
        "iCookieDuration": 60 * 60, /* persistance duration 1 hour */
        "sAjaxSource": AJAX_URL,
        "sDom": 'lprtip', 			/* table layout. see http://www.datatables.net/usage/options */
        "aoColumns": [
            { /* 0 Location */ "sWidth": "12%", "sType": "html" },
            { /* 1 Type */     "sWidth": "1%",  "sType": "html", "sClass": "center" },
            { /* 2 status */   "sWidth": "1%",  "sType": "html" },
            { /* 3 Time */ 	   "sWidth": "2%",  "sType": "string" },
            { /* 4 EU */       "sWidth": "4%",  "sType": "string", "bSortable": false },
            { /* 5 O2 */       "sWidth": "4%",  "sType": "string", "bSortable": false },
            { /* 6 MP */       "sWidth": "4%",  "sType": "string", "bSortable": false },
            { /* 7 Coo */      "sWidth": "4%",  "sType": "string", "bSortable": false },
            { /* 8 Rob */      "sWidth": "4%",  "sType": "string", "bSortable": false },
            { /* 9 LO */       "sWidth": "4%",  "sType": "string", "bSortable": false },
            { /* 10 HW */      "sWidth": "4%",  "sType": "string", "bSortable": false },
            { /* 11 Isot */    "sWidth": "4%",  "sType": "string", "bSortable": false },
            { /* 12 Stront */  "sWidth": "4%",  "sType": "string", "bSortable": false },
            { /* 13 Name HIDDEN */  "bVisible": false, "bSortable": false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            posTypeID = aData[1];
            posImgUrl = 'http://image.eveonline.com/Type/' + posTypeID + '_32.png';
            $('td:eq(1)', nRow).html('<img src="' + posImgUrl + '" title="' + aData[13] + '"/>');

            posState = aData[2];
            $('td:eq(2)', nRow).addClass(POS_CSS_STATUS[posState]);
            $('td:eq(2)', nRow).attr('title', POS_TEXT_STATUS[posState]);
            $('td:eq(2)', nRow).html('');

            for (var i=4; i<13; i++) {
                $('td:eq(' + i + ')', nRow).addClass('right');
                if (aData[i] == '0' || aData[i] == '0h') {
                    $('td:eq(' + i + ')', nRow).addClass('fuel-warning');
                }
            }

            $('td:eq(13)', nRow).hide();
            return nRow;
        },

        /* this function will be called when the table has to query data to be displayed */
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            /* Add some extra variables to the url */
            aoData.push( {
                "name": "displayMode",
                "value": DISPLAY_MODE
            } );
            $.getJSON( sSource, aoData, function (json) {
                fnCallback(json)
            } );
        },

        /* the search field being outside the table object, we need to save its status
         * explicitly here in order to restore it with the rest */
        "fnStateSaveCallback": function (oSettings, sValue) {
            var sFilter = $("#search_text").val();
            sValue = sValue.replace( /"sFilter":".*?"/, '"sFilter":"' + sFilter + '"' );
            sValue += ', "displayMode": "' + DISPLAY_MODE + '"';
            return sValue;
        },
        /* restore the search field content */
        "fnStateLoadCallback": function (oSettings, oData) {
            $("#search_text").val(oData.sFilter);
            DISPLAY_MODE = oData.displayMode;
            updateButtons();
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
    $('#pos_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });

    /* Button to select quatities values */
    $("#quantities_button").click(function() {
        if (DISPLAY_MODE != 'quantities') {
            DISPLAY_MODE = 'quantities';
            updateButtons();
            table.fnDraw();
        }
    });
    $("#days_button").click(function() {
        if (DISPLAY_MODE != 'days') {
            DISPLAY_MODE = 'days';
            updateButtons();
            table.fnDraw();
        }
    });
    $("#hours_button").click(function() {
        if (DISPLAY_MODE != 'hours') {
            DISPLAY_MODE = 'hours';
            updateButtons();
            table.fnDraw();
        }
    });
});


function updateButtons() {
    if (DISPLAY_MODE == 'quantities') {
        $("#quantities_button").addClass('selected');
        $("#days_button").removeClass('selected');
        $("#hours_button").removeClass('selected');
    } else if (DISPLAY_MODE == 'days') {
        $("#quantities_button").removeClass('selected');
        $("#days_button").addClass('selected');
        $("#hours_button").removeClass('selected');
    } else if (DISPLAY_MODE == 'hours') {
        $("#quantities_button").removeClass('selected');
        $("#days_button").removeClass('selected');
        $("#hours_button").addClass('selected');
    }
}
