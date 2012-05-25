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
    var elem_a1 = document.getElementsByName("a1")[0];
    var elem_a2 = document.getElementsByName("a2")[0];
    var elem_b1 = document.getElementsByName("b1")[0];
    var elem_b2 = document.getElementsByName("b2")[0];

    var elem_a1stats = document.getElementById("a1_stats");
    var elem_a2stats = document.getElementById("a2_stats");
    var elem_b1stats = document.getElementById("b1_stats");
    var elem_b2stats = document.getElementById("b2_stats");

    var elem_a1predict = document.getElementById("a1_predict");
    var elem_a2predict = document.getElementById("a2_predict");
    var elem_b1predict = document.getElementById("b1_predict");
    var elem_b2predict = document.getElementById("b2_predict");

    /* force other drop downs away from the name we just selected */
    var elems = [elem_a1, elem_a2, elem_b1, elem_b2];
    var elems_stats = [elem_a1stats, elem_a2stats, elem_b1stats, elem_b2stats];
    var elems_predict = [elem_a1predict, elem_a2predict, elem_b1predict, elem_b2predict];

    for(var i=0; i<4; ++i) {
        if(elem != elems[i] && elem.value == elems[i].value) {
	        /* this works in chrome, firefox */
            elems[i].value = "";
            /* this works in kindle fire browser */
	        elems[i].options.selectedIndex = 0;

            /* clear also the stats */
            elems_stats[i].innerHTML = "";
        }
    }

    /* update statistics of the player selected */
    if(elem.value != "") {
        var xmlhttp = new XMLHttpRequest();
        var reqText = "index.py?op=getstats&player=" + elem.value;
        debug("AJAX: " + reqText)
        xmlhttp.open("GET", reqText, false);
        xmlhttp.send()
        var resp = xmlhttp.responseText;
        debug("AJAX: " + resp)
        stats = resp.split(",")
    }
    else {
        stats = 0
    }

    var enameToElemStats = new Array()
    enameToElemStats["a1"] = elem_a1stats;
    enameToElemStats["a2"] = elem_a2stats;
    enameToElemStats["b1"] = elem_b1stats;
    enameToElemStats["b2"] = elem_b2stats;
    if(stats) {
        enameToElemStats[elem.name].innerHTML = stats[0] + "." + stats[1]
    }
    else {
        enameToElemStats[elem.name] = ""
    }

    /**************************************************************************
        update predictions
    **************************************************************************/
    if(elem_a1.value && elem_a2.value && elem_b1.value && elem_b2.value) {
        var temp;
        var resp;

        var reqs = [
            /* a1 wins/loses */
            "index.py?op=predict&a1=" + elem_a1.value + "&a2=" + elem_a2.value + 
                "&b1=" + elem_b1.value + "&b2=" + elem_b2.value,
            /* a2 wins/loses */
            "index.py?op=predict&a1=" + elem_a2.value + "&a2=" + elem_a1.value + 
                "&b1=" + elem_b1.value + "&b2=" + elem_b2.value,
            /* b1 wins/loses */
            "index.py?op=predict&a1=" + elem_b1.value + "&a2=" + elem_b2.value + 
                "&b1=" + elem_a1.value + "&b2=" + elem_a2.value,
            /* b2 wins/loses */
            "index.py?op=predict&a1=" + elem_b2.value + "&a2=" + elem_b1.value + 
                "&b1=" + elem_a1.value + "&b2=" + elem_a2.value,
        ];

        for(var i=0; i<4; ++i) {
            var xmlhttp = new XMLHttpRequest();
            debug("AJAX: " + reqs[i])
            xmlhttp.open("GET", reqs[i], false);
            xmlhttp.send()
            var resp = xmlhttp.responseText
            debug("AJAX: " + resp)
            resp.replace(/[\r\n]$/, "")
            vals = resp.split(",")
            elems_predict[i].innerHTML = "<font color=green>+" + vals[0] + "</font> <font color=red>" + vals[1] + "</font>"
        }
    }
    else {
        for(var i=0; i<4; ++i) {
            elems_predict[i].innerHTML = ""
        }
    }
}

