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

function membersRowCallback( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
    /* apply color to all access level cells */
    accessLvl = aData[3];
    if (accessLvl == DIRECTOR_ACCESS_LVL) {
        $('td:eq(3)', nRow).html('<b>DIRECTOR</b>');
    }
    $('td:eq(3)', nRow).addClass("row-" + getAccessColor(accessLvl, COLOR_THRESHOLDS));

    /* hide titles column */
    $('td:eq(8)', nRow).hide()

    /* set titles tooltip on each row */
    titles = aData[7]
    if (titles != "") {
        $('td:eq(3)', nRow).attr("title", titles)
        $('td:eq(3)', nRow).cluetip({
            splitTitle: '|',
            dropShadow: false,
            cluetipClass: 'jtip',
            positionBy: 'mouse',
            tracking: true
        });
    }

    return nRow;
}
        
function membersServerParams( aoData ) {
    /* Add some extra variables to the url */
	aoData.push({
		name: "skills",
		value: $.toJSON(window.SKILLS),
	}, {
		name: 'corp',
		value: $('#corp_selector').val(),
	});
}


function membersStateSaveParams (oSettings, oData) {
    oData.corp = $('#corp_selector').val();
}

function membersStateLoadParams (oSettings, oData) {
    $('#corp_selector').val(oData.corp);
    return true;
}