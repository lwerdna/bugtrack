/******************************************************************************
 * debug
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
 * UTILS
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

// stackoverflow, thx Shef!
function zfill(num, len) {
    return (Array(len).join("0") + num).slice(-len);
}

function longAgoStr(epoch) {
    var answer = ''
    var delta = (new Date().getTime() / 1000) - epoch

    if (delta < 60) {
        answer = delta + ' seconds';
    }
    else if (delta < 3600) {
        answer = (delta / 60).toFixed(1) + ' minutes';
    }
    else if (delta < 86400) {
        answer = (delta / 3600).toFixed(1) + ' hours';
    }
    else if (delta < 2592000) {
        answer = (delta / 86400).toFixed(1) + ' days';
    }
    else if (delta < 31536000) {
        answer = (delta / 2592000).toFixed(1) + ' months';
    }
    else {
        answer = (delta / 31536000.0).toFixed(1) + ' years';
    }

    return answer
}

function dateToString(d) {
    var wDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    var hours = d.getHours()

    var amPm = 'AM'

    if(hours > 12) {
        amPm = 'PM';
        hours -= 12;
    } 

    return wDays[d.getDay()] + ' ' + months[d.getMonth()] + ' ' + d.getDate() + ', ' + (1900+d.getYear()) +
        ' ' + hours + ':' + zfill(d.getMinutes(), 2) + amPm;
}

/******************************************************************************
 * global vars
 *****************************************************************************/

/* overall */
var showElems = [];

/* important play elems */
var elem_a1, elem_a2, elem_b1, elem_b2;
var elem_a1stats, elem_a2stats, elem_b1stats, elem_b2stats;
var elem_a1predict, elem_a2predict, elem_b1predict, elem_b2predict;

var playerElems = [];
var playerNames = [];
var playerToR = [];
var playerToRD = [];
var playerToT = [];

/* istats */
var elem_istatsPlayerChoice;

/******************************************************************************
 * inner-mode functions
 *****************************************************************************/

/* called when the page loads */
function bugtrackInit(x) {
    /* overall modes; play is the default */
    showElems.push(document.getElementById("play"));
    showElems.push(document.getElementById("stats"));
    showElems.push(document.getElementById("istats"));
    showElems.push(document.getElementById("games"));
    showElems.push(document.getElementById("admin"));
    showPlay();

    /* individual stats mode */
    elem_istatsPlayerChoice = document.getElementById("istatsPlayerChoice");

    /* play mode */
    elem_a1 = document.getElementById("a1");
    elem_a2 = document.getElementById("a2");
    elem_b1 = document.getElementById("b1");
    elem_b2 = document.getElementById("b2");
    playerElems = [elem_a1, elem_a2, elem_b1, elem_b2];

    elem_a1stats = document.getElementById("a1_stats");
    elem_a2stats = document.getElementById("a2_stats");
    elem_b1stats = document.getElementById("b1_stats");
    elem_b2stats = document.getElementById("b2_stats");

    elem_a1predict = document.getElementById("a1_predict");
    elem_a2predict = document.getElementById("a2_predict");
    elem_b1predict = document.getElementById("b1_predict");
    elem_b2predict = document.getElementById("b2_predict");

    /* init global player vars */
    var resp = ajax('jsIface.py?op=getplayers')
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

    /* populate player choice drop-downs */
    playerNames.sort();
    var elems = [elem_a1, elem_a2, elem_b1, elem_b2, istatsPlayerChoice];
    for(var i in elems) {
        elems[i].value = '';
        elems[i].innerHTML = '<option></option>';

        for(var j in playerNames) {
            elems[i].innerHTML += "<option>" + playerNames[j] + "</option>";
        }
    }

    /* populate the ratings */
    playShowRatings();

    /* populate the predictions */
    playShowPredictions();
}

function hideAllBut(e) {
    for(var i in showElems) {
        if(showElems[i] == e) {
            showElems[i].style.display = 'block';
        }
        else {
            showElems[i].style.display = 'none';
        }
    }
}

