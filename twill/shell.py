from IPython.Shell import IPShellEmbed

class AutoShell:
    """
    Execute commands one at at time in an IPython shell.

    Ideas:
      * on exception, drop into interactive shell.
    """
    def __init__(self):
        self.ipshell = IPShellEmbed()
        self.IP = self.ipshell.IP
        self.IP.ctb_autoquote = True

        self.execute("from twill.commands import *")

    def execute(self, cmd):
	line = self.IP.prefilter(cmd, None)
        self.IP.push(line)

    def execute_file(self, filename):
        for line in open(filename).readlines():
            self.execute(line)

    def interact(self):
        self.ipshell()
