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

def printPlayerSelectOptions(playerToRating, initial):
    print "      <option></option>"
    for player in sorted(playerToRating):
        print "      <option",
        
        if player == initial:
            print ' selected',
            
        playerStr = '%s (%d)' % (player, playerToRating[player])
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

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

print "Content-Type: text/html\x0d\x0a\x0d\x0a",

[playerToRating, playerToRD] = getPlayersData()

form = cgi.FieldStorage()

defaultTeamAPlayer1 = ''
defaultTeamAPlayer2 = ''
defaultTeamBPlayer1 = ''
defaultTeamBPlayer2 = ''

op = ''
if 'op' in form:
    op = form['op'].value

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
    winnerRating = (playerToRating[winner1] + playerToRating[winner2]) / 2;
    winnerRD = (playerToRD[winner1] + playerToRD[winner2]) / 2
    loserRating = (playerToRating[loser1] + playerToRating[loser2]) / 2
    loserRD = (playerToRD[loser1] + playerToRD[loser2]) / 2

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

    #print "winnerAdjRating: %d<br>\n" % winnerAdjRating
    #print "winnerAdjRD: %d<br>\n" % winnerAdjRD
    #print "loserAdjRating: %d<br>\n" % loserAdjRating
    #print "loserAdjRD: %d<br>\n" % loserAdjRD 

    updatePlayerData(winner1, playerToRating[winner1] + winnerAdjRating,
        playerToRD[winner1] + winnerAdjRD);
    updatePlayerData(winner2, playerToRating[winner2] + winnerAdjRating,
        playerToRD[winner2] + winnerAdjRD);

    updatePlayerData(loser1, playerToRating[loser1] + loserAdjRating,
        playerToRD[loser1] + loserAdjRD);
    updatePlayerData(loser2, playerToRating[loser2] + loserAdjRating,
        playerToRD[loser2] + loserAdjRD);

    # log it
    logGameResult(winner1, winner2, loser1, loser2, winnerAdjRating, loserAdjRating)

    [playerToRating, playerToRD] = getPlayersData()

print '<html>'
print '<head>'
print '<link rel=StyleSheet href="stylesheet.css" type="text/css">'
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
print '    <select name=TeamA_Player1>'
printPlayerSelectOptions(playerToRating, defaultTeamAPlayer1)
print '    </select>'
print '   </td>'
print '   <td bgcolor="#A9C5EB">'
print '    <select name=TeamB_Player1>'
printPlayerSelectOptions(playerToRating, defaultTeamBPlayer1)
print '    </select>'
print '   </td>'
print '  </tr>'
print '  <!-- team B -->'
print '  <tr>'
print '   <td bgcolor="#FF9797">'
print '    <select name=TeamA_Player2>'
printPlayerSelectOptions(playerToRating, defaultTeamAPlayer2)
print '    </select>'
print '   </td>'
print '   <td bgcolor="#A9C5EB">'
print '    <select name=TeamB_Player2>'
printPlayerSelectOptions(playerToRating, defaultTeamBPlayer2)
print '    </select>'
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
