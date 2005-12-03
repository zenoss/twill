import os
import testlib
import twilltestserver

n=0

def setup_module():
    global n
    
    n += 1
    if n > 1:
        raise Exception("ERRROR")
    
    print 'SETUP IS RUNNING'
    testlib.cd_testdir()

    global url
    url = testlib.run_server(twilltestserver.create_publisher)

def test():
    print 'TEST IS RUNNING'
    testlib.execute_twill_script('test-back.twill', initial_url=url)
    
def teardown_module():
    print 'TEARDOWN IS RUNNING'
    testlib.kill_server()
    testlib.pop_testdir()

if __name__ == '__main__':
    print 'MAIN IS RUNNING'
    try:
        setup()
        test()
    finally:
        teardown()
