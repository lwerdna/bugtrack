#!/usr/bin/python

import re
import os
import cgi
import math
import time
import glicko
from Db import Db

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

print 'Creating a database object...'
bug_db = Db()
bug_db.createDatabase()
bug_db.createNewPlayer('Andrew Watts', 100)
bug_db.createNewPlayer('A Potato', 200)
bug_db.setPlayerRating('Andrew Watts', 25)
bug_db.setPlayerRD('Andrew Watts', 5)
print bug_db.getPlayerList()
print bug_db.getPlayerRating('Andrew Watts')
print bug_db.getPlayerRD('Andrew Watts')
print bug_db.getPlayerRating('A Potato')
print bug_db.getPlayerRD('A Potato')
print bug_db.getPlayerStats('Andrew Watts')
print bug_db.getPlayerStats('A Potato')
bug_db.recordGame(1000,'Andrew Watts',50,'Back To Future Sam',100,'A Potato',200,'Biff',125)

