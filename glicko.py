#!/usr/bin/python

# typed up while reading:
# http://www.freechess.org/Help/HelpFiles/glicko.html

import time;
import math;

# Glicko says this works best when rating period has player playing "moderate" 5-10 games
# rating period: 1 day
# time for decay to noob: 365 rating periods
# let 50 be the RD of a typical player
# now to solve for c for RD=350 -> noob
# 350 = sqrt(50^2 + c^2 * 365)
# math.sqrt((350*350 - 2500)/365.0)
c = 18.131936556464982

# math.log(10)/400 in original glicko; this is bughouse mod:
q = 0.0028782313662425573 # math.log(10)/800

def secToRatingPeriods(secs):
    # note that periods are 1-based (ie: 1 denotes a game played in the last rating period)

    # rating periods now are 1 day
    periods = int(1 + (secs / (24*3600)))
    return min(periods, 365)

# ratings is list where [0] is dude we're calculating for, [1] is his partner
#  [2], [3] are the opponents
# rds is same
# t is seconds since last time he played a game
# w is 1 for win, 0 for loss
#

def calcRatingRdPlayer(ratings, rds, rps, w):
    global q
    global c

    # rps (rating periods) 
    #print "rps is: ", rps
    rps = min(rps, 365)

    # for new player
    for rd in rds:
        if (rd < 30) or (rd > 350):
            raise "calcRatingRdPlayer() given rd not in [30,350]!"

    # RD adjustment due to time
    rd = rds[0]
    # original glicko squares c here, bughouse does not (mistake? or mod?)
    rd = min(math.sqrt(rd**2 + c * rps), 350.0)
    #print "rd: ", rd

    # attenuating factor
    p = .0000025180996504909944  # 3*math.log(10)**2 / (math.pi**2 * 800**2)
    f = 1/math.sqrt(1 + p*(rds[1]**2 + rds[2]**2 + rds[3]**2))
    # f should be [0, 1] ...large RD's result in small f's
    #print "f: ", f

    # average ratings
    r1 = (ratings[0]+ratings[1])/2.0
    r2 = (ratings[2]+ratings[3])/2.0

    #print "r1: ", r1
    #print "r2: ", r2
    E = 1/(1 + math.pow(10, -1*(r1-r2)*f/400))
    #print "E: ", E

    # begin-pre
    #print "q=", q
    #print "f=", f
    denom = 1/(rd*rd) + q*q*f*f*E*(1-E)
    #print "denom: ", denom
    K = q*f / denom
    #print "K: ", K
    K = max(K,16)
    #print "K: ", K

    # new rating, new rd
    rating = ratings[0] + K*(w - E)
    rd = 1/math.sqrt(denom)
    #print "rd before reduction: ", rd
    rd = min(rd, 350)
    rd = max(rd, 30)

    # done
    return [rating, rd]

def calcRatingRdDeltaPlayer(ratings, rds, t, w):
    [newRating, newRD] = calcRatingRdPlayer(ratings, rds, t, w)
    return [newRating - ratings[0], newRD - rds[0]]

# if a1 (with partner a2, opponents b1,b2) plays, return his <+win>,<-loss> adjustment
# returns [winDelta, loseDelta]
def calcRatingWinLossDeltaPlayer(ratings, rds, ts):
    [winDelta, winRD] = calcRatingRdDeltaPlayer(ratings, rds, secToRatingPeriods(int(time.time()) - ts[0]), 1)
    [loseDelta, loseRD] = calcRatingRdDeltaPlayer(ratings, rds, secToRatingPeriods(int(time.time()) - ts[0]), 0)
    #print "%d,%d" % (winDelta, loseDelta)
    return [winDelta, loseDelta]

# suppose a game is played with winners a1,a2 and losers a3,a4
# given [a1,a2,a3,a4], return the new ratings/rd's in this form:
# [[a1_RATING, a1_RD], [a2_RATING, a2_RD], [b1_RATING, b1_RD], [b2_RATING, b2_RD]]
#
def calcGameScores(ratings, rds, tds):
    # calculate new scores

    # calculate for a1 (first winner, white)
    stats1 = calcRatingRdPlayer(ratings, rds, tds[0], 1)
    #print "calling calcRatingRdPlayer(", ratings, ", ", rds, ", ", tdelta, ", 1)<br>\n"
    #print "a1 new stats: ", stats1, '<br>\n'

    # calculate for a2 (first winner, black)
    ratings = [ratings[1], ratings[0], ratings[2], ratings[3]]
    rds = [rds[1], rds[0], rds[2], rds[3]]
    stats2 = calcRatingRdPlayer(ratings, rds, tds[1], 1)
    #print "calling calcRatingRdPlayer(", ratings, ", ", rds, ", ", tdelta, ", 1)<br>\n"
    #print "a2 new stats: ", stats2, '<br>\n'

    # calculate for b1 (first loser, black)
    ratings = [ratings[2], ratings[3], ratings[0], ratings[1]]
    rds = [rds[2], rds[3], rds[0], rds[1]]
    stats3 = calcRatingRdPlayer(ratings, rds, tds[2], 0)
    #print "calling calcRatingRdPlayer(", ratings, ", ", rds, ", ", tdelta, ", 0)<br>\n"
    #print "b1 new stats: ", stats3, '<br>\n'

    ratings = [ratings[1], ratings[0], ratings[2], ratings[3]]
    rds = [rds[1], rds[0], rds[2], rds[3]]
    stats4 = calcRatingRdPlayer(ratings, rds, tds[3], 0)
    #print "calling calcRatingRdPlayer(", ratings, ", ", rds, ", ", tdelta, ", 0)<br>\n"
    #print "b2 new stats: ", stats4, '<br>\n'

    return [stats1, stats2, stats3, stats4]

