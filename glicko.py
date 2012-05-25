#!/usr/bin/python

# typed up while reading:
# http://www.freechess.org/Help/HelpFiles/glicko.html

import math;

# we define a rating period as 1 second, and the time for a player's rating to
# decay to a reliabily even with a a brand new player's rating (not reliable 
# at all) as two months, or 5184000 = 60*24*3600
# now to solve for c
# 350 = sqrt(50^2 + c^2(5184000))
# math.sqrt((350*350 - 250)/5184000.0)
c = 0.023582175925925927

# ratings is list where [0] is dude we're calculating for, [1] is his partner
#  [2], [3] are the opponents
# rds is same
# t is seconds since last time he played a game
# w is 1 for win, 0 for loss
#
def glicko(ratings, rds, t, w):
    # RD adjustment due to time
    rd = rds[0]
    rd = math.sqrt(rd*rd + c*t)
    rd = min(rd, 350)

    # attenuating factor
    p = .0000025180996504909944  # 3*math.log(10)*math.log(10) / (math.pi*math.pi * 800 * 800)
    f = 1/math.sqrt(1 + p*(rds[1]*rds[1] + rds[2]*rds[2] + rds[3]*rds[3]))

    # average ratings
    r1 = (ratings[0]+ratings[1])/2
    r2 = (ratings[2]+ratings[3])/2
    E = 1/(1 + math.exp(-1*(r1-r2)*f/400))

    # begin-pre
    q = 0.0028782313662425573 # math.log(10)/800
    denom = 1/(rd*rd) + q*q*f*f*E*(1-E)
    K = q*f / denom
    K = max(K,16)

    # new rating, new rd
    rating = ratings[0] + K*(w - E)
    rd = 1/math.sqrt(denom)

    # done
    return [rating, rd]

def glickoDelta(ratings, rds, t, w):
    [newRating, newRD] = glicko(ratings, rds, t, w)
    return [newRating - ratings[0], newRD - rds[0]]
