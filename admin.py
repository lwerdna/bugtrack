#!/usr/bin/python

import os
import sys
import time
import random

import glicko
import DbText

if __name__ == "__main__":
        
    db = DbText.DbText()

    if len(sys.argv) <= 1:
        print "send arguments!"
        exit(-1)

    if sys.argv[1] == "dumpgames":
        games = db.getGames(0)
        print games

    if sys.argv[1] == "seeddb" or sys.argv[1] == "dbseed":
        # virtual time point one year ago
        tnow = time.time() - 365*24*3600 

        #######################################################################
        # new players
        #######################################################################
        print "initializating database with random players"

        db.init()
        db.clear()

        players = ["George Washington", "John Adams", "Thomas Jefferson",
                    "James Madison", "James Monroe", "John Quincy Adams",
                    "Andrew Jackson"];

        ratings = map(lambda x: random.randint(500,1500), range(len(players)))
        rds = map(lambda x: 350, range(len(players)))

        for i,p in enumerate(players):
            print "%s %d.%d (last game: %s))" % \
                (p, ratings[i], rds[i], time.strftime("%a, %d %b %y %H:%M:%S", time.localtime(0)))

            db.setPlayerStats(p, [ratings[i], rds[i], tnow])

        #######################################################################
        # new games
        #######################################################################


        players = db.getPlayerList()

        print "playing 1000 random games"
        for i in range(1000):

            # scramble the players
            for j in range(len(players)):
                k = random.randint(0, len(players)-1)
                l = random.randint(0, len(players)-1)
                temp = players[k];
                players[k] = players[l]
                players[l] = temp

            # players are at front of list
            [a1,a2,b1,b2] = players[0:4]

            print "%s,%s    >    %s,%s\n" % (a1, a2, b1, b2)

            ratings = map(lambda x: db.getPlayerRating(x), [a1,a2,b1,b2])
            rds = map(lambda x: db.getPlayerRD(x), [a1,a2,b1,b2])
            rps = map(lambda x: glicko.secToRatingPeriods(tnow - db.getPlayerT(x)), [a1,a2,b1,b2])
            
            # log game
            db.recordGame(tnow, \
                a1, ratings[0], rds[0], a2, ratings[1], rds[1],
                b1, ratings[2], rds[2], b2, ratings[3], rds[3],
            )
        
            # compute new scores
            print "rps: ", rps
            [stats1, stats2, stats3, stats4] = glicko.calcGameScores(ratings, rds, rps)
        
            # store new scores
            db.setPlayerStats(a1, stats1 + [tnow])
            db.setPlayerStats(a2, stats2 + [tnow])
            db.setPlayerStats(b1, stats3 + [tnow])
            db.setPlayerStats(b2, stats4 + [tnow])

            # advance virtual time by at most an hour
            tnow += random.randint(1, 3600)

 



    
