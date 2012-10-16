/*

bugtrack play mode javascript
Copyright 2012 Andrew Lamoureux

This file is a part of bugtrack

bugtrack is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/

/******************************************************************************
 * global vars
 *****************************************************************************/

/* overall */
var showElems = []

/* important play elems */
var elem_A, elem_b, elem_B, elem_a
var elem_Astats, elem_bstats, elem_Bstats, elem_astats
var elem_Apredict, elem_bpredict, elem_Bpredict, elem_apredict
var lastRecord_A, lastRecord_b, lastRecord_B, lastRecord_a

var playerToSchedWeight = []
var playerToSchedProbabilityElem = []

var playerElems = []
var playerNames = []
var playerToR = []
var playerToRD = []
var playerToT = []

/******************************************************************************
 * inner-mode functions
 *****************************************************************************/

/* called when the page loads */
function playInit(x) {
    this.name = 'window_bugtrack_play'

    /* overall modes; play is the default */
    showElems.push(document.getElementById("play"))
    showElems.push(document.getElementById("scheduler"))
    showElems.push(document.getElementById("games"))
    //showElems.push(document.getElementById("admin"))
    showPlay()

    /* play mode */
    elem_A = document.getElementById("A")
    elem_b = document.getElementById("b")
    elem_B = document.getElementById("B")
    elem_a = document.getElementById("a")
    playerElems = [elem_A, elem_b, elem_B, elem_a]

    elem_Astats = document.getElementById("A_stats")
    elem_bstats = document.getElementById("b_stats")
    elem_Bstats = document.getElementById("B_stats")
    elem_astats = document.getElementById("a_stats")

    elem_Apredict = document.getElementById("A_predict")
    elem_bpredict = document.getElementById("b_predict")
    elem_Bpredict = document.getElementById("B_predict")
    elem_apredict = document.getElementById("a_predict")

    /* scheduler mode */
    elem_schedPlayerList = document.getElementById("schedulerPlayerList")
    schedCheckElems = []
    schedDisplayElems = []

    /* init global player vars */
    var resp = ajax('cgi/jsIface.py?op=getplayers')
    var lines = resp.split("\n")
    for(var j in lines) {
        var m = lines[j].match(/^(.*),(.*),(.*),(.*)$/)

        if(m) {
            playerName = m[1]
            playerNames.push(playerName)
            playerToSchedWeight[playerName] = 0 /* player initially unscheduled */
            playerToR[playerName] = parseInt(m[2])
            playerToRD[playerName] = parseInt(m[3])
            playerToT[playerName] = parseInt(m[4])
        }
    }

    /* populate player choice drop-downs */
    playerNames.sort()
    //var elems = [elem_A, elem_b, elem_B, elem_a, istatsPlayerChoice]
    var elems = [elem_A, elem_b, elem_B, elem_a]
    for(var i in elems) {
        elems[i].value = ''
        elems[i].innerHTML = '<option></option>'

        for(var j in playerNames) {
            elems[i].innerHTML += "<option>" + playerNames[j] + "</option>"
        }
    }

    /* populate the scheduler display html */
    var html = '<table><tr>'
    for(var j in playerNames) {
        if(!(j%4)) {
            html += '</tr><tr>'
        }
        html += '<td>'
        html += '<input id=schedCheck' + j + ' type=\"checkbox\" value=\"' + playerNames[j] + '"'
        html += ' onclick="schedTogglePlayer(this, \'' + playerNames[j] + '\')" />'
        html += '<span id=schedProbability' + j + '></span>'
        html += '<span>' + playerNames[j] + '</span>'
        html += "</td>"
    }
    html += '</tr></table>'
    elem_schedPlayerList.innerHTML = html
    debug(html)

    /* populate schedule element list */
    for(var j in playerNames) {
        playerToSchedProbabilityElem[playerNames[j]] = document.getElementById('schedProbability' + j)
    }

    /* populate the ratings */
    playShowRatings()

    /* populate the predictions */
    playShowPredictions()
}

function showPlay() {
    hideAllBut([document.getElementById('play')], showElems)
}

function toggleScheduler() {
    eSched = document.getElementById('scheduler')

    /* if hidden */
    if(isHidden(eSched)) {
        /* show only {play, scheduler} */
        hideAllBut([document.getElementById('play'), eSched], showElems);
    }
    /* if visible, just hide it */
    else {
        hide(eSched);
    }
}

