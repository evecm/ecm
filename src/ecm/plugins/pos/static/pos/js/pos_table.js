/*************************
 * "POS" table setup *
 *************************/
/**
 * Needs three global constants to be defined in the HTML page.
 *      - XXXX DIRECTOR_ACCESS_LVL XXXX
 *      - COLOR_THRESHOLDS
 *      - POSCOLORSTATUS
 *      - AJAX_URL
 **/
$(document).ready(function() {
	  var table = $('#pos_table').dataTable( {
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25, 		/* default display 25 items */
        "bStateSave": true, 		/* table state persistance */
        "iCookieDuration": 60 * 60, /* persistance duration 1 hour */
        "sAjaxSource": AJAX_URL,
        "sDom": 'lprtip', 			/* table layout. see http://www.datatables.net/usage/options */
        "aoColumns": [
            { /* System 0*/       "sWidth": "18%",  "sType": "html"    },
            { /* Type 1*/         "sWidth": "1%",   "sType": "html"    },
            { /* status 3*/       "sWidth": "6%",   "sType": "string"  },
            { /* Time 2*/ 	      "sWidth": "7%",  "sType": "string"  },
            { /* EU 4*/           "sWidth": "4%",   "sType": "string"  },
            { /* O2 5*/           "sWidth": "4%",   "sType": "string"  },
            { /* MP 6*/           "sWidth": "4%",   "sType": "string"  },
            { /* Coo 7*/          "sWidth": "4%",   "sType": "string"  },
            { /* Rob 8*/          "sWidth": "4%",   "sType": "string"  },
            { /* LO 9*/           "sWidth": "4%",   "sType": "string"  },
            { /* HW 10*/          "sWidth": "4%",   "sType": "string"  },
            { /* ISOT 11*/        "sWidth": "4%",   "sType": "string"  },
            { /* Stront 12*/      "sWidth": "3%",   "sType": "string"  },
            { /* ISOTy -> HIDDEN */ "bVisible": false }
            //{ /* ISOTy -> HIDDEN */"sWidth": "4%",   "sType": "string"  },
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
		  	$('td:eq(1)', nRow).html('<img src="../m/img/'+aData[13]+'.png" title="'+aData[1]+'-'+aData[13]+'">')
		  	//$('td:eq(2)', nRow).addClass("row-" + getAccessColor(aData[2], COLOR_THRESHOLDS));
		  	$('td:eq(2)', nRow).html('<span valign="middle"><img src="../m/img/lens'+POSCOLORSTATUS[aData[2]]+'.png" title="'+aData[2]+'" style="vertical-align: middle;">'+aData[2]+'</span>')
		  	$('td:eq(3)', nRow).html('<span valign="middle"><img src="../m/img/lensGreen.png" title="'+aData[3]+'" style="vertical-align: middle;">'+aData[3].split(' ')[4]+'</span>')
            //$('td:eq(13)', nRow).hide()
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
    $('#pos_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });
    /* Button to select quatities values */
    $("#Quantities_button").click(function() {
        //$("#search_text").val("");
        table.fnFilter("Qtes");
    });
    /* reset the search when clicking the "reset" button */
    $("#Days_button").click(function() {
        //$("#search_text").val("");
        table.fnFilter("Days");
    });
    /* reset the search when clicking the "reset" button */
    $("#Hours_button").click(function() {
        //$("#search_text").val("");
        table.fnFilter("Hours");
    });
});

