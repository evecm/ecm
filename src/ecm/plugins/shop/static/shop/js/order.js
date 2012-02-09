
NEW_ITEM = '<tr id="%typeID">' +
             '<td class="center"><img src="http://image.eveonline.com/Type/%typeID_32.png" /></td>' +
             '<td class="bold">%typeName</td>' +
             '<td class="right price" price="%price">%formattedPrice</td>' +
             '<td class="center"><input type="text" name="%typeID" value="%quantity" /></td>' +
             '<td class="center"><img src="/s/industry/img/trash.png" class="clickable" onClick="javascript:removeItem(this);"/></td>' +
           '</tr>';
EMPTY = '<tr id="empty"><td colspan="4" class="order_cart_empty" >Your shopping cart is empty.</td></tr>';

function removeItem(img_node) {
    var row = img_node.parentNode.parentNode;
    var typeName = $('td:eq(1)', row).text();
    if (confirm('Are you sure you want to remove "' + typeName + '" from your order?')) {
        $(row).remove();
        var rows =  $('#items tr');
        if (rows.length == 0) {
            $('#items').html(EMPTY);
        }
        updateTotal();
    }
}

function addItem(name) {
    if (name == '') {
        return;
    }
    $.getJSON("/shop/utils/itemid/", {q: name}, function(json) {
        var typeID = json[0];
        var typeName = json[1];
        var price = json[2];
        appendItemToOrder(typeID, typeName, 1, price);
        $("#search_box").val("");
        updateTotal();
    }).error(function () {
        alert('Item "' + name + '" is not available in the shop!');
    });
}

function appendItemToOrder(typeID, typeName, quantity, price) {
    $('#empty').remove();
    var rows =  $('#items tr');
    var formattedPrice = 'N/A';
    if (price != null) {
        formattedPrice = (price).formatMoney();
    }
    for (var i = 0 ; i < rows.length ; i++) {
        if (parseInt(rows[i].id) == parseInt(typeID)) {
            var qty = parseInt($('td:eq(3) input', rows[i]).val());
            $('td:eq(2)', rows[i]).text(formattedPrice);
            $('td:eq(2)', rows[i]).attr('price', price);
            $('td:eq(3) input', rows[i]).val(qty + quantity);
            return;
        }
    }
    var row = NEW_ITEM.replace(/%typeID/g, typeID)
                      .replace(/%typeName/g, typeName)
                      .replace(/%quantity/g, quantity)
                      .replace(/%formattedPrice/g, formattedPrice)
                      .replace(/%price/g, price);
    
    $(row).appendTo("#items");
    $('#' + typeID + ' td:eq(3) input').change(updateTotal);
}

function updateTotal() {
    var total = 0.0;
    var rows =  $('#items tr');
    var price = 0.0;
    for (var i = 0; i < rows.length; i++) {
        if (rows[i].id != 'empty') {
            var price = $('td.price', rows[i]).attr('price');
            var qty = $('td:eq(3) input', rows[i]).val();
            if (price == 'null') {
                $('span#total_price').text('N/A');
                return;
            } else {
                total += parseFloat(price) * parseInt(qty);
            }
        }
    }
    $('span#total_price').text((total).formatMoney() + ' ISK');
}


$(document).ready(function() {
    $("#search_box").autocomplete("/shop/utils/search/", {
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

    /* avoid submitting empty orders */
    $("#items_form").submit(function(event) {
        if ($('#empty').length > 0) {
            event.preventDefault();
        } else {
            $('#throbber-submit').show();
        }
    });
    
    /*select all the a tag with name equal to modal*/
    $('a#import-eft').click(function(event) {
        event.preventDefault();
     
        /*transition effect  */   
        $('div#eft-mask').fadeIn(500);    
     
        /*Get the window height and width*/
        var winH = $(window).height();
        var winW = $(window).width();
               
        /*Set the popup window to center*/
        $('div#eft-dialog').css({
            'top':  winH/2 - $('#eft-dialog').height()/2,
            'left': winW/2 - $('#eft-dialog').width()/2
        });
     
        /*transition effect*/
        $('div#eft-dialog').fadeIn(300); 
     
    });
     
    /*if close button is clicked*/
    $('a#eft-close').click(function (event) {
        event.preventDefault();
        $('div#eft-mask, div#eft-dialog').fadeOut(300);
    });     
     
    /*if mask is clicked*/
    $('div#eft-mask').click(function () {
        $('div#eft-mask, div#eft-dialog').fadeOut(300);
    });
    
    /* reposition the modal window and recalculate the dimension 
       of mask if user resized the windows */
    $(window).resize(function () {
        /*Get the window height and width*/
        var winH = $(window).height();
        var winW = $(window).width();
        var dialog = $('div#eft-dialog');
        /*Set the popup window to center*/
        dialog.css({
            'top':  winH/2 - dialog.height()/2,
            'left': winW/2 - dialog.width()/2
        });
    });
    
    /* when eft modal dialog is submited */
    $('a#eft-submit').click(function (event) {
        event.preventDefault();
        
        $('div#eft-mask, div#eft-dialog').fadeOut(300);
        $('#throbber').show();
        $.post('/shop/utils/parseeft/', {
            'eft_block': $('#eft-block').val(),
            'quantity': $('#eft-quantity').val()
         })
         .success(function (data) {
             for (var i=0; i < data.length; i++) {
                 appendItemToOrder(data[i].typeID, 
                                   data[i].typeName, 
                                   data[i].quantity, 
                                   data[i].price);
             }
             updateTotal();
             $('#eft-block').val('');
             $('#eft-quantity').val('1')
         })
         .error(function () {
             alert('Error while parsing EFT fitting!');
         })
         .complete(function () {
             $('#throbber').hide();
         });
    });
});
