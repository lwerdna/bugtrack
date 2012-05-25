#!/usr/bin/python

import re
import os
import cgi
import math
import time
import glicko
import DbText

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

db = DbText.DbText()
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
    # if a1 (with partner a2, opponents b1,b2) plays, return his <+win>,<-loss> adjustment

    a1 = form['a1'].value
    a2 = form['a2'].value
    b1 = form['b1'].value
    b2 = form['b2'].value

    t = db.getPlayerT(a1)

    ratings = map(lambda x: db.getPlayerRating(x), [a1,a2,b1,b2])
    rds = map(lambda x: db.getPlayerRD(x), [a1,a2,b1,b2])

    [winDelta, winRD] = glicko.glickoDelta(ratings, rds, int(time.time()) - t, 1)
    [loseDelta, loseRD] = glicko.glickoDelta(ratings, rds, int(time.time()) - t, 0)

    print "%d,%d" % (winDelta, loseDelta)

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
        (winner1, winner2, loser1, loser2) = \
            (a1, a2, b1, b2)

        defaultTeamAPlayer1 = a1
        defaultTeamAPlayer2 = a2

    elif 'TeamBWins' in form:
        (winner1, winner2, loser1, loser2) = \
            (b1, b2, a1, a2)

        defaultTeamBPlayer1 = b1
        defaultTeamBPlayer2 = b2

    else:
        raise "Who won?"

    # log game
    tnow = int(time.time())
    db.recordGame(tnow, winner1, db.getPlayerRating(winner1), winner2, \
        db.getPlayerRating(winner2), loser1, db.getPlayerRating(loser1), loser2, \
        db.getPlayerRating(loser2))

    #print 'winner1', winner1, '<br>\n'
    #print 'winner2', winner2, '<br>\n'
    #print 'loser1', loser1, '<br>\n'
    #print 'loser2', loser2, '<br>\n'

    # calculate new scores
    ratings = map(lambda x: db.getPlayerRating(x), [winner1, winner2, loser1, loser2])
    rds = map(lambda x: db.getPlayerRD(x), [winner1, winner2, loser1, loser2])
    tdelta = tnow - db.getPlayerT(winner1)
    stats1 = glicko.glicko(ratings, rds, tdelta, 1) + [tnow]
    #print "calling glicko(", ratings, ", ", rds, ", ", tdelta, ", 1)<br>\n"
    #print "winner1 new stats: ", stats1, '<br>\n'

    ratings = map(lambda x: db.getPlayerRating(x), [winner2, winner1, loser1, loser2])
    rds = map(lambda x: db.getPlayerRD(x), [winner2, winner1, loser1, loser2])
    tdelta = tnow - db.getPlayerT(winner2)
    stats2 = glicko.glicko(ratings, rds, tdelta, 1) + [tnow]
    #print "calling glicko(", ratings, ", ", rds, ", ", tdelta, ", 1)<br>\n"
    #print "winner2 new stats: ", stats2, '<br>\n'

    ratings = map(lambda x: db.getPlayerRating(x), [loser1, loser2, winner1, winner2])
    rds = map(lambda x: db.getPlayerRD(x), [loser1, loser2, winner2, winner1])
    tdelta = tnow - db.getPlayerT(loser1)
    stats3 = glicko.glicko(ratings, rds, tdelta, 0) + [tnow]
    #print "calling glicko(", ratings, ", ", rds, ", ", tdelta, ", 0)<br>\n"
    #print "loser1 new stats: ", stats3, '<br>\n'

    ratings = map(lambda x: db.getPlayerRating(x), [loser2, loser1, winner1, winner2])
    rds = map(lambda x: db.getPlayerRD(x), [loser2, loser1, winner1, winner2])
    tdelta = tnow - db.getPlayerT(loser2)
    stats4 = glicko.glicko(ratings, rds, tdelta, 0) + [tnow]
    #print "calling glicko(", ratings, ", ", rds, ", ", tdelta, ", 0)<br>\n"
    #print "loser2 new stats: ", stats4, '<br>\n'
   
    # store new scores
    db.setPlayerStats(winner1, stats1)
    db.setPlayerStats(winner2, stats2)
    db.setPlayerStats(loser1, stats3)
    db.setPlayerStats(loser2, stats4)

    print 'OK'

if op == 'play':
    print '<html>'
    print '<head>'
    print '<link rel=StyleSheet href="stylesheet.css" type="text/css">'
    print '<script type="text/javascript" src="./bugtrack.js"></script>'
    print '</head>'
    print '<body>'
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
    print '   </td>'
    print '   <td bgcolor="#A9C5EB">'
    print '    <input name="TeamBWins" type=submit value="WIN" onClick="recordGame(this)">'
    print '   </td>'
    print '  </tr>'
    print ' </table>'
    #print ' </form>'
    print '</body>'
    print '</html>'
