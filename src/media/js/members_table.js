/*************************
 * "Members" table setup *
 *************************/
/**
 * Needs three global constants to be defined:
 *      - DIRECTOR_ACCESS_LVL
 *      - COLOR_THRESHOLDS
 *      - AJAX_URL
 **/
$(document).ready(function() {
	  var table = $('#members_table').dataTable( {
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25, /* default display 25 items */
        "bStateSave": true, /* table state persistance */
        "iCookieDuration": 60 * 60, /* persistance duration 1 hour */
        "sCookiePrefix": COOKIE_NAME,
        "sAjaxSource": AJAX_URL,
        "sDom": 'lprtip', /* table layout. see http://www.datatables.net/usage/options */
        "aoColumns": [
            { /* Name */         "sWidth": "20%",   "sType": "html"    },
            { /* Nickname */     "sWidth": "20%",   "sType": "string"  },
            { /* Player */       "sWidth": "15%",   "sType": "html"    },
            { /* Access Level */ "sWidth": "5%",    "sType": "numeric" },
            { /* Corp Date */    "sWidth": "10%",   "sType": "string"  },
            { /* Last Login */   "sWidth": "10%",   "sType": "string"  },
            { /* Location */     "sWidth": "20%",   "sType": "string"  },
            { /* titles -> HIDDEN */ "bVisible": false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
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
    $('#members_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });

} );

