/*************************
 * "Catalog" table setup *
 *************************/
/**
 * Needs global constants to be defined in the HTML page.
 *      - AJAX_URL
 *      - DISPLAY_MODE
 **/
$(document).ready(function() {

    var table = $('#pricehistory_table').dataTable( {
        sPaginationType: "full_numbers",
        bProcessing: true,
        bServerSide: true,
        bAutoWidth: false,
        iDisplayLength: 10, 		/* default display 25 items */
        bStateSave: true, 		/* table state persistance */
        iCookieDuration: 60 * 60, /* persistance duration 1 hour */
        sAjaxSource: AJAX_URL,
        sDom: 'lprtip', 			/* table layout. see http://www.datatables.net/usage/options */
        aoColumns: [
            { /* 0 Date */  bSortable: false },
            { /* 1 Price */ bSortable: false  },
        ],
        fnRowCallback: function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            $('td:eq(1)', nRow).addClass('right');
            return nRow;
        }
    });
    $('td#price').editable( '/industry/catalog/supplies/price/', {
        submitdata : {id: SUPPLY_ID},
        tooltip: 'Click to edit...',
        callback: function( sValue, y ) {
            table.fnDraw();
        },
    });
    $('#update_checkbox').click(function () {
        var params = {
            id: SUPPLY_ID,
            value: $(this).is(':checked')
        };
        $.post('/industry/catalog/supplies/autoUpdate/', params);
    });
    $('#supply_source').change(function () {
        var params = {
            id: SUPPLY_ID,
            value: $(this).val()
        };
        $.post('/industry/catalog/supplies/supplySource_id/', params);
    });
    $('#update_button').click(function () {
        var oldPrice = $('input#price').html();
        $('td#price').html('<img src="/static/ecm/img/throbber.gif"/>');
        $.get('/industry/catalog/supplies/' + SUPPLY_ID + '/updateprice/')
         .success(function (data) {
            $('td#price').html(data);
            table.fnDraw();
         })
         .error(function (data) {
            $('td#price').html(oldPrice);
         });
    });
});
