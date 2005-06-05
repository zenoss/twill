"""
Code parsing and evaluation for the twill mini-language.
"""

import sys
from errors import TwillAssertionError
from pyparsing import OneOrMore, Word, printables, quotedString, Optional, \
     alphas, alphanums, ParseException, ZeroOrMore, restOfLine, Combine, \
     removeQuotes, Literal

import twill.commands as commands

### pyparsing stuff

# basically, a valid Python identifier:
command = Word(alphas + "_", alphanums + "_")

# arguments to it.
arguments = OneOrMore(
    quotedString.setParseAction(removeQuotes) |
    Word(printables)
    )

# comment line.
comment = Literal('#') + restOfLine

full_command = comment ^ command + Optional(arguments)
#full_command = command + Optional(arguments)
#full_command.ignore(comment)

### initialization and global/local dicts

global_dict = local_dict = None

def _init_twill_glocals():
    global global_dict, local_dict

    global_dict = {}
    local_dict = {}
    exec "from twill.commands import *" in global_dict, local_dict

def get_twill_glocals():
    global global_dict, local_dict

    return global_dict, local_dict

### command/argument handling.

def process_args(args, globals_dict, locals_dict):
    """
    Take a list of string arguments parsed via pyparsing, unquote
    those that are quoted, and evaluate the special variables ('__*').
    Return a new list.
    """
    newargs = []
    for arg in args:
        # strip quotes from quoted strings.
        # don't use string.strip, which will remove more than one...
        if arg[0] == arg[-1] and arg[0] in "\"'":
            newargs.append(arg[1:-1])
        elif arg[0:2] == '__':
            val = eval(arg, globals_dict, locals_dict)
            newargs.append(val)
        else:
            newargs.append(arg)

    return newargs

def execute_command(cmd, args, globals_dict, locals_dict):
    """
    Actually execute the command.

    Side effects: __args__ is set to the argument tuple, __cmd__ is set to
    the command.
    """
    # execute command.
    locals_dict['__cmd__'] = cmd
    locals_dict['__args__'] = args

    eval_str = "%s(*__args__)" % (cmd,)

    # set __url__
    locals_dict['__url__'] = commands.state.url()

    return eval(eval_str, global_dict, local_dict)

def parse_command(line, globals_dict, locals_dict):
    """
    Parse command.
    """
    res = full_command.parseString(line)
    command = res[0]
    args = process_args(res[1:], globals_dict, locals_dict)

    return (command, args)

def execute_file(filename, init_glocals = True):
    """
    Execute commands from a file.
    """
    finished = 0

    # initialize global/local dictionaries.
    if init_glocals:
        _init_twill_glocals()

    # reset browser
    commands.reset_state()
        
    lines = open(filename).readlines()

    n = 0
    for line in lines:
        n += 1
        
        if not line.strip():            # skip empty lines
            continue
        
        cmd, args = parse_command(line, global_dict, local_dict)

        if cmd == '#':                  # skip comments
            continue

        try:
            execute_command(cmd, args, global_dict, local_dict)
        except SystemExit:
            # abort script execution, if a SystemExit is raised.
            return
        except TwillAssertionError, e:
            sys.stderr.write('''\
Oops!  Twill assertion error on line %d of '%s' while executing
 
 >> %s
    
''' % (n, filename, line.strip(),))
            raise
        except Exception, e:
            sys.stderr.write("EXCEPTION raised at line %d of '%s'\n\n\t%s\n" % (n, filename, line.strip(),))
            sys.stderr.write(str(e))
            raise