function showPlay() {
    hideAllBut(document.getElementById('play'));
}

function showStats() {
    hideAllBut(document.getElementById('stats'));

    // each graph has a function dedicated to loading it...
    loadAllRatingsVsGamesGraph();
    loadAllRatingsHistoryGraph();
}

function showIStats() {
    hideAllBut(document.getElementById('istats'));

    // graphs don't load until user makes player selection 
}

function showGamesList() {
    hideAllBut(document.getElementById('games'));

    loadGamesList();
}

function showAdmin() {
    hideAllBut(document.getElementById('admin'));
}

/******************************************************************************
 * PLAY MODE stuff
 *****************************************************************************/
function playClearPredicts(x) {
    elem_a1predict.innerHTML = "";
    elem_a2predict.innerHTML = "";
    elem_b1predict.innerHTML = "";
    elem_b2predict.innerHTML = "";
}

function playShowRatings() {
    /* update statistics (rating.rd) */
    var enameToElemStats = []
    enameToElemStats["a1"] = elem_a1stats;
    enameToElemStats["a2"] = elem_a2stats;
    enameToElemStats["b1"] = elem_b1stats;
    enameToElemStats["b2"] = elem_b2stats;

    for(var i in playerElems) {
        if(playerElems[i].value) {
            enameToElemStats[playerElems[i].id].innerHTML = 
                playerToR[playerElems[i].value] + "." + playerToRD[playerElems[i].value]
        }

        else {
            /* user chose the initial blank entry */
            enameToElemStats[playerElems[i].id].innerHTML = ""
        }
    }
}

function playShowPredictions() {
    // if all 4 players are selected, make game prediction
    if(elem_a1.value && elem_a2.value && elem_b1.value && elem_b2.value) {
        var ratings = []
        var rds = []
        var ts = []

        for(var i in playerElems) {
            ratings.push(playerToR[playerElems[i].value]);
            rds.push(playerToRD[playerElems[i].value]);
            ts.push(playerToT[playerElems[i].value]);
        }

        var deltas = []

        /* if a1 wins */
        delta = calcRatingWinLossDeltaPlayer(ratings, rds, ts);
        elem_a1predict.innerHTML = "<font color=green>+" + delta[0] + "</font> " + 
                                    "<font color=red>" + delta[1] + "</font>"
        /* if a2 wins */
        ratings = [ratings[1], ratings[0], ratings[2], ratings[3]];
        rds = [rds[1], rds[0], rds[2], rds[3]];
        ts = [ts[1], ts[0], ts[2], ts[3]];
        delta = calcRatingWinLossDeltaPlayer(ratings, rds, ts);
        elem_a2predict.innerHTML = "<font color=green>+" + delta[0] + "</font> " + 
                                    "<font color=red>" + delta[1] + "</font>"

        /* if b1 wins */
        ratings = [ratings[2], ratings[3], ratings[1], ratings[0]];
        rds = [rds[2], rds[3], rds[1], rds[0]];
        ts = [ts[2], ts[3], ts[1], ts[0]];
        delta = calcRatingWinLossDeltaPlayer(ratings, rds, ts);
        elem_b1predict.innerHTML = "<font color=green>+" + delta[0] + "</font> " + 
                                    "<font color=red>" + delta[1] + "</font>"

        /* if b2 wins */
        ratings = [ratings[1], ratings[0], ratings[2], ratings[3]];
        rds = [rds[1], rds[0], rds[2], rds[3]];
        ts = [ts[1], ts[0], ts[2], ts[3]];
        delta = calcRatingWinLossDeltaPlayer(ratings, rds, ts);
        elem_b2predict.innerHTML = "<font color=green>+" + delta[0] + "</font> " + 
                                    "<font color=red>" + delta[1] + "</font>"
    }
    // otherwise clear the predictions
    else {
        playClearPredicts(); 
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
            elems_predict[i].innerHTML = "";
        }
    }

    /* populate ratings */
    playShowRatings();

    /* possibly (if 4 players) show game predictions */
    playShowPredictions();
}

