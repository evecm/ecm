
// disable multi column sorting
$('#roles_table thead th').click(function(event) {
    if (!$(event.target).hasClass('sorthandle')) {
        event.shiftKey = false;
    }
});


$(document).ready(function() {
    
    oTable = $('#roles_table').dataTable( {
        "bProcessing": true,
        "bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 50,
        "sAjaxSource": "/roles/" + current_role_type + "/data",
        "sDom": 'rt',
        "aoColumns": [
            { "sTitle": "Role Name",    "sWidth": "30%", "sType": "html",    "bSortable": false },
            { "sTitle": "Description",  "sWidth": "55%", "sType": "string",  "bSortable": false },
            { "sTitle": "Access Level", "sWidth": "5%", "sType": "numeric",  "bSortable": false },
            { "sTitle": "Members",      "sWidth": "5%", "sType": "numeric",  "bSortable": false },
            { "sTitle": "Titles",       "sWidth": "5%", "sType": "numeric",  "bSortable": false },
            { "bVisible": false },
            { "bVisible": false },
            { "bVisible": false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
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
            $('td:eq(2)', nRow).editable( '/roles/update', {
                "callback": function( sValue, y ) {
                    var aPos = oTable.fnGetPosition( this );
                    oTable.fnUpdate( sValue, aPos[0], aPos[1] );
                },
                "submitdata": function ( value, settings ) {
                    return { "id": this.parentNode.getAttribute('id')};
                },
                tooltip   : 'Click to edit...'
            } );
            
            return nRow;
        }
    } );

} );