/*

bugtrack general javascript
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
 * debug
 *****************************************************************************/
var g_DEBUG = 1

function debug(msg) {
    if(g_DEBUG) {
        console.log(msg)
    }
}

/******************************************************************************
 * UTILS
 *****************************************************************************/
function ajax(url) {
    var xmlhttp = new XMLHttpRequest()
    debug("AJAX: " + url)
    xmlhttp.open("GET", url, false)
    xmlhttp.send()
    var resp = xmlhttp.responseText
    debug("AJAX: " + resp)
    return resp
}

// stackoverflow, thx Shef!
function zfill(num, len) {
    return (Array(len).join("0") + num).slice(-len)
}

function longAgoStr(epoch) {
    var answer = ''
    var delta = (new Date().getTime() / 1000) - epoch

    if (delta < 60) {
        answer = delta.toFixed(1) + ' seconds'
    }
    else if (delta < 3600) {
        answer = (delta / 60).toFixed(1) + ' minutes'
    }
    else if (delta < 86400) {
        answer = (delta / 3600).toFixed(1) + ' hours'
    }
    else if (delta < 2592000) {
        answer = (delta / 86400).toFixed(0) + ' days'
    }
    else if (delta < 31536000) {
        answer = (delta / 2592000).toFixed(0) + ' months'
    }
    else {
        answer = (delta / 31536000.0).toFixed(0) + ' years'
    }

    return answer
}

function longAgoStrStealth(epoch) {
    var answer = ''
    var delta = (new Date().getTime() / 1000) - epoch
    var wDays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    var dateNow = new Date()
    var dateThen = new Date()
    dateThen.setTime(epoch*1000)

    /* if within the last 60 seconds, display "X seconds ago" */
    if (delta < 60) {
        answer = delta.toFixed(1) + ' seconds ago'
    }
    /* if within the last 10 minutes, display "X minutes ago" */
    else if (delta < 10*60) {
        answer = (delta / 60).toFixed(1) + ' minutes ago'
    }
    /* if within the last day, just say "today" */
    else if (delta < 24*60*60) {
        if(dateNow.getDay() != dateThen.getDay()) {
            answer = 'yesterday'
        }
        else {
            answer = 'today'
        }
    }
    /* if within a week */
    else if (delta < 7*24*60*60) {

        if(dateThen.getDay() < dateNow.getDay()) {
            answer = 'this ' + wDays[dateThen.getDay()]
        }
        else {
            answer = 'last ' + wDays[dateThen.getDay()]; 
        }
    }
    /* print the date and the days ago string */
    else {
        answer = dateToStringMini(dateNow) + '<br>\n(' + longAgoStr(epoch) + ' ago )'
    }

    return answer
}

function dateToString(d) {
    var wDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    var hours = d.getHours()

    var amPm = 'AM'

    if(hours > 12) {
        amPm = 'PM'
        hours -= 12
    } 

    return wDays[d.getDay()] + ' ' + months[d.getMonth()] + ' ' + d.getDate() + ', ' + (1900+d.getYear()) +
        ' ' + hours + ':' + zfill(d.getMinutes(), 2) + amPm
}

function dateToStringMini(d) {
    var wDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    var months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    var hours = d.getHours()

    var amPm = 'AM'

    if(hours > 12) {
        amPm = 'PM'
        hours -= 12
    } 

    return wDays[d.getDay()] + ' ' + months[d.getMonth()] + ' ' + d.getDate() + ', ' + (1900+d.getYear())
}

function swapElemVals(a, b)
{
    var t = a.value
    a.value = b.value
    b.value = t
}

function swapElemHTML(a, b)
{
    var t = a.innerHTML
    a.innerHTML = b.innerHTML
    b.innerHTML = t
}

function repositionTable(a) {
    /* using the ordering (as in database) of:
        [A, b, B, a]
        [white, black, white, black]
        we swap the players boards, preserving colors
        this is useful when, say, positioning winners to front of the array
        before storing game result information
        */
    return [a[2], a[3], a[0], a[1]]
}

function repositionColor(a) {
    /* using the ordering (as in database) of:
        [A, b, B, a]
        [white, black, white, black]
        we swap the players' colors
        this is useful when, say, positioning player to front of array 
        before querying predicted rating/rd change
        */
    return [a[1], a[0], a[3], a[2]]
}

function scrambleArray(a) {
    var swaps = a.length * 2

    for(var i=0; i<swaps; ++i) {
        var src = Math.round(Math.random() * (a.length - 1))
        var dst = Math.round(Math.random() * (a.length - 1))
        var t = a[src]
        a[src] = a[dst]
        a[dst] = t
    }

    return a
}

/******************************************************************************
 * inner-mode functions
 *****************************************************************************/
function isHidden(elem) {
    return elem.style.display == 'none'
}

function hide(elem) {
    elem.style.display = 'none'
}

function unHide(elem) {
    elem.style.display = 'block'
}

function hideAllBut(included, all) {
    for(var i in all) {
        /* if in the included array, display */
        if(included.indexOf(all[i]) >= 0) {
            all[i].style.display = 'block'
        }
        /* otherwise, hide */
        else {
            all[i].style.display = 'none'
        }
    }
}
