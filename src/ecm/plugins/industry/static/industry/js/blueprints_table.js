/*************************
 * "Catalog" table setup *
 *************************/
/**
 * Needs global constants to be defined in the HTML page.
 *      - AJAX_URL
 *      - DISPLAY_MODE
 **/
$(document).ready(function() {

    var table = $('#blueprints_table').dataTable( {
        sPaginationType: "full_numbers",
        bProcessing: true,
        bServerSide: true,
        bAutoWidth: false,
        iDisplayLength: 25, 		/* default display 25 items */
        bStateSave: true, 		/* table state persistance */
        iCookieDuration: 60 * 60, /* persistance duration 1 hour */
        sAjaxSource: AJAX_URL,
        sDom: 'lprtip', 			/* table layout. see http://www.datatables.net/usage/options */
        aoColumns: [
            { /* 0 Blueprint */ sWidth: "80%", bSortable: false },
            { /* 1 ME */        sWidth: "5%", bSortable: false  },
            { /* 2 PE */        sWidth: "5%", bSortable: false  },
            { /* 3 Copy */      sWidth: "5%", bSortable: false, sClass: 'center'},
            { /* 4 Runs */      sWidth: "5%", bSortable: false  },
            { /* 5 blueprint_id */    bVisible: false, bSortable: false  },
        ],
        fnRowCallback: function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            var bp_id = aData[5];

            $('td:eq(1)', nRow).addClass('right');
            $('td:eq(1)', nRow).attr('id', bp_id);
            /* Apply jEditable handlers to the cells each time we redraw the table */
            $('td:eq(1)', nRow).editable( '/industry/catalog/blueprints/me/', {
                tooltip: 'Click to edit...',
                callback: function( sValue, y ) {
                    var aPos = oTable.fnGetPosition( this );
                    oTable.fnUpdate( sValue, aPos[0], aPos[1] );
                },
            } );

            $('td:eq(2)', nRow).addClass('right');
            $('td:eq(2)', nRow).attr('id', bp_id);
            /* Apply jEditable handlers to the cells each time we redraw the table */
            $('td:eq(2)', nRow).editable( '/industry/catalog/blueprints/pe/', {
                tooltip: 'Click to edit...',
                callback: function( sValue, y ) {
                    var aPos = oTable.fnGetPosition( this );
                    oTable.fnUpdate( sValue, aPos[0], aPos[1] );
                },
            } );

            var copy = aData[3];
            var checked = '';
            if (copy == 'true') {
                checked += 'checked ';
            }
            $('td:eq(3)', nRow).html('<input id="' + bp_id + '" type="checkbox" ' + checked + '/>');
            $('td:eq(3) input', nRow).click(function () {
                var params = {
                    id: $(this).attr('id'),
                    value: $(this).is(':checked')
                };
                $.post('/industry/catalog/blueprints/copy/', params);
            });

            $('td:eq(4)', nRow).addClass('right');
            $('td:eq(4)', nRow).attr('id', bp_id);
            /* Apply jEditable handlers to the cells each time we redraw the table */
            $('td:eq(4)', nRow).editable( '/industry/catalog/blueprints/runs/', {
                tooltip: 'Click to edit...',
                callback: function( sValue, y ) {
                    var aPos = oTable.fnGetPosition( this );
                    oTable.fnUpdate( sValue, aPos[0], aPos[1] );
                },
            } );

            $('td:eq(5)', nRow).hide();
            return nRow;
        },

        /* this function will be called when the table has to query data to be displayed */
        fnServerData: function ( sSource, aoData, fnCallback ) {
            /* Add some extra variables to the url */
            aoData.push( {
                name: 'displayMode',
                value: DISPLAY_MODE
            } );
            $.getJSON( sSource, aoData, function (json) {
                fnCallback(json)
            } );
        },

        /* the search field being outside the table object, we need to save its status
         * explicitly here in order to restore it with the rest */
        fnStateSaveCallback: function (oSettings, sValue) {
            var sFilter = $('#search_text').val();
            sValue = sValue.replace( /"sFilter":".*?"/, '"sFilter":"' + sFilter + '"' );
            sValue += ', "displayMode": ' + DISPLAY_MODE;
            return sValue;
        },
        /* restore the search field content */
        fnStateLoadCallback: function (oSettings, oData) {
            $("#search_text").val(oData.sFilter);
            if ('displayMode' in oData) {
                DISPLAY_MODE = oData.displayMode;
                updateButtons();
            }
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
    $('#blueprints_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });


    /* Button to select quatities values */
    $("#display_all").click(function() {
        if (DISPLAY_MODE != 'all') {
            DISPLAY_MODE = 'all';
            updateButtons();
            table.fnDraw();
        }
    });
    $("#display_originals").click(function() {
        if (DISPLAY_MODE != 'originals') {
            DISPLAY_MODE = 'originals';
            updateButtons();
            table.fnDraw();
        }
    });
    $("#display_copies").click(function() {
        if (DISPLAY_MODE != 'copies') {
            DISPLAY_MODE = 'copies';
            updateButtons();
            table.fnDraw();
        }
    });

    updateButtons();
});

function updateButtons() {
    if (DISPLAY_MODE == 'originals') {
        $("#display_all").removeClass('selected');
        $("#display_originals").addClass('selected');
        $("#display_copies").removeClass('selected');
    } else if (DISPLAY_MODE == 'copies') {
        $("#display_all").removeClass('selected');
        $("#display_originals").removeClass('selected');
        $("#display_copies").addClass('selected');
    } else {
        $("#display_all").addClass('selected');
        $("#display_originals").removeClass('selected');
        $("#display_copies").removeClass('selected');
    }
}
