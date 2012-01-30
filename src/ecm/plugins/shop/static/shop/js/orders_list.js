/************************************
 * "Orders List" table setup *
 ************************************/


$(document).ready(function() {
      var table = $('#orders_list').dataTable( {
        sPaginationType: "full_numbers",
        bProcessing: true,
        bServerSide: true,
        bAutoWidth: false,
        iDisplayLength: 25, /* default display 25 items */
        bStateSave: true, /* table state persistance */
        iCookieDuration: 60 * 60, /* persistance duration 1 hour */
        sAjaxSource: AJAX_URL,
        sDom: 'lprtip', /* table layout. see http://www.datatables.net/usage/options */
        aoColumns: [
            { /* # */               sWidth: "10%" },
            { /* State */           sWidth: "10%" },
            { /* Items */           sWidth: "40%", bSortable: false },
            { /* Quote */           sWidth: "15%", sClass: 'right'},
        ],
        fnRowCallback: function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            return nRow;
        },

        /* the search field being outside the table object, we need to save its status
         * explicitly here in order to restore it with the rest */
        fnStateSaveCallback: function (oSettings, sValue) {
            var sFilter = $("#search_text").val();
            sValue = sValue.replace( /"sFilter":".*?"/, '"sFilter":"' + sFilter + '"' );
            return sValue;
        },
        /* restore the search field content */
        fnStateLoadCallback: function (oSettings, oData) {
            $("#search_text").val(oData.sFilter);
            return true;
        }
    });

    /* trigger the search when pressing return in the text field */
    $("#search_form").submit(function(event) {
        event.preventDefault();
        table.fnFilter($("#search_text").val());
    });

    /* trigger the search when clicking the "search" button */
    $("#search_button").click(function() {
        table.fnFilter($("#search_text").val());
    });

    /* reset the search when clicking the "reset" button */
    $("#clear_search").click(function() {
        $("#search_text").val("");
        table.fnFilter("");
    });

    /* disable multi column sorting */
    $('#orders_list thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });

} );
