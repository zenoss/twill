"""
A cmd.Cmd interpreter for twill.
"""

import cmd
from twill import commands, parse

class _command_loop_metaclass(type):
    def __init__(cls, cls_name, cls_bases, cls_dict):
        super(_command_loop_metaclass, cls).__init__(cls_name,
                                                     cls_bases,
                                                     cls_dict)

        #
        # create 'do_' functions for all of the commands.
        #
        
        for command in commands.__all__:
            name = 'do_%s' % (command,)
            fn = getattr(commands, command)
            
            def do_cmd(self, rest_of_line, cmd=command):
                globals_dict, locals_dict = parse.get_twill_glocals()
        
                args = parse.arguments.parseString(rest_of_line)
                args = parse.process_args(args,globals_dict,locals_dict)

                parse.execute_command(cmd, args, globals_dict, locals_dict)
                
            setattr(cls, name, do_cmd)

            def help_cmd(self, message=fn.__doc__):
                print message

            name = 'help_%s' % (command,)
            setattr(cls, name, help_cmd)

        ## TODO, command completion coolness.

class TwillCommandLoop(object, cmd.Cmd):
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
