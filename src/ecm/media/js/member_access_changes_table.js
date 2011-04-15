/****************************************************
 * "Security access changes per member" table setup *
 ****************************************************/

$(document).ready(function() {
    $('#access_changes_table').dataTable( {
    		"sPaginationType": "full_numbers",
    		"bProcessing": true,
    		"bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 10,
        "bStateSave": true,
        "iCookieDuration": 60*60*24,
        "sAjaxSource": "/members/" + member_id + "/access_changes_data",
        "sDom": 'lprtip',
        "aoColumns": [
      			{ "sTitle": "Change",			 "sWidth": "15%", "sType": "html" ,  "bSortable": false },
      			{ "sTitle": "Title/Role",  "sWidth": "60%", "sType": "html" ,  "bSortable": false },
      			{ "sTitle": "Date",        "sWidth": "25%", "sType": "string", "bSortable": false }
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