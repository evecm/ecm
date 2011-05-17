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
    $('#title_composition_table').dataTable({
        "sPaginationType": "full_numbers",
        "bProcessing" : true,
        "bServerSide" : true,
        "bAutoWidth" : false,
        "iDisplayLength" : 10,
        "bStateSave" : true,
        "iCookieDuration" : 60 * 60 * 24,
        "sAjaxSource" : "/titles/" + TITLE_ID + "/composition_data",
        "sDom" : 'lprtip',
        "aoColumns": [
            {"sTitle": "Role",         "sWidth": "50%", "sType": "html" ,   "bSortable" : false},
            {"sTitle": "Category",     "sWidth": "30%", "sType": "html" ,   "bSortable" : false},
            {"sTitle": "Access Level", "sWidth": "20%", "sType": "numeric", "bSortable" : false}
        ],
        "fnRowCallback" : function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
            // apply color to all access level cells
            accessLvl = aData[2];
            $('td:eq(2)', nRow).addClass("row-" + getAccessColor(accessLvl, COLOR_THRESHOLDS));
            return nRow;
        }
    });
});


// title_compo_diff_table dataTable setup
$(document).ready(function() {
    $('#title_compo_diff_table').dataTable({
        "sPaginationType": "full_numbers",
        "bProcessing" : true,
        "bServerSide" : true,
        "bAutoWidth" : false,
        "iDisplayLength" : 10,
        "bStateSave" : true,
        "iCookieDuration" : 60 * 60 * 24,
        "sAjaxSource" : "/titles/" + TITLE_ID + "/compo_diff_data",
        "sDom" : 'lprtip',
        "aoColumns": [
            {"sTitle": "Change",            "sWidth": "10%", "sType": "html",    "bSortable" : false},
            {"sTitle": "Role",              "sWidth": "40%", "sType": "html",    "bSortable" : false},
            {"sTitle": "Category",          "sWidth": "25%", "sType": "html",    "bSortable" : false},
            {"sTitle": "Modification Date", "sWidth": "25%", "sType": "numeric", "bSortable" : false}
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
