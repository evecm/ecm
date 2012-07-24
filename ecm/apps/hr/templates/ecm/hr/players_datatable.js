/*************************
 * "Players" table setup *
 *************************/

function playersRowCallback( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
    /* if the player has no roles, display him/her in red */
    var group_count = aData[4];
    if (group_count == 0) {
        $(nRow).addClass("row-red");
    }
    var admin = aData[1];
    if (admin) {
        $('td:eq(1)', nRow).html('<img src="/static/admin/img/icon-yes.gif" alt="True">');
    } else {
        $('td:eq(1)', nRow).html('<img src="/static/admin/img/icon-no.gif" alt="False">');
    }
    return nRow;
}
