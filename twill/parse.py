"""
Code parsing and evaluation for the twill mini-language.
"""

import sys
from errors import TwillAssertionError
from pyparsing import OneOrMore, Word, printables, quotedString, Optional, \
     alphas, alphanums, ParseException, ZeroOrMore, restOfLine, Combine, \
     Literal

import twill.commands as commands
import namespaces

### pyparsing stuff

# basically, a valid Python identifier:
command = Word(alphas + "_", alphanums + "_")
command.setName("command")

# arguments to it.
arguments = OneOrMore(
    quotedString |
    Word(printables.replace('#', ''), printables) # ignore comments
    )
arguments.setName("arguments")

# comment line.
comment = Literal('#') + restOfLine
comment = comment.suppress()

full_command = comment ^ (command + Optional(arguments) + Optional(comment))

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

        # __variable substitution.  @CTB do we need this?
        elif arg.startswith('__'):
            val = eval(arg, globals_dict, locals_dict)
            newargs.append(val)

        # $variable substitution
        elif arg.startswith('$'):
            val = eval(arg[1:], globals_dict, locals_dict)
            newargs.append(val)
        else:
            newargs.append(arg)

    return newargs

###

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

    result = eval(eval_str, globals_dict, locals_dict)
    
    # set __url__
    locals_dict['__url__'] = commands.state.url()

    return result

###

_print_commands = False

def parse_command(line, globals_dict, locals_dict):
    """
    Parse command.
    """
    res = full_command.parseString(line)
    if res:
        if _print_commands:
            print "twill: executing cmd '%s'" % (line.strip(),)
            
        command = res[0]
        args = process_args(res[1:], globals_dict, locals_dict)

        return (command, args)

    return None, None                   # e.g. a comment

###

def execute_file(filename, **kw):
    """
    Execute commands from a file.
    """
    finished = 0

    # initialize new local dictionary & get global + current local
    namespaces.new_local_dict()
    globals_dict, locals_dict = namespaces.get_twill_glocals()
    
    local_dict = {}
    local_dict['__url__'] = commands.state.url()

    # reset browser
    commands.reset_state()

    # go to a specific URL?
    init_url = kw.get('initial_url')
    if init_url:
        commands.go(init_url)
        local_dict['__url__'] = commands.state.url()
        
    # read the input lines
    if filename == "-":
        input = sys.stdin
    else:
        input = open(filename)
    lines = input.readlines()

    try:

        n = 0
        for line in lines:
            n += 1

            if not line.strip():            # skip empty lines
                continue

            cmd, args = parse_command(line, globals_dict, locals_dict)
            if cmd is None:
                continue

            try:
                execute_command(cmd, args, globals_dict, locals_dict)
            except SystemExit:
                # abort script execution, if a SystemExit is raised.
                return
            except TwillAssertionError, e:
                sys.stderr.write('''\
Oops!  Twill assertion error on line %d of '%s' while executing

  >> %s

%s

''' % (n, filename, line.strip(), e))
                raise
            except Exception, e:
                sys.stderr.write("EXCEPTION raised at line %d of '%s'\n\n\t%s\n" % (n, filename, line.strip(),))
                sys.stderr.write("\nError message: '%s'\n" % (str(e).strip(),))
                sys.stderr.write("\n")
                raise

    finally:
        namespaces.pop_local_dict()

###

def debug_print_commands(flag):
    """
    Turn on/off printing of commands as they are executed.  'flag' is bool.
    """
    global _print_commands
    _print_commands = bool(flag)
        
