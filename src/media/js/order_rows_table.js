// dataTable setup
$(document).ready(function() {
	$('#order_rows_table').dataTable( {
		"bProcessing": true,
		"bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25,
		"sAjaxSource": AJAX_URL_ROWS,
        "sDom": 'rt',
        "aoColumns": [
            { /* Item */    "sWidth": "50%", "sType": "html", "bSearchable": false , "bSortable": false},
            { /* Quantity */  "sWidth": "15%", "sType": "html", "bSearchable": false, "bSortable": false   },
            { /* Price */       "sWidth": "15%", "sType": "html",    "bSearchable": false, "bSortable": false },
            { /* Remove */    "sWidth": "20%", "sType": "html", "bSearchable": false, "bSortable": false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            return nRow;
        }
    } );
} );