function recordGame(elem) {
    var xmlhttp = new XMLHttpRequest();
    var req = "?op=record&a1=" + elem_a1.value + "&a2=" + elem_a2.value +
              "&b1=" + elem_b1.value + "&b2=" + elem_b2.value;

    var a1a2b1b2 = []
    var ratings = []
    var rds = []
    var ts = []
    var rps = []

    for(var i in playerElems) {
        a1a2b1b2.push(playerElems[i].value)
        ratings.push(playerToR[playerElems[i].value]);
        rds.push(playerToRD[playerElems[i].value]);
        ts.push(playerToT[playerElems[i].value]);
    }

    if(elem.name == "TeamAWins") {
        /* then arrays are in correct order */
    }
    else {
        /* position winner in locations [0], [1] */
        a1a2b1b2 = [a1a2b1b2[2], a1a2b1b2[3], a1a2b1b2[0], a1a2b1b2[1]]
        ratings = [ratings[2], ratings[3], ratings[0], ratings[1]]
        rd = [rd[2], rd[3], rd[0], rd[1]]
        ts = [ts[2], ts[3], ts[0], ts[1]]
    }
    
    /* convert those last-time-played timestamps to rating periods */
    var tNow = Math.round((new Date()).getTime() / 1000);

    for(var i in ts) {
        rps.push(secToRatingPeriods(tNow - ts[i]));
    }

    /* build the ajax request */
    var req = 'jsIface.py?op=recordGame'

    /* game stats: players, OLD r's, OLD rd's */
    req += '&t=' + tNow;
    req += '&a1=' + a1a2b1b2[0] + "&a1_r=" + playerToR[a1a2b1b2[0]] + "&a1_rd=" + playerToRD[a1a2b1b2[0]];
    req += '&a2=' + a1a2b1b2[1] + "&a2_r=" + playerToR[a1a2b1b2[1]] + "&a2_rd=" + playerToRD[a1a2b1b2[1]];
    req += '&b1=' + a1a2b1b2[2] + "&b1_r=" + playerToR[a1a2b1b2[2]] + "&b1_rd=" + playerToRD[a1a2b1b2[2]];
    req += '&b2=' + a1a2b1b2[3] + "&b2_r=" + playerToR[a1a2b1b2[3]] + "&b2_rd=" + playerToRD[a1a2b1b2[3]];
    
    /* new scores, ratings */
    var results = calcGameScores(ratings, rds, rps);

    req += "&a1_r_new=" + results[0][0] + "&a1_rd_new=" + results[0][1];
    req += "&a2_r_new=" + results[1][0] + "&a2_rd_new=" + results[1][1];
    req += "&b1_r_new=" + results[2][0] + "&b1_rd_new=" + results[2][1];
    req += "&b2_r_new=" + results[3][0] + "&b2_rd_new=" + results[3][1];

    /* do it! */
    ajax(req);

    /* message */
    if(elem.name == "TeamAWins") {
        alert("Win for " + elem_a1.value + " and " + elem_a2.value + " recorded!");
    }
    else if(elem.name == "TeamBWins") {
        alert("Win for " + elem_b1.value + " and " + elem_b2.value + " recorded!");
    }

    /* now also update the global vars */
    for(var i in a1a2b1b2) {
        playerToR[a1a2b1b2[i]] = results[i][0];
        playerToRD[a1a2b1b2[i]] = results[i][1];
        playerToT[a1a2b1b2[i]] = tNow;
    } 

    /* refresh */
    playShowRatings();
    playShowPredictions();
}

function swapElemVals(a, b)
{
    var t = a.value;
    a.value = b.value;
    b.value = t;
}

function swapElemHTML(a, b)
{
    var t = a.innerHTML;
    a.innerHTML = b.innerHTML;
    b.innerHTML = t;
}

function swapTeamA(elem)
{
    swapElemVals(elem_a1, elem_a2);
    swapElemHTML(elem_a1stats, elem_a2stats);
    swapElemHTML(elem_a1predict, elem_a2predict);
}

