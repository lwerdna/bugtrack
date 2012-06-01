#!/usr/bin/python

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

defaultTeamAPlayer1 = ''
defaultTeamAPlayer2 = ''
defaultTeamBPlayer1 = ''
defaultTeamBPlayer2 = ''

op = 'play'
if 'op' in form:
    op = form['op'].value

if op == 'recordGame':
    db.recordGame({'a1':form['a1'].value, 'a1_r':int(form['a1_r'].value), 'a1_rd':int(form['a1_rd'].value),
                   'a2':form['a2'].value, 'a2_r':int(form['a2_r'].value), 'a2_rd':int(form['a2_rd'].value),
                   'b1':form['b1'].value, 'b1_r':int(form['b1_r'].value), 'b1_rd':int(form['b1_rd'].value),
                   'b2':form['a1'].value, 'a1_r':int(form['a1_r'].value), 'a1_rd':int(form['a1_rd'].value)
                });

    db.setPlayerStats([form['a1'].value, int(form['a1_r_new'].value), int(form['a1_rd_new'].value), int(form['a1_t_new'])])
    db.setPlayerStats([form['a2'].value, int(form['a2_r_new'].value), int(form['a2_rd_new'].value), int(form['a2_t_new'])])
    db.setPlayerStats([form['b1'].value, int(form['b1_r_new'].value), int(form['b1_rd_new'].value), int(form['b1_t_new'])])
    db.setPlayerStats([form['b2'].value, int(form['b2_r_new'].value), int(form['b2_rd_new'].value), int(form['b2_t_new'])])

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

if op == 'getplayers':
    pl = db.getPlayerList()
    for p in pl:
        [rating, rd, t] = db.getPlayerStats(p)
        print "%s,%d,%d,%d" % (p, rating, rd, t)

if op == 'getstats':
    player = form['player'].value
    if player in playerList:
        [rating, rd, t] = db.getPlayerStats(player)
        print "%d,%d,%d" % (rating, rd, t)


