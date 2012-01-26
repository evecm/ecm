var positionsQueryString = '';
var positionsDataUrl = '';

google.load('visualization', '1', {
    packages : [ 'imagechart' ]
});


function extractLabels(dist) {
    var labels = new Array(3);
    labels[0] = POSITIONS['hisec'];
    labels[1] = POSITIONS['lowsec'];
    labels[2] = POSITIONS['nullsec'];
    return labels.join('|');
}

function onLoadCallback() {
    if (positionsDataUrl.length > 0) {
        var query = new google.visualization.Query(positionsDataUrl);
        query.setQuery(positionsQueryString);
        query.send(handleQueryResponse);
    } else {
        var dataTable = new google.visualization.DataTable();
        dataTable.addRows(3);
        dataTable.addColumn('number');
        dataTable.setValue(0, 0, POSITIONS['hisec']);
        dataTable.setValue(1, 0, POSITIONS['lowsec']);
        dataTable.setValue(2, 0, POSITIONS['nullsec']);
        draw(dataTable);
    }
}

function draw(dataTable) {
    var vis = new google.visualization.ImageChart(document.getElementById('positions_chart'));
    var options = {
        chxs : '0,676767,10.5',
        chxt : 'x',
        chs : '400x285',
        cht : 'p',
        chco : '60FC60|FCAF3B|FD5353',
        chd : 's:DfzHGYSH',
        chdl : 'Hi-Sec|Low-Sec|Null-Sec',
        chl : extractLabels(POSITIONS),
        chtt : 'Position of members'
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

google.setOnLoadCallback(onLoadCallback);