function showGamesList() {
    hideAllBut([document.getElementById('games')], showElems)

    loadGamesList()
}

function showAdmin() {
    hideAllBut([document.getElementById('admin')], showElems)
}

/******************************************************************************
 * PLAY MODE stuff
 *****************************************************************************/
function playClearPredicts(x) {
    elem_Apredict.innerHTML = ""
    elem_bpredict.innerHTML = ""
    elem_apredict.innerHTML = ""
    elem_Bpredict.innerHTML = ""
}

function playShowRatings() {
    /* update statistics (rating.rd) */
    var enameToElemStats = []
    enameToElemStats["A"] = elem_Astats
    enameToElemStats["b"] = elem_bstats
    enameToElemStats["B"] = elem_Bstats
    enameToElemStats["a"] = elem_astats

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
    if(elem_A.value && elem_b.value && elem_B.value && elem_a.value) {
        var ratings = []
        var rds = []
        var ts = []

        for(var i in playerElems) {
            ratings.push(playerToR[playerElems[i].value])
            rds.push(playerToRD[playerElems[i].value])
            ts.push(playerToT[playerElems[i].value])
        }

        var deltas = []

        /* if A wins */
        delta = calcRatingWinLossDeltaPlayer(ratings, rds, ts)
        elem_Apredict.innerHTML = "<font color=green>+" + delta[0] + "</font> " + 
                                    "<font color=red>" + delta[1] + "</font>"
        /* if b wins */
        var ratings_ = repositionColor(ratings)
        var rds_ = repositionColor(rds)
        var ts_ = repositionColor(ts)
        delta = calcRatingWinLossDeltaPlayer(ratings_, rds_, ts_)
        elem_bpredict.innerHTML = "<font color=green>+" + delta[0] + "</font> " + 
                                    "<font color=red>" + delta[1] + "</font>"

        /* if B wins */
        ratings_ = repositionTable(ratings)
        rds_ = repositionTable(rds)
        ts_ = repositionTable(ts)
        delta = calcRatingWinLossDeltaPlayer(ratings_, rds_, ts_)
        elem_Bpredict.innerHTML = "<font color=green>+" + delta[0] + "</font> " + 
                                    "<font color=red>" + delta[1] + "</font>"
        /* if a wins */
        ratings_ = repositionColor(ratings_)
        rds_ = repositionColor(rds_)
        ts_ = repositionColor(ts_)
        delta = calcRatingWinLossDeltaPlayer(ratings_, rds_, ts_)
        elem_apredict.innerHTML = "<font color=green>+" + delta[0] + "</font> " + 
                                    "<font color=red>" + delta[1] + "</font>"

    }
    // otherwise clear the predictions
    else {
        playClearPredicts(); 
    }

}

function selChange_cb(elem) {
    /* force other drop downs away from the name we just selected */
    var elems = [elem_A, elem_b, elem_B, elem_a]
    var elems_stats = [elem_Astats, elem_bstats, elem_Bstats, elem_astats]
    var elems_predict = [elem_Apredict, elem_bpredict, elem_Bpredict, elem_apredict]

    for(var i=0; i<4; ++i) {
        if(elem != elems[i] && elem.value == elems[i].value) {
	        /* this works in chrome, firefox */
            elems[i].value = ""
            /* this works in kindle fire browser */
	        elems[i].options.selectedIndex = 0

            /* clear also the stats */
            elems_stats[i].innerHTML = ""
            elems_predict[i].innerHTML = ""
        }
    }

    /* populate ratings */
    playShowRatings()

    /* possibly (if 4 players) show game predictions */
    playShowPredictions()
}

