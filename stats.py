#!/usr/bin/python

import cgi
import time

import glicko
import DbSqlite

def long_ago_str(epoch):
    answer = ''
    delta = time.time() - epoch

    if delta < 60:
        answer = '%d sec' % delta
    elif delta < 3600:
        answer = '%d mins' % (delta / 60)
    elif delta < 86400:
        answer = '%d hrs' % (delta / 3600)
    elif delta < 2592000:
        answer = '%d days' % (delta / 86400)
    elif delta < 31536000:
        answer = '%d mos' % (delta / 2592000)
    else:
        answer = '%.1f yrs' % (delta / 31536000.0)

    return answer

def date_div(epoch):
    mon_lookup = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep', \
                    'Oct','Nov','Dec'];
    answer = ''
    tms = time.localtime(epoch)

    mon = mon_lookup[tms.tm_mon - 1]
    day = tms.tm_mday
    year = tms.tm_year
    hour = tms.tm_hour % 12
    minute = tms.tm_min

    ampm = 'AM'
    if(tms.tm_hour >= 12):
        ampm = 'PM'

    return ("<div class=\"newsblock-date\">\n" + \
            "<div class=\"newsblock-month\">%s</div>\n" + \
            "<div class=\"newsblock-day\">%d</div>\n" + \
            "<div class=\"newsblock-year\">%d:%02d%s</div>\n" + \
            "</div>\n") % (mon, day, hour, minute, ampm)

    return answer

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

print "Content-Type: text/html\x0d\x0a\x0d\x0a",
print '<html>'
print '<head>'
print '<link rel=StyleSheet href="stats.css" type="text/css">'
print '<script type="text/javascript" src="./bugtrack.js"></script>'
print '</head>'
print '<body>'

db = DbSqlite.DbSqlite()
form = cgi.FieldStorage()

op = 'leaderboard'
if 'op' in form:
    op = form['op'].value

if op == "leaderboard":
    players = db.getPlayerList()

    playerToRating = {}
    playerToRD = {}
    playerToT = {}

    for p in players:
        playerToRating[p] = db.getPlayerRating(p)
        playerToRD[p] = db.getPlayerRD(p)
        playerToT[p] = db.getPlayerT(p)

    players = reversed(sorted(players, key=lambda x: playerToRating[x]))

    print '<ol>'
    for p in players:
        if(playerToRD[p] > 225):
            continue

        print '<li style="font-size: x-large">%s (%d.%d) (last played: %s ago)</li>' % (p, playerToRating[p], playerToRD[p], long_ago_str(playerToT[p]))
    print '</ol>'

if op == "gameslist":
    games = reversed(sorted(db.getGames(0), key=lambda x: x['t']))

    print '''
    <table cellpadding=0 cellspacing=8px>
     <tr>
      <th>time</th>
      <th bgcolor=green>winners</th>
      <th bgcolor=red>losers</th>
     </tr>
    '''

    for g in games:
        print '<tr>'
        #print ' <td>%s' % time.strftime("%d %b %I:%M%p", time.localtime(g['t'])),
        #print '(%s ago)' % long_ago_str(g['t']) 
        #print ' </td>'

        print '<td>'
        print date_div(g['t'])
        print '</td>'

        print ' <td>'
        print '  <div class=chesswhite>%s (%d.%d)</div>' % (g['a1'], g['a1_r'], g['a1_rd'])
        print '  <div class=chessblack>%s (%d.%d)</div>' % (g['a2'], g['a2_r'], g['a2_rd'])
        print ' </td>'
        print ' <td>'
        print '  <div class=chessblack>%s (%d.%d)</div>' % (g['b1'], g['b1_r'], g['a1_rd'])
        print '  <div class=chesswhite>%s (%d.%d)</div>' % (g['b2'], g['b2_r'], g['a1_rd'])
        print ' </td>'
      
        # print adjustments?
        #ratings = map(lambda x: db.getPlayerRating(x), [g['a1_r'],g['a2_r'],g['b1_r'],g['b2_r']])
        #rds = map(lambda x: db.getPlayerRD(x), [g['a1_rd'],g['a2_rd'],g['b1_rd'],g['b2_rd']])
        #tnow = int(time.time())
        #tds = map(lambda x: glicko.secToRatingPeriods(tnow - db.getPlayerT(x)), [g['a1'],g['a2'],g['b1'],g['b2']])
        # compute new scores
        #[stats1, stats2, stats3, stats4] = glicko.calcGameScores(ratings, rds, tds)
        #print ' <td>'
        #print '  %s <font color=green>+%d</font>.%d, %s <font color=green>+%d</font>.%d' % \
        #        (g['a1'], stats1[0] - g['a1_r'], stats1[1] - g['a1_rd'], g['a2'], stats2[0] - g['a2_r'], stats2[1] - g['a2_rd'])
        #print '  %s <font color=red>%d</font>.%d, %s <font color=green>%d</font>.%d' % \
        #        (g['b1'], stats3[0] - g['b1_r'], stats3[1] - g['b1_rd'], g['b2'], stats4[0] - g['b2_r'], stats4[1] - g['b2_rd'])
        #print ' </td>'

        print '</tr>'

    print '</table>'

print '</body>'
print '</html>'
