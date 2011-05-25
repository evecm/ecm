/************************************
 * "Accounting journal" table setup *
 ************************************/
$(document).ready(function() {
	  var table = $('#journal_table').dataTable( {
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25, /* default display 25 items */
        "bStateSave": true, /* table state persistance */
        "iCookieDuration": 60 * 60, /* persistance duration 1 hour */
        "sAjaxSource": "/accounting/journal/data",
        "sDom": 'lprtip', /* table layout. see http://www.datatables.net/usage/options */
        "aoColumns": [
            { /* Date */       "sWidth": "14%",   "sType": "string" },
            { /* Wallet */     "sWidth": "15%",   "sType": "html"    },
            { /* Operation */  "sWidth": "10%",   "sType": "string",    "bSortable": false },
            { /* From */       "sWidth": "15%",    "sType": "html",  "bSortable": false },
            { /* To */         "sWidth": "15%",   "sType": "html",  "bSortable": false  },
            { /* Amount */     "sWidth": "15%",   "sType": "string" , "sClass" : "right" },
            { /* Balance */    "sWidth": "15%",   "sType": "string",  "bSortable": false,  "sClass" : "right" },
            { /* reason -> HIDDEN */ "bVisible": false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            if (aData[5].charAt(0) == '+') {
                $('td:eq(5)', nRow).addClass('credit');
            } else {
                $('td:eq(5)', nRow).addClass('debit');
            }
            /* hide reason column */
            $('td:eq(7)', nRow).hide()
            
            /* set titles tooltip on each row */
            reason = aData[7]
            if (reason != "") {
                $('td:eq(5)', nRow).attr("title", reason)
                $('td:eq(5)', nRow).cluetip({
                    splitTitle: '|',
                    dropShadow: false, 
                    cluetipClass: 'jtip',
                    positionBy: 'mouse',
                    tracking: true
                });
            }
            
            return nRow;
        },
        
        /* this function will be called when the table has to query data to be displayed */
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            /* Add some extra variables to the url */
            aoData.push( { 
                "name": "walletID", 
                "value": $("#wallet_selector option:selected").val()
            },{ 
                "name": "entryTypeID", 
                "value": $("#type_selector option:selected").val()
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

    $("#wallet_selector").change(function () {
        table.fnDraw();
    });
    
    $("#type_selector").change(function () {
        table.fnDraw();
    });
    
    /* disable multi column sorting */
    $('#journal_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });
    
} );

