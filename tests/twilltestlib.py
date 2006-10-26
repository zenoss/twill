import sys

try:
    import pkg_resources
except ImportError:
    raise Exception("you must have setuptools installed to run the tests")

pkg_resources.require('quixote>=2.3')

from quixote.server.simple_server import run
from cStringIO import StringIO
import os
import socket

child_pid = None
testdir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(testdir, '../'))

import twill

def cd_testdir():
    global cwd
    cwd = os.getcwd()
    os.chdir(testdir)

def pop_testdir():
    global cwd
    os.chdir(cwd)

def execute_twill_script(filename, inp=None, initial_url=None):
    global testdir
    
    if inp:
        inp_fp = StringIO(inp)
        old, sys.stdin = sys.stdin, inp_fp

    scriptfile = os.path.join(testdir, filename)
    try:
        twill.execute_file(filename, initial_url=initial_url)
    finally:
        if inp:
            sys.stdin = old

def execute_twill_shell(filename, inp=None, initial_url=None,
                        fail_on_unknown=False):
    # use filename as the stdin *for the shell object only*
    scriptfile = os.path.join(testdir, filename)
    
    cmd_inp = open(scriptfile).read()
    cmd_inp += '\nquit\n'
    cmd_inp = StringIO(cmd_inp)

    # use inp as the std input for the actual script commands.
    if inp:
        inp_fp = StringIO(inp)
        old, sys.stdin = sys.stdin, inp_fp

    try:
        try:
            s = twill.shell.TwillCommandLoop(initial_url=initial_url,
                                             stdin=cmd_inp,
                                             fail_on_unknown=fail_on_unknown)
            s.cmdloop()
        except SystemExit:
            pass
    finally:
        if inp:
            sys.stdin = old
    

def run_server(create_fn, PORT=None):
    """
    Run a Quixote simple_server on localhost:PORT by forking & then
    _exit.  All output is captured & thrown away..

    The parent process returns the URL on which the server is running.
    """
    global child_pid

    if PORT is None:
        PORT = int(os.environ.get('TWILL_TEST_PORT', '8080'))
    
    pid = os.fork()
    if pid != 0:
        child_pid = pid
        return 'http://localhost:%d/' % (PORT,)
    else:
        outp = StringIO()
        errp = StringIO()
        oldout, sys.stdout = sys.stdout, outp
        olderr, sys.stderr = sys.stderr, errp

        try:
            run(create_fn, port=PORT)
        except SystemExit:
            os._exit(0)
        except socket.error:
            raise                       # raise doesn't work???
        except Exception, e:
            oldout.write('SERVER ERROR: %s\n' % (str(e),))
            sys.stdout, sys.stderr = oldout, olderr
            raise                       # raise doesn't work???

        sys.exit(0)

def kill_server():
    """
    Kill the previously started Quixote server.
    """
    global child_pid
    if child_pid is not None:
        try:
            os.kill(child_pid, 9)
        finally:
            child_pid = None
