__version__ = "0.7"

# add the wwwsearch stuff from the zip file.
import sys, os.path
thisdir = os.path.dirname(__file__)
sys.path.insert(0, thisdir)             # @@CTB

wwwsearchlib = os.path.join(thisdir, 'wwwsearch.zip')
sys.path.insert(0, wwwsearchlib)

pyparsinglib = os.path.join(thisdir, 'pyparsing.zip')
sys.path.insert(0, pyparsinglib)

# the only two things we really need.
from shell import TwillCommandLoop
from parse import execute_file

# convenience function or two...

import commands
def get_browser_state():
    return commands.state
