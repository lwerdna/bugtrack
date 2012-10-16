/*

bugtrack statistics javascript
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

var elem_iStatsPlayerChoice

var playerElems = []
var playerNames = []
var playerToR = []
var playerToRD = []
var playerToT = []

/******************************************************************************
 * inner-mode functions
 *****************************************************************************/

/* called when the page loads */
function statsInit(x) {
    this.name = 'window_bugtrack_stats'

    /* init global player vars */
    var resp = ajax('cgi/jsIface.py?op=getplayers')
    var lines = resp.split("\n")
    for(var j in lines) {
        var m = lines[j].match(/^(.*),(.*),(.*),(.*)$/)

        if(m) {
            playerName = m[1]
            playerNames.push(playerName)
            playerToR[playerName] = parseInt(m[2])
            playerToRD[playerName] = parseInt(m[3])
            playerToT[playerName] = parseInt(m[4])
        }
    }

    /* populate player choice drop-down in the individual stats */
    playerNames.sort()
    elem_iStatsPlayerChoice = document.getElementById("istatsPlayerChoice")
    elem_iStatsPlayerChoice.value = ''
    elem_iStatsPlayerChoice.innerHTML = '<option></option>'
    for(var j in playerNames) {
        elem_iStatsPlayerChoice.innerHTML += "<option>" + playerNames[j] + "</option>"
    }

    /* display */
    showElems.push(document.getElementById("stats"))
    showElems.push(document.getElementById("istats"))
    showStats()
}

function showStats() {
    hideAllBut([document.getElementById('stats')], showElems)

    // each graph has a function dedicated to loading it...
    loadLeaderBoard()
    loadAllRatingsVsGamesGraph()
    loadAllRatingsHistoryGraph()
}

function showIStats() {
    hideAllBut([document.getElementById('istats')], showElems)

    // graphs don't load until user makes player selection 
}

/******************************************************************************
 * OVERALL STATS MODE stuff
 *****************************************************************************/
function loadLeaderBoard() {
    document.getElementById("LeaderBoard").innerHTML = "loading..."

    rankedPlayers = playerNames
    rankedPlayers.sort(function(a,b){ return playerToR[b]-playerToR[a] })

    var html = ''
    html += '<table>'
    html += '<tr><th colspan=3>Leader Board!</th></tr>'

    var place = 1
    for(var i in rankedPlayers) {
        p = rankedPlayers[i]

        if(playerToRD[p] > 200) {
            continue
        }

        html += "<tr><td>" + place + ")</td><td align=right><font color=#64788B>" + p +  
        "</font></td><td>" + playerToR[p] + '.' + playerToRD[p] + "</td></tr>\n"

        place++
    }
    html += '</center>'
    document.getElementById("LeaderBoard").innerHTML = html
}

function loadAllRatingsHistoryGraph() {
    /* prepare the user for delay */
    document.getElementById("AllRatingsHistoryGraph_status").innerHTML = "loading..."

    /* get to work */
    var playerList = []
    var playerToObject = {}

    /* each game offers a sample point */
    var resp = ajax("cgi/jsIface.py?op=getGames")
    var lines = resp.split("\n")
    for(var i in lines) {
        var data = lines[i].split(",")
        var t = parseInt(data[0])
        var A = data[1]
        var A_r = parseInt(data[2])
        var b = data[4]
        var b_r = parseInt(data[5])
        var a = data[7]
        var a_r = parseInt(data[8])
        var B = data[10]
        var B_r = parseInt(data[11])

        if(isNaN(t)) {
            continue
        }

        var players = [A, b, a, B]
        var ratings = [A_r, b_r, a_r, B_r]

        /* update each player's data from the game */
        for(var j in players) {
            var p = players[j]
            var r = ratings[j]

            /* create if not exist yet */
            if(playerToObject[p] == undefined) {
                playerList.push(p)
                playerToObject[p] = { name: p, data: [] }
            }

            /* append this one rating sample */
            /* recall that the 'datetime' type of xAxis in highcharts expects milliseconds */
            playerToObject[p]['data'].push([t*1000, r])
        }
    }

    /* finally, push the current ratings as the last sample point for each present player */
    tNow = (new Date()).getTime()
    for(var i in playerNames) {
        p = playerNames[i]

        if(playerToObject[p] == undefined) {
            continue
        }

        playerToObject[p]['data'].push([tNow, playerToR[p]])
    }

    /* build the series as an array of player objects */
    var seriesData = []
    for(var i in playerList) {
        seriesData.push(playerToObject[playerList[i]])
    }

    /* finally, render the graph into this div */
    var chart = new Highcharts.Chart(
        {
            chart: {
                renderTo: document.getElementById("AllRatingsHistoryGraph"), 
                zoomType: 'xy', 
                type: 'line'
            },
            plotOptions: {
               series: {
                   marker: {
                       enabled: false,
                       states: {
                           hover: {
                               enabled: true
                           }
                       }
                   }
               }
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
                    return '<b>'+ this.series.name +'</b><br/>'+Highcharts.dateFormat('%e. %b', this.x) +': '+ this.y
                }
            },
            series: seriesData
        }
    )

    /* erase the "loading..." message */
    document.getElementById("AllRatingsHistoryGraph_status").innerHTML = ""
}

