"""
Code parsing and evaluation for the twill mini-language.
"""

import sys
from errors import TwillAssertionError
from pyparsing import OneOrMore, Word, printables, quotedString, Optional, \
     alphas, alphanums, ParseException, ZeroOrMore, restOfLine, Combine, \
     Literal, Group, removeQuotes, CharsNotIn

import twill.commands as commands
import namespaces

### pyparsing stuff

# basically, a valid Python identifier:
command = Word(alphas + "_", alphanums + "_")
command = command.setResultsName('command')
command.setName("command")

# arguments to it.

# we need to reimplement all this junk from pyparsing because pcre's
# idea of escapable characters contains a lot more than the C-like
# thing pyparsing implements
_bslash = "\\"
_sglQuote = Literal("'")
_dblQuote = Literal('"')
_escapables = printables
_escapedChar = Word(_bslash, _escapables, exact=2)
dblQuotedString = Combine( _dblQuote + ZeroOrMore( CharsNotIn('\\"\n\r') | _escapedChar | '""' ) + _dblQuote ).streamline().setName("string enclosed in double quotes")
sglQuotedString = Combine( _sglQuote + ZeroOrMore( CharsNotIn("\\'\n\r") | _escapedChar | "''" ) + _sglQuote ).streamline().setName("string enclosed in single quotes")
quotedArg = ( dblQuotedString | sglQuotedString )
quotedArg.setParseAction(removeQuotes)
quotedArg.setName("quotedArg")

plainArgChars = printables.replace('#', '').replace('"', '').replace("'", "")
plainArg = Word(plainArgChars)
plainArg.setName("plainArg")

arguments = Group(ZeroOrMore(quotedArg | plainArg))
arguments = arguments.setResultsName('arguments')
arguments.setName("arguments")

# comment line.
comment = Literal('#') + restOfLine
comment = comment.suppress()
comment.setName('comment')

full_command = (
    comment
    | (command + arguments + Optional(comment))
    )
full_command.setName('full_command')

### command/argument handling.

def process_args(args, globals_dict, locals_dict):
    """
    Take a list of string arguments parsed via pyparsing and evaluate
    the special variables ('__*').

    Return a new list.
    """
    newargs = []
    for arg in args:
        # __variable substitution.  @CTB do we need this?
        if arg.startswith('__'):
            try:
                val = eval(arg, globals_dict, locals_dict)
            except NameError:           # not in dictionary; don't interpret.
                val = arg
                
            newargs.append(val)

        # $variable substitution
        elif arg.startswith('$'):
            try:
                val = eval(arg[1:], globals_dict, locals_dict)
            except NameError:           # not in dictionary; don't interpret.
                val = arg
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
    locals_dict['__url__'] = commands.browser.get_url()

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
            
        args = process_args(res.arguments.asList(), globals_dict, locals_dict)
        return (res.command, args)

    return None, None                   # e.g. a comment

###

def execute_file(filename, **kw):
    """
    Execute commands from a file.
    """
    # read the input lines
    if filename == "-":
        inp = sys.stdin
    else:
        inp = open(filename)

    kw['source'] = filename

    execute_script(inp, **kw)
    
def execute_script(inp, **kw):
    """
    Execute commands from a file-like iterator.
    """
    # initialize new local dictionary & get global + current local
    namespaces.new_local_dict()
    globals_dict, locals_dict = namespaces.get_twill_glocals()
    
    locals_dict['__url__'] = commands.browser.get_url()

    # reset browser
    if not kw.get('no_reset'):
        commands.reset_browser()

    # go to a specific URL?
    init_url = kw.get('initial_url')
    if init_url:
        commands.go(init_url)
        locals_dict['__url__'] = commands.browser.get_url()

    # sourceinfo stuff
    sourceinfo = kw.get('source', "<input>")
    
    try:

        n = 0
        for line in inp:
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

''' % (n, sourceinfo, line.strip(), e))
                raise
            except Exception, e:
                sys.stderr.write("EXCEPTION raised at line %d of '%s'\n\n\t%s\n" % (n, sourceinfo, line.strip(),))
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
        
