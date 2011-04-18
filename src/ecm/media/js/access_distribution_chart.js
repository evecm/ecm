var queryString = '';
var dataUrl = '';

function extractColors(dist) {
    var colors = new Array(dist.length);
    for (var i=0 ; i < dist.length ; i++) {
        var color = getCssProperty(".row-" + dist[i]["color"], "background-color");
        if (color.lastIndexOf("#", 0) === 0) {
            color = color.substr(1);
        }
        colors[i] = color;
    }
    return colors.join("|");
}

function extractLegend(dist) {
    var legends = new Array(dist.length);
    for (var i=0 ; i < dist.length ; i++) {
        if (dist[i]["threshold"] == 0) {
            legends[i] = "No Roles";
        } else if (dist[i]["threshold"] == DIRECTOR_ACCESS_LVL) {
            legends[i] = "Directors";
        } else {
            legends[i] = "level < " + dist[i]["threshold"];
        }
    }
    return legends.join("|");
}


function extractLabels(dist) {
    var labels = new Array(dist.length);
    for (var i=0 ; i < dist.length ; i++) {
        labels[i] = dist[i]["members"];
    }
    return labels.join("|");
}

function onLoadCallback() {
    if (dataUrl.length > 0) {
        var query = new google.visualization.Query(dataUrl);
        query.setQuery(queryString);
        query.send(handleQueryResponse);
    } else {
        var dataTable = new google.visualization.DataTable();
        dataTable.addRows(DISTRIBUTION.length);
        dataTable.addColumn('number');
        for (var i=0 ; i < DISTRIBUTION.length ; i++) {
            dataTable.setValue(i, 0, DISTRIBUTION[i]["members"]);
        }
        draw(dataTable);
    }
}

function draw(dataTable) {
    var vis = new google.visualization.ImageChart(document.getElementById('distibution_chart'));
    var options = {
        chxs : '0,676767,10.5',
        chxt : 'x',
        chs : '450x285',
        cht : 'p',
        chco : extractColors(DISTRIBUTION),
        chd : 's:DfzHGYSH',
        chdl : extractLegend(DISTRIBUTION),
        chl : extractLabels(DISTRIBUTION),
        chtt : 'Security access level distribution'
    };
    vis.draw(dataTable, options);
}

function handleQueryResponse(response) {
    if (response.isError()) {
        alert('Error in query: ' + response.getMessage() + ' ' + response.getDetailedMessage());
        return;
    }
    draw(response.getDataTable());
}

google.load("visualization", "1", {
    packages : [ "imagechart" ]
});
google.setOnLoadCallback(onLoadCallback);