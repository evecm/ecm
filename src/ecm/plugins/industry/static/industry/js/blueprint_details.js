var table;

$(document).ready(function() {

    table = $('#materials_table').dataTable( {
        bProcessing: true,
        bServerSide: true,
        bAutoWidth: false,
        iDisplayLength: 50, /* default display 50 items */
        sAjaxSource: '/industry/catalog/blueprints/' + BLUEPRINT_ID + '/materials/',
        sDom: 'rt', /* table layout. see http://www.datatables.net/usage/options */
        aoColumns: [
            { /* 0 Icon */        sWidth: "10%", bSortable: false, sClass: 'center'},
            { /* 1 Item */        sWidth: "50%", bSortable: false},
            { /* 2 Quantity */    sWidth: "10%", bSortable: false},
            { /* 3 Waste */       sWidth: "10%", bSortable: false},
        ],
        fnRowCallback: function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            $('td:eq(0)', nRow).html('<img src="http://image.eveonline.com/Type/'+aData[0]+'_32.png">');
            $('td:eq(2)', nRow).addClass('right');
            $('td:eq(3)', nRow).addClass('right');
            return nRow;
        },
        /* this function will be called when the table has to query data to be displayed */
        fnServerData: function ( sSource, aoData, fnCallback ) {
            /* Add some extra variables to the url */
            aoData.push( {
                name: "activityID",
                value: ACTIVITY_ID
            } );
            $.getJSON( sSource, aoData, function (json) {
                fnCallback(json)
            } );
        },
    });

    /* Set jEditable handlers */
    $('td.me').editable('/industry/catalog/blueprints/me/', {
            callback: function () {
                table.fnDraw();
            }
    });
    $('td.pe').editable('/industry/catalog/blueprints/pe/', {
            callback: function () {
                updateTime();
            }
    });
    $('input.copy').click(function () {
        var thisId = $(this).attr('id');
        var checked = $(this).is(':checked');
        $.post('/industry/catalog/blueprints/copy/', {id: thisId, value: checked})
        .error(function () {
            alert('Failed to change copy!');
        });
    });
    $('td.runs').editable('/industry/catalog/blueprints/runs/');
    updateButtons();
});

function updateButtons() {
    var buttons = $('.activity_button');
    for (var i = 0; i < buttons.length; i++) {
        if (buttons[i].id == ACTIVITY_ID) {
            $(buttons[i]).addClass('selected');
        } else {
            $(buttons[i]).removeClass('selected');
        }
    }
}

function updateTime() {
    $('#time').load('/industry/catalog/blueprints/' + BLUEPRINT_ID + '/time/');
}

function setActivity(activityID) {
    ACTIVITY_ID = activityID;
    table.fnDraw();
    updateButtons();
}
