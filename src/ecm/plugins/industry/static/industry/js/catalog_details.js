function numbersonly(e) {
    var key;
    var keychar;

    if (window.event)
       key = window.event.keyCode;
    else if (e)
       key = e.which;
    else
       return true;

    // control keys
    if ((key==null) || (key==0) || (key==8) || (key==9) || (key==13) || (key==27) )
       return true;

    keychar = String.fromCharCode(key);
    // numbers
    if ((("-0123456789").indexOf(keychar) > -1))
       return true;

    else
       return false;
}
