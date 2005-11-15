import os
import testlib
import twilltestserver

def setup():
    testlib.cd_testdir()

    global url
    url = testlib.run_server(twilltestserver.create_publisher)

def test():
    testlib.execute_twill_script('test-http-codes.twill', initial_url=url)
    
def teardown():
    testlib.kill_server()
    testlib.pop_testdir()

if __name__ == '__main__':
    setup()
    test()
    teardown()
