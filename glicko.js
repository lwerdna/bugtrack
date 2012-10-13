/*

bugtrack glicko javascript
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
    //debug("rps is: ", rps)
    var rps = Math.min(rps, 365)

    // for new player
    for(var i in rds) {
        if(rds[i] < 30 || rds[i] > 350) {
            debug("calcRatingRdPlayer() given rd not in [30,350]!")
            return
        }
    }

    // RD adjustment due to time
    var rd = rds[0]
    // original glicko squares c here, bughouse does not (mistake? or mod?)
    rd = Math.min(Math.sqrt(Math.pow(rd,2) + c * rps), 350.0)
    //debug("rd: ", rd)

    // attenuating factor
    var p = .0000025180996504909944  // 3*Math.log(10)**2 / (Math.PI**2 * 800**2)
    var f = 1/Math.sqrt(1 + p*(Math.pow(rds[1],2) + Math.pow(rds[2],2) + Math.pow(rds[3],2)))
    // f should be [0, 1] ...large RD's result in small f's
    //debug("f: ", f)

    // average ratings
    var r1 = (ratings[0]+ratings[1])/2.0
    var r2 = (ratings[2]+ratings[3])/2.0

    //debug("r1: ", r1)
    //debug("r2: ", r2)
    var E = 1/(1 + Math.pow(10, -1*(r1-r2)*f/400))
    //debug("E: ", E)

    // begin-pre
    //debug("q=", q)
    //debug("f=", f)
    var denom = 1/(rd*rd) + q*q*f*f*E*(1-E)
    //debug("denom: ", denom
    var K = q*f / denom
    //debug("K: ", K)
    K = Math.max(K,16)
    //debug("K: ", K)

    // new rating, new rd
    var rating = ratings[0] + K*(w - E)
    var rd = 1/Math.sqrt(denom)
    //debug("rd before reduction: ", rd)
    rd = Math.min(rd, 350)
    rd = Math.max(rd, 30)

    // done
    var up = 0

    var delta = (rating - ratings[0])
    if(delta < 0 && delta > -1) {
        rating = ratings[0] - 1
    }
    else if(delta > 0 && delta < 1) {
        rating = ratings[0] + 1
    }

    rating = Math.round(rating)
    rd = Math.round(rd)

    if(rating == ratings[0]) {
        rating = ratings[0] + 1
    }

    return [rating, rd]
}

function calcRatingRdDeltaPlayer(ratings, rds, t, w) {
    ratingData = calcRatingRdPlayer(ratings, rds, t, w)
    return [ratingData[0] - ratings[0], ratingData[1] - rds[0]]
}

// if A (with partner b, opponents B,a) plays, return his <+win>,<-loss> adjustment
// returns [winDelta, loseDelta]
function calcRatingWinLossDeltaPlayer(ratings, rds, ts) {
    tNow = Math.round((new Date()).getTime() / 1000)
    winRandRD = calcRatingRdDeltaPlayer(ratings, rds, secToRatingPeriods(tNow - ts[0]), 1)
    loseRandRD = calcRatingRdDeltaPlayer(ratings, rds, secToRatingPeriods(tNow - ts[0]), 0)
    //debug("(winDelta, loseDelta) = (" + winRandRD[0] + "," + loseRandRD[0] + ")\n")
    return [winRandRD[0], loseRandRD[0]]
}

// suppose a game is played with winners A,b and losers B,a
// given [A,b,B,a], return the new ratings/rd's in this form:
// [[A_RATING, A_RD], [b_RATING, b_RD], [B_RATING, B_RD], [a_RATING, a_RD]]
//
function calcGameScores(ratings, rds, tds) {
    // calculate new scores

    // calculate for A (winner, white)
    stats1 = calcRatingRdPlayer(ratings, rds, tds[0], 1)
    debug("A new stats: " + stats1)

    // calculate for b (winner, black)
    ratings = [ratings[1], ratings[0], ratings[2], ratings[3]]
    rds = [rds[1], rds[0], rds[2], rds[3]]
    stats2 = calcRatingRdPlayer(ratings, rds, tds[1], 1)
    debug("b new stats: " + stats2)

    // calculate for B (loser, white)
    ratings = [ratings[2], ratings[3], ratings[0], ratings[1]]
    rds = [rds[2], rds[3], rds[0], rds[1]]
    stats3 = calcRatingRdPlayer(ratings, rds, tds[2], 0)
    debug("B new stats: " + stats3)

    // calculate for a (loser, black)
    ratings = [ratings[1], ratings[0], ratings[2], ratings[3]]
    rds = [rds[1], rds[0], rds[2], rds[3]]
    stats4 = calcRatingRdPlayer(ratings, rds, tds[3], 0)
    debug("a new stats: " + stats4)

    return [stats1, stats2, stats3, stats4]
}
