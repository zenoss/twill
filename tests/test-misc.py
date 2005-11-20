import testlib
import twill, twill.browser, twill.commands

def setup():
    pass

def test():
    # get the current browser obj.
    browser = twill.get_browser_state()
    assert browser is twill.commands.browser
    
    try:
        twill.commands.exit()
        assert 0, "shouldn't get here"
    except SystemExit:
        pass

def teardown():
    pass
