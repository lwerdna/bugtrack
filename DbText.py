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
    
    # returns a row from the database - currently we define row as:
    # [date, teamAwhitePlayer, teamAwhitePlayerRating,
    #        teamAblackPlayer, teamAblackPlayerRating,
    #        teamBwhitePlayer, teamBwhitePlayerRating,
    #        teamBblackPlayer, teamBblackPlayerRating]
    #
    # where, by convention, teamA are the winners, teamB are the losers
    def getGames(self, since):
        return None

    # retrieve all games that had player involved in it
    def getGamesByPlayer(self, name, since):
        return None

    # derp
    def recordGame(self, t, teamAWhite, tawRating, teamABlack, tabRating, \
            teamBWhite, tbwRating, teamBBlack, tbbRating):

        fp = open("games.dat", 'a')
        fp.write("%d %s(%d),%s(%d) > %s(%d),%s(%d)\n" % (t, teamAWhite, tawRating, \
            teamABlack, tabRating, teamBWhite, tbwRating, teamBBlack, tbbRating))
        fp.close()

        pass

    def init(self):
        for f in ['players.dat', 'games.dat']:
            if not os.path.exists(f):
                fp = open(f, 'w+')
                fp.close()

