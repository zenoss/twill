"""
A command-line interpreter for twill.

This is an implementation of a command-line interpreter based on the
'Cmd' class in the 'cmd' package of the default Python distribution.
"""

import cmd
from twill import commands, parse, __version__
import namespaces

try:
    import readline
except:
    readline = None

def make_cmd_fn(cmd):
    """
    Dynamically define a twill shell command function based on an imported
    function name.  (This is where the twill.commands functions actually
    get executed.)
    """
    
    def do_cmd(rest_of_line, cmd=cmd):
        global_dict, local_dict = namespaces.get_twill_glocals()

        args = []
        if rest_of_line.strip() != "":
            try:
                args = parse.arguments.parseString(rest_of_line)[0]
                args = parse.process_args(args, global_dict,local_dict)
            except Exception, e:
                print '\nINPUT ERROR: %s\n' % (str(e),)
                return

        try:
            parse.execute_command(cmd, args, global_dict, local_dict,
                                  "<shell>")
        except SystemExit:
            raise
        except Exception, e:
            print '\nERROR: %s\n' % (str(e),)
            raise

    return do_cmd

def make_help_cmd(cmd, docstring):
    """
    Dynamically define a twill shell help function for the given
    command/docstring.
    """
    def help_cmd(message=docstring, cmd=cmd):
        print '=' * 15
        print '\nHelp for command %s:\n' % (cmd,)
        print message.strip()
        print ''
        print '=' * 15
        print ''
        
    return help_cmd

###

class Singleton(object):
    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it
    
    def init(self, *args, **kwds):
        pass

#
# TwillCommandLoop
#

def add_command(cmd, docstring):
    x = get_command_shell()
    if x:
        x.add_command(cmd, docstring)
        
def get_command_shell():
    return getattr(TwillCommandLoop, '__it__', None)

class TwillCommandLoop(Singleton, cmd.Cmd):
    """
    Command-line interpreter for twill commands.  Singleton object: you
    can't create more than one of these at a time.

    Note: most of the do_ and help_ functions are dynamically created
    by the metaclass.
    """
    def init(self, **kw):
        if kw.has_key('stdin'):
            cmd.Cmd.__init__(self, None, stdin=kw['stdin'])
            self.use_rawinput = False
        else:
            cmd.Cmd.__init__(self)

        # initialize a new local namespace.
        namespaces.new_local_dict()

        # import readline history, if available.
        if readline:
            try:
                readline.read_history_file('.twill-history')
            except IOError:
                pass

        # fail on unknown commands? for test-shell, primarily.
        self.fail_on_unknown = kw.get('fail_on_unknown', False)

        # handle initial URL argument
        if kw.get('initial_url'):
            commands.go(kw['initial_url'])
            
        self._set_prompt()

        self.names = []
        
        global_dict, local_dict = namespaces.get_twill_glocals()

        ### add all of the commands from twill.
        for command in parse.command_list:
            fn = global_dict.get(command)
            self.add_command(command, fn.__doc__)

    def add_command(self, command, docstring):
        """
        Add the given command into the lexicon of all commands.
        """
        do_name = 'do_%s' % (command,)
        do_cmd = make_cmd_fn(command)
        setattr(self, do_name, do_cmd)

        if docstring:
            help_cmd = make_help_cmd(command, docstring)
            help_name = 'help_%s' % (command,)
            setattr(self, help_name, help_cmd)

        self.names.append(do_name)

    def get_names(self):
        """
        Return the list of commands.
        """
        return self.names

    def _set_prompt(self):
        "Set the prompt to the current page."
        url = commands.browser.get_url()
        if url is None:
            url = " *empty page* "
        self.prompt = "current page: %s\n>> " % (url,)

    def precmd(self, line):
        "Run before each command; save."
        return line

    def postcmd(self, stop, line):
        "Run after each command; set prompt."
        self._set_prompt()
        
        return stop

    def default(self, line):
        "Called when unknown command is executed."

        # empty lines ==> emptyline(); here we just want to remove
        # leading whitespace.
        line = line.strip()

        # look for command
        global_dict, local_dict = namespaces.get_twill_glocals()
        cmd, args = parse.parse_command(line, global_dict, local_dict)

        # ignore comments & empty stuff
        if cmd is None:
            return

        try:
            parse.execute_command(cmd, args, global_dict, local_dict,
                                  "<shell>")
        except SystemExit:
            raise
        except Exception, e:
            print '\nERROR: %s\n' % (str(e),)
            if self.fail_on_unknown:
                raise

    def emptyline(self):
        "Ignore empty lines."
        pass

    def do_EOF(self, *args):
        "Exit on CTRL-D"
        if readline:
            readline.write_history_file('.twill-history')
            
        raise SystemExit()

    def help_help(self):
        print "\nWhat do YOU think the command 'help' does?!?\n"

    def do_version(self, *args):
        print "\ntwill version %s.\n" % (__version__,)
        print "See http://www.idyll.org/~t/www-tools/twill/ for more info."
        print ""

    def help_version(self):
        print "\nPrint version information.\n"

    def do_exit(self, *args):
        raise SystemExit()

    def help_exit(self):
        print "\nExit twill.\n"

    do_quit = do_exit
    help_quit = help_exit

