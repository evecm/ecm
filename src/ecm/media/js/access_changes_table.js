// title_compo_diff_table dataTable setup
$(document).ready(function() {
	$('#access_changes_table').dataTable( {
		"sPaginationType": "full_numbers",
		"bProcessing": true,
		"bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25,
        "bStateSave": true,
        "iCookieDuration": 60*60*24,
		"sAjaxSource": "/members/access_changes/data",
        "sDom": 'lprtip',
        "aoColumns": [
			{ "sTitle": "Change",		"sWidth": "10%", "sType": "html" ,  "bSortable": false },
			{ "sTitle": "Member",		"sWidth": "30%", "sType": "html" ,  "bSortable": false },
			{ "sTitle": "Title/Role",   "sWidth": "40%", "sType": "html" ,  "bSortable": false },
			{ "sTitle": "Date",         "sWidth": "20%", "sType": "string", "bSortable": false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            if (aData[0] == "true") {
                $('td:eq(0)', nRow).html('<img src="/static/img/plus.png"></img>');
            } else {
                $('td:eq(0)', nRow).html('<img src="/static/img/minus.png"></img>');
            }
            return nRow;
		}
    } );

} );