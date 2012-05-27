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
    a1 = form['a1'].value
    a2 = form['a2'].value
    b1 = form['b1'].value
    b2 = form['b2'].value

    ratings = map(lambda x: db.getPlayerRating(x), [a1,a2,b1,b2])
    rds = map(lambda x: db.getPlayerRD(x), [a1,a2,b1,b2])
    ts = map(lambda x: db.getPlayerT(x), [a1,a2,b1,b2])

    [winDelta, loseDelta] = glicko.calcRatingWinLossDeltaPlayer(ratings, rds, ts)

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

    print """
<html>
<head>
  <title></title>
  <link rel=StyleSheet href="stylesheet.css" type="text/css" />
  <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js" type="text/javascript" charset="utf-8"></script>
  <script type="text/javascript" src="./bugtrack.js"></script>
</head>
<body>
<!--  <form action="index.py" method="post"> -->
    <input type="hidden" name="op" value="record" />
    <table>
      <colgroup class="teamA" />
      <colgroup class="transition" />
      <colgroup class="teamB" />
<!--      <tr><th>Team A</th><th></th><th>Team B</th></tr> -->
      <tr>
        <th><button name="TeamAWins" type="button" onclick="recordGame(this)">Team A</button></th>
        <td></td>
        <th><button name="TeamBWins" type="button" onclick="recordGame(this)">Team B</button></th>
      </tr>
      <tr>
        <td>
          <div class="player chessWhite">
            <select name="a1">
    """
    printPlayerSelectOptions(playerList, defaultTeamAPlayer1)
    print """
            </select><br />
            <span class="stats" id="a1_stats"></span>
            <span class="predict" id="a1_predict"></span>
          </div>
        </td>
        <td class="transition"><button name="SwapA1B1" type="button" onclick="swapPlayers(this)">&#x21c4;</button>
        </td>
        <td>
          <div class="player chessBlack">
            <select name="b1">
    """
    printPlayerSelectOptions(playerList, defaultTeamBPlayer1)
    print """
            </select><br />
            <span class="stats" id="b1_stats"></span>
            <span class="predict" id="b1_predict"></span>
          </div>
        </td>
      </tr>
      <!-- transition row containing player swap buttons within teams -->
      <tr class="buttonRow">
        <td>
          <button name="SwapA1A2" type="button" onclick="swapPlayers(this)">&#x21c5;</button>&emsp;
          <button name="ClearTeamA" type="button" onclick="clearPlayers(this)">clear</button>
        </td>
        <td class="transition"><!--<button name="ClearPlayers" type="button" onclick="">clear</button>--></td>
        <td>
          <button name="SwapB1B2" type="button" onclick="swapPlayers(this)">&#x21c5;</button>&emsp;
          <button name="ClearTeamB" type="button" onclick="clearPlayers(this)">clear</button>
        </td>
      </tr>
      <tr>
        <td>
          <div class="player chessBlack">
            <select name="a2">
    """
    printPlayerSelectOptions(playerList, defaultTeamAPlayer2)
    print """
            </select><br />
            <span class="stats" id="a2_stats"></span>
            <span class="predict" id="a2_predict"></span>
          </div>
        </td>
        <td class="transition"><button name="SwapA2B2" type="button" onclick="swapPlayers(this)">&#x21c4;</button></td>
        <td>
          <div class="player chessWhite">
            <select name="b2">
    """
    printPlayerSelectOptions(playerList, defaultTeamBPlayer2)
    print """
            </select><br />
            <span class="stats" id="b2_stats"></span>
            <span class="predict" id="b2_predict"></span>
          </div>
        </td>
      </tr>
<!--      <tr class="buttonRow">
        <td><button name="TeamAWins" type="button" onclick="recordGame(this)">WIN</button></td>
        <td></td>
        <td><button name="TeamBWins" type="button" onclick="recordGame(this)">WIN</button></td>
      </tr> -->
    </table>
<!--  </form> -->
</body>
</html>
    """
