from autoquote import autoquote_if_necessary

def prefilter_autoquote_fn(self, line, continuation):
    if not continuation:
        line = autoquote_if_necessary("", line)

    return self._prefilter(line, continuation)
            
# Rebind this to be the new IPython prefilter:
from IPython.iplib import InteractiveShell
InteractiveShell.prefilter = prefilter_autoquote_fn

# Clean up the namespace.
del InteractiveShell, prefilter_autoquote_fn

# Just a heads up at the console
print '*** Twill autoquoting prefilter ENABLED.'
