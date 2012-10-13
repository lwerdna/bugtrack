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
    db.recordGame({'a1':form['a1'].value, 'a1_r':int(form['a1_r'].value), 'a1_rd':int(form['a1_rd'].value),
                   'a2':form['a2'].value, 'a2_r':int(form['a2_r'].value), 'a2_rd':int(form['a2_rd'].value),
                   'b1':form['b1'].value, 'b1_r':int(form['b1_r'].value), 'b1_rd':int(form['b1_rd'].value),
                   'b2':form['b2'].value, 'b2_r':int(form['b2_r'].value), 'b2_rd':int(form['a2_rd'].value),
                   't':form['t'].value
                });

    db.setPlayerStats(form['a1'].value, [int(form['a1_r_new'].value), int(form['a1_rd_new'].value), int(form['t'].value)])
    db.setPlayerStats(form['a2'].value, [int(form['a2_r_new'].value), int(form['a2_rd_new'].value), int(form['t'].value)])
    db.setPlayerStats(form['b1'].value, [int(form['b1_r_new'].value), int(form['b1_rd_new'].value), int(form['t'].value)])
    db.setPlayerStats(form['b2'].value, [int(form['b2_r_new'].value), int(form['b2_rd_new'].value), int(form['t'].value)])

    print "OK",

if op == 'predict':
    a1 = form['a1'].value
    a2 = form['a2'].value
    b1 = form['b1'].value
    b2 = form['b2'].value

    ratings = map(lambda x: db.getPlayerRating(x), [a1,a2,b1,b2])
    rds = map(lambda x: db.getPlayerRD(x), [a1,a2,b1,b2])
    ts = map(lambda x: db.getPlayerT(x), [a1,a2,b1,b2])

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
                            g['a1'], g['a1_r'], g['a1_rd'],
                            g['a2'], g['a2_r'], g['a2_rd'],
                            g['b1'], g['b1_r'], g['b1_rd'],
                            g['b2'], g['b2_r'], g['b2_rd'] )


