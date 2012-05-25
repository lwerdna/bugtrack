# this defines the abstract interface that the other parts of bugtrack
# expect to interact with whatever method is used to store shit

# so like if you have an sqlite backend, you should implement dbSqlite,
# inheriting from this, implementing the methods

# initially, I'll make a model dbText, which uses simple text files for
# storage....

class Db(object):
    #--------------------------------------------------------------------------
    # general info
    #--------------------------------------------------------------------------
    # return list of players
    def getPlayerList(self):
        pass
    #--------------------------------------------------------------------------
    # get player stats
    #--------------------------------------------------------------------------
    # get the player's rating
    def getPlayerRating(self, name):
        pass
    # get the player's RD
    def getPlayerRD(self, name):
        pass
    # get the player's last time played
    def getPlayerT(self, name):
        pass

    # return a list [rating, RD, tLastPlayed]
    def getPlayerStats(self, name):
        pass

    #--------------------------------------------------------------------------
    # set player stats
    #--------------------------------------------------------------------------
    def setPlayerRating(self, name, r):
        pass
    def setPlayerRD(self, name, rd):
        pass
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
        pass

    # retrieve all games that had player involved in it
    def getGamesByPlayer(self, name, since):
        pass

    def recordGame(self, t, teamAWhite, tawRating, teamABlack, tabRating, \
            teamBWhite, tbwRating, teamBBlack, tbbRating):
        pass

    #--------------------------------------------------------------------------
    # setup/testing stuff
    #--------------------------------------------------------------------------
    # this should create whatever files or dependencies are necessary for this
    # db implementation to work...
    #
    # for example. DbText creates players.dat and games.dat
    #
    def init(self):
        pass
