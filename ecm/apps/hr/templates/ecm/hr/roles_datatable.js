/*************************
 * "Members" table setup *
 *************************/
/**
 * Needs three global constants to be defined:
 *      - DIRECTOR_ACCESS_LVL
 *      - COLOR_THRESHOLDS
 *      - AJAX_URL
 **/

SHOW_SHIPS = 'all';

function rolesRowCallback( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
    /* apply color to all access level cells */
    accessLvl = aData[2];
    $('td:eq(2)', nRow).addClass("row-" + getAccessColor(accessLvl, COLOR_THRESHOLDS));

    /* hide "ID" column and set the id attribute */
    $('td:eq(5)', nRow).hide();
    $(nRow).attr("id", aData[5]);

    /* set members tooltip on each row */
    $('td:eq(6)', nRow).hide();
    members = aData[6];
    if (members != "") {
        $('td:eq(3)', nRow).attr("title", members);
        $('td:eq(3)', nRow).cluetip({
          width: 150,
            splitTitle: '|',
            dropShadow: false,
            cluetipClass: 'jtip',
            positionBy: 'mouse',
            tracking: true
        });
        /* highlight the "Members" cells where there are "direct" members */
        $('td:eq(3)', nRow).addClass("row-red");
    }

    /* set titles tooltip on each row */
    $('td:eq(7)', nRow).hide();
    titles = aData[7];
    if (titles != "") {
        $('td:eq(4)', nRow).attr("title", titles);
        $('td:eq(4)', nRow).cluetip({
          width: 170,
            splitTitle: '|',
            dropShadow: false,
            cluetipClass: 'jtip',
            positionBy: 'mouse',
            tracking: true
        });
    }

    /* Apply jEditable handlers to the cells each time we redraw the table */
    $('td:eq(2)', nRow).editable( '/hr/roles/update/', {
        callback: function( sValue, y ) {
            var aPos = $('#roles_table').fnGetPosition( this );
            $('#roles_table').fnUpdate( sValue, aPos[0], aPos[1] );
        },
        submitdata: function ( value, settings ) {
            return { id: this.parentNode.getAttribute('id')};
        },
        tooltip   : 'Click to edit...'
    } );

    return nRow;
}
        
function rolesServerDataCallback( sSource, aoData, fnCallback ) {
    /* Add some extra variables to the url */
    aoData.push( {
        name: 'role_type',
        value: ROLE_TYPE
    } );
    $.getJSON( sSource, aoData, function (json) {
        fnCallback(json)
    } );
}

