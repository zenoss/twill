import sys
from IPython.Shell import IPShell, IPShellEmbed
from IPython.ipmaker import make_IPython
from errors import TwillAssertionError
import code

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

    def execute_file(self, filename):
        for line in open(filename).readlines():
            self.execute(line)

    def interact(self):
        self.ipshell()
