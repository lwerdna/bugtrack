#!/usr/bin/python

import os
import sys
import time
import random
import DbText

if __name__ == "__main__":
        
    db = DbText.DbText()

    if len(sys.argv) <= 1:
        print "send arguments!"
        exit(-1)

    if sys.argv[1] == "dbinit":
        print "initializating database with random players"

        db.init()

        players = ["George Washington", "John Adams", "Thomas Jefferson",
                    "James Madison", "James Monroe", "John Quincy Adams",
                    "Andrew Jackson"];

        ratings = map(lambda x: random.randint(500,1500), range(len(players)))
        rds = map(lambda x: random.randint(50,350), range(len(players)))
        ts = map(lambda x: int(time.time()) - random.randint(0,7*24*3600), range(len(players)))

        for i,p in enumerate(players):
            print "%s %d.%d (last game: %s))" % \
                (p, ratings[i], rds[i], time.strftime("%a, %d %b %y %H:%M:%S", time.localtime(ts[i])))

            db.setPlayerStats(p, [ratings[i], rds[i], ts[i]])

    if sys.argv[1] == "playgames":
        print "playing 1000 random games"
    

