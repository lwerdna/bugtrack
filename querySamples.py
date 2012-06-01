#!/usr/bin/python

import os
import sys
import DbSqlite

db = DbSqlite.DbSqlite()

def getPlayerScoreHistory(name):
    games = db.getGamesByPlayer(name)
    history = []
    for g in games:
        for x in ['a1','a2','b1','b2']:
            if (g[x] == name):
                history.append([g['t'],g[x+'_r']])
                break
    return history

players = db.getPlayerList()
series = 'series: ['
for p in players:
    series += '{\nname: \'' + p + '\',\ndata: ['
    ratings = getPlayerScoreHistory(p)
    for r in ratings:
        series += str(r[1]) + ','
    if (len(ratings) > 0):
        series = series[:-1]
    series += ']\n},'
series = series[:-1]
series += ']'
print series
