director_access_lvl = 999999999999;


// disable multi column sorting
$('#history_table thead th').click(function(event) {
    if (!$(event.target).hasClass('sorthandle')) {
        event.shiftKey = false;
    }
});

// dataTable setup
$(document).ready(function() {
	table = $('#history_table').dataTable( {
		"sPaginationType": "full_numbers",
		"bProcessing": true,
		"bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25,
		"sAjaxSource": "/members/history/data",
        "sDom": 'lprtip',
        "aoColumns": [
            { "sTitle": "Corped/Leaved","sWidth": "15%", "sType": "html" ,  "bSortable": false },
            { "sTitle": "Name",         "sWidth": "30%", "sType": "html" ,  "bSortable": false },
            { "sTitle": "Nickname",     "sWidth": "30%", "sType": "string", "bSortable": false },
            { "sTitle": "Corp/Leave Date",    "sWidth": "25%", "sType": "string", "bSearchable": false , "bSortable": false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            if (aData[0] == "true") {
                $('td:eq(0)', nRow).html('<img src="/m/img/plus.png"/>');
            } else {
                $('td:eq(0)', nRow).html('<img src="/m/img/minus.png"/>');
            }
            return nRow;
		}
    } );

    $("#search_form").submit(function() {
        table.fnFilter($("#search_text").val());
        return false;
    });

    $("#search_button").click(function() {
        table.fnFilter($("#search_text").val());
    });

    $("#clear_search").click(function() {
        $("#search_text").val("");
        table.fnFilter("");
    });

} );
