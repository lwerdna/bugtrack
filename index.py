#!/usr/bin/python

import config
import subprocess

print "Content-Type: text/html\x0d\x0a\x0d\x0a",
print '<html>'
print '<head>'
print '<link rel=StyleSheet href="stylesheet.css" type="text/css">'
print '<script type="text/javascript" src="./bugtrack.js"></script>'
print '</head>'
print '<body>'
print ''
print '<h2>bugtrack</h2>'
print '<hr />'
print ''
print '   <form action=play.py>'
print '   <input type=submit name=foo value=Play>'
print '   </form>'
print '   <form action=stats.py>'
print '   <input type=hidden name=op value=leaderboard>'
print '   <input type=submit name=foo value="Leader Board">'
print '   </form>'
print '   <form action=stats.py>'
print '   <input type=hidden name=op value=gameslist>'
print '   <input type=submit name=foo value="Games List">'
print '   </form>'
print ''
print '<hr />'
print ''
print '<h3>Version Information</h3>'
print ''

# show version info
if config.SHOW_GIT_COMMIT:
    print '<pre>'
    pipe = subprocess.Popen("git log --name-status HEAD^..HEAD", stdout=subprocess.PIPE, shell=True)
    print pipe.communicate()[0]
    print '</pre>'

print ''
print '</body>'
print '</html>'
