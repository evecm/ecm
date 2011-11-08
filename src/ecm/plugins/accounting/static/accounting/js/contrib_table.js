/************************************
 * "Accounting journal" table setup *
 ************************************/
$(document).ready(function() {
	  var table = $('#member_contrib_table').dataTable( {
        "sPaginationType": "full_numbers",
        "bProcessing": true,
        "bServerSide": true,
        "bAutoWidth": false,
        "iDisplayLength": 25, /* default display 25 items */
        "bStateSave": true, /* table state persistance */
        "iCookieDuration": 60 * 60, /* persistance duration 1 hour */
        "sAjaxSource": "/accounting/contributions/members/data/",
        "sDom": 'lprtip', /* table layout. see http://www.datatables.net/usage/options */
        "aaSorting": [[1,'desc']],
        "aoColumns": [
            { /* Member */       "sWidth": "50%",   "sType": "html" },
            { /* Contributions */     "sWidth": "50%",   "sType": "html" , "sClass" : "right"   }
        ],
        "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
            $('td:eq(1)', nRow).addClass('credit');
            return nRow;
        },
        
        /* this function will be called when the table has to query data to be displayed */
        "fnServerData": function ( sSource, aoData, fnCallback ) {
            /* Add some extra variables to the url */
            aoData.push( { 
                "name": "from_date", 
                "value": $("#from_date").val()
            }, { 
                "name": "to_date", 
                "value": $("#to_date").val()
            } );
            
            $.getJSON( sSource, aoData, function (json) { 
                fnCallback(json)
            } );
        },
        
    });
	
    $("#refresh_table").click(function () {
        table.fnDraw();
    });
    
    /* disable multi column sorting */
    $('#member_contrib_table thead th').click(function(event) {
        if (!$(event.target).hasClass('sorthandle')) {
            event.shiftKey = false;
        }
    });
    
} );

$(document).ready(function() {
    var table = $('#system_contrib_table').dataTable( {
      "sPaginationType": "full_numbers",
      "bProcessing": true,
      "bServerSide": true,
      "bAutoWidth": false,
      "iDisplayLength": 25, /* default display 25 items */
      "bStateSave": true, /* table state persistance */
      "iCookieDuration": 60 * 60, /* persistance duration 1 hour */
      "sAjaxSource": "/accounting/contributions/systems/data/",
      "sDom": 'lprtip', /* table layout. see http://www.datatables.net/usage/options */
      "aaSorting": [[1,'desc']],
      "aoColumns": [
          { /* Solar System */       "sWidth": "50%",   "sType": "html" },
          { /* Contributions */     "sWidth": "50%",   "sType": "html" , "sClass" : "right"   }
      ],
      "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) {
          $('td:eq(1)', nRow).addClass('credit');
          return nRow;
      },
      
      /* this function will be called when the table has to query data to be displayed */
      "fnServerData": function ( sSource, aoData, fnCallback ) {
          /* Add some extra variables to the url */
          aoData.push( { 
              "name": "from_date", 
              "value": $("#from_date").val()
          }, { 
              "name": "to_date", 
              "value": $("#to_date").val()
          } );
          
          $.getJSON( sSource, aoData, function (json) { 
              fnCallback(json)
          } );
      },
      
  });
  
  $("#refresh_table").click(function () {
      table.fnDraw();
  });
  
  /* disable multi column sorting */
  $('#system_contrib_table thead th').click(function(event) {
      if (!$(event.target).hasClass('sorthandle')) {
          event.shiftKey = false;
      }
  });
  
} );