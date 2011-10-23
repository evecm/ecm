/*****************************************
 * "Security access changes" table setup *
 *****************************************/

// disable multi column sorting
$('#history_table thead th').click(function(event) {
    if (!$(event.target).hasClass('sorthandle')) {
        event.shiftKey = false;
    }
});


$(document).ready(function() {
    var table = $('#access_changes_table').dataTable({
        "sPaginationType" : "full_numbers",
        "bProcessing" : true,
        "bServerSide" : true,
        "bAutoWidth" : false,
        "iDisplayLength" : 25,
        "bStateSave" : true,
        "sCookiePrefix": "ecm_access_changes_table_",
        "iCookieDuration" : 60 * 60 * 24,
        "sAjaxSource" : "/hr/members/accesschanges/data/",
        "sDom" : 'lprtip',
        "aoColumns" : [
            { "sTitle": "Change",     "sWidth": "10%", "sType": "html" ,  "bSortable": false },
            { "sTitle": "Member",     "sWidth": "30%", "sType": "html"  },
            { "sTitle": "Title/Role", "sWidth": "40%", "sType": "html" ,  "bSortable": false },
            { "sTitle": "Date",       "sWidth": "20%", "sType": "string" }
        ],
        "aaSorting": [[3, 'desc']],
        "fnRowCallback" : function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
            if (aData[0] == "true") {
                $('td:eq(0)', nRow).html('<img src="/s/ecm/img/plus.png"></img>');
            } else {
                $('td:eq(0)', nRow).html('<img src="/s/ecm/img/minus.png"></img>');
            }
            return nRow;
        },
        /* the search field being outside the table object, we need to save its status
         * explicitly here in order to restore it with the rest */
        "fnStateSaveCallback": function (oSettings, sValue) {
            var sFilter = $("#search_text").val();
            sValue = sValue.replace( /"sFilter":".*?"/, '"sFilter":"' + sFilter + '"' );
            return sValue;
        },
        /* restore the search field content */
        "fnStateLoadCallback": function (oSettings, oData) {
            $("#search_text").val(oData.sFilter);
            return true;
        }
    });

    $("#search_form").submit(function(event) {
        event.preventDefault();
        table.fnFilter($("#search_text").val());
    });

    $("#search_button").click(function() {
        table.fnFilter($("#search_text").val());
    });

    $("#clear_search").click(function() {
        $("#search_text").val("");
        table.fnFilter("");
    });

});