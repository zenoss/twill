# add the wwwsearch stuff from the zip file.
import sys, os.path
thisdir = os.path.dirname(__file__)
sys.path.insert(0, thisdir)             # @@CTB

wwwsearchlib = os.path.join(thisdir, 'wwwsearch.zip')
sys.path.insert(0, wwwsearchlib)

# the only thing we really need.
from shell import AutoShell

import commands
def get_browser_state():
    return commands.state
