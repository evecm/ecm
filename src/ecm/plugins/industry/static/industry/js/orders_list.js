/************************************
 * "Orders List" table setup *
 ************************************/

PARAMS = {
    states: '{%for id, name in states.items%}{{id}}{%if not forloop.last%},{%endif%}{%endfor%}',
};
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
            { /* Originator */      sWidth: "10%" },
            { /* Client */          sWidth: "10%" },
            { /* Delivery Date */   sWidth: "10%" },
            { /* Items */           sWidth: "30%", bSortable: false },
            { /* Quote */           sWidth: "20%", sClass: 'right' },
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
        },
	    /* this function will be called when the table has to query data to be displayed */
	    fnServerData: function ( sSource, aoData, fnCallback ) {
	        /* Add some extra variables to the url */
	        aoData.push( {
	            name: 'states',
	            value: PARAMS
	        } );
	        $.getJSON( sSource, aoData, function (json) {
	            fnCallback(json)
	        } );
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
    /* enable control click on state buttons */
    $('#state_buttons button').click(function (event) {
        if (event.ctrlKey) {
            /* if ctrl + click, deselect all divisions before selecting */
            $('#state_buttons button').removeClass('active');
        }
    });
    $('#apply_filter').click(function() {
        
        var stateBtns = $('#state_buttons button.active');
        var states = '';
        for (var i=0 ; i < stateBtns.length ; i++) {
            states += ',' + stateBtns[i].id;
        }
        if (states.length != 0) {
            states = states.substring(1);
        }
        PARAMS.states = states;
        table.fnDraw();
    });
    $('#reset_filter').click(function() {
        var stateBtns = $('#state_buttons button');
        var states = '';
        for (var i=0 ; i < stateBtns.length ; i++) {
            states += ',' + stateBtns[i].id;
        }
        if (states.length != 0) {
            states = states.substring(1);
        }
        PARAMS.states = states;
        table.fnDraw();
    });

} );
