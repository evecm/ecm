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
    if (color.substr(0, 1) === '#') {
        return color;
    }
    var digits = /(.*?)rgb\((\d+), (\d+), (\d+)\)/.exec(color);
    
    var red = parseInt(digits[2]);
    var green = parseInt(digits[3]);
    var blue = parseInt(digits[4]);
    
    var rgb = blue | (green << 8) | (red << 16);
    return digits[1] + '#' + rgb.toString(16);
};