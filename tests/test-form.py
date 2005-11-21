import testlib
import twilltestserver
import twill
from twill import namespaces, commands
from twill.errors import TwillAssertionError

def setup():
    global url
    
    testlib.cd_testdir()
    url = testlib.run_server(twilltestserver.create_publisher)

def test():
    # test the twill script.
    testlib.execute_twill_script('test-form.twill', initial_url=url)

    # test empty page get_title
    namespaces.new_local_dict()
    twill.commands.reset_browser()
    browser = twill.get_browser_state()
    browser.get_title()

    # now test a few special cases
    commands.go(url)
    commands.go('/login')
    commands.showforms()
    try:
        commands.fv('2', 'submit', '1')
        assert 0
    except TwillAssertionError:
        pass

    commands.fv('1', '.*you', '1')

    commands.go('http://www.example.com/')
    browser.get_title()
    
def teardown():
    testlib.kill_server()
    testlib.pop_testdir()

if __name__ == '__main__':
    try:
        setup()
        test()
    finally:
        teardown()
