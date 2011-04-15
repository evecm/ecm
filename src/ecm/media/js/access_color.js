/**
 * Return a color from a security access level given a list of color thresholds 
 * (ordered by increasing threshold)
 * 
 * A color threshold must be a hashmap with 2 elements such as this one:
 *          { "color" : "blue", "threshold" : 51245 }
 * 
 * The function returns the first color for which the threshold is less than 
 * the given access level.
 */

function getAccessColor(accessLvl, colorThresholds) {
	  for (var i=1 ; i < colorThresholds.length ; i++) {
        if (accessLvl <= colorThresholds[i]["threshold"]) {
        	return colorThresholds[i]["color"];
        }
    }
    return "";
}