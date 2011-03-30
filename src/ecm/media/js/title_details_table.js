// disable multi column sorting
$('#title_composition_table thead th').click(function(event) {
    if (!$(event.target).hasClass('sorthandle')) {
        event.shiftKey = false;
    }
});

$('#title_compo_diff_table thead th').click(function(event) {
    if (!$(event.target).hasClass('sorthandle')) {
        event.shiftKey = false;
    }
});

// title_composition_table dataTable setup
$(document).ready(function() {
	$('#title_composition_table').dataTable( {
		"bProcessing": true,
		"bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 10,
        "bStateSave": true,
        "iCookieDuration": 60*60*24,
		"sAjaxSource": "/titles/" + title_id + "/composition_data",
        "sDom": 'lprtip',
        "aoColumns": [
            { "sTitle": "Role",    		"sWidth": "75%", "sType": "html" , 	"bSortable" : false },
            { "sTitle": "Access Level", "sWidth": "25%", "sType": "numeric", "bSortable" : false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            // apply color to all access level cells
            accessLvl = aData[1];
            $('td:eq(1)', nRow).addClass("row-" + getAccessColor(accessLvl, colorThresholds));
            return nRow;
        }
    } );
} );


// title_compo_diff_table dataTable setup
$(document).ready(function() {
	$('#title_compo_diff_table').dataTable( {
		"bProcessing": true,
		"bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 10,
        "bStateSave": true,
        "iCookieDuration": 60*60*24,
		"sAjaxSource": "/titles/" + title_id + "/compo_diff_data",
        "sDom": 'lprtip',
        "aoColumns": [
            { "sTitle": "Change",       "sWidth": "10%", "sType": "html"  , 	"bSortable" : false},
            { "sTitle": "Role",    		"sWidth": "65%", "sType": "html"  , 	"bSortable" : false},
            { "sTitle": "Modification Date", "sWidth": "25%", "sType": "numeric"  , 	"bSortable" : false}
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
