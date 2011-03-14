function getAccessColor(accessLvl, colorThresholds) {
	for (var i=1 ; i < colorThresholds.length ; i++) {
        if (accessLvl <= colorThresholds[i]["threshold"]) {
        	return colorThresholds[i]["color"];
        }
    }
    return colorThresholds[0]["color"];
}