function clearTeamA(elem)
{
    elem_a1.value = ''
    elem_a1stats.innerHTML = ''
    elem_a1predict.innerHTML = ''
    elem_a2.value = ''
    elem_a2stats.innerHTML = ''
    elem_a2predict.innerHTML = ''
}

function swapTeamB(elem)
{
    swapElemVals(elem_b1, elem_b2);
    swapElemHTML(elem_b1stats, elem_b2stats);
    swapElemHTML(elem_b1predict, elem_b2predict);
}

function clearTeamB(elem)
{
    elem_b1.value = ''
    elem_b1stats.innerHTML = ''
    elem_b1predict.innerHTML = ''
    elem_b2.value = ''
    elem_b2stats.innerHTML = ''
    elem_b2predict.innerHTML = ''
}

/******************************************************************************
 * OVERALL STATS MODE stuff
 *****************************************************************************/
function loadAllRatingsHistoryGraph() {
    /* prepare the user for delay */
    document.getElementById("AllRatingsHistoryGraph_status").innerHTML = "loading...";

    /* get to work */
    var playerList = []
    var playerToObject = {}

    var resp = ajax("jsIface.py?op=getGames");
    var lines = resp.split("\n");
    for(var i in lines) {
        var data = lines[i].split(",");
        var t = parseInt(data[0]);
        var a1 = data[1];
        var a1_r = parseInt(data[2]);
        var a2 = data[4];
        var a2_r = parseInt(data[5]);
        var b1 = data[7];
        var b1_r = parseInt(data[8]);
        var b2 = data[10];
        var b2_r = parseInt(data[11]);

        if(isNaN(t)) {
            continue;
        }

        var players = [a1, a2, b1, b2];
        var ratings = [a1_r, a2_r, b1_r, b2_r];

        /* update each player's data from the game */
        for(var i in players) {
            var p = players[i];
            var r = ratings[i];

            /* create if not exist yet */
            if(playerToObject[p] == undefined) {
                playerList.push(p);
                playerToObject[p] = { name: p, data: [] };
            }

            /* append this one rating sample */
            /* recall that the 'datetime' type of xAxis in highcharts expects milliseconds */
            playerToObject[p]['data'].push([t*1000, r]);
        }
    }

    /* build the series as an array of player objects */
    var seriesData = [];
    for(var i in playerList) {
        seriesData.push(playerToObject[playerList[i]])
    }

    /* finally, render the graph into this div */
    var chart = new Highcharts.Chart(
        {
            chart: {
                renderTo: document.getElementById("AllRatingsHistoryGraph"), 
                zoomType: 'x', 
                type: 'line'
            },
            title: {
                text: 'Player Rating vs. Time'
            },
            xAxis: {
                type: 'datetime',
                dateTimeLabelFormats: { // don't display the dummy year
                    month: '%e. %b',
                    year: '%b'
                }
            },
            yAxis: {
                title: {
                    text: 'Rating'
                },
                min: 0
            },
            tooltip: {
                formatter: function() {
                    return '<b>'+ this.series.name +'</b><br/>'+Highcharts.dateFormat('%e. %b', this.x) +': '+ this.y;
                }
            },
            series: seriesData
        }
    );

    /* erase the "loading..." message */
    document.getElementById("AllRatingsHistoryGraph_status").innerHTML = "";
}

