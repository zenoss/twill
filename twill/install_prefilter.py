import code

def prefilter_autoquote_fn(self, line, continuation):
    if not continuation:
        try:
            code.compile_command(line)
        except SyntaxError, e:
            l = line.split()
            cmd, rest = l[0], l[1:]
            rest = [ '"%s"' % (i.strip("\"'"),) for i in rest ]
            
            newcmd = cmd + "(" + ",".join(rest) + ")"
            print 'newcmd:', newcmd

            try:
                code.compile_command(newcmd)
                line = newcmd
            except:
                pass
            

    return self._prefilter(line, continuation)
            
# Rebind this to be the new IPython prefilter:
from IPython.iplib import InteractiveShell
InteractiveShell.prefilter = prefilter_autoquote_fn

# Clean up the namespace.
del InteractiveShell, prefilter_autoquote_fn

# Just a heads up at the console
print '*** Twill autoquoting prefilter ENABLED.'