function loadAllRatingsVsGamesGraph() {
    /* prepare the user for delay */
    document.getElementById("AllRatingsVsGamesGraph_status").innerHTML = "loading..."

    /* get to work */
    var playerList = []
    var playerToObject = {}

    var resp = ajax("cgi/jsIface.py?op=getGames")
    var lines = resp.split("\n")
    for(var i in lines) {
        var data = lines[i].split(",")
        var t = parseInt(data[0])
        var A = data[1]
        var A_r = parseInt(data[2])
        var b = data[4]
        var b_r = parseInt(data[5])
        var a = data[7]
        var a_r = parseInt(data[8])
        var B = data[10]
        var B_r = parseInt(data[11])

        if(isNaN(t)) {
            continue
        }

        var players = [A, b, a, B]
        var ratings = [A_r, b_r, a_r, B_r]

        /* update each player's data from the game */
        for(var i in players) {
            var p = players[i]
            var r = ratings[i]

            /* create if not exist yet */
            if(playerToObject[p] == undefined) {
                playerList.push(p)
                playerToObject[p] = { name: p, data: [], nGames: 0 }
            }

            /* append this one rating sample */
            var nGames = playerToObject[p]['nGames']
            playerToObject[p]['data'].push([nGames, r])
            playerToObject[p]['nGames']++
        }
    }

    /* build the series as an array of player objects */
    var seriesData = []
    for(var i in playerList) {
        playerToObject[playerList[i]]['nGames'] = undefined
        seriesData.push(playerToObject[playerList[i]])
    }

    /* finally, render the graph into this div */
    var chart = new Highcharts.Chart(
        {
            chart: {
                renderTo: document.getElementById("AllRatingsVsGamesGraph"), 
                zoomType: 'xy', 
                type: 'line'
            },
            plotOptions: {
               series: {
                   marker: {
                       enabled: false,
                       states: {
                           hover: {
                               enabled: true
                           }
                       }
                   }
               }
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
                    return '<b>'+ this.series.name +'</b><br/>'+Highcharts.dateFormat('%e. %b', this.x) +': '+ this.y
                }
            },
            series: seriesData
        }
    )

    /* erase the "loading..." message */
    document.getElementById("AllRatingsVsGamesGraph_status").innerHTML = ""
}

/******************************************************************************
 * INDIVIDUAL STATS MODE stuff
 *****************************************************************************/
function istatsPlayerChoice_cb(elem) {
    if(elem.value != "") {
        loadIStatsExtended(elem.value)
        loadResultsVsPartnersGraph(elem.value)
        loadResultsVsOpponentsGraph(elem.value)
    }
}

function loadIStatsExtended(who) {
    document.getElementById("IStatsExtended").innerHTML = "loading..."

    var html = ''
    html += '<table>'
    var resp = ajax("cgi/jsIface.py?op=getstatsextended&player=" + who)
    var lines = resp.split("\n")

    for(var i in lines) {
        if(!lines[i]) {
            continue
        }

        nameData = lines[i].split(",")
        html += "<tr><td align=right><font color=#64788B>" + nameData[0] + ":</font></td><td>" + nameData[1] + "</td></tr>\n"
    }
    html += '</center>'
    document.getElementById("IStatsExtended").innerHTML = html

}