function recordGame(elem) {
    /* milliseconds before next game records */

    var participants = []
    var ratings = []
    var rds = []
    var ts = []
    var rps = []

    for(var i in playerElems) {
        participants.push(playerElems[i].value)
        ratings.push(playerToR[playerElems[i].value])
        rds.push(playerToRD[playerElems[i].value])
        ts.push(playerToT[playerElems[i].value])
    }

    if(elem.id == "bottomWins") {
        /* then arrays are in correct order */
    }
    else {
        /* position winner in locations [0], [1], preserving color information */
        participants = repositionTable(participants)
        ratings = repositionTable(ratings)
        rds = repositionTable(rds)
        ts = repositionTable(ts)
    }
   
    /* warn against dupliate game records */
    if(participants[0] == lastRecord_A && participants[1] == lastRecord_b &&
        participants[2] == lastRecord_B && participants[3] == lastRecord_a) {
        if(confirm('Possible duplicate game; detected same players as last game! Continue anyways?') == false) {
            return
        }
    }
    lastRecord_A = participants[0]
    lastRecord_b = participants[1]
    lastRecord_B = participants[2]
    lastRecord_a = participants[3]

    /* convert those last-time-played timestamps to rating periods */
    var tNow = Math.round((new Date()).getTime() / 1000)

    for(var i in ts) {
        rps.push(secToRatingPeriods(tNow - ts[i]))
    }

    /* build the ajax request */
    var req = 'cgi/jsIface.py?op=recordGame'

    /* game stats: players, OLD r's, OLD rd's */
    req += '&t=' + tNow
    req += '&A=' + participants[0] + "&A_r=" + playerToR[participants[0]] + "&A_rd=" + playerToRD[participants[0]]
    req += '&b=' + participants[1] + "&b_r=" + playerToR[participants[1]] + "&b_rd=" + playerToRD[participants[1]]
    req += '&B=' + participants[2] + "&B_r=" + playerToR[participants[2]] + "&B_rd=" + playerToRD[participants[2]]
    req += '&a=' + participants[3] + "&a_r=" + playerToR[participants[3]] + "&a_rd=" + playerToRD[participants[3]]
    
    /* new scores, ratings */
    var results = calcGameScores(ratings, rds, rps)

    req += "&A_r_new=" + results[0][0] + "&A_rd_new=" + results[0][1]
    req += "&b_r_new=" + results[1][0] + "&b_rd_new=" + results[1][1]
    req += "&B_r_new=" + results[2][0] + "&B_rd_new=" + results[2][1]
    req += "&a_r_new=" + results[3][0] + "&a_rd_new=" + results[3][1]

    /* do it! */
    ajax(req)

    /* message */
    alert('Win for ' + participants[0] + " and " + participants[1] + ' recorded!')

    /* now also update the global vars */
    for(var i in participants) {
        playerToR[participants[i]] = results[i][0]
        playerToRD[participants[i]] = results[i][1]
        playerToT[participants[i]] = tNow
    } 

    /* refresh */
    playShowRatings()
    playShowPredictions()

    /* if scheduling was enabled, cycle these guys to back of line */
    schedCycle()
}

function swapbottom(elem)
{
    swapElemVals(elem_A, elem_b)
    swapElemHTML(elem_Astats, elem_bstats)
    swapElemHTML(elem_Apredict, elem_bpredict)
}

function clearbottom(elem)
{
    elem_A.value = ''
    elem_Astats.innerHTML = ''
    elem_Apredict.innerHTML = ''
    elem_b.value = ''
    elem_bstats.innerHTML = ''
    elem_bpredict.innerHTML = ''
}

function swaptop(elem)
{
    swapElemVals(elem_a, elem_B)
    swapElemHTML(elem_astats, elem_Bstats)
    swapElemHTML(elem_apredict, elem_Bpredict)
}

function cleartop(elem)
{
    elem_a.value = ''
    elem_astats.innerHTML = ''
    elem_apredict.innerHTML = ''
    elem_B.value = ''
    elem_Bstats.innerHTML = ''
    elem_Bpredict.innerHTML = ''
}

/******************************************************************************
 * SCHEDULER STUFF
 *****************************************************************************/
function schedCycle()
{
    var names = [elem_A.value, elem_b.value, elem_B.value, elem_a.value]

    if(names) {
        /* triple everybody's weight (players will go to 1) */
        for(var i in playerNames) {
            playerToSchedWeight[playerNames[i]] *= 3
        }

        /* players that just played adopt weight 1 */
        for(var i in names) {
            playerToSchedWeight[names[i]] = 1
        }
    
        schedRecalcProbabilities()
    }
}

