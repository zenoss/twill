import testlib
import twilltestserver

def setup():
    global url
    
    testlib.cd_testdir()
    url = testlib.run_server(twilltestserver.create_publisher)

def test():
    testlib.execute_twill_script('test-multisub.twill', initial_url=url)
    
def teardown():
    testlib.kill_server()
    testlib.pop_testdir()

if __name__ == '__main__':
    try:
        setup()
        test()
    finally:
        teardown()
