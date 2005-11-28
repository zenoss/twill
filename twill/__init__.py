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

#import warnings
#warnings.defaultaction = "error"

__all__ = [ "TwillCommandLoop", "execute_file", "get_browser_state",
            "add_wsgi_intercept", "remove_wsgi_intercept" ]

# add the wwwsearch & pyparsing stuff from twill/wwwsearch/.
import sys, os.path
thisdir = os.path.dirname(__file__)
sys.path.insert(0, thisdir)             # @@CTB

wwwsearchlib = os.path.join(thisdir, 'wwwsearch/')
sys.path.insert(0, wwwsearchlib)

import myhttplib

# the two core components
from shell import TwillCommandLoop
from parse import execute_file

# convenience function or two...

import commands
def get_browser_state():
    return commands.browser

# initialize global dict
import namespaces
namespaces.init_global_dict()

from myhttplib import add_wsgi_intercept, remove_wsgi_intercept
