import os
import testlib
import twilltestserver

def setup_module():
    testlib.cd_testdir()

    global url
    url = testlib.run_server(twilltestserver.create_publisher)

def test():
    testlib.execute_twill_script('test-find.twill', initial_url=url)
    
def teardown_module():
    testlib.kill_server()
    testlib.pop_testdir()

if __name__ == '__main__':
    try:
        setup()
        test()
    finally:
        teardown()
