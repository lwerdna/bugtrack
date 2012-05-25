#!/usr/bin/python

import re
import os
import cgi
import math
import time
from glicko import glicko, glickoDelta
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
    [delta_r1, delta_RD1] = glickoDelta(ratings, rds);
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
    tAp1 = stripParenScore(form['TeamA_Player1'].value)
    tAp2 = stripParenScore(form['TeamA_Player2'].value)
    tBp1 = stripParenScore(form['TeamB_Player1'].value)
    tBp2 = stripParenScore(form['TeamB_Player2'].value)

    # if team A won...
    (taAdjWin, tbAdjLose) = (0,0)
    [taAdjWin, temp, tbAdjLose, temp] = \
        calculateAdjustments([db.getPlayerRating(tAp1), db.getPlayerRating(tAp2), db.getPlayerRating(tBp1), db.getPlayerRating(tBp2)], \
                            [db.getPlayerRD(tAp1), db.getPlayerRD(tAp2), db.getPlayerRD(tBp1), db.getPlayerRD(tBp2)])

    # if team B won...
    (tbAdjWin, taAdjLose) = (0,0)
    [tbAdjWin, temp, taAdjLose, temp] = \
        calculateAdjustments([db.getPlayerRating(tBp1), db.getPlayerRating(tBp2), db.getPlayerRating(tAp1), db.getPlayerRating(tAp2)], \
                            [db.getPlayerRD(tBp1), db.getPlayerRD(tBp2), db.getPlayerRD(tAp1), db.getPlayerRD(tAp2)])

    print "%d,%d,%d,%d" % (taAdjWin, taAdjLose, tbAdjWin, tbAdjLose),

if op == 'getstats':
    player = form['player'].value
    if player in playerList:
        [rating, rd] = db.getPlayerStats(player)
        print "%d,%d" % (rating, rd)

if op == 'record':
    (winner1, winner2, loser1, loser2) = ('','','','')
    teamA_Player1 = form['TeamA_Player1'].value
    teamA_Player2 = form['TeamA_Player2'].value
    teamB_Player1 = form['TeamB_Player1'].value
    teamB_Player2 = form['TeamB_Player2'].value

    teamA_Player1 = re.sub(r' \(\d.*$', '', teamA_Player1)
    teamA_Player2 = re.sub(r' \(\d.*$', '', teamA_Player2)
    teamB_Player1 = re.sub(r' \(\d.*$', '', teamB_Player1)
    teamB_Player2 = re.sub(r' \(\d.*$', '', teamB_Player2)

    #print("teamA_Player1: ", teamA_Player1);
    #print("teamA_Player2: ", teamA_Player2);
    #print("teamB_Player1: ", teamB_Player1);
    #print("teamB_Player2: ", teamB_Player2);

    if 'TeamAWins' in form:
        (winner1, winner2, loser1, loser2) = \
            (teamA_Player1, teamA_Player2, teamB_Player1, teamB_Player2)

        defaultTeamAPlayer1 = teamA_Player1
        defaultTeamAPlayer2 = teamA_Player2

    elif 'TeamBWins' in form:
        (winner1, winner2, loser1, loser2) = \
            (teamB_Player1, teamB_Player2, teamA_Player1, teamA_Player2)

        defaultTeamBPlayer1 = teamB_Player1
        defaultTeamBPlayer2 = teamB_Player2

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
    print '  <tr>'
    print '   <th width="50%" bgcolor="#FF9797">Team A</th>'
    print '   <th width="50%" bgcolor="#A9C5EB">Team B</th>'
    print '  </tr>'
    print '  <tr>'
    print '   <td bgcolor="#FF9797">'
    print '    <div class=chessWhite>'
    print '     <select name=TeamA_Player1 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(playerList, defaultTeamAPlayer1)
    print '     </select>'
    print '     <span id=tap1_stats></span>'
    print '    </div>'
    print '   </td>'
    print '   <td bgcolor="#A9C5EB">'
    print '    <div class=chessBlack>'
    print '     <select name=TeamB_Player1 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(playerList, defaultTeamBPlayer1)
    print '     </select>'
    print '     <span id=tbp1_stats></span>'
    print '    </div>'
    print '   </td>'
    print '  </tr>'
    print '  <!-- team B -->'
    print '  <tr>'
    print '   <td bgcolor="#FF9797">'
    print '    <div class=chessBlack>'
    print '     <select name=TeamA_Player2 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(playerList, defaultTeamAPlayer2)
    print '     </select>'
    print '     <span id=tap2_stats></span>'
    print '    </div>'
    print '   </td>'
    print '   <td bgcolor="#A9C5EB">'
    print '    <div class=chessWhite>'
    print '     <select name=TeamB_Player2 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(playerList, defaultTeamBPlayer2)
    print '     </select>'
    print '     <span id=tbp2_stats></span>'
    print '    </div>'
    print '   </td>'
    print '  </tr>'
    print '  <tr>'
    print '   <td bgcolor="#FF9797">'
    print '    <input name="TeamAWins" type=submit value="WIN">'
    print '    <span id="teamAPrediction"></span>'
    print '   </td>'
    print '   <td bgcolor="#A9C5EB">'
    print '    <input name="TeamBWins" type=submit value="WIN">'
    print '    <span id="teamBPrediction"></span>'
    print '   </td>'
    print '  </tr>'
    print ' </table>'
    print ' </form>'
    print '</body>'
    print '</html>'
