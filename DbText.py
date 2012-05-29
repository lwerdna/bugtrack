# this is a database module that uses text files for storing stuff
#

# example players.dat:
# Chris Tyson 888 200 1337957171
# David Jackson 1597 162 1337957172
# Luke Simpson 746 193 1337957179
# Randy Smith 1142 175 1337957199

import os
import re
import Db

class DbText(Db.Db):
    def __init__(self):
        self.playerToRating = {}
        self.playerToRD = {}
        self.playerToT = {}

        for f in ['players.dat', 'games.dat']:
            if not os.path.exists(f):
                return

        self.readInPlayers();

    def readInPlayers(self):
        self.playerToRating = {}
        self.playerToRD = {}
        self.playerToT = {}

        fp = open("players.dat")
        lines = fp.read().split("\n")
        fp.close()

        for l in lines:
            #print "trying to match on -%s-" % l
            m = re.match(r'^(.*) (\d+) (\d+) (\d+)$', l)

            if not m:
                continue

            [player, rating, rd, t] = [m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))]
            self.playerToRating[player] = rating
            self.playerToRD[player] = rd
            self.playerToT[player] = t
    
    def writeOutPlayers(self):
        fp = open("players.dat", "w+")
        
        for player in self.playerToRating:
            fp.write("%s %d %d %d\n" % (player, self.playerToRating[player], \
                self.playerToRD[player], self.playerToT[player]))
        
        fp.close()

    def getPlayerList(self):
        return self.playerToRating.keys();

    def getPlayerRating(self, name):
        return self.playerToRating[name]

    def getPlayerRD(self, name):
        return self.playerToRD[name]

    def getPlayerT(self, name):
        return self.playerToT[name]

    def getPlayerStats(self, name):
        return [self.playerToRating[name], self.playerToRD[name], \
            self.playerToT[name]]

    def setPlayerRating(self, name, r):
        self.playerToRating[name] = r
        self.writeOutPlayers()

    def setPlayerRD(self, name, rd):
        self.playerToRD[name] = r
        self.writeOutPlayers()

    def setPlayerT(self, name, t):
        self.playerToT[name] = t
        self.writeOutPlayers()

    def setPlayerStats(self, name, listStats):
        self.playerToRating[name] = listStats[0]
        self.playerToRD[name] = listStats[1]
        self.playerToT[name] = listStats[2]
        self.writeOutPlayers()

    def addPlayer(self, name, rating=1000, rd=350):
        self.setPlayerStats(name, [rating, rd, 0])
    
    # returns a row from the database - currently we define row as:
    # [date, teamAwhitePlayer, teamAwhitePlayerRating,
    #        teamAblackPlayer, teamAblackPlayerRating,
    #        teamBwhitePlayer, teamBwhitePlayerRating,
    #        teamBblackPlayer, teamBblackPlayerRating]
    #
    # where, by convention, teamA are the winners, teamB are the losers
    def getGames(self, since=0):
        games = []

        fp = open("games.dat", 'r')

        while(1):
            line = fp.readline().rstrip()
            if not line:
                break;

            #print "trying to match -%s-" % line
            m = re.match(r'^(\d+) (.*)\((\d+)\.(\d+)\),(.*)\((\d+)\.(\d+)\) > (.*)\((\d+)\.(\d+)\),(.*)\((\d+)\.(\d+)\)$', line)

            [t, \
            teamAWhite, tawRating, tawRD, \
            teamABlack, tabRating, tabRD, \
            teamBBlack, tbbRating, tbbRD, \
            teamBWhite, tbwRating, tbwRD ] = map(lambda x : m.group(x+1), range(13))
               
            [t, tawRating, tawRD, tabRating, tabRD, tbwRating, tbwRD, tbbRating, tbbRD] = \
                map(lambda x : int(x), [t, tawRating, tawRD, tabRating, tabRD, tbwRating, tbwRD, tbbRating, tbbRD])

            games.append({'t':t, \
            'a1':teamAWhite, 'a1_r':tawRating, 'a1_rd':tawRD, \
            'a2':teamABlack, 'a2_r':tabRating, 'a2_rd':tabRD, \
            'b1':teamBBlack, 'b1_r':tbbRating, 'b1_rd':tbbRD, \
            'b2':teamBWhite, 'b2_r':tbwRating, 'b2_rd':tbwRD})
       
        return games

    # retrieve all games that had player involved in it
    def getGamesByPlayer(self, name, since=0):
        return None

    # record game
    def recordGame(self, data):
        fp = open("games.dat", 'a')
        fp.write("%d %s(%d.%d),%s(%d.%d) > %s(%d.%d),%s(%d.%d)\n" % (data['t'], \
            data['a1'], data['a1_r'], data['a1_rd'], \
            data['a2'], data['a2_r'], data['a2_rd'], \
            data['b1'], data['b1_r'], data['b1_rd'], \
            data['b2'], data['b2_r'], data['b2_rd'] \
        ))

        fp.close()

        pass

    def modifyGame(self, data):
        pass

    def init(self):
        for f in ['players.dat', 'games.dat']:
            if not os.path.exists(f):
                fp = open(f, 'w+')
                fp.close()

        self.readInPlayers()

    def clear(self):
        
        for f in ['players.dat', 'games.dat']:
            fp = open(f, "w+")
            fp.close()

        self.readInPlayers()
        

