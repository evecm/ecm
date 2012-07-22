/** "Members Access Change" table setup */
{% load static from staticfiles %}

function membersAccessRowCallback(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
    if (aData[0]) {
        $('td:eq(0)', nRow).html('<img src="{% static 'ecm/img/plus.png' %}"></img>');
    } else {
        $('td:eq(0)', nRow).html('<img src="{% static 'ecm/img/minus.png' %}"></img>');
    }
    return nRow;
}
