#!/usr/bin/python
#
# bugtrack database (sqlite) python abstraction 
# 
# Copyright 2012 
# Andrew Lamoureux
# James Thompson
# 
# This file is a part of bugtrack
# 
# bugtrack is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#------------------------------------------------------------------------------
# DbSqlite.py
# Bugrack database module that uses SQLite for storage.
#------------------------------------------------------------------------------

import sqlite3
import string
import time
import os

dbFile = 'bugtrack.db'

class DbSqlite():

    #--------------------------------------------------------------------------
    # database maintenance
    #--------------------------------------------------------------------------
    SCHEMA_GAMES = [
            ['time',   'REAL PRIMARY KEY'], # Timestamp in epoch seconds
            ['WhiteA',      'TEXT'],     # Winner - White player
            ['WhiteA_r',    'INTEGER'],  # Winner - White player rating
            ['WhiteA_rd',   'INTEGER'],  # Winner - White player RD
            ['BlackB',      'TEXT'],     # Winner - Black player
            ['BlackB_r',    'INTEGER'],  # Winner - Black player rating
            ['BlackB_rd',   'INTEGER'],  # Winner - Black player RD
            ['WhiteB',      'TEXT'],     # Loser  - White player
            ['WhiteB_r',    'INTEGER'],  # Loser  - White player rating
            ['WhiteB_rd',   'INTEGER'],  # Loser  - White player RD
            ['BlackA',      'TEXT'],     # Loser  - Black player
            ['BlackA_r',    'INTEGER'],  # Loser  - Black player rating
            ['BlackA_rd',   'INTEGER']]  # Loser  - Black player RD
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
        cmd = 'drop table if exists games'
        print cmd
        self.c.execute(cmd);
        cmd = 'drop table if exists games_trash'
        print cmd
        self.c.execute(cmd);
        cmd = 'drop table if exists players'
        print cmd
        self.c.execute(cmd);

        print '\tCreating new tables'
        cmd = 'CREATE TABLE games (' + ','.join(map(lambda x: ' '.join(x), self.SCHEMA_GAMES)) + ')'
        print cmd
        self.c.execute(cmd)
        cmd = 'CREATE TABLE games_trash (' + ','.join(map(lambda x: ' '.join(x), self.SCHEMA_GAMES)) + ')'
        print cmd
        self.c.execute(cmd)
        cmd = 'CREATE TABLE players (' + ','.join(map(lambda x: ' '.join(x), self.SCHEMA_PLAYERS)) + ')'
        print cmd
        self.c.execute(cmd);

        self.conn.commit()

    # Clear the database of all entries (Yikes!)
    def clear(self):
        self.createDatabase()

    #--------------------------------------------------------------------------
    # general info
    #--------------------------------------------------------------------------
    # return list of players
    def getPlayerList(self):
        self.c.execute('SELECT name from players')
        return zip(*self.c.fetchall())[0]

    #--------------------------------------------------------------------------
    # player stats
    #--------------------------------------------------------------------------
    # get the player's rating
    def getPlayerRating(self, name):
        self.c.execute('SELECT rating from players WHERE name=?', (name,))
        return self.c.fetchone()[0]

    # get the player's RD
    def getPlayerRD(self, name):
        self.c.execute('SELECT rd from players WHERE name=?', (name,))
        return self.c.fetchone()[0]

    # get the player's T (last time played)
    def getPlayerT(self, name):
        self.c.execute('SELECT time from players WHERE name=?', (name,))
        return self.c.fetchone()[0]

    # return a list [rating, RD]
    def getPlayerStats(self, name):
        self.c.execute('SELECT rating,rd,time from players WHERE name=?', (name,))
        return self.c.fetchall()[0]

    #--------------------------------------------------------------------------
    # set player stats
    #--------------------------------------------------------------------------
    def addPlayer(self, name, rating=1000, rd=350, t=0):
        self.c.execute('INSERT into players value(?,?,?,?)', name, rating, rd, t)
        self.conn.commit()

    def setPlayerRating(self, name, r):
        self.c.execute('UPDATE players SET rating=?', (r,))
        self.conn.commit()

    def setPlayerRD(self, name, rd):
        self.c.execute('UPDATE players SET rd=?', (r,))
        self.conn.commit()

    def setPlayerStats(self, name, listStats):
        self.c.execute('UPDATE players SET rating=?, rd=? ,time=? WHERE name=?',
                (listStats[0], listStats[1], listStats[2], name)
            )
        self.conn.commit()

    #--------------------------------------------------------------------------
    # game stats
    #--------------------------------------------------------------------------

    # see README for explanation of the ordering of these columns
    def getGames(self, since=0):
        self.c.execute('SELECT * from games WHERE time>(?) order by time', (since,))

        games = []
        for x in self.c.fetchall():
            games.append({'t':x[0], \
                          'A':str(x[1]), 'A_r':x[2], 'A_rd':x[3], \
                          'b':str(x[4]), 'b_r':x[5], 'b_rd':x[6], \
                          'B':str(x[7]), 'B_r':x[8], 'B_rd':x[9], \
                          'a':str(x[10]),'a_r':x[11],'a_rd':x[12]})

        return games

    # retrieve all games that had player involved in it
    def getGamesByPlayer(self, name, since=0):
        self.c.execute('SELECT * from games WHERE' +
            ' A=? or b=? or B=? or a=?' +
            ' and time>(?)' +
            ' ORDER by time',
            (name, name, name, name, since)
        )

        games = []
        for x in self.c.fetchall():
            games.append({'t':x[0], \
                          'A':str(x[1]), 'A_r':x[2], 'A_rd':x[3], \
                          'b':str(x[4]), 'b_r':x[5], 'b_rd':x[6], \
                          'B':str(x[7]), 'B_r':x[8], 'B_rd':x[9], \
                          'a':str(x[10]),'a_r':x[11],'a_rd':x[12]})
        return games

    def deleteGame(self, t):
        self.c.execute('INSERT into games_trash SELECT * from games WHERE time=?', (t,));
        self.c.execute('DELETE from games where time=?', (t,));
        self.conn.commit();

    def undeleteGame(self, t):
        self.c.execute('INSERT into games SELECT * from games_trash WHERE time=?', (t,));
        self.c.execute('DELETE from games_trash where time=?', (t,));
        self.conn.commit();

    def recordGame(self, data):
        self.c.execute('INSERT OR REPLACE into games values(?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (data['t'], 
                data['A'], data['A_r'], data['A_rd'], 
                data['b'], data['b_r'], data['b_rd'], 
                data['B'], data['B_r'], data['B_rd'], 
                data['a'], data['a_r'], data['a_rd'])
            )
        self.conn.commit()

    #--------------------------------------------------------------------------
    # misc stats stuff
    #--------------------------------------------------------------------------
    def getPlayerCardStats(self, who):
        # Rating, RD
        self.c.execute("select rating, rd from players where name=?", (who,));
        [rating,rd] = self.c.fetchone()
        
        # Rank
        self.c.execute("select count(*) from players where (rating >= (select rating from players where name =?))", (who,));
        rank = self.c.fetchone()[0]

        # Streak
        streak = 0
        self.c.execute("select max(time) from games where (BlackB==?" +
            " or WhiteA==?)", (who, who))
        lastWin = self.c.fetchone()[0]
        self.c.execute("select max(time) from games where (BlackA==?" +
            " or B==?)", (who, who))
        lastLoss = self.c.fetchone()[0]
        if (lastWin > lastLoss):
            self.c.execute("select count(time) from games where ((BlackB==?" +
                " or WhiteA==?) and (time>?))", (who, who,lastLoss))
            streak = self.c.fetchone()[0]
        else:
            self.c.execute("select count(time) from games where ((BlackA==?" +
                " or B==?) and (time>?))", (who, who,lastWin))
            streak = self.c.fetchone()[0]

        # Wins
        self.c.execute("select count(time) from games where (BlackB==?" +
            " or WhiteA==?)", (who, who))
        numWins = self.c.fetchone()[0]

        # Losses
        self.c.execute("select count(time) from games where (BlackA==?" +
            " or B==?)", (who, who))
        numLosses = self.c.fetchone()[0]

        # Create the response
        return [rating,rd,rank,numWins,numLosses,streak]

    def getPlayerStatsExtended(self, who):
        self.c.execute("select rating, rd, time from players where name=?", (who,));
        [rating,rd,tLastGame] = self.c.fetchone()

        self.c.execute("select count(time) from games");
        numGamesFromAll = self.c.fetchone()[0]

        self.c.execute( \
            "select count(time) from games where " + 
            "(BlackB==? or WhiteA==? or WhiteB==? or BlackA==?)", 
            (who, who, who, who))
        numGames = self.c.fetchone()[0]

        self.c.execute( \
            "select count(time) from games where " + 
            "(BlackB==? or WhiteA==?)", (who, who))
        numWins = self.c.fetchone()[0]

        self.c.execute( \
            "select count(time) from games where " + 
            "(BlackA==? or WhiteB==?)", (who, who))
        numLosses = self.c.fetchone()[0]

        self.c.execute( \
            "select count(time) from games where " + 
            "(WhiteA==? or WhiteB==?)", (who, who))
        numWhite = self.c.fetchone()[0]

        self.c.execute( \
            "select count(time) from games where (BlackB==?" +
            " or BlackA==?)", (who, who))
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
            self.c.execute( \
                "select count(time) from games where " +
                "(WhiteA==? and BlackB==?) or " + 
                "(WhiteA==? and BlackB==?) or " + 
                "(WhiteB==? and BlackA==?) or " + 
                "(WhiteB==? and BlackA==?)", 
                (who, p, p, who, who, p, p, who))
            partnerToGames[p] = self.c.fetchone()[0]

            self.c.execute( \
                "select count(time) from games where " +
                "(WhiteA==? and BlackB==?) or " +
                "(WhiteA==? and BlackB==?)", 
                (who, p, p, who))
            partnerToWins[p] = self.c.fetchone()[0]

            self.c.execute( \
                "select count(time) from games where " +
                "(WhiteB==? and BlackA==?) or "
                "(WhiteB==? and BlackA==?)", 
                (who, p, p, who))
            partnerToLosses[p] = self.c.fetchone()[0]

            # opponent stuff
            self.c.execute( \
                "select count(time) from games where " +
                "((WhiteA==? or BlackB==?) and "
                " (WhiteB==? or BlackA==?)) or "
                "((WhiteA==? or BlackB==?) and "
                " (WhiteB==? or BlackA==?))", 
                (who, who, p, p, p, p, who, who))
            oppToGames[p] = self.c.fetchone()[0]

            self.c.execute( \
                "select count(time) from games where " +
                "(WhiteA==? or BlackB==?) and "
                "(WhiteB==? or BlackA==?)",
                (who, who, p, p))
            oppToWins[p] = self.c.fetchone()[0]

            self.c.execute( \
                "select count(time) from games where " +
                "(WhiteA==? or BlackB==?) and "
                "(WhiteB==? or BlackA==?)",
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

        answer += "rating,%d.%d\n" % (rating, rd)
        answer += "last played,%s\n" % time.strftime("%a %b %d %Y %H:%M:%S", time.localtime(tLastGame))
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
