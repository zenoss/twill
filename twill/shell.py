"""
Interactive and file execution stuff.
"""

import sys
import code, re

from pyparsing import OneOrMore, Word, printables, quotedString, Optional, \
     alphanums, ParseException, ZeroOrMore, restOfLine

from IPython.Shell import IPShell, IPShellEmbed
from errors import TwillAssertionError

class AutoShell:
    """
    Execute commands one at at time in an IPython shell.

    Ideas:
      * on exception, drop into interactive shell.
    """
    def __init__(self, argv=sys.argv):
        self.ipshell = IPShellEmbed(argv)
        self.IP = self.ipshell.IP
        self.last_was_incomplete = False

        self.IP.push("from twill.commands import *")
        self.IP.push("import twill.install_prefilter")

    def execute(self, cmd):
        line = self.IP.prefilter(cmd, self.last_was_incomplete)
        self.last_was_incomplete = self.IP.push(line)

    def interact(self):
        self.ipshell()

### pyparsing stuff

arguments = OneOrMore(Word(printables) ^ quotedString)
comment = Word('#', max=1) + restOfLine

full_command = comment ^ (Word(alphanums) + Optional(arguments))

def parse_command(line):
    res = full_command.parseString(line)
    command = res[0]
    
    newargs = []
    for arg in res[1:]:
        # strip quotes from quoted strings.
        # don't use string.strip, which will remove more than one...
        if arg[0] == arg[-1] and arg[0] in "\"'":
            newargs.append(arg[1:-1])
        else:
            newargs.append(arg)

    return (command, newargs)

def execute_file(filename):
    """
    Execute commands from a file.
    """
    finished = 0

    global_dict = {}
    local_dict = {}

    # initialize global/local dictionaries.
    exec "from twill.commands import *" in global_dict, local_dict
        
    lines = open(filename).readlines()

    for line in lines:
        if not line.strip():            # skip empty lines
            continue
        
        cmd, args = parse_command(line)

        if cmd == '#':                  # skip comments
            continue

        # execute command.
        callable = eval(cmd, global_dict, local_dict)

        try:
            callable(*args)
        except TwillAssertionError, e:
            sys.stderr.write('''\
Oops!  Twill assertion error while executing
 
    %s
''' % (cmd,))
            raise
        except Exception, e:
            sys.stderr.write('EXCEPTION while executing \n\n\t%s\n' % (cmd,))
            raise
