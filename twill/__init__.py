# This file is part of the twill source distribution.
#
# twill is a extensible scriptlet language for testing Web apps,
# available at http://www.idyll.org/~t/www-tools/twill.html.
#
# Contact author: C. Titus Brown, titus@caltech.edu.
#
# This program and all associated source code files are Copyright (C)
# 2005 by C. Titus Brown.  It is under the Lesser GNU Public License;
# please see the included LICENSE.txt file for more information, or
# contact Titus directly.

__version__ = "0.8"

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
    return commands.browser

# initialize global dict
import namespaces
namespaces.init_global_dict()
