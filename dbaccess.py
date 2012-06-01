#!/usr/bin/python

import re
import os
import cgi
import math
import time
import glicko
import DbSqlite

if ('HTTP_HOST' in os.environ) and (os.environ['HTTP_HOST'] == 'localhost'):
    import cgitb
    cgitb.enable()

def printPlayerSelectOptions(players, initial):
    print "      <option></option>"

    for player in sorted(players):
        print "      <option",
        
        if player == initial:
            print ' selected',
            
        print '>%s</option>' % player

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

if op == 'record':
    (winner1, winner2, loser1, loser2) = ('','','','')
    a1 = form['a1'].value
    a2 = form['a2'].value
    b1 = form['b1'].value
    b2 = form['b2'].value

    if 'TeamAWins' in form:
        pass
    elif 'TeamBWins' in form:
        [a1,a2,b1,b2] = [b2,b1,a2,a1]
    else:
        raise "Who won?"

    ratings = map(lambda x: db.getPlayerRating(x), [a1,a2,b1,b2])
    rds = map(lambda x: db.getPlayerRD(x), [a1,a2,b1,b2])
    tnow = int(time.time())
    tds = map(lambda x: glicko.secToRatingPeriods(tnow - db.getPlayerT(x)), [a1,a2,b1,b2])

    # log game
    db.recordGame({
        't': tnow, 
        'a1':a1, 'a1_r':ratings[0], 'a1_rd':rds[0],
        'a2':a2, 'a2_r':ratings[1], 'a2_rd':rds[1],
        'b1':b1, 'b1_r':ratings[2], 'b1_rd':rds[2],
        'b2':b2, 'b2_r':ratings[3], 'b2_rd':rds[3]
    })

    # compute new scores
    [stats1, stats2, stats3, stats4] = glicko.calcGameScores(ratings, rds, tds)

    # store new scores
    db.setPlayerStats(a1, stats1 + [tnow])
    db.setPlayerStats(a2, stats2 + [tnow])
    db.setPlayerStats(b1, stats3 + [tnow])
    db.setPlayerStats(b2, stats4 + [tnow])

    print 'OK'

if op == 'play':
    print '<html>'
    print '<head>'
    print '<link rel=StyleSheet href="play.css" type="text/css">'
    print '<script type="text/javascript" src="./bugtrack.js"></script>'
    print '</head>'
    print '<body style="margin:0px">'
    #print ' <form action=index.py method=post>'
    print ' <input type=hidden name="op" value="record">'
    print ' <table width="100%" cellpadding=12 cellspacing=0>'
    print '  <tr>'
    print '   <th width="50%" bgcolor="#FF9797">Team A</th>'
    print '   <th width="50%" bgcolor="#A9C5EB">Team B</th>'
    print '  </tr>'
    print '  <tr>'
    print '   <td width="50%" bgcolor="#FF9797">'
    print '    <div class=chessWhite>'
    print '     <select name=a1 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(playerList, defaultTeamAPlayer1)
    print '     </select>'
    print '     <span id=a1_stats></span>'
    print '     <span class="predict" id=a1_predict></span>'
    print '    </div>'
    print '   </td>'
    print '   <td bgcolor="#A9C5EB">'
    print '    <div class=chessBlack>'
    print '     <select name=b1 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(playerList, defaultTeamBPlayer1)
    print '     </select>'
    print '     <span id=b1_stats></span>'
    print '     <span class="predict" id=b1_predict></span>'
    print '    </div>'
    print '   </td>'
    print '  </tr>'
    print '  <!-- team B -->'
    print '  <tr>'
    print '   <td bgcolor="#FF9797">'
    print '    <div class=chessBlack>'
    print '     <select name=a2 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(playerList, defaultTeamAPlayer2)
    print '     </select>'
    print '     <span id=a2_stats></span>'
    print '     <span class="predict" id=a2_predict></span>'
    print '    </div>'
    print '   </td>'
    print '   <td bgcolor="#A9C5EB">'
    print '    <div class=chessWhite>'
    print '     <select name=b2 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(playerList, defaultTeamBPlayer2)
    print '     </select>'
    print '     <span id=b2_stats></span>'
    print '     <span class="predict" id=b2_predict></span>'
    print '    </div>'
    print '   </td>'
    print '  </tr>'
    print '  <tr>'
    print '   <td bgcolor="#FF9797">'
    print '    <input name="TeamAWins" type=submit value="WIN" onClick="recordGame(this)">'
    print '    <input name="" type=submit value="swap &#x21c5;" onClick="swapTeamA(this)">'
    print '    <input name="" type=submit value="clear &#x21bb" onClick="clearTeamA(this)">'
    print '   </td>'
    print '   <td bgcolor="#A9C5EB">'
    print '    <input name="TeamBWins" type=submit value="WIN" onClick="recordGame(this)">'
    print '    <input name="" type=submit value="swap &#x21c5 " onClick="swapTeamB(this)">'
    print '    <input name="" type=submit value="clear &#x21bb" onClick="clearTeamB(this)">'
    print '   </td>'
    print '  </tr>'
    print ' </table>'
    #print ' </form>'
    print '</body>'
    print '</html>'
