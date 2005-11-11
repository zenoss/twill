import os
import testlib
import twill.unit
import twilltestserver
from quixote.server.simple_server import run

def test():
    PORT=8090
    
    # create a function to run the server...
    def run_server_fn(run_fn=run, pub_fn=twilltestserver.create_publisher):
        run_fn(pub_fn, port=PORT)

    # 
    script = os.path.join(testlib.testdir, 'test-unit-support.twill')

    test_info = twill.unit.TestInfo(script, run_server_fn, PORT)

    twill.unit.run_test(test_info)

if __name__ == '__main__':
    test()
