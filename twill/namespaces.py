"""
Global and local dictionaries, + initialization/utility functions.
"""

import threading


thread_local = threading.local()


def init_global_dict():
    """
    Initialize global dictionary with twill commands.

    This must be done after all the other modules are loaded, so that all
    of the commands are already defined.
    """
    if not hasattr(thread_local, 'global_dict'):
        thread_local.global_dict = {}

    exec "from twill.commands import *" in thread_local.global_dict
    import twill.commands
    command_list = twill.commands.__all__
    
    import twill.parse
    twill.parse.command_list.extend(command_list)

###

# local dictionary management functions.

def new_local_dict():
    """
    Initialize a new local dictionary & push it onto the stack.
    """
    if not hasattr(thread_local, 'local_dict_stack'):
        thread_local.local_dict_stack = []

    d = {}
    thread_local.local_dict_stack.append(d)

    return d

def pop_local_dict():
    """
    Get rid of the current local dictionary.
    """
    thread_local.local_dict_stack.pop()

###

def get_twill_glocals():
    """
    Return global dict & current local dictionary.
    """
    global thread_local
    if not hasattr(thread_local, 'global_dict'):
        init_global_dict()

    assert thread_local.global_dict is not None, "must initialize global namespace first!"

    if len(thread_local.local_dict_stack) == 0:
        new_local_dict()

    return thread_local.global_dict, thread_local.local_dict_stack[-1]

###
