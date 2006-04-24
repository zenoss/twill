"""
Extension functions for parsing sys.argv.

Commands:

   get_args -- load all command-line arguments after -- into $arg0...$argN.
   
"""

def get_args():
    import sys
    from twill import commands, namespaces, shell

    global_dict, local_dict = namespaces.get_twill_glocals()

    for i, arg in enumerate(shell.twillargs):
        global_dict["arg%d" % (i,)] = arg

    print>>commands.OUT, "get_args: loaded %d args as $argN." % (i + 1,)
