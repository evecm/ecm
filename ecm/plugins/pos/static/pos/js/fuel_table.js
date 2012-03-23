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
    var table = $('#fuel_table').dataTable( {
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 10, 		/* default display 25 items */
        "bStateSave": true, 		/* table state persistance */
        "iCookieDuration": 60 * 60, /* persistance duration 1 hour */
        "sAjaxSource": AJAX_URL,
        "sDom": 'lprtip', 			/* table layout. see http://www.datatables.net/usage/options */
        "aoColumns": [
            { /* 0 Icon */      "sWidth": "10%", "sClass": "center", "bSortable": false },
            { /* 1 Name */      "sWidth": "30%", "bSortable": false  },
            { /* 2 Quantity */  "sWidth": "15%", "bSortable": false  },
            { /* 3 Cons/Hour */ "sWidth": "15%", "bSortable": false },
            { /* 4 Cons/day */  "sWidth": "15%", "bSortable": false },
            { /* 5 TimeLeft */  "sWidth": "15%", "bSortable": false },
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            fuelTypeID = aData[0];
            fuelTypeName = aData[1];
            fuelImgUrl = 'http://image.eveonline.com/Type/' + fuelTypeID + '_32.png';
            $('td:eq(0)', nRow).html('<img src="' + fuelImgUrl + '" title="' + fuelTypeName + '"/>');
            for (i=2; i<6; i++) {
                $('td:eq(' + i + ')', nRow).addClass('right');
                if (aData[i] == '0' || aData[i] == '0h') {
                    $('td:eq(' + i + ')', nRow).addClass('fuel-warning');
                }
            }
            return nRow;
        },

    });

    /* disable multi column sorting */
    $('#pos_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });

});

