

NEW_ITEM = '<tr id="%typeID">' + 
             '<td class="center"><img src="http://image.eveonline.com/Type/%typeID_32.png" /></td>' +
             '<td class="bold">%typeName</td>' +
             '<td class="center"><input type="text" name="%typeID" value="1" /></td>' + 
             '<td class="center"><img src="/m/img/trash.png" class="clickable" onClick="javascript:removeItem(this);"/></td>' + 
           '</tr>';
EMPTY = '<tr id="empty"><td colspan="4" class="order_cart_empty" >Your shopping cart is empty.</td></tr>';

$().ready(function() {
    $("#search_box").autocomplete("/industry/search/data", {
        minChars: 3,
        selectFirst: true,
        width: 300
    });
    /* trigger the search when pressing return in the text field */
    $("#search_form").submit(function(event) {
        event.preventDefault();
        addItem($("#search_box").val());
    });

    /* trigger the search when clicking the "search" button */
    $("#add_button").click(function() {
        addItem($("#search_box").val());
    });
    
});

function removeItem(img_node) {
    var row = img_node.parentNode.parentNode;
    var typeName = $('td:eq(1)', row).text();
    if (confirm('Are you sure you want to remove "' + typeName + '" from your order?')) {
        $(row).remove();
        var rows =  $('#items tr');
        if (rows.length == 0) {
            $('#items').html(EMPTY);
        }
    }
}

function addItem(name) {
    $.getJSON("/industry/search/itemid", {q: name}, function(json) {
        var typeID = json[0];
        var typeName = json[1];
        
        $('#empty').remove();

        var rows =  $('#items tr');
        for (var i = 0 ; i < rows.length ; i++) {
            if (rows[i].id == typeID) {
                var qty = parseInt($('td:eq(2) input').val());
                $('td:eq(2) input', rows[i]).val(qty + 1);
                $("#search_box").val("");
                return;
            }
        }
        
        var row = NEW_ITEM.replace(/%typeID/g, typeID).replace(/%typeName/g, typeName);
        $(row).appendTo("#items")
        $("#search_box").val("");
    }).error(function () {
        alert('Item "' + name + '" is not available in the shop!');
    });
}

