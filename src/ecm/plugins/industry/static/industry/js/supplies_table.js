/*************************
 * "Catalog" table setup *
 *************************/
/**
 * Needs global constants to be defined in the HTML page.
 *      - AJAX_URL
 *      - DISPLAY_MODE
 **/
var SELECT_SOURCE;
$(document).ready(function() {
    SELECT_SOURCE = '<select>';
    for (var i = 0; i < SUPPLY_SOURCES.length; i++) {
        SELECT_SOURCE += '<option value="' + SUPPLY_SOURCES[i][0] + '">' + SUPPLY_SOURCES[i][1] + '</option>';
    }
    SELECT_SOURCE += '</select>';


    var table = $('#supplies_table').dataTable( {
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
            { /* 0 Item */          sWidth: "50%", bSortable: false },
            { /* 1 Price */         sWidth: "15%", bSortable: false  },
            { /* 2 Auto-Update */   sWidth: "10%", bSortable: false, sClass: 'center' },
            { /* 3 Source */        sWidth: "20%", bSortable: false, sClass: 'center'},
            { /* 4 Update */        sWidth: "5%", bSortable: false  },
        ],
        fnRowCallback: function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            var item_id = aData[4];

            $('td:eq(1)', nRow).addClass('right');
            $('td:eq(1)', nRow).addClass('price');
            $('td:eq(1)', nRow).attr('id', item_id);
            /* Apply jEditable handlers to the cells each time we redraw the table */
            $('td:eq(1)', nRow).editable( '/industry/catalog/supplies/price/', {
                tooltip: 'Click to edit...',
                callback: function( sValue, y ) {
                    var aPos = oTable.fnGetPosition( this );
                    oTable.fnUpdate( sValue, aPos[0], aPos[1] );
                },
            } );

            var autoUpdate = aData[2];
            var checked = '';
            if (autoUpdate == 'true') {
                checked += 'checked ';
            }
            $('td:eq(2)', nRow).html('<input id="' + item_id + '" type="checkbox" ' + checked + '/>');
            $('td:eq(2) input', nRow).click(function () {
                var params = {
                    id: $(this).attr('id'),
                    value: $(this).is(':checked')
                };
                $.post('/industry/catalog/supplies/autoUpdate/', params);
            });


            $('td:eq(3)', nRow).html(SELECT_SOURCE);
            $('td:eq(3) select', nRow).val(aData[3]);
            $('td:eq(3) select', nRow).attr('id', item_id);
            $('td:eq(3) select', nRow).change(function () {
                var params = {
                    id: $(this).attr('id'),
                    value: $(this).val()
                };
                $.post('/industry/catalog/supplies/supplySource_id/', params);
            });


            $('td:eq(4)', nRow).html('<input type="button" class="button" value="Update"/>');
            $('td:eq(4) input', nRow).attr('id', item_id);
            $('td:eq(4) input', nRow).click(function () {
                var id = $(this).attr('id');
                var oldPrice = $('#' + id + '.price').html();
                $('#' + id + '.price').html('<img src="/s/ecm/img/throbber.gif"/>');
                $.get('/industry/catalog/supplies/' + id + '/updateprice/')
                 .success(function (data) {
                    $('#' + id + '.price').html(data);
                 })
                 .error(function (data) {
                    $('#' + id + '.price').html(oldPrice);
                 });
            });
            return nRow;
        },

        /* this function will be called when the table has to query data to be displayed */
        fnServerData: function ( sSource, aoData, fnCallback ) {
            /* Add some extra variables to the url */
            aoData.push( {
                name: 'displayMode',
                value: DISPLAY_MODE
            }, {
                name: 'filter',
                value: CURRENT_FILTER
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
            sValue += ', "filter": ' + CURRENT_FILTER;
            return sValue;
        },
        /* restore the search field content */
        fnStateLoadCallback: function (oSettings, oData) {
            $("#search_text").val(oData.sFilter);
            if ('displayMode' in oData) {
                DISPLAY_MODE = oData.displayMode;
                updateDisplayModeButtons();
            }
            if ('displayMode' in oData) {
                CURRENT_FILTER = oData.filter;
                updateFilterButtons();
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
    $('#supplies_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });


    /* Display mode buttons */
    var dispButtons = $('#search_form input.disp');
    for (var i = 0; i < dispButtons.length; i++) {
        $(dispButtons[i]).click(function () {
            var mode = $(this).attr('id').substr('display_'.length);
            if (DISPLAY_MODE != mode) {
                DISPLAY_MODE = mode;
                updateDisplayModeButtons();
                table.fnDraw();
            }
        });
    }
    /* Filter buttons */
    $('#filter_selector').change(function () {
        var filter = $(this).val().substr('filter_'.length);
        if (CURRENT_FILTER != filter) {
            CURRENT_FILTER = filter;
            table.fnDraw();
        }
    });

    updateDisplayModeButtons();
    updateFilterButtons();
});

function updateDisplayModeButtons() {
    var buttons = $('#search_form input.disp');
    for (var i = 0; i < buttons.length; i++) {
        if (endsWith(buttons[i].id, DISPLAY_MODE)) {
            $(buttons[i]).addClass('selected');
        } else {
            $(buttons[i]).removeClass('selected');
        }
    }
}

function updateFilterButtons() {
    var buttons = $('#search_form input.filter');
    for (var i = 0; i < buttons.length; i++) {
        if (endsWith(buttons[i].id, CURRENT_FILTER)) {
            $(buttons[i]).addClass('selected');
        } else {
            $(buttons[i]).removeClass('selected');
        }
    }
}


function endsWith(str, suffix) {
    return str.indexOf(suffix, str.length - suffix.length) !== -1;
}
