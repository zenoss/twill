"""
Interactive and file execution stuff.
"""

import sys
import code, re

from IPython.Shell import IPShell, IPShellEmbed
from errors import TwillAssertionError
from autoquote import autoquote_if_necessary

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

def execute_file(filename):
    """
    Execute commands from a file, rewriting them into valid Python by
    autoquoting as necessary.
    """
    finished = 0

    global_dict = {}
    local_dict = {}

    # initialize global/local dictionaries.
    exec "from twill.commands import *" in global_dict, local_dict
        
    lines = open(filename).readlines()

    # first, compile into code blocks.   this will get rid of any
    # out & out syntax errors.
    
    code_objs = []
    full_cmd = ""
    for line in lines:
        line = autoquote_if_necessary(full_cmd, line)
        
        full_cmd += line
        codeobj = code.compile_command(full_cmd, filename)
        
        if codeobj is None:         # incomplete command; punt.
            pass
        else:
            code_objs.append((codeobj, full_cmd)) # save, clear, move on.
            full_cmd = ""

    # now, EXECUTE.

    for (codeobj, cmd) in code_objs:
        try:
            # hack to support no-arg functions... @CTB how bad is this, really?
            if re.match('^[a-zA-Z_][a-zA-Z0-9_]+$', cmd):
                name = cmd.strip()
                val = global_dict.get(name)
                val = local_dict.get(name, val)
                if callable(val):
                    codeobj = code.compile_command(name + "()")

            exec codeobj in global_dict, local_dict
        except TwillAssertionError, e:
            sys.stderr.write('''\
Oops!  Twill assertion error while executing
 
    %s
''' % (cmd,))
            raise
        except Exception, e:
            sys.stderr.write('EXCEPTION while executing \n\n\t%s\n' % (cmd,))
            raise
