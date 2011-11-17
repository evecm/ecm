$(document).ready(function() {

    var table = $('#materials_table').dataTable( {
        bProcessing: true,
        bServerSide: true,
        bAutoWidth: false,
        iDisplayLength: 50,       /* default display 50 items */
        sAjaxSource: '/industry/catalog/blueprints/' + BLUEPRINT_ID + '/materials/',
        sDom: 'rt',           /* table layout. see http://www.datatables.net/usage/options */
        aoColumns: [
            { /* 0 Icon */        sWidth: "10%", 'bSortable': false, sClass: 'center'},
            { /* 1 Item */        sWidth: "50%", 'bSortable': false},
            { /* 2 Quantity */    sWidth: "10%", 'bSortable': false},
            { /* 3 Waste */       sWidth: "10%", 'bSortable': false},
        ],
        fnRowCallback: function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            $('td:eq(0)', nRow).html('<img src="http://image.eveonline.com/Type/'+aData[0]+'_32.png">');
            $('td:eq(2)', nRow).addClass('right');
            $('td:eq(3)', nRow).addClass('right');
            return nRow;
        },

    });

    /* Set jEditable handlers */
    $('td.me').editable('/industry/catalog/blueprints/me/', {
            callback: function () {
                table.fnDraw();
            }
    });
    $('td.pe').editable('/industry/catalog/blueprints/pe/');
    $('input.copy').click(function () {
        var thisId = $(this).attr('id');
        var checked = $(this).is(':checked');
        $.post('/industry/catalog/blueprints/copy/', {id: thisId, value: checked})
        .error(function () {
            alert('Failed to change copy!');
        });
    });
    $('td.runs').editable('/industry/catalog/blueprints/runs/');
});

