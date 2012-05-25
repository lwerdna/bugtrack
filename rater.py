# this module handles the complexity of glick calculations
# (for example calculating adjustments to rating and RD of all players simultaneously)

# when only the play interface made this calculations, this middle layer was unnecessary, but
# now like the admin tool does the same, so I don't want to repeat any logic
    
# if a1 (with partner a2, opponents b1,b2) plays, return his <+win>,<-loss> adjustment
# returns [winDelta, loseDelta]
def computeDelta(a1,a2,b1,b2):

    t = db.getPlayerT(a1)

    ratings = map(lambda x: db.getPlayerRating(x), [a1,a2,b1,b2])
    rds = map(lambda x: db.getPlayerRD(x), [a1,a2,b1,b2])

    [winDelta, winRD] = glicko.glickoDelta(ratings, rds, int(time.time()) - t, 1)
    [loseDelta, loseRD] = glicko.glickoDelta(ratings, rds, int(time.time()) - t, 0)

    print "%d,%d" % (winDelta, loseDelta)

    return [winDelta, loseDelta]

# suppose a game is played with winners a1,a2 and losers a3,a4
# given [a1,a2,a3,a4], return the new ratings/rd's in this form:
# [[a1_RATING, a1_RD], [a2_RATING, a2_RD], [b1_RATING, b1_RD], [b2_RATING, b2_RD]]
#
def computeGameScores(a1,a2,b1,b2):
    # calculate new scores
    ratings = map(lambda x: db.getPlayerRating(x), [a1, a2, b1, b2])
    rds = map(lambda x: db.getPlayerRD(x), [a1, a2, b1, b2])
    tdelta = tnow - db.getPlayerT(a1)
    stats1 = glicko.glicko(ratings, rds, tdelta, 1)
    #print "calling glicko(", ratings, ", ", rds, ", ", tdelta, ", 1)<br>\n"
    #print "a1 new stats: ", stats1, '<br>\n'

    ratings = map(lambda x: db.getPlayerRating(x), [a2, a1, b1, b2])
    rds = map(lambda x: db.getPlayerRD(x), [a2, a1, b1, b2])
    tdelta = tnow - db.getPlayerT(a2)
    stats2 = glicko.glicko(ratings, rds, tdelta, 1)
    #print "calling glicko(", ratings, ", ", rds, ", ", tdelta, ", 1)<br>\n"
    #print "a2 new stats: ", stats2, '<br>\n'

    ratings = map(lambda x: db.getPlayerRating(x), [b1, b2, a1, a2])
    rds = map(lambda x: db.getPlayerRD(x), [b1, b2, a2, a1])
    tdelta = tnow - db.getPlayerT(b1)
    stats3 = glicko.glicko(ratings, rds, tdelta, 0)
    #print "calling glicko(", ratings, ", ", rds, ", ", tdelta, ", 0)<br>\n"
    #print "b1 new stats: ", stats3, '<br>\n'

    ratings = map(lambda x: db.getPlayerRating(x), [b2, b1, a1, a2])
    rds = map(lambda x: db.getPlayerRD(x), [b2, b1, a1, a2])
    tdelta = tnow - db.getPlayerT(b2)
    stats4 = glicko.glicko(ratings, rds, tdelta, 0)
    #print "calling glicko(", ratings, ", ", rds, ", ", tdelta, ", 0)<br>\n"
    #print "b2 new stats: ", stats4, '<br>\n'

    return [stats1, stats2, stats3, stats4]

