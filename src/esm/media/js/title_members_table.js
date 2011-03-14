const director_access_lvl = 999999999999;


// disable multi column sorting
$('#members_table thead th').click(function(event) {
    if (!$(event.target).hasClass('sorthandle')) {
        event.shiftKey = false;
    }
});

//dataTable setup
$(document).ready(function() {
	table = $('#members_table').dataTable( {
		"sPaginationType": "full_numbers",
		"bProcessing": true,
		"bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25,
        "bStateSave": true,
        "iCookieDuration": 60*60*24,
		"sAjaxSource": "/titles/" + title_id + "/members/data",
        "sDom": 'lprtip',
        "aoColumns": [
            { "sTitle": "Name",         "sWidth": "25%", "sType": "html" },
            { "sTitle": "Nickname",     "sWidth": "20%", "sType": "string",       "bSortable": false     },
            { "sTitle": "Access Level", "sWidth": "10%", "sType": "access-level", "bSearchable": false   },
            { "sTitle": "Extra Roles",  "sWidth": "5%",  "sType": "numeric",      "bSearchable": false   },
            { "sTitle": "Corp Date",    "sWidth": "10%", "sType": "string",       "bSearchable": false   },
            { "sTitle": "Last Login",   "sWidth": "10%", "sType": "string",       "bSearchable": false   },
            { "sTitle": "Location",     "sWidth": "20%", "sType": "string",       "bSearchable": false   },
            { "sTitle": "Ship",         "sWidth": "5%",  "sType": "string" },
            { "bVisible": false },
            { "bVisible": false }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            /* apply color to all access level cells */
            accessLvl = aData[2];
            if ( accessLvl == director_access_lvl ) {
				$('td:eq(2)', nRow).html( '<b>DIRECTOR</b>' );
            }
            $('td:eq(2)', nRow).addClass("row-" + getAccessColor(accessLvl, colorThresholds));
            if (aData[3] > 0) {
                $('td:eq(3)', nRow).addClass("row-red");
            }
            
            /* set titles tooltip on each row */
            $('td:eq(8)', nRow).hide()
            titles = aData[8]
            if (titles != "") {
                $('td:eq(2)', nRow).attr("title", titles)
                $('td:eq(2)', nRow).cluetip({
                    splitTitle: '|',
                    dropShadow: false, 
                    cluetipClass: 'jtip',
                    positionBy: 'mouse',
                    tracking: true
                });
            }
            
            /* set roles tooltip on each row */
            $('td:eq(9)', nRow).hide()
            roles = aData[9]
            if (roles != "") {
                $('td:eq(3)', nRow).attr("title", roles)
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
    } );

    $("#search_form").submit(function() {
        table.fnFilter($("#search_text").val());
        return false;
    });

    $("#search_button").click(function() {
        table.fnFilter($("#search_text").val());
    });

    $("#clear_search").click(function() {
        $("#search_text").val("");
        table.fnFilter("");
    });

} );