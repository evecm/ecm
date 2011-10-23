$('#title_compo_diff_table thead th').click(function(event) {
    if (!$(event.target).hasClass('sorthandle')) {
        event.shiftKey = false;
    }
});

//title_compo_diff_table dataTable setup
$(document).ready(function() {
	$('#title_changes_table').dataTable( {
	    "sPaginationType": "full_numbers",
		"bProcessing": true,
		"bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25,
        "bStateSave": true,
		"sAjaxSource": "/hr/titles/changes/data/",
        "sDom": 'lprtip',
        "aoColumns": [
            { "sTitle": "Change",       "sWidth": "5%", "sType": "html"  , 	"bSortable" : false},
            { "sTitle": "Title",    	"sWidth": "30%", "sType": "html"  , 	"bSortable" : false},
            { "sTitle": "Role",    		"sWidth": "50%", "sType": "html"  , 	"bSortable" : false},
            { "sTitle": "Modification Date", "sWidth": "15%", "sType": "string"  , 	"bSortable" : false}
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            if (aData[0] == "true") {
                $('td:eq(0)', nRow).html('<img src="/s/ecm/img/plus.png"></img>');
            } else {
                $('td:eq(0)', nRow).html('<img src="/s/ecm/img/minus.png"></img>');
            }
            return nRow;
		}
    } );

} );