import sys, os
from StringIO import StringIO
import testlib
import twillserver
import twill

def setup():
    testlib.cd_testdir()
    testlib.run_server(twillserver.create_publisher)

def test():
    inp = StringIO("unique1\nunique2\n")
    old, sys.stdin = sys.stdin, inp
    try:
        scriptfile = os.path.join(testlib.testdir, 'test_twill.twill')
        twill.execute_file(scriptfile)
    finally:
        sys.stdin = old

def teardown():
    testlib.kill_server()
    testlib.pop_testdir()

if __name__ == '__main__':
    setup()
    test()
    teardown()
