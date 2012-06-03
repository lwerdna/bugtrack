#!/usr/bin/python

import os
import sys
from DbSqlite import DbSqlite
from time import time


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

def genPlayerCard(player):
    score_history = getPlayerScoreHistory(player)
    series = ''
    ratings = getPlayerScoreHistory(player)
    if (len(ratings) > 0):
        series += 'name: \'' + player + '\',\ndata: [\n'
        for r in ratings:
            series += '[' + str(int(r[0])*1000) + ',' + str(int(r[1])) + '],'
        series += ']\n'

    f = open('templates/template_gamer_card','r')
    template = f.read()
    f.close()

    template = template.replace('[GAMER_NAME]',player)
    template = template.replace('[GAMER_DATA]',series)

    f = open('card_' + player.replace(' ','_') + '.htm','w')
    f.write(template)
    f.close()

#-- Main --
if len(sys.argv) <= 1:
    printUsage()
    exit(-1)

if sys.argv[1] == "genPlayerCard":
   genPlayerCard(sys.argv[2]) 
