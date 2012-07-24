/*************************
 * "Titles" table setup *
 *************************/
/**
 * Needs three global constants to be defined:
 *      - DIRECTOR_ACCESS_LVL
 *      - COLOR_THRESHOLDS
 **/

SHOW_SHIPS = 'all';

function titlesRowCallback( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
    /* apply color to all access level cells */
    accessLvl = aData[1];
    $('td:eq(1)', nRow).addClass("row-" + getAccessColor(accessLvl, COLOR_THRESHOLDS));
    return nRow;
}