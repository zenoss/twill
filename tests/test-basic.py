import testlib
import twilltestserver

def setup():
    testlib.cd_testdir()
    testlib.run_server(twilltestserver.create_publisher)

def test():
    inp = "unique1\nunique2\n"
    
    testlib.execute_twill_script('test_twill.twill', inp)
    
def teardown():
    testlib.kill_server()
    testlib.pop_testdir()

if __name__ == '__main__':
    setup()
    test()
    teardown()
