bugtrack
========

small bughouse rating and tracking software

quick setup:

1. create a bugtrack.db file (run ./admin.py seeddb)
2. run ./localsrv.py to start a webserver
3. browse to http://localhost:2048


internals
=========

following the BPGN convention:
- the letters 'A' and 'B' refer to boards
- we arrange players and teams like this:

             BlackA 'a'                WhiteB 'B'
        +---------------+         +---------------+
        |               |         |               |
        |    Board A    |         |    Board B    |
        |               |         |               |
        +---------------+         +---------------+
             WhiteA 'A'                BlackB 'b'

- due to case insensitivity, the column names in the database for game history
  use the names "WhiteA", "BlackB", "WhiteB", "BlackA" (in this column order)
- for brevity, we use 'A', 'b', 'B', 'a' else (javascript, html)
- we call the teams "top" and "bottom"
- the winning team is positioned "bottom" into 'A','b' and losers into 'a','B'

