/**
 * Get a color from a security access level. The function returns the first color 
 * for which the threshold is less than the given access level. 
 * 
 * @param accessLvl
 *          integer
 * @param colorThresholds
 *          a list of color thresholds (ordered by increasing threshold) such as this 
 *          [{ "color" : "blue", "threshold" : 5000 }, { "color" : "red", "threshold" : 300000 }]
 * @returns a color
 */
function getAccessColor(accessLvl, colorThresholds) {
  for (var i=0 ; i < colorThresholds.length ; i++) {
        if (accessLvl <= colorThresholds[i]["threshold"]) {
          return colorThresholds[i]["color"];
        }
    }
    return "";
}


/**
 * Retrieve a css background-color property from the current page
 * 
 * @param cssSelector
 *          
 * @returns the property value formatted in hex #4d581e
 */
function getCssBgColor(cssSelector) {
    for (var j=0 ; j < document.styleSheets.length ; j++) {
        var rules = document.styleSheets.item(j);
        rules = rules.cssRules || rules.rules;
        for (var i = 0; i < rules.length; i++) {
            if (rules.item(i).selectorText == cssSelector) {
                return colorToHex(rules.item(i).style.backgroundColor);
            }
        }
    }
    return "#000000";
}


function colorToHex(color) {
    if (color === '') {
        return 'transparent';
    } else if (color.substr(0, 1) === '#') {
        return color;
    }
    var digits = /(.*?)rgb\((\d+), (\d+), (\d+)\)/.exec(color);
    
    var red = parseInt(digits[2]);
    var green = parseInt(digits[3]);
    var blue = parseInt(digits[4]);
    
    var rgb = blue | (green << 8) | (red << 16);
    return digits[1] + '#' + rgb.toString(16);
};

//+ Jonas Raoni Soares Silva
//@ http://jsfromhell.com/number/fmt-money [rev. #2]
Number.prototype.formatMoney = function(c, d, t){
    var n = this, c = isNaN(c = Math.abs(c)) ? 2 : c, d = d == undefined ? "." : d, t = t == undefined ? "," : t, s = n < 0 ? "-" : "",
    i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", j = (j = i.length) > 3 ? j % 3 : 0;
    return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t)
    + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
};

var DATATABLE_DEFAULTS = {
    sPaginationType: 'bootstrap',
    bProcessing: true,
    bServerSide: true,
    bAutoWidth: false,
    iDisplayLength: 25,         /* default display 25 items */
    bStateSave: true,       /* table state persistance */
    iCookieDuration: 60 * 60, /* persistance duration 1 hour */
    sDom: "<'row-fluid'<'span5'l><'span7'p>>rt<'row-fluid'<'span5'i><'span7'p>>",

    /* the search field being outside the table object, we need to save its status
     * explicitly here in order to restore it with the rest */
    fnStateSaveParams: function (oSettings, oData) {
        oData.sFilter = $('#search_text').val()
    },
    /* restore the search field content */
    fnStateLoadParams: function (oSettings, oData) {
        $('#search_text').val(oData.sFilter);
        return true;
    },
    oLanguage: {
        sLengthMenu: '_MENU_ lines per page',
        sZeroRecords: 'Nothing found to display - sorry.',
        sInfo: 'Showing _START_ to _END_ of _TOTAL_ records',
        sInfoEmpty: 'Showing 0 to 0 of 0 records',
        sInfoFiltered: '(filtered from _MAX_ total records)'
    }
};




$(function() {
    //ini plugin
    jQuery.event.freezeEvents = function(elem) {
        if (typeof (jQuery._funcFreeze) == "undefined")
            jQuery._funcFreeze = [];

        if (typeof (jQuery._funcNull) == "undefined")
            jQuery._funcNull = function() {
            };
        // don't do events on text and comment nodes
        if (elem.nodeType == 3 || elem.nodeType == 8)
            return;
        var events = jQuery.data(elem, "events"), ret, index;
        if (events) {
            for ( var type in events) {
                if (events[type]) {
                    var namespaces = type.split(".");
                    type = namespaces.shift();
                    var namespace = RegExp("(^|\\.)" + namespaces.slice().sort().join(".*\\.")
                            + "(\\.|$)");
                    for ( var handle in events[type]) {
                        if (namespace.test(events[type][handle].type)) {
                            if (events[type][handle] != jQuery._funcNull) {
                                jQuery._funcFreeze["events_freeze_" + handle] = events[type][handle];
                                events[type][handle] = jQuery._funcNull;
                            }
                        }
                    }
                }
            }
        }
    }
    jQuery.event.unFreezeEvents = function(elem) {
        // don't do events on text and comment nodes
        if (elem.nodeType == 3 || elem.nodeType == 8)
            return;
        var events = jQuery.data(elem, "events"), ret, index;
        if (events) {
            for ( var type in events) {
                if (events[type]) {
                    var namespaces = type.split(".");
                    type = namespaces.shift();
                    for ( var handle in events[type]) {
                        if (events[type][handle] == jQuery._funcNull)
                            events[type][handle] = jQuery._funcFreeze["events_freeze_" + handle];
                    }
                }
            }
        }
    }
    jQuery.fn.freezeEvents = function() {
        return this.each(function() {
            jQuery.event.freezeEvents(this);
        });
    };
    jQuery.fn.unFreezeEvents = function() {
        return this.each(function() {
            jQuery.event.unFreezeEvents(this);
        });
    };
    //end plugin
});



