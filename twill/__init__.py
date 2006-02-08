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

__version__ = "0.8.2"

#import warnings
#warnings.defaultaction = "error"

#import pychecker.checker

__all__ = [ "TwillCommandLoop",
            "execute_file",
            "execute_string",
            "get_browser",
            "add_wsgi_intercept",
            "remove_wsgi_intercept",
            "set_output"]

#
# add extensions (twill/extensions) and the the wwwsearch & pyparsing
# stuff from twill/included-packages/.  NOTE: this works with eggs! hooray!
#

import sys, os.path
thisdir = os.path.dirname(__file__)
sys.path.insert(0, thisdir)

extensions = os.path.join(thisdir, 'extensions/')
sys.path.insert(0, extensions)

wwwsearchlib = os.path.join(thisdir, 'wwwsearch/')
sys.path.insert(0, wwwsearchlib)

# the two core components of twill:
from shell import TwillCommandLoop
from parse import execute_file, execute_string

# convenience function or two...
from commands import get_browser

def get_browser_state():
    import warnings
    warnings.warn("get_browser_state is deprecated; use 'twill.get_browser() instead.", DeprecationWarning)
    return get_browser()

# initialize global dict
import namespaces
namespaces.init_global_dict()

from wsgi_intercept import add_wsgi_intercept, remove_wsgi_intercept

def set_output(fp):
    """
    Have standard output from twill go to the given fp instead of
    stdout.  fp=None will reset to stdout.
    """
    import commands, browser
    commands.OUT = browser.OUT = fp
