import sys
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

def execute_twill_script(filename, inp=None):
    global testdir
    
    if inp:
        inp_fp = StringIO(inp)
        old, sys.stdin = sys.stdin, inp_fp

    scriptfile = os.path.join(testdir, filename)
    try:
        twill.execute_file(filename)
    finally:
        if inp:
            sys.stdin = old

def run_server(create_fn, PORT=8080):
    """
    Run a Quixote simple_server on localhost:PORT by forking & then
    _exit.  All output is captured & thrown away..
    """
    global child_pid
    
    pid = os.fork()
    if pid != 0:
        child_pid = pid
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
