"""
Autoquoting hacks.

(Don't quote me on that.)
"""

import re, code

def autoquote_if_necessary(previous, line):
    """
    Does this previous+line combo compile w/o syntax error?  If so,
    fine.  If not, try autoquoting & compiling.
    """
    try:
        codeobj = code.compile_command(previous + line)
    except SyntaxError, e:
        newcmd = autoquote(line)

        try:
            code.compile_command(previous + newcmd)
            line = newcmd
        except:
            pass
            
    return line

def autoquote(line):
    """
    Auto-quote arguments.
    """
    
    # save prefix whitespace, if any.
    whitespace = re.match('^(\s)+', line.rstrip())
    if whitespace:
        whitespace = whitespace.group()
    else:
        whitespace = ""

    # split up the line & try recomposing it with quotes.
    l = line.split()
    if l:
        cmd, rest = l[0], l[1:]

        # de-quote (remove ", ') on either side of each element.  This
        # prevents errors on double-quoting, at the expense of preventing
        # "'asdf'" quoting.
        
        rest = [ '"%s"' % (i.strip("\"'"),) for i in rest ]

        # recompose the command.
        newcmd = whitespace + cmd + "(" + ",".join(rest) + ")" + "\n"

        return newcmd
    
    return ""
