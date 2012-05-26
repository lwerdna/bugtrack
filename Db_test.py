#!/usr/bin/python

import re
import os
import cgi
import math
import time
import glicko
from DbSqlite import DbSqlite

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

print 'Creating a database object...'
bug_db = DbSqlite()
bug_db.createDatabase()
bug_db.createNewPlayer('Andrew W', 100)
bug_db.createNewPlayer('A Potato', 200)
bug_db.setPlayerRating('Andrew W', 25)
bug_db.setPlayerRD('Andrew W', 5)
print bug_db.getPlayerList()
print bug_db.getPlayerRating('Andrew W')
print bug_db.getPlayerRD('Andrew W')
print bug_db.getPlayerRating('A Potato')
print bug_db.getPlayerRD('A Potato')
print bug_db.getPlayerStats('Andrew W')
print bug_db.getPlayerStats('A Potato')
#bug_db.recordGame(1000,'Andrew W',50,'Back To Future Sam',100,'A Potato',200,'Biff',125)

bug_db.importPlayersDat('players.dat')
bug_db.importGamesDat('games.dat.trimmed')
