/*************************
 * Wallet journal JS file
 *
 * 
 * ***********************/

function walletJournalRowCallback(nRow, aData, iDisplayIndex, iDisplayIndexFull){
    if (aData[5].charAt(0) == '+') {
        $('td:eq(5)', nRow).addClass('journal-credit');
    } else {
        $('td:eq(5)', nRow).addClass('journal-debit');
    }
    /* hide reason column */
    $('td:eq(7)', nRow).hide()

    /* set titles tooltip on each row */
    reason = aData[7]
    if (reason != "") {
        $('td:eq(5)', nRow).attr("title", reason)
        $('td:eq(5)', nRow).cluetip({
            splitTitle: '|',
            dropShadow: false,
            cluetipClass: 'jtip',
            positionBy: 'mouse',
            tracking: true
        });
    }

    return nRow;
}


