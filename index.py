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

def updatePlayerData(player, rating, rd):
    fp = open('players.dat')
    fpdata = fp.read()
    fp.close()

    lines = fpdata.split("\n")

    for i,l in enumerate(lines):
        m = re.match('^(.*) (\d+) (\d+)$', l)
        name = m.group(1)
        if name == player:
            lines[i] = '%s %d %d' % (player, rating, rd)
            break

    fp = open('players.dat', 'w+')
    fp.write("\n".join(lines))
    fp.close()

# given [a1,a2,b1,b2], return rating deltas and RD deltas [[delta_r1, delta_r2, delta_r3, delta_r4],
#  [delta_RD1, delta_RD2, delta_RD3, delta_RD4]]
def calculateAdjustments(ratings, rds, times):
    [delta_r1, delta_r2, delta_r3, delta_r4] = [0,0,0,0]
    [delta_RD1, delta_RD2, delta_RD3, delta_RD4] = [0,0,0,0]

    # suppose a1 wins:
    [delta_r1, delta_RD1] = glicko.glickoDelta(ratings, rds);
    # suppose a2 wins:
    [ratings[0], ratings[1]] = [ratings[1], ratings[0]]
    [rds[0], rds[1]] = [rds[1], rds[0]]
    [times[0], times[1]] = [times[1], times[0]]
    [delta_r2, delta_RD2] = glickoDelta(ratings, rds);
    # suppose a3 wins:
    ratings = ratings[2:] + ratings[:2]
    rds = rds[2:] + rds[:2]
    times = times[2:] + times[:2]
    [delta_r3, delta_RD3] = glickoDelta(ratings, rds);
    # suppose a4 wins:
    [ratings[0], ratings[1]] = [ratings[1], ratings[0]]
    [rds[0], rds[1]] = [rds[1], rds[0]]
    [times[0], times[1]] = [times[1], times[0]]
    [delta_r4, delta_RD4] = glickoDelta(ratings, rds);


    [newRating, newRD] = glicko
    winnerAdjRating = - ratings[0]
    # winners: indices 0,1 - losers: indices 2,3
    # calculate new score
    winnerRating = (ratings[0] + ratings[1]) / 2;
    winnerRD = (rds[0] + rds[1]) / 2
    loserRating = (ratings[2] + ratings[3]) / 2
    loserRD = (rds[2] + rds[3]) / 2

    #print "glickoWinner(%d, %d)<br>\n" % (winnerRating, winnerRD)
    glickoWinner = glicko.Player(winnerRating, winnerRD)
    #print "glickoLoser(%d, %d)<br>\n" % (loserRating, loserRD)
    glickoLoser = glicko.Player(loserRating, loserRD)
           
    #print "calculating...<br>\n"
    glickoWinner.update_player([loserRating], [loserRD], [1])
    #print "glickoWinner (.rating, .rd) = (%d, %d)<br>\n" % (glickoWinner.rating, glickoWinner.rd)
    glickoLoser.update_player([winnerRating], [winnerRD], [0])
    #print "glickoLoser (.rating, .rd) = (%d, %d)<br>\n" % (glickoLoser.rating, glickoLoser.rd)

    winnerAdjRating = int(glickoWinner.rating - winnerRating)
    winnerAdjRD = int(glickoWinner.rd - winnerRD)
    loserAdjRating = int(glickoLoser.rating - loserRating)
    loserAdjRD = int(glickoLoser.rd - loserRD)

    # at least one point must be exchanged
    if not winnerAdjRating:
        winnerAdjRating = 1;
    if not loserAdjRating:
        loserAdjRating = -1

    return [winnerAdjRating, winnerAdjRD, loserAdjRating, loserAdjRD]

def stripParenScore(p):
    # converts "Luke (796)" to "Luke"
    m = re.match(r'^(.*) \(\d+\)$', p)
    if m:
        p = m.group(1)
    return p

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
    ts = map(lambda x: db.getPlayerT(x), [a1,a2,b1,b2])

    [winDelta, winRD] = glicko.glickoDelta(ratings, rds, ts[0], 1)
    [loseDelta, loseRD] = glicko.glickoDelta(ratings, rds, ts[0], 0)

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

    a1 = re.sub(r' \(\d.*$', '', a1)
    a2 = re.sub(r' \(\d.*$', '', a2)
    b1 = re.sub(r' \(\d.*$', '', b1)
    b2 = re.sub(r' \(\d.*$', '', b2)

    #print("a1: ", a1);
    #print("a2: ", a2);
    #print("b1: ", b1);
    #print("b2: ", b2);

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

    # log it
    db.recordGame(int(time.time()), winner1, db.getPlayerRating(winner1), winner2, \
        db.getPlayerRating(winner2), loser1, db.getPlayerRating(loser1), loser2, \
        db.getPlayerRating(loser2))
  
    # calculate new score
    [winnerAdjRating, winnerAdjRD, loserAdjRating, loserAdjRD] = \
        calculateAdjustments([db.getPlayerRating(winner1), db.getPlayerRating(winner2), \
                                db.getPlayerRating(loser1), db.getPlayerRating(loser2)], \
                            [db.getPlayerRD(winner1), db.getPlayerRD(winner2), \
                                db.getPlayerRD(loser1), db.getPlayerRD(loser2)])

    # update all players
    updatePlayerData(winner1, db.getPlayerRating(winner1) + winnerAdjRating,
        db.getPlayerRD(winner1) + winnerAdjRD);
    updatePlayerData(winner2, db.getPlayerRating(winner2) + winnerAdjRating,
        db.getPlayerRD(winner2) + winnerAdjRD);

    updatePlayerData(loser1, db.getPlayerRating(loser1) + loserAdjRating,
        db.getPlayerRD(loser1) + loserAdjRD);
    updatePlayerData(loser2, db.getPlayerRating(loser2) + loserAdjRating,
        db.getPlayerRD(loser2) + loserAdjRD);

    # fall through to "play" mode
    op = 'play'

if op == 'play':
    print '<html>'
    print '<head>'
    print '<link rel=StyleSheet href="stylesheet.css" type="text/css">'
    print '<script type="text/javascript" src="./bugtrack.js"></script>'
    print '</head>'
    print '<body>'
    print ' <form action=index.py method=post>'
    print ' <input type=hidden name="op" value="record">'
    print ' <table width="100%" cellpadding=12 cellspacing=0>'
#    print '  <tr>'
#    print '   <th width="50%" bgcolor="#FF9797" style="color:red">Team A</th>'
#    print '   <th width="50%" bgcolor="#A9C5EB" style="color:blue">Team B</th>'
#    print '  </tr>'
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
    print '    <input name="TeamAWins" type=submit value="WIN">'
    print '   </td>'
    print '   <td bgcolor="#A9C5EB">'
    print '    <input name="TeamBWins" type=submit value="WIN">'
    print '   </td>'
    print '  </tr>'
    print ' </table>'
    print ' </form>'
    print '</body>'
    print '</html>'
