#!/usr/bin/python
#
# bugtrack javascript interface 
# 
# Copyright 2012 
# Andrew Lamoureux
# James Thompson
# 
# This file is a part of bugtrack
# 
# bugtrack is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# this is the interface by which the JavaScript interacts with the "back-end"
# (database, persistent storage) of the rest of bugtrack
#
# the JS makes get/post requests to this CGI, and this prints data (initially
# in CSV format) which the JS parses and presents to the user (via HTML or
# high charts, etc.)

import os
import cgi
import DbSqlite

if ('HTTP_HOST' in os.environ) and (os.environ['HTTP_HOST'] == 'localhost'):
    import cgitb
    cgitb.enable()

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

print "Content-Type: text/html\x0d\x0a\x0d\x0a",

db = DbSqlite.DbSqlite()
playerList = db.getPlayerList()

form = cgi.FieldStorage()

op = 'play'
if 'op' in form:
    op = form['op'].value

if op == 'recordGame':
    db.recordGame({'A':form['A'].value, 'A_r':int(form['A_r'].value), 'A_rd':int(form['A_rd'].value),
                   'b':form['b'].value, 'b_r':int(form['b_r'].value), 'b_rd':int(form['b_rd'].value),
                   'a':form['a'].value, 'a_r':int(form['a_r'].value), 'a_rd':int(form['a_rd'].value),
                   'B':form['B'].value, 'B_r':int(form['B_r'].value), 'B_rd':int(form['b_rd'].value),
                   't':form['t'].value
                });

    db.setPlayerStats(form['A'].value, [int(form['A_r_new'].value), int(form['A_rd_new'].value), int(form['t'].value)])
    db.setPlayerStats(form['b'].value, [int(form['b_r_new'].value), int(form['b_rd_new'].value), int(form['t'].value)])
    db.setPlayerStats(form['a'].value, [int(form['a_r_new'].value), int(form['a_rd_new'].value), int(form['t'].value)])
    db.setPlayerStats(form['B'].value, [int(form['B_r_new'].value), int(form['B_rd_new'].value), int(form['t'].value)])

    print "OK",

if op == 'predict':
    A = form['A'].value
    b = form['b'].value
    a = form['a'].value
    B = form['B'].value

    ratings = map(lambda x: db.getPlayerRating(x), [A,b,a,B])
    rds = map(lambda x: db.getPlayerRD(x), [A,b,a,B])
    ts = map(lambda x: db.getPlayerT(x), [A,b,a,B])

    [winDelta, loseDelta] = glicko.calcRatingWinLossDeltaPlayer(ratings, rds, ts)

    print "%d,%d" % (winDelta, loseDelta)

if op == 'deleteGame':
    db.deleteGame(form['t'].value)
    print "OK",

if op == 'getplayers':
    pl = db.getPlayerList()
    for p in pl:
        [rating, rd, t] = db.getPlayerStats(p)
        print "%s,%d,%d,%d" % (p, rating, rd, t)

if op == 'getstats':
    player = form['player'].value
    pl = db.getPlayerList()
    if player in pl:
        [rating, rd, t] = db.getPlayerStats(player)
        print "%d,%d,%d" % (rating, rd, t)

if op == 'getcardstats':
    player = form['player'].value
    pl = db.getPlayerList()
    if player in pl:
        [rating,rd,rank,wins,losses,streak] = db.getPlayerCardStats(player)
        print "%d,%d,%d,%d,%d,%d" % (rating,rd,rank,wins,losses,streak)

if op == 'getstatsextended':
    player = form['player'].value
    estats = db.getPlayerStatsExtended(player)
    print estats,

if op == 'getGames':
    games = db.getGames()
    for g in games:
        print "%d,%s,%d,%d,%s,%d,%d,%s,%d,%d,%s,%d,%d" % (
                            g['t'], 
                            g['A'], g['A_r'], g['A_rd'], # team bottom
                            g['b'], g['b_r'], g['b_rd'],
                            g['a'], g['a_r'], g['a_rd'], # team top
                            g['B'], g['B_r'], g['B_rd'] )


