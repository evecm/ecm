// disable multi column sorting
$('#roles_table thead th').click(function(event) {
    if (!$(event.target).hasClass('sorthandle')) {
        event.shiftKey = false;
    }
});

// dataTable setup
$(document).ready(function() {
	table = $('#roles_table').dataTable( {
		"bProcessing": true,
		"bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 50,
		"sAjaxSource": "/roles/all_data",
        "sDom": 'rt',
        "aoColumns": [
            { "sTitle": "Role Name",    "sWidth": "20%", "sType": "html" },
            { "sTitle": "Description",  "sWidth": "70%", "sType": "string" },
            { "sTitle": "Access Level", "sWidth": "10%", "sType": "numeric", "bSortable": false },
            { "sTitle": "Members",    	"sWidth": "10%", "sType": "html", 	 "bSortable": false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            /* apply color to all access level cells */
            accessLvl = aData[2];
            $('td:eq(2)', nRow).addClass("row-" + getAccessColor(accessLvl));
            return nRow;
		}
    } );

} );


// utility function for getting color from access level
function getAccessColor(accessLvl) {
    for (var i=0 ; i < colorThresholds.length ; i++) {
        if (accessLvl <= colorThresholds[i]["threshold"]) {
            return colorThresholds[i]["color"];
        }
    }
    return colorThresholds[0]["color"]
}

