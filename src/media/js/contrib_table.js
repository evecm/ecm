/************************************
 * "Accounting journal" table setup *
 ************************************/
$(document).ready(function() {
	  var table = $('#contrib_table').dataTable( {
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25, /* default display 25 items */
        "bStateSave": true, /* table state persistance */
        "iCookieDuration": 60 * 60, /* persistance duration 1 hour */
        "sAjaxSource": "/accounting/contributions/data",
        "sDom": 'lprtip', /* table layout. see http://www.datatables.net/usage/options */
        "aaSorting": [[1,'desc']],
        "aoColumns": [
            { /* Member */       "sWidth": "50%",   "sType": "html" },
            { /* Contributions */     "sWidth": "50%",   "sType": "html" , "sClass" : "right"   }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            $('td:eq(1)', nRow).addClass('credit');
            return nRow;
        },
        
        /* this function will be called when the table has to query data to be displayed */
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            /* Add some extra variables to the url */
            aoData.push( { 
                "name": "since", 
                "value": $("#since_selector option:selected").val()
            } );
            
            $.getJSON( sSource, aoData, function (json) { 
                fnCallback(json)
            } );
        },
        
    });
	
    $("#since_selector").change(function () {
        table.fnDraw();
    });
    
    /* disable multi column sorting */
    $('#journal_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });
    
} );

