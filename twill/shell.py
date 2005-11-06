"""
A command-line interpreter for twill.

This is an implementation of a command-line interpreter based on the
'Cmd' class in the 'cmd' package of the default Python distribution.
A metaclass is used to automagically suck in commands published by
the 'twill.commands' module & create do_ and help_ functions for
them.
"""

import cmd
from twill import commands, parse, __version__
import namespaces

try:
    import readline
except:
    readline = None

class _command_loop_metaclass(type):
    """
    A metaclass to automatically create do_ and help_ functions
    for all of the twill.commands functions.
    """
    def __init__(cls, cls_name, cls_bases, cls_dict):
        super(_command_loop_metaclass, cls).__init__(cls_name,
                                                     cls_bases,
                                                     cls_dict)

        #
        # create 'do_' and 'help_' functions for all of the commands.
        #
        
        for command in commands.__all__:
            fn = getattr(commands, command)
            
            def do_cmd(self, rest_of_line, cmd=command):
                global_dict, local_dict = namespaces.get_twill_glocals()

                args = []
                if rest_of_line.strip() != "":
                    args = parse.arguments.parseString(rest_of_line)
                    args = parse.process_args(args, global_dict, local_dict)

                try:
                    parse.execute_command(cmd, args, global_dict, local_dict)
                except Exception, e:
                    print '\nERROR: %s\n' % (str(e),)
                
            name = 'do_%s' % (command,)
            setattr(cls, name, do_cmd)

            def help_cmd(self, message=fn.__doc__, cmd=command):
                print '=' * 15
                print '\nHelp for command %s:\n' % (cmd,)
                print message.strip()
                print ''
                print '=' * 15
                print ''

            name = 'help_%s' % (command,)
            setattr(cls, name, help_cmd)

        ## TODO, command completion coolness.

#
# TwillCommandLoop
#

class TwillCommandLoop(object, cmd.Cmd):
    """
    Command-line interpreter for twill commands.

    Note: most of the do_ and help_ functions are dynamically created
    by the metaclass.
    """
    __metaclass__ = _command_loop_metaclass
    
    def __init__(self, **kw):
        cmd.Cmd.__init__(self)

        # initialize a new local namespace.
        
        namespaces.new_local_dict()
        self.use_raw_input = False

        # import readline history, if available.
        if readline:
            try:
                readline.read_history_file('.twill-history')
            except IOError:
                pass

        if kw.get('initial_url'):
            commands.go(kw['initial_url'])
            
        self._set_prompt()

    def _set_prompt(self):
        "Set the prompt to the current page."
        url = commands.browser.url()
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
            parse.execute_command(cmd, args, global_dict, local_dict)
        except SystemExit:
            raise
        except Exception, e:
            print '\nERROR: %s\n' % (str(e),)

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
        print "See http://www.idyll.org/~t/www-tools/twill.html for more info."
        print ""

    def help_version(self):
        print "\nPrint version information.\n"

    def do_exit(self, *args):
        raise SystemExit()

    def help_exit(self):
        print "\nExit twill.\n"

    do_quit = do_exit
    help_quit = help_exit
