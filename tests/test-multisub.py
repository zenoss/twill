import testlib
import twilltestserver

def setup():
    testlib.cd_testdir()
    testlib.run_server(twilltestserver.create_publisher)

def test():
    testlib.execute_twill_script('test-multisub.twill')
    
def teardown():
    testlib.kill_server()
    testlib.pop_testdir()

if __name__ == '__main__':
    setup()
    test()
    teardown()
