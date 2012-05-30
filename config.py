#!/usr/bin/python

SHOW_GIT_COMMIT = 1

# if the server is not in the same timezone as you, you may want to offset
# its clock with some delta here to make time reading make sense in your
# area

# by convention, let's let the DB contain time that makes sense for the server
# and only when it ready to DISPLAY the time, do we adjust
TIME_ADJUST = 3*24*3600
