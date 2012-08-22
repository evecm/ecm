/**
 * SaveAsCSV jQuery datatables plugin
 * 
 * This plugin allows to add a "Save As CSV" button in the table DOM.
 * To add the button, simply insert C in the sDom parameter.
 * 
 *   Example: sDom: '<<"span5"l><"span7"C>>rt<<"span5"i><"span7"p>>'
 *      
 * When this button is clicked, it makes a direct (non-ajax) request
 * with the exact same current parameters of the related datatable but
 * adds another parameter: 
 * 
 *   sFormat=csv
 * 
 * This allows to take it in consideration on the server side and return 
 * properly formatted CSV data.
 * 
 * TIP: the HTTP response should contain a Content-Disposition header with
 *      the filename.
 *      
 *   Example:    Content-Disposition: attachment; filename="toto.csv"
 * 
 * The text and appearance of the button can be changed with the initial 
 * datatable settings.
 * 
 *   Example:
 *    
 *      $('#my_table').dataTable({
 *          bStateSave: true,
 *  	    bProcessing: true,
 *  	    bServerSide: true,
 *          sAjaxSource: "/hr/members/data/",
 *          sPaginationType: "bootstrap",
 *          iDisplayLength: 25,
 *          bAutoWidth: false,
 *          sDom: '<<"span5"l><"span7"C>>rt<<"span5"i><"span7"p>>',
 *          oSaveAsCSV: {
 *              sButtonText: 'Download CSV',
 *              sButtonClass: 'button-small',
 *              sIconClass: 'icon-disk',
 *          },
 *      });
 *      
 * NB: the default settings are:
 * 
 *      oSaveAsCSV: {
 *          sButtonText: 'Save as CSV',
 *          sButtonClass: 'btn pull-right',
 *          sIconClass: 'icon-download-alt',
 *      },
 * 
 */
(function($, window, document) {

/* * * * * * * * * * * 
 * CONSTANTS
 * * * * * * * * * * */
var SaveAsCSV = {
	defaults: {
	    sButtonText: 'Save as CSV',
	    sButtonClass: 'btn pull-right',
	    sIconClass: 'icon-download-alt',
	},
};

/* * * * * * * * * * *
 * INIT PLUGIN
 * * * * * * * * * * */
if (typeof $.fn.dataTable == "function" &&
    typeof $.fn.dataTableExt.fnVersionCheck == "function" &&
    $.fn.dataTableExt.fnVersionCheck('1.8.0')
    )
{
    $.fn.dataTableExt.aoFeatures.push({
        fnInit: function(oDTSettings) {
            
        	var oOpts = typeof oDTSettings.oInit.oSaveAsCSV != 'undefined' ? 
    				oDTSettings.oInit.oSaveAsCSV : {};
    		oOpts = $.extend({}, SaveAsCSV.defaults, oOpts) 
    				
            var 
              nButton = document.createElement('button'),
              nIcon = document.createElement('i'),
              nText = document.createElement('span');
            
            nButton.setAttribute('id', oDTSettings.sInstance + '_csv_btn');
            nButton.className = oOpts.sButtonClass;
            nIcon.className = oOpts.sIconClass;
            nText.innerHTML = oOpts.sButtonText;

            nButton.appendChild(nIcon);
            nButton.appendChild(nText);
            
            $(nButton).on('click', function () {
                var aoAjaxParams = oDTSettings.oApi._fnAjaxParameters(oDTSettings);
                oDTSettings.oApi._fnServerParams(oDTSettings, aoAjaxParams);
                aoAjaxParams.push({
                    name: 'sFormat',
                    value: 'csv',
                })
                window.location = oDTSettings.sAjaxSource + '?' + $.param(aoAjaxParams);
            });
            
            
            return nButton;
        },
        cFeature: "C",
        sFeature: "SaveAsCSV"
    } );
}
else
{
    alert("Warning: SaveAsCSV requires DataTables 1.8.0 or greater - www.datatables.net/download");
}
 
})(jQuery, window, document);