function loadAllRatingsVsGamesGraph() {
    /* prepare the user for delay */
    document.getElementById("AllRatingsVsGamesGraph_status").innerHTML = "loading...";

    /* get to work */
    var playerList = []
    var playerToObject = {}

    var resp = ajax("jsIface.py?op=getGames");
    var lines = resp.split("\n");
    for(var i in lines) {
        var data = lines[i].split(",");
        var t = parseInt(data[0]);
        var a1 = data[1];
        var a1_r = parseInt(data[2]);
        var a2 = data[4];
        var a2_r = parseInt(data[5]);
        var b1 = data[7];
        var b1_r = parseInt(data[8]);
        var b2 = data[10];
        var b2_r = parseInt(data[11]);

        if(isNaN(t)) {
            continue;
        }

        var players = [a1, a2, b1, b2];
        var ratings = [a1_r, a2_r, b1_r, b2_r];

        /* update each player's data from the game */
        for(var i in players) {
            var p = players[i];
            var r = ratings[i];

            /* create if not exist yet */
            if(playerToObject[p] == undefined) {
                playerList.push(p);
                playerToObject[p] = { name: p, data: [], nGames: 0 };
            }

            /* append this one rating sample */
            var nGames = playerToObject[p]['nGames'];
            playerToObject[p]['data'].push([nGames, r]);
            playerToObject[p]['nGames']++;
        }
    }

    /* build the series as an array of player objects */
    var seriesData = [];
    for(var i in playerList) {
        playerToObject[playerList[i]]['nGames'] = undefined;
        seriesData.push(playerToObject[playerList[i]]);
    }

    /* finally, render the graph into this div */
    var chart = new Highcharts.Chart(
        {
            chart: {
                renderTo: document.getElementById("AllRatingsVsGamesGraph"), 
                zoomType: 'x', 
                type: 'spline'
            },
            title: {
                text: 'Player Rating vs. Amount Games Played'
            },
            xAxis: {
                title: {
                    text: 'n\'th game'
                },
                min: 0
            },
            yAxis: {
                title: {
                    text: 'Rating'
                },
                min: 0
            },
            tooltip: {
                formatter: function() {
                    return '<b>'+ this.series.name +'</b><br/>'+Highcharts.dateFormat('%e. %b', this.x) +': '+ this.y;
                }
            },
            series: seriesData
        }
    );

    /* erase the "loading..." message */
    document.getElementById("AllRatingsVsGamesGraph_status").innerHTML = "";
}

/******************************************************************************
 * INDIVIDUAL STATS MODE stuff
 *****************************************************************************/
function istatsPlayerChoice_cb(elem) {
    if(elem.value != "") {
        loadIStatsExtended(elem.value);
        loadResultsVsPartnersGraph(elem.value);
        loadResultsVsOpponentsGraph(elem.value);
    }
}

function loadIStatsExtended(who) {
    document.getElementById("IStatsExtended").innerHTML = "loading...";

    var html = ''
    html += '<table bgcolor=white border=black>'
    var resp = ajax("jsIface.py?op=getstatsextended&player=" + who)
    var lines = resp.split("\n");
    for(var i in lines) {
        if(!lines[i]) {
            continue;
        }

        nameData = lines[i].split(",");
        html += "<tr><td align=right bgcolor=lightgrey>" + nameData[0] + ":</td><td>" + nameData[1] + "</td></tr>\n"
    }
    html += '</center>'
    document.getElementById("IStatsExtended").innerHTML = html

}

