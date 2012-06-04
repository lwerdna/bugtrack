#!/usr/bin/python

import os
import sys
from DbSqlite import DbSqlite
from time import time
from datetime import datetime


db = DbSqlite()

def printUsage():
    print 'Usage:'
    print '\tbugstats.py <command> <parameters>'

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

def getPlayerRecord(history):
    record = [0,0,0]
    for i in range(len(history)-1):
        if (history[i+1][1] > history[i][1]):
            record[0] += 1
            if (record[2] > 0):
                record[2] += 1
            else:
                record[2] = 1
        else:
            record[1] += 1
            if (record[2] > 0):
                record[2] = -1
            else:
                record[2] -= 1
    return record

def genPlayerCard(player):
    history = getPlayerScoreHistory(player)
    record  = getPlayerRecord(history)
    series  = ''
    if (len(history) > 0):
        series += 'name: \'' + player + '\',\ndata: [\n'
        for h in history:
            series += '[' + str(int(h[0])*1000) + ',' + str(int(h[1])) + '],'
        series += ']\n'
   
    streak = str(abs(record[2]))
    if (record[2] > 0):
        streak += ' Win'
        if (record[2] > 1):
            streak += 's'
    else:
        streak += ' Loss'
        if (record[2] < -1):
            streak += 'es'
    lastPlayed = datetime.fromtimestamp(db.getPlayerT(player)).strftime('%d %b %y')

    f = open('templates/template_gamer_card','r')
    template = f.read()
    f.close()

    template = template.replace('[GAMER_NAME]',player)
    template = template.replace('[GAMER_DATA]',series)
    template = template.replace('[GAMER_RECORD]', str(record[0]) + '-' + str(record[1]))
    template = template.replace('[GAMER_STREAK]', streak)
    template = template.replace('[GAMER_LAST_PLAYED]', lastPlayed)

    f = open('card_' + player.replace(' ','_') + '.htm','w')
    f.write(template)
    f.close()

#-- Main --
if len(sys.argv) <= 1:
    printUsage()
    exit(-1)

if sys.argv[1] == "genPlayerCard":
   genPlayerCard(sys.argv[2]) 
