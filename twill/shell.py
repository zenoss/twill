"""
Interactive and file execution stuff.
"""

import sys
import code, re

from pyparsing import OneOrMore, Word, printables, quotedString, Optional, \
     alphas, alphanums, ParseException, ZeroOrMore, restOfLine, Combine

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

# valid Python identifier:
command = Combine(Word(alphas + "_", max=1) + Word(alphanums + "_"))

# arguments to it.
arguments = OneOrMore(Word(printables) ^ quotedString)

# comment line.
comment = Word('#', max=1) + restOfLine

full_command = comment ^ (command + Optional(arguments))

def parse_command(line, globals_dict, locals_dict):
    res = full_command.parseString(line)
    command = res[0]
    
    newargs = []
    for arg in res[1:]:
        # strip quotes from quoted strings.
        # don't use string.strip, which will remove more than one...
        if arg[0] == arg[-1] and arg[0] in "\"'":
            newargs.append(arg[1:-1])
        elif arg[0:2] == '__':
            val = eval(arg, globals_dict, locals_dict)
            newargs.append(val)
        else:
            newargs.append(arg)

    return (command, newargs)

global_dict = local_dict = None

def _init_twill_glocals():
    global global_dict, local_dict

    global_dict = {}
    local_dict = {}
    exec "from twill.commands import *" in global_dict, local_dict

def get_twill_glocals():
    global global_dict, local_dict

    return global_dict, local_dict

def execute_file(filename, init_glocals = True):
    """
    Execute commands from a file.
    """
    finished = 0

    # initialize global/local dictionaries.
    if init_glocals:
        _init_twill_glocals()
        
    lines = open(filename).readlines()

    for line in lines:
        if not line.strip():            # skip empty lines
            continue
        
        cmd, args = parse_command(line, global_dict, local_dict)

        if cmd == '#':                  # skip comments
            continue

        # execute command.
        local_dict['__args__'] = args

        eval_str = "%s(*__args__)" % (cmd,)

        try:
            eval(eval_str, global_dict, local_dict)
        except TwillAssertionError, e:
            sys.stderr.write('''\
Oops!  Twill assertion error while executing
 
    %s
''' % (cmd,))
            raise
        except Exception, e:
            sys.stderr.write('EXCEPTION while executing \n\n\t%s\n' % (cmd,))
            raise
