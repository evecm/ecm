/*****************************************
 * "Security access changes" table setup *
 *****************************************/

$(document).ready(function() {
    $('#access_changes_table').dataTable({
        "sPaginationType" : "full_numbers",
        "bProcessing" : true,
        "bServerSide" : true,
        "bAutoWidth" : false,
        "iDisplayLength" : 25,
        "bStateSave" : true,
        "iCookieDuration" : 60 * 60 * 24,
        "sAjaxSource" : "/members/accesschanges/data",
        "sDom" : 'lprtip',
        "aoColumns" : [
            { "sTitle": "Change",     "sWidth": "10%", "sType": "html" ,  "bSortable": false },
            { "sTitle": "Member",     "sWidth": "30%", "sType": "html" ,  "bSortable": false },
            { "sTitle": "Title/Role", "sWidth": "40%", "sType": "html" ,  "bSortable": false },
            { "sTitle": "Date",       "sWidth": "20%", "sType": "string", "bSortable": false }
        ],
        "fnRowCallback" : function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
            if (aData[0] == "true") {
                $('td:eq(0)', nRow).html('<img src="/m/img/plus.png"></img>');
            } else {
                $('td:eq(0)', nRow).html('<img src="/m/img/minus.png"></img>');
            }
            return nRow;
        }
    });
});