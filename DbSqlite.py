#------------------------------------------------------------------------------
# DbSqlite.py
# Bugrack database module that uses SQLite for storage.
#------------------------------------------------------------------------------

import sqlite3
import string
from ConfigParser import SafeConfigParser
import os

class DbSqlite():

    #--------------------------------------------------------------------------
    # database maintenance
    #--------------------------------------------------------------------------
    SCHEMA_GAMES = [
            ['time',            'REAL PRIMARY KEY'],  # Timestamp in epoch seconds
            ['teamAwhite',      'TEXT'],     # Winner - White player
            ['teamAwhiteRating','INTEGER'],  # Winner - White player rating
            ['teamAwhiteRD',    'INTEGER'],  # Winner - White player RD
            ['teamAblack',      'TEXT'],     # Winner - Black player
            ['teamAblackRating','INTEGER'],  # Winner - Black player rating
            ['teamAblackRD',    'INTEGER'],  # Winner - Black player RD
            ['teamBwhite',      'TEXT'],     # Loser  - White player
            ['teamBwhiteRating','INTEGER'],  # Loser  - White player rating
            ['teamBwhiteRD',    'INTEGER'],  # Loser  - White player RD
            ['teamBblack',      'TEXT'],     # Loser  - Black player
            ['teamBblackRating','INTEGER'],  # Loser  - Black player rating
            ['teamBblackRD',    'INTEGER']]  # Loser  - Black player RD
    SCHEMA_ACHIEVEMENTS = [
            ['id',    'INTEGER PRIMARY KEY'],
            ['name',  'TEXT'],     # Player Name
            ['title', 'INTEGER'],  # Achievement title
            ['time',  'REAL']]     # Timestamp of achievement 
    SCHEMA_PLAYERS = [
            ['name',  'TEXT PRIMARY KEY'],     # Name
            ['rating','INTEGER'],  # Rating
            ['rd',    'INTEGER'],  # Rd
            ['time',  'REAL']]     # Timestamp of last game played

    # Database configuration and initialization ------------------------------
    def createDatabase(self):
        print '\tDropping old tables'
        cmd = 'DROP TABLE IF EXISTS ' + self.config.get('Database','table_games') + ';'
        self.c.execute(cmd)
        cmd = 'DROP TABLE IF EXISTS ' + self.config.get('Database','table_players') + ';'
        self.c.execute(cmd)
        print '\tCreating new tables'

        # Games
        cmd = 'CREATE TABLE ' + self.config.get('Database','table_games') + ' ('
        for field in self.SCHEMA_GAMES:
            cmd += field[0] + ' ' + field[1] + ', '
        cmd = cmd[:-2]
        cmd += ');'
        self.c.execute(cmd)

        # Players
        cmd = 'CREATE TABLE ' + self.config.get('Database','table_players') + ' ('
        for field in self.SCHEMA_PLAYERS:
            cmd += field[0] + ' ' + field[1] + ', '
        cmd = cmd[:-2]
        cmd += ');'
        self.c.execute(cmd)
        self.conn.commit()

    # Clear the database of all entries (Yikes!)
    def clear(self):
        self.createDatabase()

    def genDBEntry(self, schema, table, db_values):
        cmd = 'INSERT INTO ' + table + '('
        for field in schema:
            cmd += field[0] + ','
        cmd = cmd[:-1]
        cmd += ') VALUES ('
        for value in db_values:
            cmd += str(value) + ','
        cmd = cmd[:-1]
        cmd += ');'
        self.c.execute(cmd)
        self.conn.commit()

    def importGamesDat(self, filename):
        print 'Importing game data from [' + filename + ']...'
        f = open(filename,'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            time             = line[:10]
            teamAwhite       = '\'' + line[11:].split(',')[0].split('(')[0] + '\''
            teamAwhiteRating =        line[11:].split(',')[0].split('(')[1].split(')')[0].split('.')[0]
            teamAwhiteRD     =        line[11:].split(',')[0].split('(')[1].split(')')[0].split('.')[1]
            teamAblack       = '\'' + line[11:].split(',')[1].split('(')[0] + '\''
            teamAblackRating =        line[11:].split(',')[1].split('(')[1].split(')')[0].split('.')[0]
            teamAblackRD     =        line[11:].split(',')[1].split('(')[1].split(')')[0].split('.')[1] 
            teamBwhite       = '\'' + line[11:].split(',')[1].split('>')[1].split('(')[0][1:] + '\''
            teamBwhiteRating =        line[11:].split(',')[1].split('>')[1].split('(')[1].split(')')[0].split('.')[0]
            teamBwhiteRD     =        line[11:].split(',')[1].split('>')[1].split('(')[1].split(')')[0].split('.')[1]
            teamBblack       = '\'' + line[11:].split(',')[2].split('(')[0] + '\''
            teamBblackRating =        line[11:].split(',')[2].split('(')[1].split(')')[0].split('.')[0]
            teamBblackRD     =        line[11:].split(',')[2].split('(')[1].split(')')[0].split('.')[1]
            self.genDBEntry(self.SCHEMA_GAMES, self.config.get('Database','table_games'), \
                [time, \
                 teamAwhite, teamAwhiteRating, teamAwhiteRD, \
                 teamAblack, teamAblackRating, teamAblackRD, \
                 teamBwhite, teamBwhiteRating, teamBwhiteRD, \
                 teamBblack, teamBblackRating, teamBblackRD])

    def importPlayersDat(self, filename):
        print 'Importing player data from [' + filename + ']...'
        f = open(filename,'r')
        lines = f.readlines()
        f.close()
        for line in lines:
            tokens = line[:-1].split(" ")
            t      = tokens[len(tokens)-1]
            rd     = tokens[len(tokens)-2]
            rating = tokens[len(tokens)-3]
            player = '\''
            for i in range(len(tokens) - 3):
                player += tokens[i] + ' '
            player = player[:-1] + '\''
            self.genDBEntry(self.SCHEMA_PLAYERS, self.config.get('Database','table_players'), [player,rating,rd,t])

    def offsetGameTime(self, offset):
        print 'Applying game time offset of ' + str(offset) + ' to all recorded games...'
        games = self.getGames()
        for g in games:
            newtime = g['t'] + float(offset)
            cmd = 'UPDATE ' + self.config.get('Database','table_games') + \
                  ' set time = ' + str(newtime) + ' WHERE (time = ' + str(g['t']) + ');'
            self.c.execute(cmd)
        self.conn.commit()

    #--------------------------------------------------------------------------
    # general info
    #--------------------------------------------------------------------------
    # return list of players
    def getPlayerList(self):
        self.c.execute('SELECT name from ' + self.config.get('Database','table_players') + ';')
        return list(zip(*self.c.fetchall())[0])

    #--------------------------------------------------------------------------
    # get player stats
    #--------------------------------------------------------------------------
    # get the player's rating
    def getPlayerRating(self, name):
        self.c.execute('SELECT rating from ' + self.config.get('Database','table_players') + \
                       ' WHERE (name = \'' + name + '\');')
        return [ row for row in self.c.fetchall() ][0][0]

    # get the player's RD
    def getPlayerRD(self, name):
        self.c.execute('SELECT rd from ' + self.config.get('Database','table_players') + \
                       ' WHERE (name = \'' + name + '\');')
        return [ row for row in self.c.fetchall() ][0][0]

    # get the player's T (last time played)
    def getPlayerT(self, name):
        self.c.execute('SELECT time from ' + self.config.get('Database','table_players') + \
                       ' WHERE (name = \'' + name + '\');')
        return [ row for row in self.c.fetchall() ][0][0]

    # return a list [rating, RD]
    def getPlayerStats(self, name):
        self.c.execute('SELECT rating,rd,time from ' + self.config.get('Database','table_players') + \
                       ' WHERE (name = \'' + name + '\');')
        return [ row for row in self.c.fetchall() ][0]

    #--------------------------------------------------------------------------
    # set player stats
    #--------------------------------------------------------------------------
    def addPlayer(self, name, rating=1000, rd=350, t=0):
        cmd = 'INSERT into ' + self.config.get('Database','table_players') + \
              ' (name,rating,rd,time) VALUES (\'' +  \
              name + '\',' + str(rating) + ',' + str(rd) + ',' + str(t) + ');'
        self.c.execute(cmd)
        self.conn.commit()

    def setPlayerRating(self, name, r):
        cmd = 'UPDATE ' + self.config.get('Database','table_players') + \
              ' set rating = ' + str(r) + ' WHERE (name = \'' + name + '\');'
        self.c.execute(cmd)
        self.conn.commit()

    def setPlayerRD(self, name, rd):
        cmd = 'UPDATE ' + self.config.get('Database','table_players') + \
              ' set rd = ' + str(rd) + ' WHERE (name = \'' + name + '\');'
        self.c.execute(cmd)
        self.conn.commit()

    def setPlayerStats(self, name, listStats):
        cmd = 'INSERT or REPLACE INTO ' + self.config.get('Database','table_players') + \
              '(name,rating,rd,time) VALUES (' + \
              '\'' + name + '\', ' + \
              str(listStats[0]) + ',' + str(listStats[1]) + ',' + str(listStats[2]) + ')'
        self.c.execute(cmd)
        self.conn.commit()

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
    def getGames(self, since=0):
        self.c.execute('SELECT * from ' + self.config.get('Database','table_games') + \
                       ' WHERE (time > ' + str(since) + ') order by time desc;')

        games = []
        for x in self.c.fetchall():
            games.append({'t':x[0], \
                          'a1':str(x[1]), 'a1_r':x[2], 'a1_rd':x[3], \
                          'a2':str(x[4]), 'a2_r':x[5], 'a2_rd':x[6], \
                          'b1':str(x[7]), 'b1_r':x[8], 'b1_rd':x[9], \
                          'b2':str(x[10]),'b2_r':x[11],'b2_rd':x[12]})
        return games

    # retrieve all games that had player involved in it
    def getGamesByPlayer(self, name, since=0):
        self.c.execute('SELECT * from ' + self.config.get('Database','table_games') + \
                       ' WHERE ((' + \
                       '(teamAwhite =  \"' + name + '\") OR '\
                       '(teamAblack =  \"' + name + '\") OR '\
                       '(teamBwhite =  \"' + name + '\") OR '\
                       '(teamBblack =  \"' + name + '\")) AND '\
                       '(time > ' + str(since) + ')) ' \
                       'ORDER by time;')

        games = []
        for x in self.c.fetchall():
            games.append({'t':x[0], \
                          'a1':str(x[1]), 'a1_r':x[2], 'a1_rd':x[3], \
                          'a2':str(x[4]), 'a2_r':x[5], 'a2_rd':x[6], \
                          'b1':str(x[7]), 'b1_r':x[8], 'b1_rd':x[9], \
                          'b2':str(x[10]),'b2_r':x[11],'b2_rd':x[12]})
        return games

    def recordGame(self, data):
        cmd = 'INSERT INTO ' + self.config.get('Database','table_games') + '('
        for field in self.SCHEMA_GAMES:
             cmd += field[0] + ','
        cmd = cmd[:-1]
        cmd += ') VALUES (\''
        for value in (data['t'], \
                      data['a1'], data['a1_r'], data['a1_rd'], \
                      data['a2'], data['a2_r'], data['a2_rd'], \
                      data['b1'], data['b1_r'], data['b1_rd'], \
                      data['b2'], data['b2_r'], data['b2_rd']):
            cmd += str(value) + '\',\''
        cmd = cmd[:-3]
        cmd += '\');'
        self.c.execute(cmd)
        self.conn.commit()

    #--------------------------------------------------------------------------
    # misc stats stuff
    #--------------------------------------------------------------------------
    def getPlayerStatsExtended(self, who):
        self.c.execute("select count(time) from games");
        numGamesFromAll = self.c.fetchone()[0]

        self.c.execute("select count(time) from games where (teamAblack==?" +
            " or teamAwhite==? or teamBwhite==? or teamBblack==?)", (who, who,
            who, who))
        numGames = self.c.fetchone()[0]

        self.c.execute("select count(time) from games where (teamAblack==?" +
            " or teamAwhite==?)", (who, who))
        numWins = self.c.fetchone()[0]

        self.c.execute("select count(time) from games where (teamBblack==?" +
            " or teamBwhite==?)", (who, who))
        numLosses = self.c.fetchone()[0]

        self.c.execute("select count(time) from games where (teamAwhite==?" +
            " or teamBwhite==?)", (who, who))
        numWhite = self.c.fetchone()[0]

        self.c.execute("select count(time) from games where (teamAblack==?" +
            " or teamBblack==?)", (who, who))
        numBlack = self.c.fetchone()[0]

        #
        players = self.getPlayerList()

        partnerToWins = {}
        partnerToLosses = {}
        partnerToGames = {}
        oppToWins = {}
        oppToLosses = {}
        oppToGames = {}

        for p in players:
            # partner stuff
            self.c.execute("select count(time) from games where " +
                "(teamAwhite==? and teamAblack==?) or (teamAwhite==?" +
                " and teamAblack==?) or (teamBwhite==? and teamBblack==?)" +
                " or (teamBwhite==? and teamBblack==?)", 
                (who, p, p, who, who, p, p, who))
            partnerToGames[p] = self.c.fetchone()[0]

            self.c.execute("select count(time) from games where " +
                "(teamAwhite==? and teamAblack==?) or (teamAwhite==?" +
                " and teamAblack==?)", (who, p, p, who))
            partnerToWins[p] = self.c.fetchone()[0]

            self.c.execute("select count(time) from games where " +
                "(teamBwhite==? and teamBblack==?) or (teamBwhite==?" +
                " and teamBblack==?)", (who, p, p, who))
            partnerToLosses[p] = self.c.fetchone()[0]

            # opponent stuff
            self.c.execute("select count(time) from games where " +
                "((teamAwhite==? or teamAblack==?) and "
                " (teamBwhite==? or teamBblack==?)) or "
                "((teamAwhite==? or teamAblack==?) and "
                " (teamBwhite==? or teamBblack==?))", 
                (who, who, p, p, p, p, who, who))
            oppToGames[p] = self.c.fetchone()[0]

            self.c.execute("select count(time) from games where " +
                "(teamAwhite==? or teamAblack==?) and "
                "(teamBwhite==? or teamBblack==?)",
                (who, who, p, p))
            oppToWins[p] = self.c.fetchone()[0]

            self.c.execute("select count(time) from games where " +
                "(teamAwhite==? or teamAblack==?) and "
                "(teamBwhite==? or teamBblack==?)",
                (p, p, who, who))
            oppToLosses[p] = self.c.fetchone()[0]
       
        # partner win stats
        partnerMaxWin = 0
        partnerMaxWinName = ''
        partnerMaxRatioWin = 0
        partnerMaxRatioWinName = ''

        for p,w in partnerToWins.iteritems():
            if not partnerToGames[p]:
                continue

            if(w > partnerMaxWin):
                partnerMaxWin = w;
                partnerMaxWinName = p;

            if(w/partnerToGames[p]*1.0 > partnerMaxRatioWin):
                partnerMaxRatioWin = w/partnerToGames[p]*1.0
                partnerMaxRatioWinName = p

        # partner loss stats
        partnerMaxLoss = 0
        partnerMaxRatioLoss = 0
        partnerMaxLossName = ''
        partnerMaxRatioLossName = ''

        for p,l in partnerToLosses.iteritems():
            if not partnerToGames[p]:
                continue

            if(l > partnerMaxLoss):
                partnerMaxLoss = l;
                partnerMaxLossName = p;

            if(l/partnerToGames[p]*1.0 > partnerMaxRatioLoss):
                partnerMaxRatioLoss = l/partnerToGames[p]*1.0
                partnerMaxRatioLossName = p

        # opponent win stats
        oppMaxWin = 0
        oppMaxRatioWin = 0
        oppMaxWinName = ''
        oppMaxRatioWinName = ''

        for p,w in oppToWins.iteritems():
            if not oppToGames[p]:
                continue

            if(w > oppMaxWin):
                oppMaxWin = w;
                oppMaxWinName = p;

            if(w/oppToGames[p]*1.0 > oppMaxRatioWin):
                oppMaxRatioWin = w/oppToGames[p]*1.0
                oppMaxRatioWinName = p

        # opp loss stats
        oppMaxLoss = 0
        oppMaxRatioLoss = 0
        oppMaxLossName = ''
        oppMaxRatioLossName = ''

        for p,l in oppToLosses.iteritems():
            if not oppToGames[p]:
                continue

            if(l > oppMaxLoss):
                oppMaxLoss = l;
                oppMaxLossName = p;

            if(l/oppToGames[p]*1.0 > oppMaxRatioLoss):
                oppMaxRatioLoss = l/oppToGames[p]*1.0
                oppMaxRatioLossName = p

        #print partnerToWins
        #print partnerToLosses
        #print partnerToGames
        #print oppToWins
        #print oppToLosses
        #print oppToGames

        answer = ''

        answer += "total games,%d (%.02f%%)\n" % (numGames, 100.0 * numGames/numGamesFromAll)
        answer += "wins,%d (%.02f%%)\n" % (numWins, 100.0 * numWins/numGames)
        answer += "losses,%d (%.02f%%)\n" % (numLosses, 100.0 * numLosses/numGames)
        answer += "plays as white,%d (%.02f%%)\n" % (numWhite, 100.0 * numWhite/numGames)
        answer += "plays as black,%d (%.02f%%)\n" % (numBlack, 100.0 * numBlack/numGames)

        if partnerMaxWinName:
            answer += "won most games with partner,%s (%d wins)\n" % (partnerMaxWinName, partnerMaxWin)

        if partnerMaxRatioWinName:
            answer += "largest win/games ratio with partner,%s at %d/%d (%.02f%%)\n" % \
                (partnerMaxRatioWinName, 
                partnerToWins[partnerMaxRatioWinName], partnerToGames[partnerMaxRatioWinName], 
                partnerMaxRatioWin*100)

        if partnerMaxLossName:
            answer += "lost most games with partner,%s (%d losses)\n" % (partnerMaxLossName, partnerMaxLoss)

        if partnerMaxRatioLossName:
            answer += "largest loss/games ratio with partner,%s at %d/%d (%.02f%%)\n" % \
                (partnerMaxRatioLossName, 
                partnerToLosses[partnerMaxRatioLossName], partnerToGames[partnerMaxRatioLossName], 
                partnerMaxRatioLoss*100)

        if oppMaxWinName:
            answer += "won most games against opp,%s (%d wins)\n" % (oppMaxWinName, oppMaxWin)

        if oppMaxRatioWin:
            answer += "largest win/games ratio against opp,%s at %d/%d (%.02f%%)\n" % \
                (oppMaxRatioWinName, 
                oppToWins[oppMaxRatioWinName], oppToGames[oppMaxRatioWinName], 
                oppMaxRatioWin*100)

        if oppMaxLossName:
            answer += "lost most games against opp,%s (%d losses)\n" % (oppMaxLossName, oppMaxLoss)

        if oppMaxRatioLossName:
            answer += "largest loss/games ratio against opp,%s at %d/%d (%.02f%%)" % \
                (oppMaxRatioLossName, 
                oppToLosses[oppMaxRatioLossName], oppToGames[oppMaxRatioLossName], 
                oppMaxRatioLoss*100)

        return answer

    #--------------------------------------------------------------------------
    # setup/testing stuff
    #--------------------------------------------------------------------------
    #
    def __init__(self):
        # Read configuration file
        self.config = SafeConfigParser()
        self.config.read('DbSqlite.ini')
        dbFile = self.config.get('Database','filename')

        # Determine if the database already exists
        createDB = 1
        if ( os.path.exists(dbFile) ):
            createDB = 0

        # Connect to database
        #print 'Connecting to database [' + dbFile + ']...'
        self.conn = sqlite3.connect(dbFile)
        self.c = self.conn.cursor()

        # If the database did not already exist, create it from scratch
        if ( createDB ):
            print '\tInitializing new database...'
            self.createDatabase()