function loadResultsVsPartnersGraph(who) {
    /* prepare the user for delay */
    document.getElementById("ResultsVsPartnersGraph_status").innerHTML = "loading..."

    /* get to work */

    var partnerList = []
    var partnerToObj = {}

    var resp = ajax("cgi/jsIface.py?op=getGames")
    var lines = resp.split("\n")
    for(var i in lines) {
        var data = lines[i].split(",")
        var t = parseInt(data[0])
        var A = data[1]
        var A_r = parseInt(data[2])
        var b = data[4]
        var b_r = parseInt(data[5])
        var a = data[7]
        var a_r = parseInt(data[8])
        var B = data[10]
        var B_r = parseInt(data[11])
        var partner
        var result

        if(isNaN(t)) {
            continue
        }

        /* can find partner? */
        if(A == who) {
            partner = b
            result = 1
        }
        else if(b == who) {
            partner = A
            result = 1
        }
        else if(a == who) {
            partner = B
            result = 0
        }
        else if(B == who) {
            partner = a
            result = 0
        }
        else {
            continue
        }

        /* create entry if not exist */
        if(partnerToObj[partner] == undefined) {
            partnerList.push(partner)
            partnerToObj[partner] = { name: "Partner: " + partner, data: [0,0] }
        }

        if(result == 1) {
            partnerToObj[partner].data[0]++
        }
        else {
            partnerToObj[partner].data[1]++
        }
    }

    /* build the series as an array of player objects */
    var seriesData = [{name: 'Wins', data:[]}, {name: 'Losses', data:[]}]
    for(var i in partnerList) {
        seriesData[0].data.push(partnerToObj[partnerList[i]].data[0])
        seriesData[1].data.push(partnerToObj[partnerList[i]].data[1])
    }

    /* finally, render the graph into this div */
    var chart = new Highcharts.Chart(
        {
            chart: {
                renderTo: document.getElementById("ResultsVsPartnersGraph"), 
                type: 'bar'
            },
            plotOptions: {
               series: {
                   marker: {
                       enabled: false,
                       states: {
                           hover: {
                               enabled: true
                           }
                       }
                   }
               }
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
            series: seriesData
        }
    )

    /* erase the "loading..." message */
    document.getElementById("ResultsVsPartnersGraph_status").innerHTML = ""
}

function loadResultsVsOpponentsGraph(who) {
    /* prepare the user for delay */
    document.getElementById("ResultsVsOpponentsGraph_status").innerHTML = "loading..."

    /* get to work */

    var oppList = []
    var oppToObj = {}

    var resp = ajax("cgi/jsIface.py?op=getGames")
    var lines = resp.split("\n")
    for(var i in lines) {
        var data = lines[i].split(",")
        var t = parseInt(data[0])
        var A = data[1]
        var A_r = parseInt(data[2])
        var b = data[4]
        var b_r = parseInt(data[5])
        var a = data[7]
        var a_r = parseInt(data[8])
        var B = data[10]
        var B_r = parseInt(data[11])
        var opponents = []
        var result

        if(isNaN(t)) {
            continue
        }

        /* can find opponent? */
        if(A == who) {
            opponents.push(a)
            opponents.push(B)
            result = 1
        }
        else if(b == who) {
            opponents.push(a)
            opponents.push(B)
            result = 1
        }
        else if(a == who) {
            opponents.push(A)
            opponents.push(b)
            result = 0
        }
        else if(B == who) {
            opponents.push(A)
            opponents.push(b)
            result = 0
        }
        else {
            continue
        }

        /* create entry if not exist */
        for(var i in opponents) {
            if(oppToObj[opponents[i]] == undefined) {
                oppList.push(opponents[i])
                oppToObj[opponents[i]] = { name: "Opponent: " + opponents[i], data: [0,0] }
            }
    
            if(result == 1) {
                oppToObj[opponents[i]].data[0]++
            }
            else {
                oppToObj[opponents[i]].data[1]++
            }
        }
    }

    /* build the series as an array of player objects */
    var seriesData = [{name: 'Wins', data:[]}, {name: 'Losses', data:[]}]
    for(var i in oppList) {
        seriesData[0].data.push(oppToObj[oppList[i]].data[0])
        seriesData[1].data.push(oppToObj[oppList[i]].data[1])
    }

    /* finally, render the graph into this div */
    var chart = new Highcharts.Chart(
        {
            chart: {
                renderTo: document.getElementById("ResultsVsOpponentsGraph"), 
                type: 'bar'
            },
            plotOptions: {
               series: {
                   marker: {
                       enabled: false,
                       states: {
                           hover: {
                               enabled: true
                           }
                       }
                   }
               }
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
    )

    /* erase the "loading..." message */
    document.getElementById("ResultsVsOpponentsGraph_status").innerHTML = ""
}


