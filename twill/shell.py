"""
A command-line interpreter for twill.

This is an implementation of a command-line interpreter based on the
'Cmd' class in the 'cmd' package of the default Python distribution.
A metaclass is used to automagically suck in commands published by
the 'twill.commands' module & create do_ and help_ functions for
them.
"""

import cmd
from twill import commands, parse

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
                globals_dict, locals_dict = parse.get_twill_glocals()

                args = []
                if rest_of_line.strip() != "":
                    args = parse.arguments.parseString(rest_of_line)
                    args = parse.process_args(args,globals_dict,locals_dict)

                parse.execute_command(cmd, args, globals_dict, locals_dict)
                
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

    Note: all of the do_ and help_ functions are dynamically created
    by the metaclass.
    """
    __metaclass__ = _command_loop_metaclass
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        parse._init_twill_glocals()
        self.use_raw_input = False
        self._set_prompt()

    def emptyline(self):
        pass

    def _set_prompt(self):
        url = commands.state.url()
        self.prompt = "current page: %s\n>> " % (url,)

    def postcmd(self, stop, line):
        self._set_prompt()
        
        return stop

    def do_EOF(self, *args):
        raise SystemExit()

    def default(self, line):
        line = line.strip()
        if line[0] == '#':              # ignore comments
            return

        cmd.Cmd.default(self, line)