def main():
    import sys
    from twill import TwillCommandLoop, execute_file, __version__
    from optparse import OptionParser
    from cStringIO import StringIO

    ###
    # make sure that the current working directory is in the path.  does this
    # work on Windows??

    if not '.' in sys.path:
        sys.path.append('.')
    ###

    #### OPTIONS

    parser = OptionParser()

    parser.add_option('-q', '--quiet', action="store_true", dest="quiet",
                      help = 'do not show normal output')

    parser.add_option('-i', '--interactive', action="store_true", dest="interact",
              help = 'drop into an interactive shell after running files (if any)')

    parser.add_option('-f', '--fail', action="store_true", dest="fail",
                      help = 'fail exit on first file to fail')

    parser.add_option('-v', '--version', action="store_true", dest="show_version",
                      help = 'show version information and exit')

    parser.add_option('-u', '--url', nargs=1, action="store", dest="url",
                      help="start at the given URL before each script")

    ####

    # parse arguments.
    (options, args) = parser.parse_args()

    if options.show_version:
        print 'twill version %s.' % (__version__,)
        sys.exit(0)

    if options.quiet:
        assert not options.interact, "interactive mode is incompatible with -q"
        assert args, "interactive mode is incompatible with -q"

        old_stdout = sys.stdout
        sys.stdout = StringIO()

    # If run from the command line, find & run any scripts put on the command
    # line.  If none, drop into an interactive AutoShell.

    failed = False
    if len(args):
        success = []
        failure = []
        for filename in args:
            if filename[-1] == '~':
                print 'SKIPPING backup file:', filename
                continue

            print '>> EXECUTING FILE', filename

            try:
                execute_file(filename, initial_url=options.url)
                success.append(filename)
            except Exception, e:
                if options.fail:
                    raise
                else:
                    print '** UNHANDLED EXCEPTION:', str(e)
                    failure.append(filename)

        print '--'
        print '%d of %d files SUCCEEDED.' % (len(success),
                                             len(success) + len(failure),)
        if len(failure):
            print 'Failed:\n\t',
            print "\n\t".join(failure)
            failed = True

    if not args or options.interact:
        welcome_msg = ""
        if not args:
            welcome_msg = "\n -= Welcome to twill! =-\n"

        shell = TwillCommandLoop(initial_url=options.url)

        while 1:
            try:
                shell.cmdloop(welcome_msg)
            except KeyboardInterrupt:
                sys.stdout.write('\n')
            except SystemExit:
                raise

            welcome_msg = ""

    if failed:
        sys.exit(1)
    sys.exit(0)
