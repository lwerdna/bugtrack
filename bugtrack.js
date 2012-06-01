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
 * AJAX
 *****************************************************************************/
function ajax(url) {
    var xmlhttp = new XMLHttpRequest();
    debug("AJAX: " + url)
    xmlhttp.open("GET", url, false);
    xmlhttp.send()
    var resp = xmlhttp.responseText;
    debug("AJAX: " + resp)
    return resp
}

/******************************************************************************
 * global vars
 *****************************************************************************/
var elem_a1, elem_a2, elem_b1, elem_b2;
var elem_a1stats, elem_a2stats, elem_b1stats, elem_b2stats;
var elem_a1predict, elem_a2predict, elem_b1predict, elem_b2predict;

var playerNames = [];
var playerToR = [];
var playerToRD = [];
var playerToT = [];

/* called when the play page loads */
function playInit(x) {
    /* init global vars */
    elem_a1 = document.getElementById("a1");
    elem_a2 = document.getElementById("a2");
    elem_b1 = document.getElementById("b1");
    elem_b2 = document.getElementById("b2");

    elem_a1stats = document.getElementById("a1_stats");
    elem_a2stats = document.getElementById("a2_stats");
    elem_b1stats = document.getElementById("b1_stats");
    elem_b2stats = document.getElementById("b2_stats");

    elem_a1predict = document.getElementById("a1_predict");
    elem_a2predict = document.getElementById("a2_predict");
    elem_b1predict = document.getElementById("b1_predict");
    elem_b2predict = document.getElementById("b2_predict");

    /* populate the player drop-down */
    var resp = ajax("dbaccess.py?op=getplayers")
    var lines = resp.split("\n")
    for(var j in lines) {
        var m = lines[j].match(/^(.*),(.*),(.*),(.*)$/);

        if(m) {
            playerName = m[1];
            playerNames.push(playerName);
            playerToR[playerName] = parseInt(m[2])
            playerToRD[playerName] = parseInt(m[3])
            playerToT[playerName] = parseInt(m[4])
        }
    }

    playerNames.sort();
    var elems = [elem_a1, elem_a2, elem_b1, elem_b2];
    for(var i in elems) {
        elems[i].value = '';
        elems[i].innerHTML = '<option></option>';

        for(var j in playerNames) {
            elems[i].innerHTML += "<option>" + playerNames[j] + "</option>";
        }
    }
}

function selChange_cb(elem) {
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

    var enameToElemStats = []
    enameToElemStats["a1"] = elem_a1stats;
    enameToElemStats["a2"] = elem_a2stats;
    enameToElemStats["b1"] = elem_b1stats;
    enameToElemStats["b2"] = elem_b2stats;
    enameToElemStats[elem.id].innerHTML = playerToR[elem.value] + "." + playerToRD[elem.value]

    /**************************************************************************
        update predictions
    **************************************************************************/
    if(elem_a1.value && elem_a2.value && elem_b1.value && elem_b2.value) {
        var temp;
        var resp;

        var reqs = [
            /* a1 wins/loses */
            "play.py?op=predict&a1=" + elem_a1.value + "&a2=" + elem_a2.value + 
                "&b1=" + elem_b1.value + "&b2=" + elem_b2.value,
            /* a2 wins/loses */
            "play.py?op=predict&a1=" + elem_a2.value + "&a2=" + elem_a1.value + 
                "&b1=" + elem_b1.value + "&b2=" + elem_b2.value,
            /* b1 wins/loses */
            "play.py?op=predict&a1=" + elem_b1.value + "&a2=" + elem_b2.value + 
                "&b1=" + elem_a1.value + "&b2=" + elem_a2.value,
            /* b2 wins/loses */
            "play.py?op=predict&a1=" + elem_b2.value + "&a2=" + elem_b1.value + 
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

function recordGame(elem) {
    var xmlhttp = new XMLHttpRequest();
    var req = "?op=record&a1=" + elem_a1.value + "&a2=" + elem_a2.value +
              "&b1=" + elem_b1.value + "&b2=" + elem_b2.value;

    if(elem.name == "TeamAWins") {
        req += "&TeamAWins=1"
    }
    else if(elem.name == "TeamBWins") {
        req += "&TeamBWins=1"
    }

    debug("AJAX: " + req);
    xmlhttp.open("GET", req, false);
    xmlhttp.send();
    debug("AJAX: " + xmlhttp.responseText);

    if(elem.name == "TeamAWins") {
        alert("Win for " + elem_a1.value + " and " + elem_a2.value + " recorded!");
    }
    else if(elem.name == "TeamBWins") {
        alert("Win for " + elem_b1.value + " and " + elem_b2.value + " recorded!");
    }

    /* refresh selections */
    selChange_cb(elem_a1);
    selChange_cb(elem_a2);
    selChange_cb(elem_b1);
    selChange_cb(elem_b2);
}

function swapTeamA(elem)
{
    var elem_a1 = document.getElementsByName("a1")[0];
    var elem_a2 = document.getElementsByName("a2")[0];

    var temp = elem_a1.value;
    elem_a1.value = elem_a2.value;
    elem_a2.value = temp;

    selChange_cb(elem_a1);
    selChange_cb(elem_a2);

}

function clearTeamA(elem)
{
    var elem_a1 = document.getElementsByName("a1")[0];
    var elem_a2 = document.getElementsByName("a2")[0];

    elem_a1.value = ""
    elem_a2.value = ""

    selChange_cb(elem_a1);
    selChange_cb(elem_a2);
}

function swapTeamB(elem)
{
    var elem_b1 = document.getElementsByName("b1")[0];
    var elem_b2 = document.getElementsByName("b2")[0];

    var temp = elem_b1.value;
    elem_b1.value = elem_b2.value;
    elem_b2.value = temp;

    selChange_cb(elem_b1);
    selChange_cb(elem_b2);

}

function clearTeamB(elem)
{
    var elem_b1 = document.getElementsByName("b1")[0];
    var elem_b2 = document.getElementsByName("b2")[0];

    elem_b1.value = ""
    elem_b2.value = ""

    selChange_cb(elem_b1);
    selChange_cb(elem_b2);
}

