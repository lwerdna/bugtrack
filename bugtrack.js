/******************************************************************************
 * globals
 *****************************************************************************/
// [0,3] from least to greatest
var g_DEBUG_LEVEL = 1;

function debug3(msg) {
    if(g_DEBUG_LEVEL >= 3) {
        console.log(msg);
    }
}

function debug2(msg) {
    if(g_DEBUG_LEVEL >= 2) {
        console.log(msg);
    }
}

function debug1(msg) {
    if(g_DEBUG_LEVEL >= 1) {
        console.log(msg);
    }
}

function debug0(msg) {
    console.log(msg);
}

function debug(msg) {
    console.log(msg);
}

/******************************************************************************
 * DOM junk
 *****************************************************************************/
function selChange_cb(elem) {
    var elem_a1 = document.getElementsByName("TeamA_Player1")[0]
    var elem_a2 = document.getElementsByName("TeamA_Player2")[0]
    var elem_b1 = document.getElementsByName("TeamB_Player1")[0]
    var elem_b2 = document.getElementsByName("TeamB_Player2")[0]

    /* force other drop downs away from the name we just selected */
    var elems = [elem_a1, elem_a2, elem_b1, elem_b2]
    for(var i=0; i<4; ++i) {
        if(elem != elems[i] && elem.value == elems[i].value) {
	    /* this works in chrome, firefox */
            elems[i].value = "";
            /* this works in kindle fire browser */
	    elems[i].options.selectedIndex = 0;
        }
    }

    /* update predictions */
    var elem_predictA = document.getElementById("teamAPrediction")
    var elem_predictB = document.getElementById("teamBPrediction")

    if(elem_a1.value && elem_a2.value && elem_b1.value && elem_b2.value) {
        /* ajax a request back to the script */
        var xmlhttp = new XMLHttpRequest();
        // document.location.pathname is everything after the url
        // eg: "http://localhost:2048/index.html"
        //   -> document.location.pathname is "/index.html" (including slash)
        var reqText = "index.py?op=predict" + 
            "&TeamA_Player1=" + elem_a1.value + "&TeamA_Player2=" + elem_a2.value + 
            "&TeamB_Player1=" + elem_b1.value + "&TeamB_Player2=" + elem_b2.value

        xmlhttp.open("GET", reqText, false);
        // xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xmlhttp.send();

        var resp = xmlhttp.responseText;
        resp = resp.replace(/[\r\n]$/, "")
        vals = resp.split(",")

        elem_predictA.innerHTML = "<font color=green>+" + vals[0] + "</font> (opp. gets " + vals[3] + ")"
        elem_predictB.innerHTML = "<font color=green>+" + vals[2] + "</font> (opp. gets " + vals[1] + ")"
    }
    else {
        elem_predictA.innerHTML = ""
        elem_predictB.innerHTML = ""
    }
}

