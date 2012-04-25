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
    var table = $('#members_table').dataTable($.extend(true, {}, DATATABLE_DEFAULTS, {
        sCookiePrefix: COOKIE_NAME,
        sAjaxSource: AJAX_URL,
        ships: '',
        aoColumns: [
            { /* Name */         sWidth: "15%",   sType: "html"    },
            { /* Nickname */     sWidth: "15%",   sType: "string"  },
            { /* Player */       sWidth: "15%",   sType: "html"    },
            { /* Access Level */ sWidth: "5%",    sType: "numeric" },
            { /* Corp Date */    sWidth: "10%",   sType: "string"  },
            { /* Last Login */   sWidth: "10%",   sType: "string"  },
            { /* Location */     sWidth: "15%",   sType: "string"  },
            { /* Ship */         sWidth: "15%",   sType: "string"  },
            { /* titles -> HIDDEN */ bVisible: false }
        ],
        fnRowCallback: function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            /* apply color to all access level cells */
            accessLvl = aData[3];
            if (accessLvl == DIRECTOR_ACCESS_LVL) {
                $('td:eq(3)', nRow).html('<b>DIRECTOR</b>');
            }
            $('td:eq(3)', nRow).addClass("row-" + getAccessColor(accessLvl, COLOR_THRESHOLDS));

            /* hide titles column */
            $('td:eq(8)', nRow).hide()

            /* set titles tooltip on each row */
            titles = aData[8]
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
    }));

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

