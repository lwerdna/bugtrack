bugtrack
========

small bughouse rating and tracking software

quick setup:
1) create a games.dat file (see below for example)
2) create a players.dat file (see below for example)
3) install thttpd
4) run localsrv.sh (just calls thttpd with proper parameters)
5) browser to http://localhost:2048
6) click index.py

example games.dat file:
~~start~~
[Wed May 23, 2012 23:12:03] Chris,David (+10) > Luke,Randy (-10)
[Wed May 23, 2012 23:12:07] Luke,Randy (+173) > Chris,David (-163)
[Wed May 23, 2012 23:12:15] Luke,David (+73) > Chris,Randy (-84)
~~end~~

example players.at file:
(format is <name> <rating> <rd>)
~~start~~
Chris 863 199
David 1551 156
Luke 796 193
Randy 1171 170
~~end~~

