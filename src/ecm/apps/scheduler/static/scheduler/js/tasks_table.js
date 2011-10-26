// dataTable setup
$(document).ready(function() {
  table = $('#tasks_table').dataTable( {
    "bProcessing": true,
    "bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25,
    "sAjaxSource": "/scheduler/tasks/data/",
        "sDom": 'rt',
        "aoColumns": [
            { "sTitle": "Task description",    "sWidth": "50%", "sType": "html", "bSearchable": false , "bSortable": false},
            { "sTitle": "Next execution",  "sWidth": "15%", "sType": "html", "bSearchable": false, "bSortable": false   },
            { "sTitle": "Frequency",       "sWidth": "15%", "sType": "html",    "bSearchable": false, "bSortable": false },
            { "sTitle": "Is running",    "sWidth": "10%", "sType": "html", "bSearchable": false, "bSortable": false },
            { "sTitle": "Force Execution", "sWidth": "10%", "sType": "html",  "bSearchable": false, "bSortable": false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            if (aData[3] == 'true') {
                $('td:eq(3)', nRow).html('<img src="/s/admin/img/admin/icon-yes.gif" alt="True">');
            } else {
                $('td:eq(3)', nRow).html('<img src="/s/admin/img/admin/icon-no.gif" alt="False">');
            }
            return nRow;
    }
    } );

} );
