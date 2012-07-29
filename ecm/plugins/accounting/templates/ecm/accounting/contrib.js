/*******************
 * Tax contributions js file
 *
 */

function contribRowCallback(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
    $('td:eq(1)', nRow).addClass('credit');
    return nRow;
}
