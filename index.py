#!/usr/bin/python

import re
import os
import cgi
import math
import time
import glicko

if ('HTTP_HOST' in os.environ) and (os.environ['HTTP_HOST'] == 'localhost'):
    import cgitb
    cgitb.enable()

def getPlayersData():
    fp = open('players.dat')
    fpstuff = fp.read()
    fp.close()

    lines = fpstuff.split("\n")

    [playersToRating, playersToRD] = [{}, {}]
    for l in lines:
        #print "derp -%s-" % l
        m = re.match(r'^(.*) ([\d\.]+) ([\d\.]+)', l)
        if m:
            playersToRating[m.group(1)] = float(m.group(2))
            playersToRD[m.group(1)] = float(m.group(3))

    return [playersToRating, playersToRD]

def printPlayerSelectOptions(p2r, initial):
    print "      <option></option>"
    for player in sorted(p2r):
        print "      <option",
        
        if player == initial:
            print ' selected',
            
        playerStr = '%s (%d)' % (player, p2r[player])
        print '>%s</option>' % playerStr

def logGameResult(winner1, winner2, loser1, loser2, rateAdjWin, rateAdjLose):
    fp = open('games.dat', 'a')
    dateStr = time.strftime("%a %b %d, %Y %H:%M:%S", time.gmtime(time.time() - 4*3600))
    fp.write("[%s] %s,%s (+%d) > %s,%s (%d)\n" % (dateStr, winner1, winner2, rateAdjWin, loser1, loser2, rateAdjLose));
    fp.close()

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

def calculateAdjustments(ratings, rds):
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

[p2r, p2rd] = getPlayersData()

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
        calculateAdjustments([p2r[tAp1], p2r[tAp2], p2r[tBp1], p2r[tBp2]], \
                            [p2rd[tAp1], p2rd[tAp2], p2rd[tBp1], p2rd[tBp2]])

    # if team B won...
    (tbAdjWin, taAdjLose) = (0,0)
    [tbAdjWin, temp, taAdjLose, temp] = \
        calculateAdjustments([p2r[tBp1], p2r[tBp2], p2r[tAp1], p2r[tAp2]], \
                            [p2rd[tBp1], p2rd[tBp2], p2rd[tAp1], p2rd[tAp2]])

    print "%d,%d,%d,%d" % (taAdjWin, taAdjLose, tbAdjWin, tbAdjLose),

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
  
    # calculate new score
    [winnerAdjRating, winnerAdjRD, loserAdjRating, loserAdjRD] = \
        calculateAdjustments([p2r[winner1], p2r[winner2], \
                                p2r[loser1], p2r[loser2]], \
                            [p2rd[winner1], p2rd[winner2], \
                                p2rd[loser1], p2rd[loser2]])

    # update all players
    updatePlayerData(winner1, p2r[winner1] + winnerAdjRating,
        p2rd[winner1] + winnerAdjRD);
    updatePlayerData(winner2, p2r[winner2] + winnerAdjRating,
        p2rd[winner2] + winnerAdjRD);

    updatePlayerData(loser1, p2r[loser1] + loserAdjRating,
        p2rd[loser1] + loserAdjRD);
    updatePlayerData(loser2, p2r[loser2] + loserAdjRating,
        p2rd[loser2] + loserAdjRD);

    # log it
    logGameResult(winner1, winner2, loser1, loser2, winnerAdjRating, loserAdjRating)

    # fall through to "play" mode
    op = 'play'
    [p2r, p2rd] = getPlayersData()

if op == 'play':
    print '<html>'
    print '<head>'
    print '<link rel=StyleSheet href="stylesheet.css" type="text/css">'
    print '<script type="text/javascript" src="./bugtrack.js"></script>'
    print '</head>'
    print '<body>'
    print ' <form action=index.py method=post>'
    print ' <input type=hidden name="op" value="record">'
    print ' <table width="100%" cellpadding=8 cellspacing=0>'
    print '  <tr>'
    print '   <th bgcolor="#FF9797">Team A</th>'
    print '   <th bgcolor="#A9C5EB">Team B</th>'
    print '  </tr>'
    print '  <!-- team A -->'
    print '  <tr>'
    print '   <td bgcolor="#FF9797">'
    print '    <select name=TeamA_Player1 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(p2r, defaultTeamAPlayer1)
    print '    </select>'
    print '   </td>'
    print '   <td bgcolor="#A9C5EB">'
    print '    <select name=TeamB_Player1 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(p2r, defaultTeamBPlayer1)
    print '    </select>'
    print '   </td>'
    print '  </tr>'
    print '  <!-- team B -->'
    print '  <tr>'
    print '   <td bgcolor="#FF9797">'
    print '    <select name=TeamA_Player2 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(p2r, defaultTeamAPlayer2)
    print '    </select>'
    print '   </td>'
    print '   <td bgcolor="#A9C5EB">'
    print '    <select name=TeamB_Player2 onchange=\'selChange_cb(this)\'>'
    printPlayerSelectOptions(p2r, defaultTeamBPlayer2)
    print '    </select>'
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
