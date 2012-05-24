#!/usr/bin/python

"""
Copyright (c) 2009 Ryan Kirkman

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import math

class Player:
    # Class attribute.
    # The q constant of the Glicko system. 
    _q = math.log(10)/400

    def __init__(self, rating = 1500, rd = 200):
        # For testing purposes, preload the values assigned to an unrated player.
        self.rating = rating
        self.rd = rd
        
    def _preRatingRD(self, t = 1, c = 63.2):
        """ Calculates and updates the player's rating deviation for the
        beginning of a rating period.
        
        preRatingRD(int, float) -> None
        """
        
        # Calculate the new rating deviation.
        self.rd = math.sqrt(math.pow(self.rd, 2) + 
            (math.pow(c, 2) * t))
        # Ensure RD doesn't rise above that of an unrated player.
        self.rd = min(self.rd, 350)
        # Ensure RD doesn't drop too low so rating can still change appreciably.
        self.rd = max(self.rd, 30)
        
    def update_player(self, rating_list, RD_list, outcome_list):
        """ Calculates the new rating and rating deviation of the player.
        
        update_player(list[int], list[int], list[bool]) -> None
        """
        # Calculate pre - rating period rating deviation.
        # This can be done either before or after updating ratings and 
        # deviations, as even if all players are unrated, the rating deviation
        # won't rise above 350.
        self._preRatingRD()
        
        # Update rating.
        d2 = self._d2(rating_list, RD_list)
        rPrime = (self._q / ((1 / math.pow(self.rd, 2)) + 
            (1 / d2)))
        
        tempSum = 0
        for i in range(len(rating_list)):
            tempSum += self._g(RD_list[i]) * (outcome_list[i] - self._E(rating_list[i], RD_list[i]))
        
        rPrime *= tempSum
        rPrime += self.rating
        self.rating = rPrime
        
        # Update rating deviation.
        self.rd = math.sqrt(1 / ((1 / math.pow(self.rd, 2)) + (1 / d2)))
        
    def _d2(self, rating_list, RD_list):
        """ The d^2 function of the Glicko system.
        
        _d2(list[int], list[int]) -> float
        """
        tempSum = 0
        for i in range(len(rating_list)):
            tempE = self._E(rating_list[i], RD_list[i])
            tempSum += math.pow(self._g(RD_list[i]), 2) * tempE * (1 - tempE)
        return 1 / (math.pow(self._q, 2) * tempSum)
        
    def _E(self, p2rating, p2RD):
        """ The Glicko E function.
        
        _E(int) -> float
        """
        return 1 / (1 + math.pow(10, (-1 * self._g(p2RD) * (self.rating - p2rating) / 400)))
        
    def _g(self, RD):
        """ The Glicko g(RD) function.
        
        _gRD() -> float
        """
        return 1 / math.sqrt(1 + 3 * math.pow(self._q, 2) 
            * math.pow(RD, 2) / math.pow(math.pi, 2))
