$(document).ready(function() {
    $('#availability_checkbox').click(function () {
    	var params = {
    		available: $(this).is(':checked')
    	};
    	$.post('/industry/catalog/items/' + ITEM_ID + '/availability/', params)
    	 .error(function () {
    		alert('Failed to change availability!'); 
    	});
    });
    
    $('#price').editable('/industry/catalog/items/' + ITEM_ID + '/price/', {
        loadurl: '/industry/catalog/items/' + ITEM_ID + '/price/',
        width: 200,
        name: 'price',
        tooltip: 'Click to edit...'
    });
    
    setEditableHandlers();
});

function setEditableHandlers() {
    $('td.me').editable('/industry/catalog/blueprints/me/');
    $('td.pe').editable('/industry/catalog/blueprints/pe/');
    $('input.copy').click(function () {
        var thisId = $(this).attr('id');
        var checked = $(this).is(':checked');
        $.post('/industry/catalog/blueprints/copy/', {id: thisId, value: checked})
        .error(function () {
            alert('Failed to change copy!');
        });
    });
    $('td.runs').editable('/industry/catalog/blueprints/runs/');
}


EMPTY = '<tr id="empty"><td colspan="4" class="center">None</td></tr>';

function deleteBlueprint(blueprintID) {
    var row = $('#blueprints tr#' + blueprintID);
    if (confirm('Are you sure you want to delete this blueprint?')) {
        $.get('/industry/catalog/blueprints/' + blueprintID + '/delete/')
            .success(function () {
                $(row).remove();
                var rows =  $('#blueprints tr');
                if (rows.length == 0) {
                    $('#blueprints').html(EMPTY);
                }
            })
            .error(function () {
                alert('Failed to delete blueprint.');
            });
    }
}
NEW_BP = '<tr id="%id">' +
           '<td><a href="%url" title="Blueprint details">' +
             '<img src="http://image.eveonline.com/Type/%blueprintTypeID_32.png" />' +
           '</a></td>' +
           '<td class="me" id="%id">%me</td>' +
           '<td class="pe" id="%id">%pe</td>' +
           '<td><input class="copy" id="%id" type="checkbox" %checked/></td>' +
           '<td class="runs" id="%id">%runs</td>' +
           '<td><input class="button" type="button" value="Delete Blueprint" onClick="deleteBlueprint(%id);"/></td>' +
         '</tr>';
function addBlueprint(itemID) {
    $.getJSON('/industry/catalog/items/' + itemID + '/addblueprint/')
        .success(function(json) {
            $('#empty').remove();
            var checked;
            if (json['copy']) {
                checked = 'checked';
            } else {
                checked = '';
            }
            var row = NEW_BP.replace(/%id/g, json['id'])
                            .replace(/%url/g, json['url'])
                            .replace(/%blueprintTypeID/g, json['blueprintTypeID'])
                            .replace(/%me/g, json['me'])
                            .replace(/%pe/g, json['pe'])
                            .replace(/%checked/g, checked)
                            .replace(/%runs/g, json['runs']);
            $(row).appendTo("#blueprints")
        }).error(function () {
            alert('Failed to add blueprint.');
        });
}