function loadResultsVsPartnersGraph(who) {
    /* prepare the user for delay */
    document.getElementById("ResultsVsPartnersGraph_status").innerHTML = "loading...";

    /* get to work */

    var partnerList = [];
    var partnerToObj = {};

    var resp = ajax("jsIface.py?op=getGames");
    var lines = resp.split("\n");
    for(var i in lines) {
        var data = lines[i].split(",");
        var t = parseInt(data[0]);
        var a1 = data[1];
        var a1_r = parseInt(data[2]);
        var a2 = data[4];
        var a2_r = parseInt(data[5]);
        var b1 = data[7];
        var b1_r = parseInt(data[8]);
        var b2 = data[10];
        var b2_r = parseInt(data[11]);
        var partner;
        var result;

        if(isNaN(t)) {
            continue;
        }

        /* can find partner? */
        if(a1 == who) {
            partner = a2;
            result = 1;
        }
        else if(a2 == who) {
            partner = a1;
            result = 1;
        }
        else if(b1 == who) {
            partner = b2;
            result = 0;
        }
        else if(b2 == who) {
            partner = b1;
            result = 0;
        }
        else {
            continue;
        }

        /* create entry if not exist */
        if(partnerToObj[partner] == undefined) {
            partnerList.push(partner);
            partnerToObj[partner] = { name: "Partner: " + partner, data: [0,0] }
        }

        if(result == 1) {
            partnerToObj[partner].data[0]++;
        }
        else {
            partnerToObj[partner].data[1]++;
        }
    }

    /* build the series as an array of player objects */
    var seriesData = [{name: 'Wins', data:[]}, {name: 'Losses', data:[]}];
    for(var i in partnerList) {
        seriesData[0].data.push(partnerToObj[partnerList[i]].data[0]);
        seriesData[1].data.push(partnerToObj[partnerList[i]].data[1]);
    }

    /* finally, render the graph into this div */
    var chart = new Highcharts.Chart(
        {
            chart: {
                renderTo: document.getElementById("ResultsVsPartnersGraph"), 
                type: 'bar'
            },
            title: {
                text: 'Player Result vs. Partners'
            },
            xAxis: {
                categories: partnerList,
                title: {
                    text: null
                }
            },
            yAxis: {
                title: {
                    text: 'Wins/Losses',
                    align: 'high'
                },
                min: 0
            },
            tooltip: {
                formatter: function() {
                    return '<b>'+ this.series.name +'</b><br/>'+Highcharts.dateFormat('%e. %b', this.x) +': '+ this.y;
                }
            },
            series: seriesData
        }
    );

    /* erase the "loading..." message */
    document.getElementById("ResultsVsPartnersGraph_status").innerHTML = "";
}

function loadResultsVsOpponentsGraph(who) {
    /* prepare the user for delay */
    document.getElementById("ResultsVsOpponentsGraph_status").innerHTML = "loading...";

    /* get to work */

    var oppList = [];
    var oppToObj = {};

    var resp = ajax("jsIface.py?op=getGames");
    var lines = resp.split("\n");
    for(var i in lines) {
        var data = lines[i].split(",");
        var t = parseInt(data[0]);
        var a1 = data[1];
        var a1_r = parseInt(data[2]);
        var a2 = data[4];
        var a2_r = parseInt(data[5]);
        var b1 = data[7];
        var b1_r = parseInt(data[8]);
        var b2 = data[10];
        var b2_r = parseInt(data[11]);
        var opponents = [];
        var result;

        if(isNaN(t)) {
            continue;
        }

        /* can find opponent? */
        if(a1 == who) {
            opponents.push(b1);
            opponents.push(b2);
            result = 1;
        }
        else if(a2 == who) {
            opponents.push(b1);
            opponents.push(b2);
            result = 1;
        }
        else if(b1 == who) {
            opponents.push(a1);
            opponents.push(a2);
            result = 0;
        }
        else if(b2 == who) {
            opponents.push(a1);
            opponents.push(a2);
            result = 0;
        }
        else {
            continue;
        }

        /* create entry if not exist */
        for(var i in opponents) {
            if(oppToObj[opponents[i]] == undefined) {
                oppList.push(opponents[i]);
                oppToObj[opponents[i]] = { name: "Opponent: " + opponents[i], data: [0,0] }
            }
    
            if(result == 1) {
                oppToObj[opponents[i]].data[0]++;
            }
            else {
                oppToObj[opponents[i]].data[1]++;
            }
        }
    }

    /* build the series as an array of player objects */
    var seriesData = [{name: 'Wins', data:[]}, {name: 'Losses', data:[]}];
    for(var i in oppList) {
        seriesData[0].data.push(oppToObj[oppList[i]].data[0]);
        seriesData[1].data.push(oppToObj[oppList[i]].data[1]);
    }

    /* finally, render the graph into this div */
    var chart = new Highcharts.Chart(
        {
            chart: {
                renderTo: document.getElementById("ResultsVsOpponentsGraph"), 
                type: 'bar'
            },
            title: {
                text: 'Player Result vs. Opponents (either color)'
            },
            xAxis: {
                categories: oppList,
                title: {
                    text: null
                }
            },
            yAxis: {
                title: {
                    text: 'Wins/Losses',
                    align: 'high'
                },
                min: 0
            },
            series: seriesData
        }
    );

    /* erase the "loading..." message */
    document.getElementById("ResultsVsOpponentsGraph_status").innerHTML = "";
}