function schedRecalcProbabilities()
{
    /* calculate total weights (divisor) */
    var total = 0
    for(var i in playerNames) {
        total += playerToSchedWeight[playerNames[i]]
    }

    /* calculate percentage weight for each player */
    for(var i in playerNames) {
        var whom = playerNames[i]
        var weight = playerToSchedWeight[whom]
        if(weight && (total>=4)) {
            //var prob = 1 - Math.pow((total-weight)/total, 4)
            var prob = weight/total
            playerToSchedProbabilityElem[whom].innerHTML =
                '<font size=large color=red>' + Math.round(prob*100) + '% </font>'
        }
        else {
            playerToSchedProbabilityElem[whom].innerHTML = ''
        } 
    }
}

function schedTogglePlayer(elem, who)
{
    if(elem.checked == true) {
        playerToSchedWeight[who] = 1
    }
    else {
        playerToSchedWeight[who] = 0
    }

    schedRecalcProbabilities()
}

function schedGetHead()
{
    /* calculate total weights (divisor) */
    var spinToWinner = []
    var spin = 0
    var total = 0
    for(var i in playerNames) {
        var name = playerNames[i]
        var weight = playerToSchedWeight[name]

        for(var j=0; j<weight; ++j) {
            spinToWinner[spin++] = name
        }
        
        total += weight
    }

    if(total < 4) {
        alert("ERROR: less than 4 players scheduled!")
        return
    }

    /* random spin across the total */
    var winners = new Array(0)
    while(winners.length < 4) {
        var spin = Math.floor(Math.random() * 1000000) % total
   
        who = spinToWinner[spin]

        if(winners.indexOf(who) == -1) {
            winners.push(who)
        }
    }
 
    return winners
}

function schedLoadPlayers(names)
{
    /* randomly choose black/white */
    if(Math.random() > .5) {
        names = [names[1], names[0], names[3], names[2]]
    }

    /* load them into the player slots */
    elem_A.value = names[0]
    elem_b.value = names[1]
    elem_B.value = names[2]
    elem_a.value = names[3]

    /* refresh stats */
    selChange_cb(elem_A)
    selChange_cb(elem_b)
    selChange_cb(elem_B)
    selChange_cb(elem_a)
}
    
function schedLoadPlayersRandom()
{
    var names = schedGetHead()

    if(names) {
        schedLoadPlayers(names);
    }
}

function schedLoadPlayersFair()
{
    var names = schedGetHead()

    if(names) {
        /* sort names, best to worst */
        names.sort(function(a,b) { return playerToR[b] - playerToR[a] })

        /* 0,3 vs. 1,2 */
        names = [names[0], names[3], names[1], names[2]]

        schedLoadPlayers(names);
    }
}

function schedLoadPlayersUnfair()
{
    var names = schedGetHead()

    if(names) {
        /* sort names, best to worst */
        names.sort(function(a,b) { return playerToR[b]-playerToR[a] })

        /* default order is A,b,B,a so [0],[1] slots (top 2) already on team */
        schedLoadPlayers(names);
    }
}

function schedLoadIntoEmpty()
{
    /* collect the players currently sitting */
    var current = []
    var empties = [] 
    for(var i in playerElems) {
        if(playerElems[i].value) {
            current.push(playerElems[i].value)
        }
        else {
            empties.push(playerElems[i])
        }
    }

    if(current.length == 4) {
        return;
    }

    /* get the replacements */
    var replacements = []
    var head = schedGetHead()
    for(var i in head) {
        /* is currently sitting? skip */
        if(current.indexOf(head[i]) >= 0) {
            continue;
        }

        /* else is valid replacement */
        replacements.push(head[i])
    }

    if(replacements.length < empties.length) {
        alert("ERROR: scheduler provides " + replacements.length + " to fill " + empties.length + " chairs!")
        return;
    }

    /* finally, seat them, update stats */
    for(var i=0; i<empties.length; ++i) {
        empties[i].value = replacements[i]
        selChange_cb(empties[i])
    }
}

/******************************************************************************
 * GAMES LIST MODE
 *****************************************************************************/
