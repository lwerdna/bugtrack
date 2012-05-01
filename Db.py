# this defines the abstract interface that the other parts of bugtrack
# expect to interact with whatever method is used to store shit

# so like if you have an sqlite backend, you should implement dbSqlite,
# inheriting from this, implementing the methods

# initially, I'll make a model dbText, which uses simple text files for
# storage....

import sqlite3
import string
from ConfigParser import SafeConfigParser

class Db(object):

    #--------------------------------------------------------------------------
    # database maintenance
    #--------------------------------------------------------------------------
    SCHEMA_GAMES = [
            ['time',            'INTEGER'],  # Timestamp in epoch seconds
            ['teamAwhite',      'TEXT'],     # Winner - White player
            ['teamAwhiteRating','INTEGER'],  # Winner - White player rating
            ['teamAblack',      'TEXT'],     # Winner - Black player
            ['teamAblackRating','INTEGER'],  # Winner - Black player rating
            ['teamBwhite',      'TEXT'],     # Loser  - White player
            ['teamBwhiteRating','INTEGER'],  # Loser  - White player rating
            ['teamBblack',      'TEXT'],     # Loser  - Black player
            ['teamBblackRating','INTEGER']]  # Loser  - Black player rating
    SCHEMA_PLAYERS = [
            ['name',  'TEXT'],     # Name
            ['rating','INTEGER'],  # Rating
            ['rd',    'INTEGER']]  # Rd

    # Database configuration and initialization ------------------------------
    def createDatabase(self):
        print '\tDropping old tables'
        cmd = 'DROP TABLE IF EXISTS ' + self.config.get('Database','table_games') + ';'
        self.c.execute(cmd)
        cmd = 'DROP TABLE IF EXISTS ' + self.config.get('Database','table_players') + ';'
        self.c.execute(cmd)
        print '\tCreating new tables'

        # Games
        cmd = 'CREATE TABLE ' + self.config.get('Database','table_games') + ' (id INTEGER PRIMARY KEY, '
        for field in self.SCHEMA_GAMES:
            cmd += field[0] + ' ' + field[1] + ', '
        cmd = cmd[:-2]
        cmd += ');'
        self.c.execute(cmd)

        # Players
        cmd = 'CREATE TABLE ' + self.config.get('Database','table_players') + ' (id INTEGER PRIMARY KEY, '
        for field in self.SCHEMA_PLAYERS:
            cmd += field[0] + ' ' + field[1] + ', '
        cmd = cmd[:-2]
        cmd += ');'
        self.c.execute(cmd)

        self.conn.commit()

    #--------------------------------------------------------------------------
    # general info
    #--------------------------------------------------------------------------
    # return list of players
    def getPlayerList(self):
        self.c.execute('SELECT name from ' + self.config.get('Database','table_players') + ';')
        return [ row for row in self.c.fetchall() ]

    def createNewPlayer(self, name, rating):
        cmd = 'INSERT into ' + self.config.get('Database','table_players') + ' (name,rating,rd) VALUES (\'' + name + '\',' + str(rating) + ',350);'
        self.c.execute(cmd)
        self.conn.commit()

    #--------------------------------------------------------------------------
    # get player stats
    #--------------------------------------------------------------------------
    # get the player's rating
    def getPlayerRating(self, name):
        self.c.execute('SELECT rating from ' + self.config.get('Database','table_players') + ' WHERE (name = \'' + name + '\');')
        return [ row for row in self.c.fetchall() ][0][0]

    # get the player's RD
    def getPlayerRD(self, name):
        self.c.execute('SELECT rd from ' + self.config.get('Database','table_players') + ' WHERE (name = \'' + name + '\');')
        return [ row for row in self.c.fetchall() ][0][0]

    # return a list [rating, RD]
    def getPlayerStats(self, name):
        self.c.execute('SELECT rating,rd from ' + self.config.get('Database','table_players') + ' WHERE (name = \'' + name + '\');')
        return [ row for row in self.c.fetchall() ][0]

    #--------------------------------------------------------------------------
    # set player stats
    #--------------------------------------------------------------------------
    def setPlayerRating(self, name, r):
        cmd = 'UPDATE ' + self.config.get('Database','table_players') + ' set rating = ' + str(r) + ' WHERE (name = \'' + name + '\');'
        self.c.execute(cmd)
        self.conn.commit()

    def setPlayerRD(self, name, rd):
        cmd = 'UPDATE ' + self.config.get('Database','table_players') + ' set rd = ' + str(rd) + ' WHERE (name = \'' + name + '\');'
        self.c.execute(cmd)
        self.conn.commit()

    def setPlayerStats(self, name, listStats):
        pass

    #--------------------------------------------------------------------------
    # game stats
    #--------------------------------------------------------------------------

    # returns a row from the database - currently we define row as:
    # [date, teamAwhitePlayer, teamAwhitePlayerRating,
    #        teamAblackPlayer, teamAblackPlayerRating,
    #        teamBwhitePlayer, teamBwhitePlayerRating,
    #        teamBblackPlayer, teamBblackPlayerRating]
    #
    # where, by convention, teamA are the winners, teamB are the losers
    #
    # (change this comment if the db schema changes please)
    def getGames(self, since):
        self.c.execute('SELECT * from ' + self.config.get('Database','table_games') + ' WHERE (time > ' + str(since) + ');'
        return [ row for row in self.c.fetchall() ]

    # retrieve all games that had player involved in it
    def getGamesByPlayer(self, name, since):
        pass

    def recordGame(self, t, teamAWhite, tawRating, teamABlack, tabRating, \
               teamBWhite, tbwRating, teamBBlack, tbbRating):
        cmd = 'INSERT INTO ' + self.config.get('Database','table_games') + '('
        for field in self.SCHEMA_GAMES:
             cmd += field[0] + ','
        cmd = cmd[:-1]
        cmd += ') VALUES (\''
        for value in (t,teamAWhite, tawRating, teamABlack, tabRating, teamBWhite, tbwRating, teamBBlack, tbbRating):
            cmd += str(value) + '\',\''
        cmd = cmd[:-3]
        cmd += '\');'
        self.c.execute(cmd)
        self.conn.commit()

    #--------------------------------------------------------------------------
    # setup/testing stuff
    #--------------------------------------------------------------------------
    # this should create whatever files or dependencies are necessary for this
    # db implementation to work...
    #
    # for example. DbText creates players.dat and games.dat
    #
    def __init__(self):
        # Read configuration file
        self.config = SafeConfigParser()
        self.config.read('config.ini')

        # Connect to database
        print 'Connecting to database [' + self.config.get('Database','filename') + ']...'
        self.conn = sqlite3.connect(self.config.get('Database','filename'))
        self.c = self.conn.cursor()

        pass