/******************************************************************************
 * GAMES LIST MODE
 *****************************************************************************/
function loadGamesList() {
    var resp = ajax("jsIface.py?op=getGames");
    var lines = resp.split("\n");

    var date = new Date();

    var html = ''
    html += '<table cellpadding=0 cellspacing=8px>\n'
    html += '<tr>\n'
    html += '  <th>time</th>\n'
    html += '  <th bgcolor=green>winners</th>\n'
    html += '  <th bgcolor=red>losers</th>\n'
    html += '</tr>\n'

    for(var i in lines) {
        if(!lines[i]) {
            continue;
        }

        var gameData = lines[i].split(",");
        var t = parseInt(gameData[0]);
        var a1 = gameData[1];
        var a1_r = parseInt(gameData[2]);
        var a2 = gameData[4];
        var a2_r = parseInt(gameData[5]);
        var b1 = gameData[7];
        var b1_r = parseInt(gameData[8]);
        var b2 = gameData[10];
        var b2_r = parseInt(gameData[11]);

        date.setTime(t*1000);

        html += '<tr>\n';
        html += '  <td>\n';
        html += dateToString(date);
        html += '<br>(' + longAgoStr(date.getTime() / 1000) + " ago)\n"
        html += '  </td>\n';
        html += '  <td>\n';
        html += '    <div class=chesswhite>' + a1 + "(" + a1_r + ")</div>\n";
        html += '    <div class=chessblack>' + b1 + "(" + b1_r + ")</div>\n";
        html += '  </td>\n';
        html += '  <td>\n';
        html += '    <div class=chessblack>' + a2 + "(" + a2_r + ")</div>\n";
        html += '    <div class=chesswhite>' + b2 + "(" + b2_r + ")</div>\n";
        html += '  </td>\n';
        html += '</tr>\n';
    }

    html += '</table>\n';

    document.getElementById("games").innerHTML = html;
}

/******************************************************************************
 * Glicko 
 *****************************************************************************/
// Glicko says this works best when rating period has player playing "moderate" 5-10 games
// rating period: 1 day
// time for decay to noob: 365 rating periods
// let 50 be the RD of a typical player
// now to solve for c for RD=350 -> noob
// 350 = sqrt(50^2 + c^2 * 365)
// Math.sqrt((350*350 - 2500)/365.0)
var c = 18.131936556464982

// Math.log(10)/400 in original glicko; this is bughouse mod:
var q = 0.0028782313662425573 // Math.log(10)/800

function secToRatingPeriods(secs) {
    // note that periods are 1-based (ie: 1 denotes a game played in the last rating period)

    // rating periods now are 1 day
    periods = parseInt(1 + (secs / (24*3600)))
    return Math.min(periods, 365)
}

