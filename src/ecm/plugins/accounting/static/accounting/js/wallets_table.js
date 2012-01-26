
// disable multi column sorting
$('#history_table thead th').click(function(event) {
    if (!$(event.target).hasClass('sorthandle')) {
        event.shiftKey = false;
    }
});

// dataTable setup
$(document).ready(function() {
    table = $('#wallets_table').dataTable( {
        bProcessing: true,
        bServerSide: true,
        iDisplayLength: 25,
        sAjaxSource: "/accounting/wallets/data/",
        sDom: 'rt',
        aoColumns: [
            { /* Wallet */    sType: "html"    },
            { /* Balance */   sType: "string",  sClass : "right" },
        ]
    });
});
