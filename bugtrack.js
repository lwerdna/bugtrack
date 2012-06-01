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

var elemDivPlay, elemDivStats, elemDivGames;

var playerElems = [];
var playerNames = [];
var playerToR = [];
var playerToRD = [];
var playerToT = [];

function playClearPredicts(x) {
    elem_a1predict.innerHTML = "";
    elem_a2predict.innerHTML = "";
    elem_b1predict.innerHTML = "";
    elem_b2predict.innerHTML = "";
}

/* called when the play page loads */
function playInit(x) {
    /* init global DOM vars */
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

    elemDivPlay = document.getElementById("play");
    elemDivStats = document.getElementById("stats");
    elemDivGames = document.getElementById("games");

    /* init global player vars */
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

    /* populate the play choice drop-downs */
    playerNames.sort();
    var elems = [elem_a1, elem_a2, elem_b1, elem_b2];
    for(var i in elems) {
        //elems[i].value = '';
        //elems[i].innerHTML = '<option></option>';

        for(var j in playerNames) {
            elems[i].innerHTML += "<option>" + playerNames[j] + "</option>";
        }
    }

    /* populate the ratings */
    playShowRatings();

    /* populate the predictions */
    playShowPredictions();
}

/******************************************************************************
 * show/hide divs
 *****************************************************************************/
function showPlay() {
    elemDivPlay.style.display = 'block';
    elemDivStats.style.display = 'none';
    elemDivGames.style.display = 'none';
}

function showStats() {
    elemDivPlay.style.display = 'none';
    elemDivStats.style.display = 'block';
    elemDivGames.style.display = 'none';
}

function showGamesList() {
    elemDivPlay.style.display = 'none';
    elemDivStats.style.display = 'none';
    elemDivGames.style.display = 'block';
}

/******************************************************************************
 * 
 *****************************************************************************/
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

//        var predictions = calcGameScores(ratings, rds, ts);
//
//        elem_a1predict.innerHTML = "<font color=green>+" + predictions[0][0] + "</font> " + 
//                                    "<font color=red>" + predictions[0][1] + "</font>"
//        elem_a2predict.innerHTML = "<font color=green>+" + predictions[1][0] + "</font> " + 
//                                    "<font color=red>" + predictions[1][1] + "</font>"
//        elem_b1predict.innerHTML = "<font color=green>+" + predictions[2][0] + "</font> " + 
//                                    "<font color=red>" + predictions[2][1] + "</font>"
//        elem_b2predict.innerHTML = "<font color=green>+" + predictions[3][0] + "</font> " + 
//                                    "<font color=red>" + predictions[3][1] + "</font>"
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

function recordGame() {
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
    var elems = [elem_a1, elem_a1stats, elem_a1predict,
                    elem_a2, elem_a2stats, elem_a2predict];

    for(var i in elems) {
        elems[i].value = ""
    }
}

function swapTeamB(elem)
{
    swapElemVals(elem_b1, elem_b2);
    swapElemHTML(elem_b1stats, elem_b2stats);
    swapElemHTML(elem_b1predict, elem_b2predict);
}

function clearTeamB(elem)
{
    var elems = [elem_b1, elem_b1stats, elem_b1predict,
                    elem_b2, elem_b2stats, elem_b2predict];

    for(var i in elems) {
        elems[i].value = ""
    }
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
    stats2 = calcRatingRdPlayer(ratings, rds, tds[1], 1)
    debug("a2 new stats: " + stats2 + '<br>\n');

    // calculate for b1 (first loser, black)
    ratings = [ratings[2], ratings[3], ratings[0], ratings[1]]
    rds = [rds[2], rds[3], rds[0], rds[1]]
    stats3 = calcRatingRdPlayer(ratings, rds, tds[2], 0)
    debug("b1 new stats: " + stats3 + '<br>\n');

    ratings = [ratings[1], ratings[0], ratings[2], ratings[3]]
    rds = [rds[1], rds[0], rds[2], rds[3]]
    stats4 = calcRatingRdPlayer(ratings, rds, tds[3], 0)
    debug("b2 new stats: " + stats4 + '<br>\n');

    return [stats1, stats2, stats3, stats4]
}
