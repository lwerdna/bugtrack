#!/usr/bin/python

import os
import sys
import DbSqlite
from time import time

db = DbSqlite.DbSqlite()

def getPlayerScoreHistory(name, since=0):
    games = db.getGamesByPlayer(name,since)
    history = []
    for g in games:
        for x in ['a1','a2','b1','b2']:
            if (g[x] == name):
                history.append([g['t'],g[x+'_r']])
                break
    history.append([db.getPlayerT(name),db.getPlayerRating(name)])
    return history

def genMatchupData(players, history_len=3600):
    series = 'series: ['
    for p in players:
        ratings = getPlayerScoreHistory(p, int(time() - history_len))
        if (len(ratings) > 0):
            series += '{\nname: \'' + p + '\',\ndata: [\n'
            for r in ratings:
                series += '[' + str(int(r[0])*1000) + ',' + str(int(r[1])) + '],'
            series += ']\n},'
    series = series[:-1]
    series += ']'

    f = open('templates/template_stats_game','r')
    template = f.read()
    f.close()

    TOKEN = '[DATA_GOES_HERE]'
    template = template.replace(TOKEN,series)

    f = open('rankings.htm','w')
    f.write(template)
    f.close()

genMatchupData([sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]], int(sys.argv[5]))