function loadGamesList() {
    var resp = ajax("cgi/jsIface.py?op=getGames")
    var lines = resp.split("\n")

    var date = new Date()

    var html = ''
    html += '<table cellpadding=0 cellspacing=8px>\n'
    html += '<tr>\n'
    html += '  <th>time</th>\n'
    html += '  <th bgcolor=green>winners</th>\n'
    html += '  <th bgcolor=red>losers</th>\n'
    html += '</tr>\n'

    lines.reverse()

    for(var i in lines) {
        if(!lines[i]) {
            continue
        }

        var gameData = lines[i].split(",")
        var t = parseInt(gameData[0])
        var A = gameData[1]
        var A_r = parseInt(gameData[2])
        var b = gameData[4]
        var b_r = parseInt(gameData[5])
        var B = gameData[7]
        var B_r = parseInt(gameData[8])
        var a = gameData[10]
        var a_r = parseInt(gameData[11])

        date.setTime(t*1000)

        html += '<tr>\n'
        html += '  <td>\n'
        html += longAgoStrStealth(date.getTime() / 1000) + "\n"
        html += '  </td>\n'
        html += '  <td>\n'
        html += '    <div class=chesswhite>' + A + "(" + A_r + ")</div>\n"
        html += '    <div class=chessblack>' + b + "(" + b_r + ")</div>\n"
        html += '  </td>\n'
        html += '  <td>\n'
        html += '    <div class=chessblack>' + B + "(" + B_r + ")</div>\n"
        html += '    <div class=chesswhite>' + a + "(" + a_r + ")</div>\n"
        html += '  </td>\n'
        html += '  <td>\n'
        html += '    <input type=submit value="Delete" onClick="deleteGame_cb(this, ' + t + ')">\n'
        html += '  </td>\n'
        html += '</tr>\n'
    }

    html += '</table>\n'

    document.getElementById("games").innerHTML = html
}

/******************************************************************************
 * MISC ADMIN
 *****************************************************************************/
function deleteGame_cb(e, gameId) {
    ajax("cgi/jsIface.py?op=deleteGame&t=" + gameId)
    e.disabled = 1
}

function recalcScores() {
    /* clear players' stats */
    for(var i in playerNames) {
        playerToR[playerNames[i]] = 1000
        playerToRD[playerNames[i]] = 350
        playerToT[playerNames[i]] = 0
    }

    /* get games */
    var resp = ajax("cgi/jsIface.py?op=getGames")
    var lines = resp.split("\n")

    /* for each game */
    for(var i in lines) {
        var gameData = lines[i].split(",")
        var t = parseInt(gameData[0])
        var A = gameData[1]
        var b = gameData[4]
        var B = gameData[7]
        var a = gameData[10]

        if(isNaN(t)) {
            continue
        }

        /* prepare parameters to calculate RESULTING game scores */ 
        var players = [A,b,B,a]
        var ratings = []
        var rds = []
        var rps = []
        for(var j in players) {
            ratings.push(playerToR[players[j]])
            rds.push(playerToRD[players[j]])
            rps.push(secToRatingPeriods(t - playerToT[players[j]]))
        }

        /* calculate new scores for next loop */
        var results = calcGameScores(ratings, rds, rps); 

        /* save them to database */
        var req = 'cgi/jsIface.py?op=recordGame'
        req += '&t=' + t
        req += '&A=' + A + "&A_r=" + playerToR[A] + "&A_rd=" + playerToRD[A]
        req += '&b=' + b + "&b_r=" + playerToR[b] + "&b_rd=" + playerToRD[b]
        req += '&B=' + B + "&B_r=" + playerToR[B] + "&B_rd=" + playerToRD[B]
        req += '&a=' + a + "&a_r=" + playerToR[a] + "&a_rd=" + playerToRD[a]
        req += "&A_r_new=" + results[0][0] + "&A_rd_new=" + results[0][1]
        req += "&b_r_new=" + results[1][0] + "&b_rd_new=" + results[1][1]
        req += "&B_r_new=" + results[2][0] + "&B_rd_new=" + results[2][1]
        req += "&a_r_new=" + results[3][0] + "&a_rd_new=" + results[3][1]
        ajax(req)

        /* save them locally, for next loop */
        playerToR[A] = results[0][0]
        playerToRD[A] = results[0][1]
        playerToT[A] = t
        playerToR[b] = results[1][0]
        playerToRD[b] = results[1][1]
        playerToT[b] = t
        playerToR[B] = results[2][0]
        playerToRD[B] = results[2][1]
        playerToT[B] = t
        playerToR[a] = results[3][0]
        playerToRD[a] = results[3][1]
        playerToT[a] = t
    }

    debug("done")
}