// ratings is list where [0] is dude we're calculating for, [1] is his partner
//  [2], [3] are the opponents
// rds is same
// t is seconds since last time he played a game
// w is 1 for win, 0 for loss
//
function calcRatingRdPlayer(ratings, rds, rps, w) {
    // rps (rating periods) 
    //debug("rps is: ", rps);
    rps = Math.min(rps, 365)

    // for new player
    for(var i in rds) {
        if(rds[i] < 30 || rds[i] > 350) {
            debug("calcRatingRdPlayer() given rd not in [30,350]!");
            return;
        }
    }

    // RD adjustment due to time
    rd = rds[0]
    // original glicko squares c here, bughouse does not (mistake? or mod?)
    rd = Math.min(Math.sqrt(Math.pow(rd,2) + c * rps), 350.0)
    //debug("rd: ", rd);

    // attenuating factor
    p = .0000025180996504909944  // 3*Math.log(10)**2 / (Math.PI**2 * 800**2)
    f = 1/Math.sqrt(1 + p*(Math.pow(rds[1],2) + Math.pow(rds[2],2) + Math.pow(rds[3],2)))
    // f should be [0, 1] ...large RD's result in small f's
    //debug("f: ", f);

    // average ratings
    r1 = (ratings[0]+ratings[1])/2.0
    r2 = (ratings[2]+ratings[3])/2.0

    //debug("r1: ", r1);
    //debug("r2: ", r2);
    E = 1/(1 + Math.pow(10, -1*(r1-r2)*f/400))
    //debug("E: ", E);

    // begin-pre
    //debug("q=", q);
    //debug("f=", f);
    denom = 1/(rd*rd) + q*q*f*f*E*(1-E)
    //debug("denom: ", denom
    K = q*f / denom
    //debug("K: ", K);
    K = Math.max(K,16)
    //debug("K: ", K);

    // new rating, new rd
    rating = ratings[0] + K*(w - E)
    rd = 1/Math.sqrt(denom)
    //debug("rd before reduction: ", rd);
    rd = Math.min(rd, 350)
    rd = Math.max(rd, 30)

    // done
    return [Math.round(rating), Math.round(rd)]
}

function calcRatingRdDeltaPlayer(ratings, rds, t, w) {
    ratingData = calcRatingRdPlayer(ratings, rds, t, w)
    return [ratingData[0] - ratings[0], ratingData[1] - rds[0]]
}

// if a1 (with partner a2, opponents b1,b2) plays, return his <+win>,<-loss> adjustment
// returns [winDelta, loseDelta]
function calcRatingWinLossDeltaPlayer(ratings, rds, ts) {
    tNow = Math.round((new Date()).getTime() / 1000);
    winRandRD = calcRatingRdDeltaPlayer(ratings, rds, secToRatingPeriods(tNow - ts[0]), 1)
    loseRandRD = calcRatingRdDeltaPlayer(ratings, rds, secToRatingPeriods(tNow - ts[0]), 0)
    debug("(winDelta, loseDelta) = (" + winRandRD[0] + "," + loseRandRD[0] + ")\n");
    return [winRandRD[0], loseRandRD[0]]
}

// suppose a game is played with winners a1,a2 and losers a3,a4
// given [a1,a2,a3,a4], return the new ratings/rd's in this form:
// [[a1_RATING, a1_RD], [a2_RATING, a2_RD], [b1_RATING, b1_RD], [b2_RATING, b2_RD]]
//
function calcGameScores(ratings, rds, tds) {
    // calculate new scores

    // calculate for a1 (first winner, white)
    stats1 = calcRatingRdPlayer(ratings, rds, tds[0], 1)
    debug("a1 new stats: " + stats1 + '<br>\n');

    // calculate for a2 (first winner, black)
    ratings = [ratings[1], ratings[0], ratings[2], ratings[3]]
    rds = [rds[1], rds[0], rds[2], rds[3]]
    debug("calcRatingRdPlayer(" + ratings + ", " + rds + ", " + tds[1] + ", 1);");
    stats2 = calcRatingRdPlayer(ratings, rds, tds[1], 1)
    debug("a2 new stats: " + stats2 + '<br>\n');

    // calculate for b1 (first loser, black)
    ratings = [ratings[2], ratings[3], ratings[0], ratings[1]]
    rds = [rds[2], rds[3], rds[0], rds[1]]
    stats3 = calcRatingRdPlayer(ratings, rds, tds[2], 0)
    debug("b1 new stats: " + stats3 + '<br>\n');

    // calculate for b2 (first loser, white)
    ratings = [ratings[1], ratings[0], ratings[2], ratings[3]]
    rds = [rds[1], rds[0], rds[2], rds[3]]
    stats4 = calcRatingRdPlayer(ratings, rds, tds[3], 0)
    debug("b2 new stats: " + stats4 + '<br>\n');

    return [stats1, stats2, stats3, stats4]
}
